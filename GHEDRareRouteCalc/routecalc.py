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
    Route_Cutoff = 11.25
    __Selection_Mult = .25
    __Valid_Systems = []
    __Fit_Type = FitnessType.EvenSplit
    __Population_Sizes = [50,300,450,800,1250,1500,1950,2500,3000]

    @classmethod
    def GetSelectionMult(cls) -> float:
        return cls.__Selection_Mult

    @classmethod
    def StartGeneticSolver(cls, validSystems: list, routeLength: int, silent: bool, fitType: FitnessType) -> tuple:
        '''
        Creates the initial population for the genetic algorithm and starts it running.
        Population is a list of EDRareRoutes
        '''
        #TODO: EvenSplit type routes don't seem to be working now???
        errMin = "Minimum route length required: {0}"
        errMax = "Maximum route length: {0}"
        if fitType == FitnessType.EvenSplit:
            if routeLength < EDRareRoute.MinLen_Split:
                raise Exception(errMin.format(EDRareRoute.MinLen_Split))
            if routeLength > EDRareRoute.MaxLen_Split:
                raise Exception(errMax.format(EDRareRoute.MaxLen_Split))
        elif fitType == FitnessType.FirstOver:
            if routeLength < EDRareRoute.MinLen_Alt:
                raise Exception(errMin.format(EDRareRoute.MinLen_Alt))
            if routeLength > EDRareRoute.MaxLen_Alt:
                raise Exception(errMax.format(EDRareRoute.MaxLen_Alt))
        RouteCalc.__Fit_Type = fitType
                   
        RouteCalc.__Valid_Systems = validSystems        
        if len(RouteCalc.__Valid_Systems) < routeLength:
            raise Exception("Not enough systems for a route...")

        popSize = cls.__Population_Sizes[min(math.floor(routeLength/4),len(cls.__Population_Sizes)-1)]

        population = [EDRareRoute(sysList, fitType) for sysList in GenerateSystemLists(popSize,routeLength,validSystems)]
        return cls.__GeneticSolver(population,silent)

    @classmethod
    def __GeneticSolver(cls,startingPopulation: list, silent: bool, optimize = True) -> tuple:
        '''
        Actually does the solving. Goes through the population and, based on
        how close to the goal they are, picks 2 parents to merge/shuffle/mutate
        until a new population is ready.
        '''       
        currentGeneration = 1
        currentPopulation = startingPopulation
        lastRouteFoundOn = currentGeneration
        baseMutation = 0.15
        mutationChance = baseMutation
        
        #Just keep track of the single best route
        bestRoute = max(currentPopulation,key=operator.attrgetter('Fitness'))

        #Want the program to keep running until it finds something, which it will eventually (maybe).
        #Going to increase the mutation chance for every x00 generations it goes without increasing
        #the value of the best route.
        mutationIncrease = 0.30
        timeBetweenIncrease = 300
        cutoffAfterRouteFound = 150
        lastIncrease = currentGeneration
        numIncreases = 0
        maxIncreases = 2
        #print("Current Fit Type: {0}\nCurrent Num Systems: {1}".format(RouteCalc.__Fit_Type, RouteCalc.__Valid_Systems.__len__()))
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
                numReplace = math.ceil(len(currentPopulation) * .75)
                tempPop = GenerateSystemLists(numReplace,bestRoute.Length,RouteCalc.__Valid_Systems)
                for i in range(numReplace):
                    currentPopulation[i] = EDRareRoute(tempPop[i],RouteCalc.__Fit_Type)

                if not silent:
                    print("{0:>7} -> mutation chance: {1:.1f}%".format(currentGeneration,mutationChance*100))

            relativeFitnessVals = cls.__CalcRelativeFitness(currentPopulation)

            while len(nextPopulation) != len(currentPopulation):
                child1,child2 = cls.__Reproduce(currentPopulation,relativeFitnessVals)
                if random.random() <= mutationChance:
                    child1 = cls.__Mutate(child1)
                if random.random() <= mutationChance:
                    child2 = cls.__Mutate(child2)
                nextPopulation.append(EDRareRoute(child1,RouteCalc.__Fit_Type))
                if len(nextPopulation) < len(currentPopulation):
                    nextPopulation.append(EDRareRoute(child2,RouteCalc.__Fit_Type))

            currentPopulation = nextPopulation

        if optimize:
            bestRoute = cls.__StartOptimizer(bestRoute,silent)
        return (bestRoute,currentGeneration)

    @classmethod
    def __CalcRelativeFitness(cls, population: list) -> list:
        '''
        We rank each route relative to the others in the population.
        We then assign them a value such that values[0] is percent[0] and values[pop-1] is
        X times the population size, set by __Selection_Mult
        '''
        upperVal = len(population) * RouteCalc.__Selection_Mult
        total = sum([route.Fitness for route in population])     

        selectionValues = [population[0].Fitness/total * upperVal]
        for i in range(1,len(population)):
            percentTotal = population[i].Fitness/total * upperVal
            selectionValues.append(percentTotal + selectionValues[i-1])

        
        return selectionValues

    @classmethod
    def __Reproduce(cls, population: list, selectionValues: list) -> tuple: 
        '''
        Chooses 2 parent nodes based on relative goodness of the population.
        A child node is created by combining the parent nodes
        Upper end of rand.uni is X times the population size, set by __Selection_Mult
        ''' 
        #Get the parents
        parents = []
        numLoops = 0
        #Picks the 2 parents, both parents can be the same system
        while len(parents) != 2:
            value = random.uniform(0,len(population) * RouteCalc.__Selection_Mult)        
            tempParent = population[bisect.bisect(selectionValues,value)]
            parents.append(tempParent)
        
        # If the 2 parents are the same, just shuffle them and return
        # This can still cause children to be the same sometimes but better than just returning the
        # parent systems
        if parents[0] == parents[1]:
            child1 = [sys for sys in parents[0].Systems]
            child2 = [sys for sys in parents[0].Systems]
            random.shuffle(child1)
            random.shuffle(child2)
            return (child1,child2)

        #Create the new children
        route1 = parents[0].Systems
        route2 = parents[1].Systems
        if len(route1) != len(route2):
            raise Exception("Routes of uneven length")
        routeLength = len(route1)
        pivot = random.randrange(1,routeLength-1)
        child1 = []
        child2 = []

        for i in range(0,pivot):
            child1.append(route1[i])
        i = pivot
        while len(child1) != routeLength:
            toAdd = route2[i%routeLength]
            if child1.count(toAdd) != 0:
                i += 1
                continue
            child1.append(toAdd)
            i += 1

        for i in range(0,pivot):
            child2.append(route2[i])
        i = pivot
        while len(child2) != routeLength:
            toAdd = route1[i%routeLength]
            if child2.count(toAdd) != 0:
                i += 1
                continue
            child2.append(toAdd)
            i += 1

        return (child1,child2)

    @classmethod
    def __Mutate(cls,route: list) -> list:
        tempRoute = [system for system in route]
        
        #Have a chance to either shuffle the route or introduce new systems in the route
        mutateType = random.random()
        if mutateType < 0.2 or len(route) == len(RouteCalc.__Valid_Systems):
            #shuffle route
            random.shuffle(tempRoute)
        else:
            #change up to half the systems in a route
            numSystemsToChange = random.randrange(1,math.ceil(len(tempRoute)/2))
            changedSystems = []
            for i in range(0, numSystemsToChange):
                
                systemToChange = random.randrange(len(tempRoute))
                while changedSystems.count(systemToChange) != 0 :
                    systemToChange = random.randrange(len(tempRoute))
                changedSystems.append(systemToChange)
                
                newSystem = random.choice(RouteCalc.__Valid_Systems)            
                while tempRoute.count(newSystem) != 0:
                    newSystem = random.choice(RouteCalc.__Valid_Systems) 
                tempRoute[systemToChange] = newSystem    

        return tempRoute

    @classmethod
    def __StartOptimizer(cls,route: EDRareRoute, silent: bool) -> EDRareRoute:
        '''
        Attempts to optimize the given route by rearranging the systems
        '''
        if not silent:
            print("Attempting to optimize route...")     
        
        RouteCalc.__Valid_Systems = route.Systems       
        popSize = cls.__Population_Sizes[min(math.floor(route.Length/4),len(cls.__Population_Sizes)-1)]//2
        
        #First check if we get a better value by finding the (maybe) shortest distance between systems
        RouteCalc.__Fit_Type = FitnessType.Distance
        population = [EDRareRoute(sysList, FitnessType.Distance) for sysList in GenerateSystemLists(popSize,route.Length,route.Systems)]     
        potentialRoute,_ = cls.__GeneticSolver(population,silent=True,optimize=False)
        potentialRoute = EDRareRoute(potentialRoute.Systems,route.Fitness_Type)
        if potentialRoute.Fitness > route.Fitness:
            if not silent:
                print("Optimization found!")
            return potentialRoute

        #Cutoff here on bad routes to skip the next part which could run for a while if the route is really bad
        #TODO: Maybe remove this since the whole point of this is to see if a "bad" route isn't that bad
        if route.Fitness < RouteCalc.Route_Cutoff * 0.7:
            if not silent:
                print("No optimization found")
            return route
        
        #Then check if we get a better value by running the route finder again with only the current systems as the valid systems
        RouteCalc.__Fit_Type = route.Fitness_Type
        population = [EDRareRoute(sysList, route.Fitness_Type) for sysList in GenerateSystemLists(popSize,route.Length,route.Systems)]   
        potentialRoute,_ = cls.__GeneticSolver(population,silent=True,optimize=False)
        if potentialRoute.Fitness > route.Fitness:
            if not silent:
                print("Optimization found!")
            return potentialRoute
        
        if not silent:
            print("No optimization found")
        return route

    @classmethod
    def SetValidSystems(cls,systems: list):
        cls.__Valid_Systems = systems

    @classmethod
    def Wrap_CalcRelativeFitness(cls,population: list) -> list:
        return cls.__CalcRelativeFitness(population);

    @classmethod
    def Wrap_Reproduce(cls,population: list, selectVals: list) -> tuple:
        return cls.__Reproduce(population,selectVals)

    @classmethod
    def Wrap_Mutate(cls,route: list) -> list:
        return cls.__Mutate(route)



def GenerateSystemLists(numToCreate: int, routeLength: int, validSystems: list) -> list:
    '''
    Generates lists of length routeLength made up of the systems in the validSystems list
    '''
    if len(validSystems) < routeLength:
        raise Exception("Not enough systems for a route")

    generatedLists = []
    for i in range(numToCreate):
        tempSystemList = random.sample(validSystems,routeLength)
        generatedLists.append(tempSystemList)
    return generatedLists

