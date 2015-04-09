from edsystem import EDSystem
from EDSystemPair import EDSystemPair
import random
import collections
import itertools
import math
import sys
import operator

class EDRareRoute(object):
    '''
    TODO: Take into account sellers when printing the route
        Change Best_Sellers to All_Sellers
        put Best_Sellers in the RouteOrder object
        Take into account stations with multiple rares
    '''
    def __init__(self,systemList: []):
        self.__Route = [val for val in systemList]
        if self.__Route.__len__() > 14 or self.__Route.__len__() < 4:
            raise Exception("Error: Route must be 4 - 12 in length")
            
        #self.__Station_Distances = self.__DistancesBetweenSystems()
        self.SellersPerStation = {}
        self.TotalSupply = sum([val.Max_Supply for val in self.__Route])
        self.Best_Sellers = self.__CalcSellers()
        self.Best_Order = []
        self.Fitness_Values = self.__Fitness()

    def GetRoute(self):
        return [val for val in self.__Route]       

    def __Fitness(self):
        '''
        So far: Have a list of distances from one system to all others in the route.
                Have potential combo of systems that account for selling goods from
                    all systems.
        We want total supply for the run to be about 10 per system
        Need to weight that values such that routes accounting for all systems
        are worth more.

        Changing this to a genetic type thing. Population is a list of edsystems
        '''   
        population = []
        validSystems = [system for system in self.__Route]
        popSize = 15
        maxGens = 25
        routeLength = self.__Route.__len__()


        for i in range(0,popSize):
            tempSystemList = []
            for j in range(0,routeLength):
                tempSystem = random.randrange(0,validSystems.__len__())
                   
                #Need to avoid duplicates
                while tempSystemList.count(tempSystem) != 0:
                    tempSystem = random.randrange(0,validSystems.__len__())
                tempSystemList.append(tempSystem)
            population.append(RouteOrder(tempSystemList, self.__Route, self.Best_Sellers, self.SellersPerStation))

        return self.__GeneticRouteStart(population, maxGens, validSystems)

    def __GeneticRouteStart(self, startingPop: [], maxGenerations: int, validSystems: []):
        currentGen = 0
        currentPopulation = startingPop
        bestRoute = startingPop[0]

        #Don't really have a 'solved' state, so we just get best of each generation if it is better
        #Than our current best
        while currentGen <= maxGenerations:
            currentGen += 1
            nextPopulation = []

            #Getting the best route in the current population
            '''
            We get a list of orders for the current route.
            We want to find which, our of those orders, is the best
            '''
            currentBest = max(currentPopulation,key=operator.attrgetter('Value'))
            if currentBest.Value > bestRoute.Value:
                bestRoute = currentBest

            for i in range(0,currentPopulation.__len__()):
                parents = self.__GetRouteParents(currentPopulation)
                child = self.__RouteReproduce(parents)
                if random.random() <= 0.05:
                    child = self.__RouteMutate(child)
                nextPopulation.append(child)

            currentPopulation = nextPopulation

        self.Best_Order = bestRoute.Order
        return bestRoute.Value

    def __GetRouteParents(self, population):
        percentages = []
        total = sum([order.Value for order in population])
        for value in [order.Value for order in population]:
            percentages.append(value/total * 1.0)
       
        parents = []
        selectionValues = [percentages[0]]
        for i in range(1,percentages.__len__()):
            selectionValues.append(percentages[i] + selectionValues[i-1])

        while parents.__len__() != 2:
            value = random.random()
            for i in range(0,population.__len__()):
                if value <= selectionValues[i]:
                    #Again, we need to avoid duplicates
                    if parents.count(population[i]) == 0:
                        parents.append(population[i])
                    # Need to break out so the loop starts again with a new value to check
                    break

        return parents

    def __RouteReproduce(self, parents: [2]):
        order1 = parents[0].Order
        order2 = parents[1].Order
        pivot = random.randrange(order1.__len__())
        newOrder = []


        if random.randrange(0,sys.maxsize)%2 == 0:
            for i in range(0,pivot):
                newOrder.append(order1[i])
            for i in range(0,order2.__len__()):
                toAdd = order2[i]
                while newOrder.count(toAdd) != 0 and newOrder.__len__() != order1.__len__():
                    i += 1
                    toAdd = order2[i]
                if newOrder.__len__() != order1.__len__():
                    newOrder.append(toAdd)
        else:
            for i in range(0,pivot):
                newOrder.append(order2[i])
            for i in range(0,order1.__len__()):
                toAdd = order1[i]
                while newOrder.count(toAdd) != 0 and newOrder.__len__() != order1.__len__():
                    i += 1
                    toAdd = order1[i]
                if newOrder.__len__() != order1.__len__():
                    newOrder.append(toAdd)

        # need to eliminate duplicates
        if set(order1) != set(newOrder):
            # if sets aren't equal then there is at least one duplicate
            notIncluded = set(order1).difference(set(newOrder))
            count = collections.Counter(newOrder)       
            for key,val in count.items():
                if val > 1:
                    index = newOrder.index(key)
                    newOrder[index] = notIncluded.pop()


        #print("\n\t***Child created***\n",EDRareRoute(newRoute))
        return RouteOrder(newOrder,self.__Route, self.Best_Sellers, self.SellersPerStation)

    def __RouteMutate(self, child):
        newOrder = [var for var in child.Order]
        swap1 = random.randrange(0,newOrder.__len__())
        swap2 = random.randrange(0,newOrder.__len__())
        while swap2 == swap1:
            swap2 = random.randrange(0,newOrder.__len__())
        temp = newOrder[swap1]
        newOrder[swap1] = newOrder[swap2]
        newOrder[swap2] = temp
        return RouteOrder(newOrder,self.__Route, self.Best_Sellers, self.SellersPerStation)

    def __CalcSellers(self):
        sellingDistance = 140
        self.SellersPerStation = {}
        for system in self.__Route:
            tempSellers = []
            for distToCheck in self.__Route:
                if system.System_Distances[distToCheck.Index] >= sellingDistance:
                    tempSellers.append(distToCheck)
            self.SellersPerStation[system] = tempSellers

        combosWithAllSystems = []
        for combo in itertools.combinations(self.__Route,2):
            #If sellers can't sell to each other we know the combo is bad
            if combo[0].System_Distances[combo[1].Index] < sellingDistance:
                continue
            sellersPerCombo = []
            for obj in combo:
                sellersPerCombo += [val for val in self.SellersPerStation[obj]]
            if set(sellersPerCombo) == set(self.__Route):
                combosWithAllSystems.append(combo)

        #Want to remove combos with a difference greater than 1
        maxDifference = math.floor(self.__Route.__len__() / 2)
        while combosWithAllSystems.__len__ != 0:
            combosToRemove = []
            for combo in combosWithAllSystems:
                numSellers = self.SellersPerStation[combo[0]].__len__()
                badCombo = False
                for system in combo:
                    numToCheck = self.SellersPerStation[system].__len__()
                    leftOver = math.fabs(numSellers - numToCheck)
                    if leftOver > maxDifference:
                        badCombo = True
                if badCombo:
                    combosToRemove.append(combo)
            
            if combosToRemove.__len__() == combosWithAllSystems.__len__():
                #This means we are about to remove every combo, we don't want that
                break   
            for combo in combosToRemove:
                combosWithAllSystems.remove(combo)    
            maxDifference -= 1
        #Need to add 1 to get the difference before all were eliminated
        maxDifference += 1

        if maxDifference > 1:
            combosWithAllSystems = []
        
        return combosWithAllSystems
        

    def __str__(self):
        strList = []
        strList.append("\n\tRare route!!! Value:{0}\n".format(self.Fitness_Values))
        for index in self.Best_Order:
            strList.append('{0}\n'.format(self.__Route[index]))
        strList.append("\tEnd Rare Route!!!\n")
        return ''.join(strList)

