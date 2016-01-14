from edsystem import EDSystem, DisplayLocation
from collections import Counter
import itertools
import math
from enum import Enum,unique

@unique
class RouteType(Enum):
    Other = 0
    Cluster = 1
    Spread = 2
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
@unique
class FitnessType(Enum):
    Default = 0
    Alternative = 1
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class EDRareRoute(object):
#------------------------------------------------------------------------------
    def __init__(self,systemList: [], fType = FitnessType.Default):
        self.__Route = systemList
        self.__Seller_Min = 155
        self.Total_Distance = 0
        self.Total_Supply = sum([val.Max_Supply for val in self.__Route])
        self.Best_Sellers = None
        self.Route_Type = RouteType.Other #Just default to 'other' as a catch all
        self.Fitness_Type = fType #Probably can get rid of this once CalcFitAlt is done
        self.Fitness_Value = self.__CalcFitness() if fType == FitnessType.Default else self.__CalcFitnessAlt()
#------------------------------------------------------------------------------
    def GetRoute(self):
        return [val for val in self.__Route]       
#------------------------------------------------------------------------------
    def __CalcFitness(self):
        #TODO: Maybe scale value based on longest distance to station
        #      Some routes come out "backwards", need to flag this 
        #      Set up some kind of flag on worst value from supply/distance/cost
        routeLength = self.__Route.__len__()     
       
        clusterShortLY = 50
        clusterLongLY = 145
        spreadMaxLY = 110
        maxJumpRangeLY = 200
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
            if jumpDistance <= spreadMaxLY:
                spreadJumps += 1 
        
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
        
        #Special case for shorter routes
        maxGoodDistance = routeLength * 100
        if routeLength < 6:
            maxGoodDistance = maxGoodDistance * 1.2
        #Less total distance needs to give a higher value
        weightedDistance = (maxGoodDistance/self.Total_Distance) * 2
        
        minSupply = routeLength * 12
        weightedSupply = math.log(self.Total_Supply,minSupply) * 2
  
        avgCost = sum([sum(val.Cost) for val in self.__Route])/routeLength
        #using log because these values can be very high
        weightedCost = math.log(avgCost,1000)



        totalValue = (pairValue + weightedCost + weightedDistance + weightedSupply)
        if weightedCost < 1 or weightedDistance < 2 or weightedSupply < 2:
            totalValue = totalValue * 0.5
        if longestJump > maxJumpRangeLY:
            totalValue = totalValue * 0.7

        return totalValue
#------------------------------------------------------------------------------
    #TODO: Alternative fitness value based on just accounting for all systems in a route without
    #      regard to systems positions in the route
    def __CalcFitnessAlt(self):
        routeLength = self.__Route.__len__()
        maxJumpDistance = 100
        overMax = False
        for i in range(0,routeLength):
            currentSystem = self.__Route[i]
            nextSystem = self.__Route[(i+1)%routeLength]
            jumpDistance = currentSystem.System_Distances[nextSystem.Index]
            if jumpDistance > maxJumpDistance:
                overMax = True
            self.Total_Distance += jumpDistance
        if overMax:
            return 0.1

        systemsBySeller = {}
        for seller in self.__Route:
            systemsBySeller[seller] = []
            for system in self.__Route:
                if seller.System_Distances[system.Index] > self.__Seller_Min:
                    systemsBySeller[seller].append(system)
        #TODO: Find least number of systems that account for all rares to sell
        #       Go by groups of 2,3,....to maybe len/2. Stop when we find the
        #       First occurance of all systems. This should give us the min needed
        
        #Place holder so I can actually use this to run the program    
        from random import uniform
        return uniform(0,12)
