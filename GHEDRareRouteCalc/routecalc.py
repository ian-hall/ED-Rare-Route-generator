from edsystem import EDSystem
from edrareroute import EDRareRoute, FitnessType
import random
import math
import operator
import bisect
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class RouteCalc(object):
    '''
    Class for calculating rare trade routes
    '''
    Route_Cutoff = 11.25
    __Selection_Mult = 1
    __Valid_Systems = []
    __Fit_Type = FitnessType.EvenSplit
#------------------------------------------------------------------------------
    @classmethod
    def GetSelectionMult(cls) -> float:
        return cls.__Selection_Mult
#------------------------------------------------------------------------------
    @classmethod
    def StartGeneticSolver(cls,popSize: int, validSystems: list, routeLength: int, silent: bool, fitType: FitnessType) -> tuple:
        '''
        Creates the initial population for the genetic algorithm and starts it running.
        Population is a list of EDRareRoutes
        '''
        #TODO:  Eventually add something here that calculates popSize based on route length
        RouteCalc.__Fit_Type = fitType
        if RouteCalc.__Fit_Type == FitnessType.EvenSplit:
            if routeLength < 3 or routeLength > 15:
                raise Exception("Split routes must have lengths [3-15]")
        elif RouteCalc.__Fit_Type == FitnessType.Distance:
            pass
        else:
            if routeLength < 6 or routeLength > 35:
                raise Exception("Alternate type routes must have lengths [6-35]")

        if popSize < 3:
            raise Exception("Must have a population size of at least 3")
            
        RouteCalc.__Valid_Systems = validSystems
        
        if RouteCalc.__Valid_Systems.__len__() < routeLength:
            raise Exception("Not enough systems for a route...")

        population = [EDRareRoute(sysList, fitType) for sysList in GenerateSystemLists(popSize,routeLength,validSystems)]

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
        bestRoute = max(currentPopulation,key=operator.attrgetter('Fitness'))

        #Want the program to keep running until it finds something, which it will eventually (maybe).
        #Going to increase the mutation chance for every x00 generations it goes without increasing
        #the value of the best route.
        mutationIncrease = 0.35
        timeBetweenIncrease = 350
        cutoffAfterRouteFound = 100
        lastIncrease = currentGeneration
        numIncreases = 0
        maxIncreases = 2

        #Force an exit if X generations pass with no improvement
        maxGensSinceLast = (maxIncreases+1)*timeBetweenIncrease

        while True:    
            possibleRoute = max(currentPopulation,key=operator.attrgetter('Fitness'))

            if not silent:
                if currentGeneration == 1:
                    print("Starting value: {0:.5f}".format(possibleRoute.Fitness))

            currentGeneration += 1
            nextPopulation = []

            if possibleRoute.Fitness > bestRoute.Fitness:
                if not silent:
                    print("{0:>7} -> {1:.5f}".format(currentGeneration,possibleRoute.Fitness))
                bestRoute = possibleRoute
                lastRouteFoundOn = currentGeneration
                #Reset mutation chance when finding a new best route
                if mutationChance != baseMutation:
                    mutationChance = baseMutation
                    if not silent:
                        print("{0:>7} -> mutation chance: {1:.1f}%".format("",mutationChance*100))

            #Exit if we are at least at the Route_Cutoff value and its been X generations since last increase
            if bestRoute.Fitness >= RouteCalc.Route_Cutoff and currentGeneration - lastRouteFoundOn >= cutoffAfterRouteFound:
                break
            
            #Exit if it has been X generations since last found route
            if currentGeneration - lastRouteFoundOn >= maxGensSinceLast:
                break

            #Increase mutation chance and replace the X lowest valued systems in the current population
            if currentGeneration - lastRouteFoundOn >= timeBetweenIncrease and (currentGeneration - lastIncrease) >= timeBetweenIncrease:
                mutationChance += mutationIncrease
                lastIncrease = currentGeneration
                currentPopulation = sorted(currentPopulation,key=operator.attrgetter('Fitness'))
                #Replace a percentage of the routes with lowest values, maybe make this smart to not include adding systems already commonly in the top routes
                numReplace = math.ceil(currentPopulation.__len__() * .75)
                tempPop = GenerateSystemLists(numReplace,bestRoute.Length,RouteCalc.__Valid_Systems)
                for i in range(numReplace):
                    currentPopulation[i] = EDRareRoute(tempPop[i],RouteCalc.__Fit_Type)

                if not silent:
                    print("{0:>7} -> mutation chance: {1:.1f}%".format(currentGeneration,mutationChance*100))

            relativeFitnessVals = cls.__CalcRelativeFitness(currentPopulation)

            while nextPopulation.__len__() != currentPopulation.__len__():
                child1,child2 = cls.__Reproduce(currentPopulation,relativeFitnessVals)
                if random.random() <= mutationChance:
                    child1 = cls.__Mutate(child1)
                if random.random() <= mutationChance:
                    child2 = cls.__Mutate(child2)
                nextPopulation.append(EDRareRoute(child1,RouteCalc.__Fit_Type))
                if nextPopulation.__len__() < currentPopulation.__len__():
                    nextPopulation.append(EDRareRoute(child2,RouteCalc.__Fit_Type))

            currentPopulation = nextPopulation

        return (bestRoute,currentGeneration)
#------------------------------------------------------------------------------
    @classmethod
    def __CalcRelativeFitness(cls, population: list) -> list:
        '''
        We rank each route relative to the others in the population.
        We then assign them a value such that values[0] is percent[0] and values[pop-1] is
        X times the population size, set by __Selection_Mult
        '''
        upperVal = population.__len__() * RouteCalc.__Selection_Mult
        total = sum([route.Fitness for route in population])     

        selectionValues = [population[0].Fitness/total * upperVal]
        for i in range(1,population.__len__()):
            percentTotal = population[i].Fitness/total * upperVal
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
        route1 = parents[0].Systems
        route2 = parents[1].Systems
        if route1.__len__() != route2.__len__():
            raise Exception("Routes of uneven length")
        routeLength = route1.__len__()
        pivot = random.randrange(1,routeLength-1)
        child1 = []
        child2 = []

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
        tempRoute = [system for system in route]
        
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
    @classmethod
    def SetValidSystems(cls,systems: list):
        cls.__Valid_Systems = systems
#------------------------------------------------------------------------------
    @classmethod
    def Wrap_CalcRelativeFitness(cls,population: list) -> list:
        return cls.__CalcRelativeFitness(population);
#------------------------------------------------------------------------------
    @classmethod
    def Wrap_Reproduce(cls,population: list, selectVals: list) -> tuple:
        return cls.__Reproduce(population,selectVals)
#------------------------------------------------------------------------------
    @classmethod
    def Wrap_Mutate(cls,route: list) -> list:
        return cls.__Mutate(route)
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
def GenerateSystemLists(numToCreate: int, routeLength: int, validSystems: list) -> list:
    '''
    Generates lists of length routeLength made up of the systems in the validSystems list
    '''
    if validSystems.__len__() < routeLength:
        raise Exception("Not enough systems for a route")

    generatedLists = []
    for i in range(numToCreate):
        tempSystemList = random.sample(validSystems,routeLength)
        generatedLists.append(tempSystemList)
    return generatedLists
#------------------------------------------------------------------------------