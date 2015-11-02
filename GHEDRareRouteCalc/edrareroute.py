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
    Cluster = 1.3
    Spread = 1.5
class EDRareRoute(object):
    def __init__(self,systemList: []):
        #Range of route lengths that are allowed, need at least 3 systems for the genetic alg to work
        if systemList.__len__() > 11 or systemList.__len__() < 3:
            raise Exception("Error: Route needs to have length [3-11]")
        self.__Route = systemList
        self.__Seller_Min = 160
        self.Total_Supply = sum([val.Max_Supply for val in self.__Route])
        self.Best_Sellers = None
        self.Route_Type = None
        self.Fitness_Value = self.__CalcFitness()

    def GetRoute(self):
        return [val for val in self.__Route]       

    def __CalcFitness(self):
        routeLength = self.__Route.__len__()     
       

        # Max good distance for a route should avg around Xly a jump 
        maxGoodDistance = routeLength * 110
        totalDistance = 0
        clusterShortLY = 45
        clusterLongLY = 155
        spreadMinLY = 0
        spreadMaxLY = 115
        maxJumpRangeLY = 230
        clusterShort = 0
        clusterLong = 0
        spreadJumps = 0

        for i in range(0,routeLength):
            currentSystem = self.__Route[i]
            nextSystem = self.__Route[(i+1)%routeLength]
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

        #TODO: Make sure this is actually right

        for systemPair in itertools.combinations(self.__Route,2):
            system1 = systemPair[0]
            system2 = systemPair[1]
            allSystemsSellable = [0 for i in range(routeLength)]

            system1Index = self.__Route.index(system1)
            system2Index = self.__Route.index(system2)
            systemDistance = abs(system1Index-system2Index)

            if routeLength%2 == 0 :
                if systemDistance != math.floor(routeLength/2):
                    continue
            else:
                if (systemDistance != math.floor(routeLength/2) and systemDistance != math.ceil(routeLength/2)):
                    continue

            #TODO: Condense this into a single loop 
            system1Sellers = []
            firstIndex = -999
            for i in range(1,routeLength):
                index = (i + system1Index) % routeLength
                currentSystem = self.__Route[index]
                if system1.System_Distances[currentSystem.Index] >= self.__Seller_Min:
                    if firstIndex > 0:
                        if system1Sellers[-1]:
                            system1Sellers.append(True)
                            allSystemsSellable[index] = 1
                        else:
                            system1Sellers.append(False)
                    else:
                        firstIndex = index
                        system1Sellers.append(True)
                        allSystemsSellable[index] = 1
                else:
                    system1Sellers.append(False)
            num1 = 0
            for val in system1Sellers:
                if val:
                    num1 += 1
          
            system2Sellers = []
            firstIndex = -999
            for i in range(1,routeLength):
                index = (i + system2Index) % routeLength
                currentSystem = self.__Route[index]
                if system2.System_Distances[currentSystem.Index] >= self.__Seller_Min:
                    if firstIndex > 0:
                        if system2Sellers[-1]:
                            system2Sellers.append(True)
                            allSystemsSellable[index] = 1
                        else:
                            system2Sellers.append(False)
                    else:
                        firstIndex = index
                        system2Sellers.append(True)
                        allSystemsSellable[index] = 1
                else:
                    system2Sellers.append(False)
            num2 = 0
            for val in system2Sellers:
                if val:
                    num2 += 1
            
            
            if sum(allSystemsSellable) == 0:
                continue


            if abs(num2-num1) <= 1:
                if (num2 + num1) == routeLength:
                    if sum(allSystemsSellable) == routeLength:
                        self.Best_Sellers = systemPair
                        pairValue = goodPair
                        break
                else:
                    if pairValue < sum(allSystemsSellable) / 5:
                        pairValue = sum(allSystemsSellable) / 5
                        self.Best_Sellers = systemPair
            else:
                if pairValue < sum(allSystemsSellable)/ 15:
                    pairValue = sum(allSystemsSellable) / 15
                    self.Best_Sellers = systemPair
            
        #If no combo of systems yields good seller spacing, or not all systems accounted for in the best pair, return here
        if not self.Best_Sellers:
            return 0.01
        
        #Less total distance needs to give a higher value
        weightedDistance = maxGoodDistance/totalDistance
        magicSupply = routeLength * 12
        weightedSupply = self.Total_Supply/magicSupply
  
        avgCost = sum([sum(val.Cost) for val in self.__Route])/routeLength
        #"normalize" this by taking log base 1000 of avg
        weightedCost = math.log(avgCost,1000)



        totalValue = (pairValue + weightedCost + weightedDistance + weightedSupply) * self.Route_Type.value
        if weightedCost < 1 or weightedDistance < 1 or weightedSupply < 1:
            totalValue = totalValue * 0.7

        return totalValue

    def __str__(self):
        avgCost = sum([sum(val.Cost) for val in self.__Route])/self.__Route.__len__()
        strList = []
        count = 0
        if self.Best_Sellers:
            sellersPerSystem = {}
            for system in self.__Route:
                tempSellers = []
                for distToCheck in self.__Route:
                    if system.System_Distances[distToCheck.Index] >= self.__Seller_Min:
                        tempSellers.append(distToCheck)
                sellersPerSystem[system] = tempSellers
            strList.append("\n\tRoute Value:{0}\n".format(self.Fitness_Value))
            for system in self.__Route:
                if system in self.Best_Sellers:
                    strList.append("{0}: <{1} ({2})>".format(count+1,system.System_Name, system.Station_Name))
                else:
                    strList.append("{0}: [{1} ({2})]".format(count+1,system.System_Name, system.Station_Name))
                strList.append("\n")
                count += 1
            
            for station in self.Best_Sellers:
                strList.append("\nAt <{0}> sell:\n\t".format(station.System_Name))
                for seller in sellersPerSystem[station]:
                    if seller in self.Best_Sellers:
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