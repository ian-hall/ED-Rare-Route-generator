from edsystem import EDSystem
import random
import collections
import itertools
import math
import sys
import operator
from enum import Enum,unique

@unique
class RouteType(Enum):
    Other = 1
    Cluster = 1.15
    Spread = 1.3
class EDRareRoute(object):
    def __init__(self,systemList: []):
        #Range of route lengths that are allowed, need at least 3 systems for the genetic alg to work
        if systemList.__len__() > 11 or systemList.__len__() < 3:
            raise Exception("Error: Route needs to have length [3-11]")
        self.__Route = [val for val in systemList]
            
        self.Sellers_Per_Station = {}
        self.Total_Supply = sum([val.Max_Supply for val in self.__Route])
        self.Possible_Sell_Points = self.__CalcSellers()
        self.Best_Sell_Points = []
        self.Route_Type = None
        self.Fitness_Value = self.__Fitness()

    def GetRoute(self):
        return [val for val in self.__Route]       

    def __Fitness(self):
        '''
        Takes into account:
            total supply of the route
            total distance of the route
            number of systems that are valid selling points
        TODO:
            maybe replace this whole thing with RouteOrder
            Print a list of all possible seller pairs if more than 1 exists.
        '''   

        currentRoute = RouteOrder(self.__Route, self.Possible_Sell_Points, self.Sellers_Per_Station, self.Total_Supply)
        self.Best_Sell_Points = currentRoute.Best_Sellers
        self.Route_Type = currentRoute.Route_Type
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
            if self.Sellers_Per_Station[combo[0]].count(combo[1]) == 0:
                continue
            sellersPerCombo = []
            for seller in combo:
                for system in self.Sellers_Per_Station[seller]:
                    sellersPerCombo.append(system)
            if set(sellersPerCombo) == set(self.__Route):
                if abs(self.Sellers_Per_Station[combo[0]].__len__() - self.Sellers_Per_Station[combo[1]].__len__()) <= 1:
                    combosWithAllSystems.append(combo)

        return combosWithAllSystems
        

    def __str__(self):
        avgCost = sum([sum(val.Cost) for val in self.__Route])/self.__Route.__len__()
        strList = []
        count = 0
        if self.Best_Sell_Points:
            strList.append("\n\tRoute Value:{0}\n".format(self.Fitness_Value))
            for system in self.__Route:
                #strList.append("({0})[{1}]".format(system.Index,system.System_Name))
                if system in self.Best_Sell_Points:
                    strList.append("{0}: <{1} ({2})>".format(count+1,system.System_Name, system.Station_Name))
                else:
                    strList.append("{0}: [{1} ({2})]".format(count+1,system.System_Name, system.Station_Name))
                strList.append("\n")
                count += 1
            
            for station in self.Best_Sell_Points:
                strList.append("\nAt <{0}> sell:\n\t".format(station.System_Name))
                for seller in self.Sellers_Per_Station[station]:
                    #strList.append("[{0}] ".format(seller.System_Name))
                    if seller in self.Best_Sell_Points:
                        strList.append(" <{0}> ".format(seller.System_Name))
                    else:
                        strList.append(" [{0}] ".format(seller.System_Name))
        
        else:
            strList.append("\n(Bad)Route with value:{0}\n".format(self.Fitness_Value))
            for system in self.__Route:
               strList.append('{0}\n'.format(system))

        strList.append("\n\nTotal goods: {0}".format(self.Total_Supply))
        strList.append("\nAvg cost: {0}".format(avgCost))
        strList.append("\nType: {0}".format(self.Route_Type))
        return ''.join(strList)

