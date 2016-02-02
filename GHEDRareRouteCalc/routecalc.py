﻿from edsystem import EDSystem
from edrareroute import EDRareRoute, FitnessType
import random
import math
import operator
import itertools
import bisect
from multiprocessing import Pool

class RouteCalc(object):
    '''
    Class for calculating rare trade routes
    '''
    Route_Cutoff = 11.5
    __Selection_Mult = .25
    __Pool_Size = 3
    __Valid_Systems = []
    __Fit_Type = FitnessType.Default
#------------------------------------------------------------------------------
    @classmethod
    def GeneticSolverStart(self,popSize, validSystems: [], routeLength, silent, fitType = FitnessType.Default):
        '''
        Creates the initial population for the genetic algorithm and starts it running.
        Population is a list of EDRareRoutes
        '''
        if routeLength < 3 or routeLength > 50:
            raise Exception("Routes need length between 3 and XX")
        RouteCalc.__Fit_Type = fitType

        population = []
        RouteCalc.__Valid_Systems = validSystems
        
        if RouteCalc.__Valid_Systems.__len__() < routeLength:
            print("Not enough systems for a route...")
            return

        tempPopulation = []
        for i in range(0,popSize):
            tempSystemList = []
            for j in range(0,routeLength):
                tempSystem = random.choice(validSystems)                  
                #Need to avoid duplicates
                while tempSystemList.count(tempSystem) != 0:
                    tempSystem = random.choice(validSystems)
                tempSystemList.append(tempSystem)
            population.append(EDRareRoute(tempSystemList,RouteCalc.__Fit_Type))

        return self.__GeneticSolver(population,silent)
#------------------------------------------------------------------------------
    @classmethod
    def __GeneticSolver(self,startingPopulation: [], silent):
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

        #Want the program to keep running until it finds something, which it will eventually (maybe).
        #Going to increase the mutation chance for every couple generations it goes without increasing
        #the value of the best route.
        mutationIncrease = 0.35
        timeBetweenIncrease = 400
        lastIncrease = currentGeneration
        numIncreases = 0
        maxIncreases = 2

        #Force an exit if X generations pass with no improvement
        maxGensSinceLast = (maxIncreases+1)*timeBetweenIncrease

        while True:    
            possibleRoute = max(currentPopulation,key=operator.attrgetter('Fitness_Value'))

            if not silent:
                if currentGeneration == 1:
                    print("Starting value: {0:.5f}".format(possibleRoute.Fitness_Value))

            currentGeneration += 1
            nextPopulation = []

            if possibleRoute.Fitness_Value > bestRoute.Fitness_Value:
                if not silent:
                    print("{0:>7}-> {1:.5f}".format(currentGeneration,possibleRoute.Fitness_Value))
                bestRoute = possibleRoute
                lastRouteFoundOn = currentGeneration
                #Reset mutation chance when finding a new best route
                if mutationChance != baseMutation:
                    mutationChance = baseMutation
                    if not silent:
                        print("{0:>7}-> mutation chance: {1:.1f}%".format("",mutationChance*100))

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
                currentPopulation = sorted(currentPopulation,key=operator.attrgetter('Fitness_Value'))
                #Replace a percentage of the routes with lowest values, maybe make this smart to not include adding systems already commonly in the top routes
                numReplace = math.ceil(currentPopulation.__len__() * .75)
                tempPop = []
                for i in range(0,numReplace):
                    tempSystemList = []
                    for j in range(0,bestRoute.GetRoute().__len__()):
                        tempSystem = random.choice(RouteCalc.__Valid_Systems)                   
                        #Need to avoid duplicates
                        while tempSystemList.count(tempSystem) != 0:
                            tempSystem = random.choice(RouteCalc.__Valid_Systems)
                        tempSystemList.append(tempSystem)
                    tempPop.append(tempSystemList)
                for i in range(0,numReplace):
                    currentPopulation[i] = EDRareRoute(tempPop[i],RouteCalc.__Fit_Type)


                if not silent:
                    print("{0:>7}-> mutation chance: {1:.1f}%".format(currentGeneration,mutationChance*100))

            relativeFitnessVals = self.__CalculateRelativeFitness(currentPopulation)

            #for i in range(0,currentPopulation.__len__()):
            while nextPopulation.__len__() != currentPopulation.__len__():
                children = self.__Reproduce(currentPopulation,relativeFitnessVals)
                child1 = children[0]
                child2 = children[1]
                if random.random() <= mutationChance:
                    child1 = self.__Mutate(child1)
                    child2 = self.__Mutate(child2)
                nextPopulation.append(EDRareRoute(child1,RouteCalc.__Fit_Type))
                if nextPopulation.__len__() < currentPopulation.__len__():
                    nextPopulation.append(EDRareRoute(child2,RouteCalc.__Fit_Type))

            currentPopulation = nextPopulation

        return (bestRoute,currentGeneration)
#------------------------------------------------------------------------------
    @classmethod
    def __CalculateRelativeFitness(self, population: []):
        '''
        We rank each route relative to the others in the population.
        We then assign them a value such that values[0] is percent[0] and values[pop-1] is
        X times the population size, set by __Selection_Mult
        '''
        #percentages = []
        upperVal = population.__len__() * RouteCalc.__Selection_Mult
        total = sum([route.Fitness_Value for route in population])     

        selectionValues = [population[0].Fitness_Value/total * upperVal]
        for i in range(1,population.__len__()):
            percentTotal = population[i].Fitness_Value/total * upperVal
            selectionValues.append(percentTotal + selectionValues[i-1])

        
        return selectionValues
