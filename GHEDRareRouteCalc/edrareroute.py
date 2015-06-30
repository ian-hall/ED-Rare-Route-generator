from edsystem import EDSystem
from EDSystemPair import EDSystemPair
import random
import collections
import itertools
import math
import sys
import operator

class EDRareRoute(object):
    def __init__(self,systemList: []):
        self.__Route = [val for val in systemList]
        if self.__Route.__len__() > 14 or self.__Route.__len__() < 4:
            raise Exception("Error: Route must be 4 - 12 in length")
            
        #self.__Station_Distances = self.__DistancesBetweenSystems()
        self.Sellers_Per_Station = {}
        self.Total_Supply = sum([val.Max_Supply for val in self.__Route])
        self.Possible_Sell_Points = self.__CalcSellers()
        self.Best_Order = []
        self.Best_Sell_Points = []
        self.Fitness_Values = self.__Fitness()

    def GetRoute(self):
        return [val for val in self.__Route]       

    def __Fitness(self):
        '''
        Takes into account:
            total supply of the route
            total distance of the route
            number of systems that are valid selling points
        TODO:
            maybe replace this whole thing with RouteOrder since
                i'm not doing another genetic thing here
            Print a list of all possible seller pairs if more than 1 exists.
                RouteOrder class will always return the last pair found as the best...and while it will work it might not be best
        '''   
        tempSystemList = [ i for i in range(0,self.__Route.__len__()) ]

        currentRoute = RouteOrder(tempSystemList, self.__Route, self.Possible_Sell_Points, self.Sellers_Per_Station, self.Total_Supply)
        self.Best_Order = currentRoute.Order
        self.Best_Sell_Points = currentRoute.Best_Sellers
        return currentRoute.Value

    def __CalcSellers(self):
        sellingDistance = 160
        self.Sellers_Per_Station = {}
        for system in self.__Route:
            tempSellers = []
            for distToCheck in self.__Route:
                if system.System_Distances[distToCheck.Index] >= sellingDistance:
                    tempSellers.append(distToCheck)
            self.Sellers_Per_Station[system] = tempSellers

        combosWithAllSystems = []
        for combo in itertools.combinations(self.__Route,2):
            #If sellers can't sell to each other we know the combo is bad
            if combo[0].System_Distances[combo[1].Index] < sellingDistance:
                continue
            sellersPerCombo = []
            for obj in combo:
                sellersPerCombo += [val for val in self.Sellers_Per_Station[obj]]
            if set(sellersPerCombo) == set(self.__Route):
                combosWithAllSystems.append(combo)

        #Want to remove combos with a difference greater than 1
        maxDifference = math.floor(self.__Route.__len__() / 2)
        while combosWithAllSystems.__len__ != 0:
            combosToRemove = []
            for combo in combosWithAllSystems:
                numSellers = self.Sellers_Per_Station[combo[0]].__len__()
                badCombo = False
                for system in combo:
                    numToCheck = self.Sellers_Per_Station[system].__len__()
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
        if self.Best_Sell_Points:
            strList.append("\n\tRare route!!! Value:{0}\n".format(self.Fitness_Values))
            for index in self.Best_Order:
                strList.append('{0}\n'.format(self.__Route[index]))
            strList.append("\n\tSell rares at:\n")
            for seller in self.Best_Sell_Points:
                strList.append('{0}\n'.format(seller))
            strList.append("\tEnd Rare Route!!!\n")
        else:
            strList.append("\nFound a route with value:{0}, but it is no good".format(self.Fitness_Values))
        return ''.join(strList)