class RouteOrder(object):
    def __init__(self, systems: [], sellLocs: [], sellersPerStation: {}, itemSupply):
        '''
        systems: list of systems in route order
        sellLocs: list of possible selling locations
        sellersPerSTation: dictionary containing each system and systems that can sell to it
        itemSupply: total supply of items buyable on the rotue
        '''
        self.__Systems = systems
        self.__SellLocs = sellLocs
        self.Route_Sellers = sellersPerStation
        self.Supply = itemSupply
        self.Best_Sellers = None
        self.Route_Type = None
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

        routeLength = self.__Systems.__len__()     
       

        # Max good distance for a route should avg around Xly a jump 
        maxGoodDistance = routeLength * 110
        totalDistance = 0
        clusterShortLY = 40
        clusterLongLY = 160
        spreadMinLY = 50
        spreadMaxLY = 110
        maxJumpRangeLY = 230
        clusterShort = 0
        clusterLong = 0
        spreadJumps = 0

        for i in range(0,routeLength):
            currentSystem = self.__Systems[i]
            nextSystem = self.__Systems[(i+1)%routeLength]
            jumpDistance = currentSystem.System_Distances[nextSystem.Index]
            totalDistance += jumpDistance
            if jumpDistance <= clusterShortLY:
                clusterShort += 1
            if jumpDistance >= clusterLongLY and jumpDistance <= maxJumpRangeLY:
                clusterLong += 1 
            if jumpDistance >= spreadMinLY and jumpDistance <= spreadMaxLY:
                spreadJumps += 1 

        self.Route_Type = RouteType.Other
        
        #Route has 2 groups of systems separated by a long jump
        #Ideally clusterLongJumps would be variable and equal to the number of sellers,
        #but I'm just worrying about 2 sellers for now
        if clusterLong == 2 and (clusterLong + clusterShort) == routeLength:
           self.Route_Type = RouteType.Cluster

        #Route has fairly evenly spaced jumps
        #Maybe a higher multiplier to compensate for the longer distances
        if spreadJumps == routeLength:
            self.Route_Type = RouteType.Spread

        pairValue = -999
        goodPair = 6
        potentialPair = 2

        #TODO: Change logic here: We have index of the sellers, check systems immediately before/after and:
        #   If system right before a seller can sell to it, and it is a cluster type, good
        #   "" , and it is spread type, bad
        # Two systems back can sell, and cluster, good depending on route length
        # '', and spread, good

        for sellerPair in self.__SellLocs:
            loc1 = sellerPair[0]
            loc2 = sellerPair[1]

            loc1Index = self.__Systems.index(loc1)
            loc2Index = self.__Systems.index(loc2)

            indexForSystemsSellingLoc1 = []
            indexForSystemsSellingLoc2 = []
            for system in self.Route_Sellers[loc1]:
                indexForSystemsSellingLoc1.append(self.__Systems.index(system))
            for system in self.Route_Sellers[loc2]:
                indexForSystemsSellingLoc2.append(self.__Systems.index(system))

            if loc1Index > loc2Index:
                numBefore1 = 0
                for i in range(loc2Index,loc1Index):
                    if indexForSystemsSellingLoc1.count(i) != 0:
                        numBefore1 += 1
                        
                numBefore2 = 0
                for i in range(loc1Index,loc2Index + routeLength):
                    if indexForSystemsSellingLoc2.count(i % routeLength) != 0:
                        numBefore2 += 1
            else:
                numBefore2 = 0
                for i in range(loc1Index,loc2Index):
                    if indexForSystemsSellingLoc2.count(i) != 0:
                        numBefore2 += 1
                        
                numBefore1 = 0
                for i in range(loc2Index,loc1Index + routeLength):
                    if indexForSystemsSellingLoc1.count(i % routeLength) != 0:
                        numBefore1 += 1
            
            #TODO: make this work
            #      and also make this have the logic that I want which it apparently doesn't have right now
            # At this point we have the location of the sellers in the route
            # as well as the number of jumps between them.
            # Spread route, even length:
            #   Equal number of systems between sellers
            #   One non-selling system before each sell location, or numBefore1+numBefore2 = len-2
            # Spread route, odd length:
            #   Number of systems between sellers should have a difference of 1
            #   One non-selling systems before each sell location.
            # Cluster route, even length:
            #   Equal number of systems between sellers
            #   0 or 1 non-selling systems before each sell location
            # Cluster route, odd length:
            #   Number of systems between sellers should have a difference of 1
            #   0 or 1 non-selling systems before each sell location
            
            if self.Route_Type == RouteType.Spread and routeLength%2 == 0:
                if numBefore1 == numBefore2:
                    if (numBefore1 + numBefore2) == (routeLength - 2):
                        pairValue = goodPair
                        self.Best_Sellers = sellerPair
                    else:
                        if pairValue < potentialPair:
                            pairValue = potentialPair
                            self.Best_Sellers = sellerPair
                if pairValue < (numBefore1 + numBefore2) / 10:
                    pairValue = (numBefore1 + numBefore2) / 10
                    self.Best_Sellers = sellerPair
            if self.Route_Type == RouteType.Spread and routeLength%2 == 1:
                if math.fabs(numBefore1-numBefore2) == 1:
                    if (numBefore1 + numBefore2) == (routeLength - 2):
                        pairValue = goodPair
                        self.Best_Sellers = sellerPair
                    else:
                        if pairValue < potentialPair:
                            pairValue = potentialPair
                            self.Best_Sellers = sellerPair
                if pairValue < (numBefore1 + numBefore2) / 10:
                    pairValue = (numBefore1 + numBefore2) / 10
                    self.Best_Sellers = sellerPair
            if self.Route_Type == RouteType.Cluster and routeLength%2 == 0:
                if numBefore1 == numBefore2:
                    if (numBefore1 + numBefore2) >= (routeLength - 2):
                        pairValue = goodPair
                        self.Best_Sellers = sellerPair
                    else:
                        if pairValue < potentialPair:
                            pairValue = potentialPair
                            self.Best_Sellers = sellerPair
                if pairValue < (numBefore1 + numBefore2) / 10:
                    pairValue = (numBefore1 + numBefore2) / 10
                    self.Best_Sellers = sellerPair
            if self.Route_Type == RouteType.Cluster and routeLength%2 == 1:
                if math.fabs(numBefore1-numBefore2) == 1:
                    if (numBefore1 + numBefore2) > (routeLength - 2):
                        pairValue = goodPair
                        self.Best_Sellers = sellerPair
                    else:
                        if pairValue < potentialPair:
                            pairValue = potentialPair
                            self.Best_Sellers = sellerPair
                if pairValue < (numBefore1 + numBefore2) / 10:
                    pairValue = (numBefore1 + numBefore2) / 10
                    self.Best_Sellers = sellerPair
            if self.Route_Type == RouteType.Other:
                if pairValue < (numBefore1 + numBefore2) / 15:
                        pairValue = (numBefore1 + numBefore2) / 15
                        self.Best_Sellers = sellerPair
            
            '''
            if self.Route_Type == RouteType.Other:
                if potentialPair > pairValue:
                    pairValue = potentialPair
                    self.Best_Sellers = sellerPair          
            else:
                if routeLength % 2 == 0:
                    if (numBefore1 == numBefore2) and math.fabs(numBefore1 - routeLength/2) <=1:
                        pairValue = goodPair
                        self.Best_Sellers = sellerPair                 
                    else:
                        if (numBefore1 + numBefore2) / 15 > pairValue:
                            pairValue = (numBefore1 + numBefore2) / 15
                            self.Best_Sellers = sellerPair
                else:
                    if math.fabs(numBefore1 - numBefore2) == 1:
                        pairValue = goodPair
                        self.Best_Sellers = sellerPair
                    else:
                        if (numBefore1 + numBefore2) / 15 > pairValue:
                            pairValue = (numBefore1 + numBefore2) / 15
                            self.Best_Sellers = sellerPair
           '''
            


        #Less total distance needs to give a higher value
        weightedDistance = maxGoodDistance/totalDistance
        magicSupply = self.__Systems.__len__() * 12
        weightedSupply = self.Supply/magicSupply
  
        avgCost = sum([sum(val.Cost) for val in self.__Systems])/self.__Systems.__len__()
        #"normalize" this by taking log base 1000 of avg
        weightedCost = math.log(avgCost,1000)



        totalValue = (pairValue + weightedCost + weightedDistance + weightedSupply) * self.Route_Type.value
        if weightedCost < 1 or weightedDistance < 1 or weightedSupply < 1:
            totalValue = totalValue * 0.7

        return totalValue