from edsystem import EDSystem
from edrareroute import EDRareRoute
import random
import math
import sys
import operator
import itertools

class RouteCalc(object):
    '''
    Class for calculating rare trade routes
    '''
    @classmethod
    def GeneticSolverStart(self,popSize, maxGenerations, allSystems: [], maxStationDistance, routeLength):
        '''
        Creates the initial population for the genetic algorithm and starts it running.
        Population is a list of EDRareRoutes
        '''
        population = []

        #check for max station distance and also exclude systems that require a permit to enter
        validSystems = [system for system in allSystems if system.Station_Distance <= maxStationDistance and "permit" not in system.System_Name ]
        if validSystems.__len__() < routeLength:
            print("Not enough systems for a route...")
            return

        for i in range(0,popSize):
            tempSystemList = []
            for j in range(0,routeLength):
                tempSystem = validSystems[random.randrange(0,validSystems.__len__())]
                   
                #Need to avoid duplicates
                while tempSystemList.count(tempSystem) != 0:
                    tempSystem = validSystems[random.randrange(0,validSystems.__len__())]
                tempSystemList.append(tempSystem)
            population.append(EDRareRoute(tempSystemList))

        return self.__GeneticSolver(population,maxGenerations,validSystems)

    @classmethod
    def __GeneticSolver(self,startingPopulation: [], maxGenerations: int, validSystems: []):
        '''
        Actually does the solving. Goes through the population and, based on
        how close to the goal they are, picks 2 parent states. These states
        are then merged into a child that has a low (5%) chance to be
        mutated. Children are created until they have a number equal to 
        the population. If a solution is found in these children, or if
        this is the last generation, the best of the children is 
        selected.
        '''
        
        currentGeneration = 0
        currentPopulation = startingPopulation
        lastRouteFoundOn = currentGeneration
        
        #Just add this now so we don't have to worry about the list being empty
        #If it turns out to be the best... I guess we did a lot of work for nothing
        possibleRoutes = [max(currentPopulation,key=operator.attrgetter('Fitness_Value'))]

        #Don't really have a 'solved' state, so we just get best of each generation if it is better
        #Than our current best. We go until we hit the maxGenerations or until we go a certain number
        #of generations with no improvement.
        while currentGeneration < maxGenerations and lastRouteFoundOn >= (currentGeneration-5000):
            if (currentGeneration%500) == 0:
                print("Generation: {0}".format(currentGeneration))
            currentGeneration += 1
            nextPopulation = []

            #Getting the best route in the current population
            bestRoute = max(currentPopulation,key=operator.attrgetter('Fitness_Value'))
            if bestRoute.Fitness_Value > possibleRoutes[-1].Fitness_Value:
                print("\tpotential route found: generation {0}".format(currentGeneration))
                lastRouteFoundOn = currentGeneration
                possibleRoutes.append(bestRoute)

            for i in range(0,currentPopulation.__len__()):
                parents = self.__SelectParents(currentPopulation)
                child = self.__Reproduce(parents)
                if random.random() <= 0.05:
                    child = self.__Mutate(child,validSystems)
                nextPopulation.append(EDRareRoute(child))

            currentPopulation = nextPopulation

        return possibleRoutes


    @classmethod
    def __SelectParents(self,population: []):       
        '''
        Returns a list of size 2 with the chosen parents.
        Parents are chosen based on how good the route is.
        We rank each route relative to the others in the population.
        We then assign them a value such that values[0] is percent[0] and values[pop-1] is 1
        Rand is called and the closest value over is chosen

        TODO: Find why the percentages and selectionValues lists sometimes have pop+1 elements
                    (maybe only when debugging?)
              Change this to scale at a higher value... percentages my get too small with very large
                    populations
        '''
        percentages = []
        total = sum([route.Fitness_Value for route in population])
        for value in [route.Fitness_Value for route in population]:
            percentages.append(value/total * 1.0)
       
        #print("percent: {0}".format(percentages.__len__()))
        #print("pop: {0}".format(population.__len__()))
        
        parents = []
        selectionValues = [percentages[0]]
        for i in range(1,percentages.__len__()):
            selectionValues.append(percentages[i] + selectionValues[i-1])

        #print("values: {0}".format(selectionValues.__len__()))

        while parents.__len__() != 2:
            #uniform(0,1) might be the same as random()? looks like we can get 0.9999999999999 which is good enough
            value = random.uniform(0,1)
            for i in range(0,population.__len__()):
                #stopping at the first selectionValue greater than the random value
                if value <= selectionValues[i]:
                    #Again, we need to avoid duplicates
                    if parents.count(population[i]) == 0:
                        parents.append(population[i])
                    # Need to break out so the loop starts again with a new value to check
                    break
        return parents

    @classmethod
    def __Reproduce(self,parents: [2]):
        '''
        Returns a new state based off the 2 parents states.
        Rand is used to determine which board is copied first
        '''
        route1 = parents[0].GetRoute()
        route2 = parents[1].GetRoute()
        pivot = random.randrange(route1.__len__())
        newRoute = []

        if random.randrange(0,sys.maxsize)%2 == 0:
            for i in range(0,pivot):
                newRoute.append(route1[i])
            for i in range(0,route2.__len__()):
                toAdd = route2[i]
                if newRoute.count(toAdd) != 0:  #and newRoute.__len__() != route2.__len__():
                    continue
                if newRoute.__len__() != route2.__len__():
                    newRoute.append(toAdd)
        else:
            for i in range(0,pivot):
                newRoute.append(route2[i])
            for i in range(0,route1.__len__()):
                toAdd = route1[i]
                if newRoute.count(toAdd) != 0: #and newRoute.__len__() != route1.__len__():
                    continue
                if newRoute.__len__() != route1.__len__():
                    newRoute.append(toAdd)
        return newRoute
    @classmethod
    def __Mutate(self,route: [], validSystems: []):
        '''
        TODO: Modify to allow more types of mutation:
                    Chance to simply shuffle around the systems
                    Chance to replace X number of systems instead of just 1
                    Reasoning: It is possible to have a great group of systems that are just in the wrong order.
                               Need to try and give these groups a chance to like...actually be great
        '''
        #tempRoute = route.GetRoute()
        tempRoute = [val for val in route]
        systemToChange = random.randrange(0,tempRoute.__len__())
        newSystem = validSystems[random.randrange(0,validSystems.__len__())]                 
        #Need to avoid duplicates
        while tempRoute.count(newSystem) != 0:
            newSystem = validSystems[random.randrange(0,validSystems.__len__())]
        tempRoute[systemToChange] = newSystem

        return tempRoute

    @classmethod
    def Brute(self, allSystems: [], maxStationDistance, routeLength):
        goodRoutes = []
        validSystems = [system for system in allSystems if system.Station_Distance <= maxStationDistance and "permit" not in system.System_Name ]
        if validSystems.__len__() < routeLength:
            print("Not enough systems for a route...")
            return
        allRoutes = itertools.permutations(validSystems,routeLength)
        for route in allRoutes:
            current = EDRareRoute(route)
            if current.Fitness_Value >= 10 * routeLength:
                goodRoutes.append(current)

        return sorted(goodRoutes,key=operator.attrgetter('Fitness_Value'))