#------------------------------------------------------------------------------
    @classmethod
    def __Reproduce(self, population: [], selectionValues: []): 
        '''
        Chooses 2 parent nodes based on relative goodness of the population.
        A child node is created by combining the parent nodes
        Upper end of rand.uni is X times the population size, set by __Selection_Mult
        '''      
        #Get the parents
        parents = []
        while parents.__len__() != 2:
            value = random.uniform(0,population.__len__() * RouteCalc.__Selection_Mult)
            parent = population[bisect.bisect(selectionValues,value)]
            while parents.count(parent) != 0:
                value = random.uniform(0,population.__len__() * RouteCalc.__Selection_Mult)
                parent = population[bisect.bisect(selectionValues,value)]
            parents.append(parent)
        #Create the new child
        route1 = parents[0].GetRoute()
        route2 = parents[1].GetRoute()
        if route1.__len__() != route2.__len__():
            raise Exception("Routes of uneven length")
        routeLength = route1.__len__()
        pivot = random.randrange(1,routeLength-1)
        child1 = []
        child2 = []

        #TODO: Maybe combine these loops since they have the same bounds
        for i in range(0,pivot):
            child1.append(route1[i])
        i = pivot
        while child1.__len__() != routeLength:
            toAdd = route2[i%routeLength]
            if child1.count(toAdd) != 0:
                i += 1
                continue
            child1.append(toAdd)
            i += 1

        for i in range(0,pivot):
            child2.append(route2[i])
        i = pivot
        while child2.__len__() != routeLength:
            toAdd = route1[i%routeLength]
            if child2.count(toAdd) != 0:
                i += 1
                continue
            child2.append(toAdd)
            i += 1

        #if random.randrange(281)%2 == 0:
            #Start with route1    
        #i = pivot
        #while child1.__len__() != routeLength and child2.__len__() != routeLength:
        #    toAdd1 = route2[i%routeLength]
        #    if child1.count(toAdd1) != 0:
        #        pass
        #    if child1.__len__() != routeLength:
        #        child1.append(toAdd1)

        #    toAdd2 = route1[i%routeLength]
        #    if child2.count(toAdd2) != 0:
        #        pass
        #    if child2.__len__() != routeLength:
        #        child2.append(toAdd2)
            
        #    i += 1
        #else:
        #    #Start with route2
        #    for i in range(0,pivot):
        #        child1.append(route2[i])
        #    for i in range(pivot, pivot + routeLength):
        #        toAdd = route1[i%routeLength]
        #        if child1.count(toAdd) != 0:
        #            continue
        #        if child1.__len__() != routeLength:
        #            child1.append(toAdd)

        return (child1,child2)
#------------------------------------------------------------------------------ 
    @classmethod
    def __Mutate(self,route: []):
        tempRoute = [val for val in route]
        
        #Have a chance to either shuffle the route or introduce new systems in the route
        mutateType = random.random()
        if mutateType < 0.2:
            #shuffle route
            random.shuffle(tempRoute)
        else:
            #change up to half the systems in a route
            numSystemsToChange = random.randrange(1,math.ceil(tempRoute.__len__()/2))
            changedSystems = []
            for i in range(0, numSystemsToChange):
                
                systemToChange = random.randrange(tempRoute.__len__())
                while changedSystems.count(systemToChange) != 0 :
                    systemToChange = random.randrange(tempRoute.__len__())
                changedSystems.append(systemToChange)
                
                newSystem = random.choice(RouteCalc.__Valid_Systems)            
                while tempRoute.count(newSystem) != 0:
                    newSystem = random.choice(RouteCalc.__Valid_Systems) 
                tempRoute[systemToChange] = newSystem    

        return tempRoute
#------------------------------------------------------------------------------
    @classmethod
    def Brute(self, validSystems: [], routeLength):
        RouteCalc.__Valid_Systems = validSystems
        if RouteCalc.__Valid_Systems.__len__() < routeLength:
            print("Not enough systems for a route...")
            return []
        
        tempBrute = []
        fullResults = []
        num = 0
        print("Starting brute force method...")
        #Combinations instead of permutations because we are playing "fast" and loose here
        for sysList in itertools.combinations(RouteCalc.__Valid_Systems,routeLength):
            if tempBrute.__len__() < 10000000:
                tempBrute.append(sysList)
                num += 1
            else:
                print("Processing: {0}".format(num))
                with Pool(RouteCalc.__Pool_Size) as p:
                    results = p.map(RouteCalc.BruteHelper,tempBrute)
                fullResults.extend([val for val in results if val])
                tempBrute = [sysList]
                num += 1
        print("Processing: {0}".format(num))
        with Pool(RouteCalc.__Pool_Size) as p:
            results = p.map(RouteCalc.BruteHelper,tempBrute)
        fullResults.extend([val for val in results if val])
        return sorted(fullResults,key=operator.attrgetter('Fitness_Value'))
#------------------------------------------------------------------------------
    @classmethod
    def BruteHelper(self,systemList):
        newRoute = EDRareRoute(systemList)
        if newRoute.Fitness_Value > RouteCalc.Route_Cutoff:
            return newRoute
        else:
            return None
#------------------------------------------------------------------------------