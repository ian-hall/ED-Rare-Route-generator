from edsystem import EDSystem
from edrareroute import EDRareRoute
import random
import math
import sys
import operator
import itertools
import bisect

class RouteCalc(object):
    '''
    Class for calculating rare trade routes
    '''
    Route_Cutoff = 14
    @classmethod
    def GeneticSolverStart(self,popSize, validSystems: [], routeLength, silent):
        '''
        Creates the initial population for the genetic algorithm and starts it running.
        Population is a list of EDRareRoutes
        '''
        population = []

        if validSystems.__len__() < routeLength:
            print("Not enough systems for a route...")
            return

        for i in range(0,popSize):
            tempSystemList = []
            for j in range(0,routeLength):
                tempSystem = random.choice(validSystems)
                   
                #Need to avoid duplicates
                while tempSystemList.count(tempSystem) != 0:
                    tempSystem = random.choice(validSystems)
                tempSystemList.append(tempSystem)
            population.append(EDRareRoute(tempSystemList))

        return self.__GeneticSolver(population,validSystems, silent)

    @classmethod
    def __GeneticSolver(self,startingPopulation: [], validSystems: [], silent):
        '''
        Actually does the solving. Goes through the population and, based on
        how close to the goal they are, picks 2 parent states. These states
        are then merged into a child that has a chance to be
        mutated. Children are created until they have a number equal to 
        the population. If a solution is found in these children, or if
        this is the last generation, the best of the children is 
        selected. 
        '''
        
        currentGeneration = 1
        currentPopulation = startingPopulation
        lastRouteFoundOn = currentGeneration
        baseMutation = 0.05
        mutationChance = baseMutation
        
        #Just keep track of the single best route
        bestRoute = max(currentPopulation,key=operator.attrgetter('Fitness_Value'))

        #Want the program to keep running until it finds something, which it will eventually.
        #Going to increase the mutation chance for every couple generations it goes without increasing
        #the value of the best route.
        mutationIncrease = 0.43
        timeBetweenIncrease = 1200
        lastIncrease = currentGeneration

        #Force an exit if X generations pass with no improvement
        maxGensSinceLast = 3*timeBetweenIncrease

        while True:    
            possibleRoute = max(currentPopulation,key=operator.attrgetter('Fitness_Value'))

            if not silent:
                if (currentGeneration%500) == 0:
                    print("Generation: {0}".format(currentGeneration))
                if currentGeneration == 1:
                    print("Starting value: {0}".format(possibleRoute.Fitness_Value))

            currentGeneration += 1
            nextPopulation = []

            if possibleRoute.Fitness_Value > bestRoute.Fitness_Value:
                if not silent:
                    print("\t{0} -> {1}".format(currentGeneration,possibleRoute.Fitness_Value))
                bestRoute = possibleRoute
                lastRouteFoundOn = currentGeneration
                #Reset mutation chance when finding a new best route
                mutationChance = baseMutation

            #Exit if we are at least at the Route_Cutoff value and going to increase the mutation chance this gen
            if bestRoute.Fitness_Value >= RouteCalc.Route_Cutoff and currentGeneration - lastRouteFoundOn >= timeBetweenIncrease:
                break
            
            #Exit if it has been X generations since last found route
            if currentGeneration - lastRouteFoundOn >= maxGensSinceLast:
                break

            #Should probably check to make sure this stops at 1 but I guess it doesnt really matter since random() always returns < 1
            if currentGeneration - lastRouteFoundOn >= timeBetweenIncrease and (currentGeneration - lastIncrease) >= timeBetweenIncrease:
                mutationChance += mutationIncrease
                lastIncrease = currentGeneration
                if not silent:
                    print("\tCurrent mutation chance: {0}".format(mutationChance))

            relativeFitnessVals = self.__CalculateRelativeFitness(currentPopulation)
            
            
            for i in range(0,currentPopulation.__len__()):
                child = self.__Reproduce(currentPopulation,relativeFitnessVals)
                if random.random() <= mutationChance:
                    child = self.__Mutate(child,validSystems)
                nextPopulation.append(EDRareRoute(child))

            currentPopulation = nextPopulation

        return (bestRoute,currentGeneration)

    @classmethod
    def __CalculateRelativeFitness(self, population: []):
        '''
        We rank each route relative to the others in the population.
        We then assign them a value such that values[0] is percent[0] and values[pop-1] is
        120% the size of the population
        '''
        #percentages = []
        upperVal = math.ceil(population.__len__() * 1.2)
        total = sum([route.Fitness_Value for route in population])
        
        #for value in [route.Fitness_Value for route in population]:
        #    percentages.append(value/total * 1000)
               
        #selectionValues = [percentages[0]]
        #for i in range(1,percentages.__len__()):
        #    selectionValues.append(percentages[i] + selectionValues[i-1])

        selectionValues = [population[0].Fitness_Value/total * upperVal]
        for i in range(1,population.__len__()):
            percentTotal = population[i].Fitness_Value/total * upperVal
            selectionValues.append(percentTotal + selectionValues[i-1])

        
        return selectionValues
    
    @classmethod
    def __Reproduce(self, population: [], selectionValues: []): 
        '''
        Chooses 2 parent nodes based on relative goodness of the population.
        A child node is created by combining the parent nodes
        Upper end of rand.uni is equal to 120% the size of the population
        '''
              
        #Get the parents
        parents = []
        while parents.__len__() != 2:
            value = random.uniform(0,math.ceil(population.__len__() * 1.2))
            parents.append(population[bisect.bisect(selectionValues,value)])
            '''
            i = 0
            while True:
                currentSelection = None
                if value <= selectionValues[i]:
                    currentSelection = population[i]
                    parents.append(currentSelection)
                    break
                i += 1
            '''
        #Create the new child
        route1 = parents[0].GetRoute()
        route2 = parents[1].GetRoute()
        pivot = random.randrange(1,route1.__len__()-1)
        newRoute = []

        if random.randrange(sys.maxsize)%2 == 0:
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

        return newRoute
        
    @classmethod
    def __Mutate(self,route: [], validSystems: []):
        tempRoute = [val for val in route]
        
        #Have a chance to either shuffle the route or introduce new systems in the route
        mutateType = random.random()
        if mutateType < 0.1:
            #shuffle route
            random.shuffle(tempRoute)
        else:
            #change up to half the systems in a route
            #TODO: Avoid replacing the same system more than once
            numSystemsToChange = random.randrange(1,math.ceil(tempRoute.__len__()/2))
            for i in range(0, numSystemsToChange):
                systemToChange = random.randrange(tempRoute.__len__())
                newSystem = random.choice(validSystems)            
                #Need to avoid duplicates
                while tempRoute.count(newSystem) != 0:
                    newSystem = random.choice(validSystems) 
                tempRoute[systemToChange] = newSystem    

        return tempRoute

    @classmethod
    def Brute(self, validSystems: [], routeLength):
        
        goodRoutes = []
        goodRouteCutoff = RouteCalc.Route_Cutoff
        
        if validSystems.__len__() < routeLength:
            print("Not enough systems for a route...")
            return []
        for route in itertools.permutations(validSystems,routeLength):
            current = EDRareRoute(route)
            if current.Fitness_Value >= self.Route_Cutoff:
                goodRoutes.append(current)
        
        return sorted(goodRoutes,key=operator.attrgetter('Fitness_Value'))
    
    @classmethod
    def MP_Helper(self,route):
        newRoute = EDRareRoute(route)
        if newRoute.Fitness_Value > RouteCalc.Route_Cutoff:
            print(newRoute)