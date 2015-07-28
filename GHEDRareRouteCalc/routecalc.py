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
    def GeneticSolverStart(self,popSize, maxGenerations, allSystems: [], maxStationDistance, routeLength, silent):
        '''
        Creates the initial population for the genetic algorithm and starts it running.
        Population is a list of EDRareRoutes
        '''
        population = []

        #check for max station distance and also exclude systems that require a permit to enter
        validSystems = [system for system in allSystems if system.Station_Distance <= maxStationDistance and "permit" not in system.System_Name]
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

        return self.__GeneticSolver(population,maxGenerations,validSystems, silent)

    @classmethod
    def __GeneticSolver(self,startingPopulation: [], maxGenerations: int, validSystems: [], silent):
        '''
        Actually does the solving. Goes through the population and, based on
        how close to the goal they are, picks 2 parent states. These states
        are then merged into a child that has a chance to be
        mutated. Children are created until they have a number equal to 
        the population. If a solution is found in these children, or if
        this is the last generation, the best of the children is 
        selected. 
        '''
        
        currentGeneration = 0
        currentPopulation = startingPopulation
        lastRouteFoundOn = currentGeneration
        mutationChance = 0.5
        
        goodRouteCutoff = 65
        #Just add this now so we don't have to worry about the list being empty
        #If it turns out to be the best... I guess we did a lot of work for nothing
        possibleRoutes = [max(currentPopulation,key=operator.attrgetter('Fitness_Value'))]

        #Don't really have a 'solved' state, so we just get best of each generation if it is better
        #Than our current best. We go until we hit the maxGenerations or until we go a certain number
        #of generations with no improvement.
        maxGenUntilExit = 2500
        while currentGeneration < maxGenerations and lastRouteFoundOn >= (currentGeneration-maxGenUntilExit):
            if (currentGeneration%500) == 0 and not silent:
                print("Generation: {0}".format(currentGeneration))
            currentGeneration += 1
            nextPopulation = []

            #Getting the best route in the current population
            bestRoute = max(currentPopulation,key=operator.attrgetter('Fitness_Value'))
            #The last element of the possibleRoutes list should be the max, so we don't need to call max
            if bestRoute.Fitness_Value > possibleRoutes[0].Fitness_Value:
                if not silent:
                    print("\t{0} -> {1}".format(currentGeneration,bestRoute.Fitness_Value))
                possibleRoutes[0] = bestRoute
                lastRouteFoundOn = currentGeneration
                if bestRoute.Fitness_Value > goodRouteCutoff:
                    possibleRoutes.append(bestRoute)

            relativeFitnessVals = self.__CalculateRelativeFitness(currentPopulation)
            for i in range(0,currentPopulation.__len__()):
                child = self.__Reproduce(currentPopulation,relativeFitnessVals)
                if random.random() <= mutationChance:
                    child = self.__Mutate(child,validSystems)
                nextPopulation.append(EDRareRoute(child))

            currentPopulation = nextPopulation

        return possibleRoutes

    @classmethod
    def __CalculateRelativeFitness(self, population: []):
        '''
        We rank each route relative to the others in the population.
        We then assign them a value such that values[0] is percent[0] and values[pop-1] is 1
        '''
        percentages = []
        total = sum([route.Fitness_Value for route in population])
        for value in [route.Fitness_Value for route in population]:
            percentages.append(value/total * 1.0)
               
        selectionValues = [percentages[0]]
        for i in range(1,percentages.__len__()):
            selectionValues.append(percentages[i] + selectionValues[i-1])
        return selectionValues
    
    @classmethod
    def __Reproduce(self, population: [], selectionValues: []): 
        '''
        Chooses 2 parent nodes based on relative goodness of the population.
        A child node is created by combining the parent nodes
        '''
              
        #Get the parents
        parents = []
        while parents.__len__() != 2:
            value = random.uniform(0,1)
            i = 0
            while True:
                currentSelection = None
                if value <= selectionValues[i]:
                    currentSelection = population[i]
                    #if parents.count(currentSelection) == 0:
                    parents.append(currentSelection)
                    break
                i += 1
        #Create the new child
        route1 = parents[0].GetRoute()
        route2 = parents[1].GetRoute()
        pivot = random.randrange(route1.__len__())
        newRoute = []

        if random.randrange(0,sys.maxsize)%2 == 0:
            for i in range(0,pivot):
                newRoute.append(route1[i])
            for i in range(0,route2.__len__()):
                toAdd = route2[i]
                if newRoute.count(toAdd) != 0:
                    continue
                if newRoute.__len__() != route2.__len__():
                    newRoute.append(toAdd)
        else:
            for i in range(0,pivot):
                newRoute.append(route2[i])
            for i in range(0,route1.__len__()):
                toAdd = route1[i]
                if newRoute.count(toAdd) != 0:
                    continue
                if newRoute.__len__() != route1.__len__():
                    newRoute.append(toAdd)
        #print(parents)
        #input("wait")
        return newRoute
        
    @classmethod
    def __Mutate(self,route: [], validSystems: []):
        tempRoute = [val for val in route]
        
        #Going to do a 80/20 split for replacing systems or shuffling the route
        mutateType = random.random()
        if mutateType < 0.20:
            #shuffle route
            random.shuffle(tempRoute)
        else:
            #change up to half the systems in a route
            numSystemsToChange = random.randrange(1,math.ceil(tempRoute.__len__()/2))
            for i in range(0, numSystemsToChange):
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
        goodRouteCutoff = 65
        validSystems = [system for system in allSystems if system.Station_Distance <= maxStationDistance and "permit" not in system.System_Name ]
        if validSystems.__len__() < routeLength:
            print("Not enough systems for a route...")
            return []
        allRoutes = itertools.permutations(validSystems,routeLength)
        for route in allRoutes:
            current = EDRareRoute(route)
            if current.Fitness_Value >= goodRouteCutoff:
                goodRoutes.append(current)

        return sorted(goodRoutes,key=operator.attrgetter('Fitness_Value'))