#------------------------------------------------------------------------------
    #Draws the route
    #TODO: Maybe do some kind of ratio between oldX/newX to squish xVals so the route doesn't look so wide
    def DrawRoute(self):
        maxCols = 53
        maxRows = 20

        xVals = [system.Location['x'] for system in self.__Route]
        yVals = [system.Location['y'] for system in self.__Route]

        xMin = min(xVals)
        yMin = min(yVals)

        if xMin < 0:
            xValsNew = [abs(xMin) + val for val in xVals]
        else:
            xValsNew = [val - xMin for val in xVals]
        if yMin < 0:
            yValsNew = [abs(yMin) + val for val in yVals]
        else:
            yValsNew = [val - yMin for val in yVals]

        xMax = max(xValsNew)
        yMax = max(yValsNew)
        points = []

        #Everything is shifted so mins are 0 and max() is the difference between points
        #Round stuff to graph it
        if xMax == 0 or yMax == 0:
            print("Unable to draw route")
            return

        for i in range(xValsNew.__len__()):
            if xValsNew[i] != 0:
                if xValsNew[i] == xMax:
                    xValsNew[i] = maxCols
                else:
                    xValsNew[i] = round((maxCols / xMax) * xValsNew[i])
            if yValsNew[i] != 0:
                if yValsNew[i] == yMax:
                    yValsNew[i] = maxRows
                else:
                    yValsNew[i] = round((maxRows / yMax) * yValsNew[i])
            points.append(DisplayLocation(row=yValsNew[i],col=xValsNew[i],name=self.__Route[i].System_Name))
        
        #Fudge numbers so we dont have same row/col for systems, shift on the cols most of the time, then a row
        #if we get in some kind of loop. (really only one group of systems this applies to)
        pointsCounter = Counter(points)
        split = 10
        loops = 0
        while sum([v for k,v in pointsCounter.items() if v == 1]) != points.__len__():
            for k,v in pointsCounter.items():
                if v > 1:
                    toChange = points.index(k)
                    if loops%split == split-1:
                        if points[toChange].Row + 1 < maxRows:
                            points[toChange].Row += 1
                        else:
                            points[toChange].Row -= 1
                    else:
                        if points[toChange].Col + 1 < maxCols:
                            points[toChange].Col += 1
                        else:
                            points[toChange].Col -= 1

            loops += 1
            pointsCounter = Counter(points)

        for i in range(points.__len__()):
            for j in range(points.__len__()):
                if i != j:
                    if points[i] == points[j]:
                        print("Unable to draw route")
                        return

        strList = []
        #rowRange is reversed because we print from the top down
        rowRange = range(maxRows,-1,-1)
        colRange = range(maxCols+1)

        for row in rowRange:
            for col in colRange:
                pointToCheck = DisplayLocation(row,col)
                if pointToCheck in points:
                    pIndex = points.index(pointToCheck)
                    if self.__Route.__len__() < 10:
                        strList.append('{0}'.format(pIndex + 1))
                    else:
                        strList.append('{0}'.format(points[pIndex].System_Name[0]))
                else:
                    strList.append('-')
            strList.append('\n')
        print(''.join(strList))
#------------------------------------------------------------------------------
    def __str__(self):
        avgCost = sum([sum(val.Cost) for val in self.__Route])/self.__Route.__len__()
        strList = []
        count = 0
        if self.Best_Sellers and self.Fitness_Type == FitnessType.Default:
            sellersPerSystem = {}
            for system in self.__Route:
                tempSellers = []
                for distToCheck in self.__Route:
                    if system.System_Distances[distToCheck.Index] >= self.__Seller_Min:
                        tempSellers.append(distToCheck)
                sellersPerSystem[system] = tempSellers
            strList.append("\t\tRoute Value:{0:.5f}\n".format(self.Fitness_Value))
            for system in self.__Route:
                if system in self.Best_Sellers:
                    strList.append("{0}: <{1} ({2})>".format(count+1,system.System_Name, system.Station_Name))
                else:
                    strList.append("{0}: {1} ({2})".format(count+1,system.System_Name, system.Station_Name))
                if system.PermitReq:
                    strList.append("**Permit**")
                strList.append("\n")
                count += 1
            
            for station in self.Best_Sellers:
                strList.append("\nAt <{0}> sell:\n\t".format(station.System_Name))
                for seller in sellersPerSystem[station]:
                    if seller in self.Best_Sellers:
                        strList.append(" <{0}> ".format(seller.System_Name))
                    else:
                        strList.append(" {0} ".format(seller.System_Name))
        
        else:
            strList.append("\n(Really bad)Route value:{0}\n".format(self.Fitness_Value))
            for system in self.__Route:
               strList.append('{0}\n'.format(system))

        strList.append("\nTotal distance: {0:.3f}ly".format(self.Total_Distance))
        strList.append("\nTotal goods: {0:.2f}".format(self.Total_Supply))
        strList.append("\nAvg cost: {0:.2f}".format(avgCost))
        strList.append("\nType: {0}".format(self.Route_Type.name))

        return ''.join(strList)