class RouteOrder(object):
    '''
    We are given a list of ints and a list of systems. 
    The list of ints represents an order for the systems, with the 
    ints themselves being the index of the system in the list of systems.
    '''
    def __init__(self, indexList: [], systems: [], sellLocs: [], sellersPerStation: {}, itemSupply):
        '''
        sellLocs members will always be length 2
        '''
        self.Order = indexList
        self.__Systems = systems
        self.__SellLocs = sellLocs
        self.Route_Sellers = sellersPerStation
        self.Supply = itemSupply
        self.Best_Sellers = None
        self.Value = self.__CalcValue()

    def __CalcValue(self):
        '''
        We want a route with an even number, or within one, of stations between each designated seller
        so we give routes like that a high value. Then we need to calculate the total distance to go
        through that route round trip and combine the two into a good number
        '''
        totalValue = 0.01
        #if this group has no valid sellers just return now
        if self.__SellLocs.__len__() == 0:
            return totalValue

        orderedSystems = []
        for index in self.Order:
            orderedSystems.append(self.__Systems[index])

        routeLength = orderedSystems.__len__()

        pairValue = 0.01
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
            for system in self.Route_Sellers[loc1]:
                indexForSystemsSellingLoc1.append(orderedSystems.index(system))
            for system in self.Route_Sellers[loc2]:
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
                for i in range(loc1Index,loc2Index + routeLength):
                    if indexForSystemsSellingLoc2.count(i % routeLength) != 0:
                        numBefore2 += 1
                #print("2: ",numBefore2)
            else:
                numBefore2 = 0
                for i in range(loc1Index,loc2Index):
                    if indexForSystemsSellingLoc2.count(i) != 0:
                        numBefore2 += 1
                #print("2: ",numBefore2)
                        
                numBefore1 = 0
                for i in range(loc2Index,loc1Index + routeLength):
                    if indexForSystemsSellingLoc1.count(i % routeLength) != 0:
                        numBefore1 += 1
                #print("1: ",numBefore1)
               
            # if the total number before each = len-2 or len then we have a good one... should treat each the same
            # as far as value goes len-2 means we have a rather evenly spaced loop, len means we have grouped systems
            if routeLength % 2 == 0:
                if (numBefore1 == numBefore2):
                    pairValue = 50
                    self.Best_Sellers = sellerPair                 
                else:
                    if (numBefore1 + numBefore2) < pairValue:
                        pairValue = pairValue
                    else:
                        pairValue = (numBefore1 + numBefore2)
                        self.Best_Sellers = sellerPair
            else:
                if math.fabs(numBefore1 - numBefore2) <= 1:
                    pairValue = 50
                    self.Best_Sellers = sellerPair
                else:
                    if (numBefore1 + numBefore2) < pairValue:
                        pairValue = pairValue
                    else:
                        pairValue = (numBefore1 + numBefore2)
                        self.Best_Sellers = sellerPair

        # magicnumber is supposed to be an absolute max for distance.... originally 100ly per system
        # if the total distance is further than this we are going to weigh the total 
        # value lower
        maxGoodDistance = routeLength * 100
        totalDistance = 0
        clusterShortLY = 40
        clusterLongLY = 120
        spreadMinLY = 50
        spreadMaxLY = 110
        maxJumpRangeLY = 200
        clusterShortJumps = 0
        clusterLongJumps = 0
        spreadJumps = 0
        longestJump = -1
        for i in range(0,routeLength):
            currentSystem = orderedSystems[i]
            nextSystem = orderedSystems[(i+1)%routeLength]
            jumpDistance = currentSystem.System_Distances[nextSystem.Index]
            totalDistance += jumpDistance
            if longestJump < jumpDistance:
                longestJump = jumpDistance
            if jumpDistance <= clusterShortLY:
                clusterShortJumps += 1
            elif jumpDistance >= spreadMinLY and jumpDistance <= spreadMaxLY:
                spreadJumps += 1
            elif jumpDistance >= clusterLongLY:
                clusterLongJumps += 1  

        #set this at a default value less than 1 since most routes will have this
        routeTypeMult = 0.5
        
        #Route has 2 groups systems separated by a long jump
        #Ideally clusterLongJumps would be variable and equal to the number of sellers,
        #but I'm just worrying about 2 sellers for now
        if clusterLongJumps == 2 and (clusterLongJumps + clusterShortJumps) == orderedSystems.__len__():
            routeTypeMult = 1.25

        #Route has fairly evenly spaced jumps
        if spreadJumps == orderedSystems.__len__():
            routeTypeMult = 1.25

        #lower multiplier if we have an extra long jump between systems
        if routeTypeMult > 1 and longestJump >= maxJumpRangeLY:
            routeTypeMult = .8

        #Less total distance needs to give a higher value
        weightedDistance = maxGoodDistance/totalDistance
        magicSupply = orderedSystems.__len__() * 10
        #greater supply is a greater number, this is so we don't have supply playing as large a roll in total value
        weightedSupply = self.Supply/magicSupply
        totalValue = (pairValue * weightedSupply * weightedDistance) * routeTypeMult

        return totalValue