class RouteOrder(object):
    '''
    We are given a list of ints and a list of systems. 
    The list of ints represents an order for the systems, with the 
    ints themselves being the index of the system in the list of systems.
    '''
    def __init__(self, indexList: [], systems: [], sellLocs: [], sellersPerStation: {}):
        '''
        sellLocs members will always be length 2
        '''
        self.Order = indexList
        self.__Systems = systems
        self.__SellLocs = sellLocs
        self.SellersPerStation = sellersPerStation

        self.Value = self.__CalcValue()

    def __CalcValue(self):
        '''
        We want a route with an even number, or within one, of stations between each designated seller
        so we give routes like that a high value. Then we need to calculate the total distance to go
        through that route round trip and combine the two into a good number

        TODO: Take into account total supply of the route, need to pass it in above
            Also need to take into account routes that do not have evenly spaced if even, or a difference of 1 of odd, 
            stations between the designated sellers.
        '''
        totalValue = 0.01
        #if comboswithsystems.len is 1 then we have a maybe good thing
        # if 0 then we have a bad and maybe just return now a small number
        if self.__SellLocs.__len__() == 0:
            return totalValue

        orderedSystems = []
        for index in self.Order:
            orderedSystems.append(self.__Systems[index])

        pairValue = -10
        for sellerPair in self.__SellLocs:
            loc1 = sellerPair[0]
            loc2 = sellerPair[1]

            loc1Index = orderedSystems.index(loc1)
            loc2Index = orderedSystems.index(loc2)
            jumpsBetween = 0

            if loc1Index > loc2Index:
                jumpsBetween = loc1Index - loc2Index
            else:
                jumpsBetween = loc2Index - loc1Index

            indexForSystemsSellingLoc1 = []
            indexForSystemsSellingLoc2 = []
            for system in self.SellersPerStation[loc1]:
                indexForSystemsSellingLoc1.append(orderedSystems.index(system))
            for system in self.SellersPerStation[loc2]:
                indexForSystemsSellingLoc2.append(orderedSystems.index(system))

            # At this point we have the location of the sellers in the route
            # as well as the number of jumps between them. Ideally we want 
            # the sellers to be evenly spaced out, so routelen/2 distance apart
            # We should not check for the location of systems that can sell 
            # to loc1 and loc2

            if loc1Index > loc2Index:
                numBefore1 = 0
                for i in range(loc2Index,loc1Index):
                    if indexForSystemsSellingLoc1.count(i) != 0:
                        numBefore1 += 1
                #print("1: ",numBefore1)
                        
                numBefore2 = 0
                for i in range(loc1Index,loc2Index + orderedSystems.__len__()):
                    if indexForSystemsSellingLoc2.count(i % orderedSystems.__len__()) != 0:
                        numBefore2 += 1
                #print("2: ",numBefore2)
            else:
                numBefore2 = 0
                for i in range(loc1Index,loc2Index):
                    if indexForSystemsSellingLoc2.count(i) != 0:
                        numBefore2 += 1
                #print("2: ",numBefore2)
                        
                numBefore1 = 0
                for i in range(loc2Index,loc1Index + orderedSystems.__len__()):
                    if indexForSystemsSellingLoc1.count(i % orderedSystems.__len__()) != 0:
                        numBefore1 += 1
                #print("1: ",numBefore1)
               
            # if the total number before each = len-2 or len then we have a good one... should treat each the same
            # as far as value goes len-2 means we have a rather evenly spaced loop, len means we have grouped systems
            if (numBefore1 == numBefore2) or math.fabs(numBefore1-numBefore2) == 1:
                pairValue = 50
            else:
                pairValue = pairValue if (numBefore1 + numBefore2) < pairValue else (numBefore1 + numBefore2)

            # now we check how far apart the sellers are and adjust the pairValue
            #if jumpsBetween < (orderedSystems.__len__() / 2):
            #    pairValue *= 0.5
            #elif jumpsBetween > (orderedSystems.__len__() / 2):
            #    pairValue *= 0.5
        magicNumber = 10000
        totalDistance = 0
        for i in range(0,orderedSystems.__len__()):
            currentSystem = orderedSystems[i]
            nextSystem = orderedSystems[(i+1)%orderedSystems.__len__()]
            totalDistance += currentSystem.System_Distances[nextSystem.Index]

        #Less total distance needs to give a higher value
        weightedDistance = magicNumber - totalDistance
        totalValue = pairValue * (weightedDistance / 100)

        return totalValue