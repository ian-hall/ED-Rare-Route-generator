from edsystem import EDSystem
from edrareroute import EDRareRoute, FitnessType
import random
import math
import operator
import bisect

class RouteCalc(object):
    '''
    Class for calculating rare trade routes
    '''
    Route_Cutoff = 11.5
    __Selection_Mult = .25
    __Pool_Size = 3
    __Valid_Systems = []
    __Fit_Type = FitnessType.EvenSplit
#------------------------------------------------------------------------------
    @classmethod
    def GeneticSolverStart(cls,popSize: int, validSystems: list, routeLength: int, silent: bool, fitType: FitnessType) -> tuple:
        '''
        Creates the initial population for the genetic algorithm and starts it running.
        Population is a list of EDRareRoutes
        '''
        #TODO: Eventually add something here that calculates popSize based on route length
        RouteCalc.__Fit_Type = fitType
        if RouteCalc.__Fit_Type == FitnessType.EvenSplit:
            if routeLength < 3 or routeLength > 15:
                raise Exception("Split routes must have lengths [3-15]")
        else:
            if routeLength < 6 or routeLength > 55:
                raise Exception("Alternate type routes must have lengths [6-XX]")
            


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

        return cls.__GeneticSolver(population,silent)
#------------------------------------------------------------------------------
    @classmethod
    def __GeneticSolver(cls,startingPopulation: list, silent: bool) -> tuple:
        '''
        Actually does the solving. Goes through the population and, based on
        how close to the goal they are, picks 2 parents to merge/shuffle/mutate
        until a new population is ready.
        '''
        
        currentGeneration = 1
        currentPopulation = startingPopulation
        lastRouteFoundOn = currentGeneration
        baseMutation = 0.05
        mutationChance = baseMutation
        
        #Just keep track of the single best route
        bestRoute = max(currentPopulation,key=operator.methodcaller('GetFitValue'))

        #Want the program to keep running until it finds something, which it will eventually (maybe).
        #Going to increase the mutation chance for every couple generations it goes without increasing
        #the value of the best route.
        mutationIncrease = 0.35
        timeBetweenIncrease = 400
        cutoffAfterRouteFound = 100
        lastIncrease = currentGeneration
        numIncreases = 0
        maxIncreases = 2

        #Force an exit if X generations pass with no improvement
        maxGensSinceLast = (maxIncreases+1)*timeBetweenIncrease

        while True:    
            possibleRoute = max(currentPopulation,key=operator.methodcaller('GetFitValue'))

            if not silent:
                if currentGeneration == 1:
                    print("Starting value: {0:.5f}".format(possibleRoute.GetFitValue()))

            currentGeneration += 1
            nextPopulation = []

            if possibleRoute.GetFitValue() > bestRoute.GetFitValue():
                if not silent:
                    print("{0:>7}-> {1:.5f}".format(currentGeneration,possibleRoute.GetFitValue()))
                bestRoute = possibleRoute
                lastRouteFoundOn = currentGeneration
                #Reset mutation chance when finding a new best route
                if mutationChance != baseMutation:
                    mutationChance = baseMutation
                    if not silent:
                        print("{0:>7}-> mutation chance: {1:.1f}%".format("",mutationChance*100))

            #Exit if we are at least at the Route_Cutoff value and its been X generations since last increase
            if bestRoute.GetFitValue() >= RouteCalc.Route_Cutoff and currentGeneration - lastRouteFoundOn >= cutoffAfterRouteFound:
                break
            
            #Exit if it has been X generations since last found route
            if currentGeneration - lastRouteFoundOn >= maxGensSinceLast:
                break

            if currentGeneration - lastRouteFoundOn >= timeBetweenIncrease and (currentGeneration - lastIncrease) >= timeBetweenIncrease:
                mutationChance += mutationIncrease
                lastIncrease = currentGeneration
                currentPopulation = sorted(currentPopulation,key=operator.methodcaller('GetFitValue'))
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

            relativeFitnessVals = cls.__CalculateRelativeFitness(currentPopulation)

            while nextPopulation.__len__() != currentPopulation.__len__():
                children = cls.__Reproduce(currentPopulation,relativeFitnessVals)
                child1 = children[0]
                child2 = children[1]
                if random.random() <= mutationChance:
                    child1 = cls.__Mutate(child1)
                    child2 = cls.__Mutate(child2)
                nextPopulation.append(EDRareRoute(child1,RouteCalc.__Fit_Type))
                if nextPopulation.__len__() < currentPopulation.__len__():
                    nextPopulation.append(EDRareRoute(child2,RouteCalc.__Fit_Type))

            currentPopulation = nextPopulation

        return (bestRoute,currentGeneration)
#------------------------------------------------------------------------------
    @classmethod
    def __CalculateRelativeFitness(cls, population: list) -> list:
        '''
        We rank each route relative to the others in the population.
        We then assign them a value such that values[0] is percent[0] and values[pop-1] is
        X times the population size, set by __Selection_Mult
        '''
        upperVal = population.__len__() * RouteCalc.__Selection_Mult
        total = sum([route.GetFitValue() for route in population])     

        selectionValues = [population[0].GetFitValue()/total * upperVal]
        for i in range(1,population.__len__()):
            percentTotal = population[i].GetFitValue()/total * upperVal
            selectionValues.append(percentTotal + selectionValues[i-1])

        
        return selectionValues
#------------------------------------------------------------------------------
    @classmethod
    def __Reproduce(cls, population: list, selectionValues: list) -> tuple: 
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
        
        #Create the new children
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

        return (child1,child2)
#------------------------------------------------------------------------------ 
    @classmethod
    def __Mutate(cls,route: list) -> list:
        tempRoute = [val for val in route]
        
        #Have a chance to either shuffle the route or introduce new systems in the route
        mutateType = random.random()
        if mutateType < 0.2 or route.__len__() == RouteCalc.__Valid_Systems.__len__():
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