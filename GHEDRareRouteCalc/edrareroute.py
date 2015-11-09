﻿from edsystem import EDSystem
import itertools
import math
from enum import Enum,unique

@unique
class RouteType(Enum):
    Other = 0
    Cluster = 1
    Spread = 2
class EDRareRoute(object):
    def __init__(self,systemList: []):
        self.__Route = systemList
        self.__Seller_Min = 160
        self.Total_Distance = 0
        self.Total_Supply = sum([val.Max_Supply for val in self.__Route])
        self.Best_Sellers = None
        self.Route_Type = None
        self.Fitness_Value = self.__CalcFitness()

    def GetRoute(self):
        return [val for val in self.__Route]       

    def __CalcFitness(self):
        routeLength = self.__Route.__len__()     
       
        clusterShortLY = 50
        clusterLongLY = 155
        spreadMinLY = 0
        spreadMaxLY = 120
        maxJumpRangeLY = 230
        clusterShort = 0
        clusterLong = 0
        spreadJumps = 0
        longestJump = -999

        for i in range(0,routeLength):
            currentSystem = self.__Route[i]
            nextSystem = self.__Route[(i+1)%routeLength]
            jumpDistance = currentSystem.System_Distances[nextSystem.Index]
            self.Total_Distance += jumpDistance
            longestJump = jumpDistance if jumpDistance > longestJump else longestJump
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

            #TODO: Fix spacing
            system1Sellers = []
            system1LastIndex = -999
            system2Sellers = []
            system2LastIndex = -999
            for i in range(1,routeLength):
                system1IndexToCheck = (i + system1Index) % routeLength
                currentSystem = self.__Route[system1IndexToCheck]
                if system1.System_Distances[currentSystem.Index] >= self.__Seller_Min:
                    if system1LastIndex > 0:
                        if system1Sellers[-1]:
                            system1Sellers.append(True)
                            allSystemsSellable[system1IndexToCheck] = 1
                        else:
                            system1Sellers.append(False)
                    else:
                        system1LastIndex = system1IndexToCheck
                        system1Sellers.append(True)
                        allSystemsSellable[system1IndexToCheck] = 1
                else:
                    system1Sellers.append(False)

          
            #for i in range(1,routeLength):
                system2IndexToCheck = (i + system2Index) % routeLength
                currentSystem = self.__Route[system2IndexToCheck]
                if system2.System_Distances[currentSystem.Index] >= self.__Seller_Min:
                    if system2LastIndex > 0:
                        if system2Sellers[-1]:
                            system2Sellers.append(True)
                            allSystemsSellable[system2IndexToCheck] = 1
                        else:
                            system2Sellers.append(False)
                    else:
                        system2LastIndex = system2IndexToCheck
                        system2Sellers.append(True)
                        allSystemsSellable[system2IndexToCheck] = 1
                else:
                    system2Sellers.append(False)
            
            num1 = 0
            for val in system1Sellers:
                if val:
                    num1 += 1
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
            
        #If no combo of systems yields good seller spacing, or not all systems accounted for in the best pair(?), return here
        if not self.Best_Sellers:
            return 0.01
        
        maxGoodDistance = routeLength * 100
        #Less total distance needs to give a higher value
        weightedDistance = (maxGoodDistance/self.Total_Distance) * 2
        
        minSupply = routeLength * 12
        weightedSupply = math.log(self.Total_Supply,minSupply) * 2
  
        avgCost = sum([sum(val.Cost) for val in self.__Route])/routeLength
        #using log because these values can be very high
        weightedCost = math.log(avgCost,1000)



        totalValue = (pairValue + weightedCost + weightedDistance + weightedSupply) #* self.Route_Type.value
        if weightedCost < 1 or weightedDistance < 2 or weightedSupply < 2:
            totalValue = totalValue * 0.5
        if longestJump > maxJumpRangeLY:
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

        strList.append("\nTotal distance: {0}ly".format(self.Total_Distance))
        strList.append("\nTotal goods: {0}".format(self.Total_Supply))
        strList.append("\nAvg cost: {0}".format(avgCost))
        strList.append("\nType: {0}".format(self.Route_Type.name))
        return ''.join(strList)