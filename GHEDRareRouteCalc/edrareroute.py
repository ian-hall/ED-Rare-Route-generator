from edsystem import EDSystem, DisplayLocation
from collections import Counter, defaultdict
import itertools
import math
from enum import Enum,unique

@unique
class RouteType(Enum):
    Other = 0
    Cluster = 1
    Spread = 2
    Alt = 3
    LongAlt = 4
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
@unique
class FitnessType(Enum):
    EvenSplit = 0
    FirstOver = 1
    Farthest = 2
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class EDRareRoute(object):
#------------------------------------------------------------------------------
    def __init__(self,systemList: [], fType: FitnessType):
        self.__Route = systemList
        self.__Seller_Min = 160
        self.Total_Distance = 0
        self.Total_Supply = sum((val.Max_Supply for val in self.__Route))
        self.Sellers_List = None
        self.Sellers_Dict = None
        self.Max_Cargo = 0
        self.Route_Type = RouteType.Other
        self.Longest_Jump = 0
        
        self.Fitness_Value = -1
        if fType == FitnessType.FirstOver:
            self.Fitness_Value = self.__CalcFitnessAlt()
        elif fType == FitnessType.Farthest:
            self.Fitness_Value = self.__BreakingFitnessAgain()
        else:
            self.Fitness_Value = self.__CalcFitness()
#------------------------------------------------------------------------------
    def GetRoute(self):
        return [val for val in self.__Route]       
#------------------------------------------------------------------------------
    def __CalcFitness(self):
        '''
        Fitness value based on having a roughly even number of systems between sellers
        '''
        #TODO:  Maybe scale value based on longest distance to station
        #       Some routes come out "backwards", need to flag this 
        #       Set up some kind of flag on worst value from supply/distance/cost
        #       Add tracking for max cargo used
        routeLength = self.__Route.__len__()
        self.Total_Distance = 0     
       
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
        self.Longest_Jump = longestJump
        #Route has 2 groups of systems separated by a long jump
        if clusterLong == 2 and (clusterLong + clusterShort) == routeLength:
           self.Route_Type = RouteType.Cluster

        #Route has fairly evenly spaced jumps
        if spreadJumps == routeLength:
            self.Route_Type = RouteType.Spread

        pairValue = -999
        goodPair = 6

        for systemPair in itertools.combinations(self.__Route,2):
            system1 = systemPair[0]
            system2 = systemPair[1]
            allSystemsSellable = [0 for i in range(routeLength)]

            system1Index = self.__Route.index(system1)
            system2Index = self.__Route.index(system2)
            systemJumpsApart = abs(system1Index-system2Index)

            if routeLength%2 == 0 :
                if systemJumpsApart != math.floor(routeLength/2):
                    continue
            else:
                if (systemJumpsApart != math.floor(routeLength/2) and systemJumpsApart != math.ceil(routeLength/2)):
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
                        self.Sellers_List = systemPair
                        pairValue = goodPair
                        break
                else:
                    if pairValue < sum(allSystemsSellable) / 5:
                        pairValue = sum(allSystemsSellable) / 5
                        self.Sellers_List = systemPair
            else:
                if pairValue < sum(allSystemsSellable)/ 15:
                    pairValue = sum(allSystemsSellable) / 15
                    self.Sellers_List = systemPair
            
        #If no combo of systems yields good seller spacing, or not all systems accounted for in the best pair(?), return here
        if self.Sellers_List is None:
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



        totalValue = (((pairValue/goodPair) * pairValue) + weightedCost + weightedDistance + weightedSupply)
        if weightedCost < 1 or weightedDistance < 2 or weightedSupply < 2:
            totalValue = totalValue * 0.5
        if longestJump > maxJumpRangeLY:
            totalValue = totalValue * 0.7

        return totalValue
#------------------------------------------------------------------------------
    def __CalcFitnessAlt(self):
        '''
        Alternative fitness value based on just accounting for all systems in a route without
        regard to system positions in the route.
        Based on selling to the first system next on the route over the __Seller_Min distance
        Also a lot faster than the original __CalcFitness.
        '''
        #TODO: Maybe force leesti/lave/diso/uszaa/orerrere to all be together in a route if more than 2 show up
        #       and the route is long enough, probably do this in the main mutate method
        #       So like, if route is [1,2,3,4,5,6,7] and say {2: 4,6; 3: 1,7; 4: 2,6; 6: 4,2; 7:3,5}
        #       It would be: JUMP       SOLD                UNSOLD
        #                    1                              1
        #                    2                              1,2
        #                    3          1                   2,3
        #                    4          1,2                 3,4
        #                    5          1,2                 3,4,5
        #                    6          1,2,4               3,5,6
        #                    7          1,2,4,3,5           6,7
        #                    8          1,2,4,3,5           6,7,1
        #                    9          1,2,4,3,5,6         7,1,2
        #                   10          1,2,4,3,5,6,7,1     2,3  *DONE*
        routeLength = self.__Route.__len__()
        self.Total_Distance = 0
        self.Route_Type = RouteType.Alt
        sellerScale = 1
        baseValue = 6
        longJumpDistance = 135
        maxJumpDistance = 200
        longestJump = -1
        overLongJump = False
        for i in range(0,routeLength):
            currentSystem = self.__Route[i]
            nextSystem = self.__Route[(i+1)%routeLength]
            jumpDistance = currentSystem.System_Distances[nextSystem.Index]
            if jumpDistance > longestJump:
                longestJump = jumpDistance
            
            if jumpDistance > longJumpDistance:
                overLongJump = True
                self.Route_Type = RouteType.LongAlt
            self.Total_Distance += jumpDistance

        self.Longest_Jump = longestJump
        systemsBySeller = {}
        for seller in self.__Route:
            systemsBySeller[seller] = []
            for system in self.__Route:
                if seller.System_Distances[system.Index] >= self.__Seller_Min:
                    systemsBySeller[seller].append(system)
        ableToSell = routeLength
        for k,v in systemsBySeller.items():
            if v.__len__() == 0:
                ableToSell -= 1
        sellersValue = ableToSell/routeLength * baseValue
        
        #Skip this part if we already know we can't sell all goods
        maxSellersWaiting = -1
        maxCargo = 0
        if sellersValue >= baseValue:
            #sellersUsed = []
            sold = []
            unsold = []
            #Go through at most twice, since if a systems doesnt sell by then it won't sell
            #TODO: GO through the route in reverse at the same time, i forgot why though
            for i in range(routeLength*2):
                currentSys = self.__Route[i%routeLength];
                unsold.append(currentSys)
                toRemove = []
                numUnsold = 0
                for checkSys in unsold:
                    #Means we can sell checkSys at currentSys
                    sellableSystems = systemsBySeller[currentSys]
                    if systemsBySeller[currentSys].count(checkSys) != 0:
                        toRemove.append(checkSys)
                        sold.append(checkSys)
                    numUnsold += 1
                if numUnsold > maxSellersWaiting:
                    maxSellersWaiting = numUnsold
                if toRemove.__len__() != 0:
                    maxCargo = max(maxCargo,sum((sys.Max_Supply for sys in unsold[:-1])))
                    #sellersUsed.append(currentSys)
                    if self.Sellers_Dict == None:
                        self.Sellers_Dict = defaultdict(list)
                    self.Sellers_Dict[currentSys].extend(toRemove)
                for sys in toRemove:
                    unsold.remove(sys)
                if set(sold) == set(self.__Route):
                    break
        else:
            #Scale overall value down
            sellerScale = 0.25

        maxGoodDistance = routeLength * longJumpDistance
        weightedDistance = (maxGoodDistance/self.Total_Distance) * 2
        
        minSupply = routeLength * 12
        weightedSupply = math.log(self.Total_Supply,minSupply) * 2
  
        avgCost = sum([sum(val.Cost) for val in self.__Route])/routeLength
        #using log because these values can be very high
        weightedCost = math.log(avgCost,1000)

        totalValue = (sellersValue + weightedCost + weightedDistance + weightedSupply) * sellerScale
        
        if weightedCost < 1 or weightedDistance < 2 or weightedSupply < 2:
            totalValue = totalValue * 0.5
        if sellersValue < baseValue/2:
            totalValue = totalValue * 0.25

        #Only lower value for maxwaiting and maxjump on shorter routes
        #TODO: Change this to not be so lax on larger routes, too common to have 10+ stations sell at one place
        if overLongJump and routeLength < 16:
            totalValue = totalValue * 0.8
        if longestJump > maxJumpDistance:
            totalValue = totalValue * 0.45
        
        #TODO: scale this based off some set cargo amount that increases for longer routes
        if maxCargo > 80:
            totalValue = totalValue * 1
        
        self.Max_Cargo = maxCargo
        return totalValue
#------------------------------------------------------------------------------
    #Draws the route
    #TODO: Maybe do some kind of ratio between oldX/newX to squish xVals so the route doesn't look so wide
    #       Add a better way to represent large routes than first letter of system, too many duplicates
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

        #For printing split fitness values
        #TODO: Flag systems that can be sold at either seller
        if self.Sellers_List is not None:
            sellersPerSystem = {}
            for system in self.__Route:
                tempSellers = []
                for distToCheck in self.__Route:
                    if system.System_Distances[distToCheck.Index] >= self.__Seller_Min:
                        tempSellers.append(distToCheck)
                sellersPerSystem[system] = tempSellers
            strList.append("\t\tRoute Value:{0:.5f}\n".format(self.Fitness_Value))
            for system in self.__Route:
                if system in self.Sellers_List:
                    strList.append("{0}: <{1} ({2})>".format(count+1,system.System_Name, system.Station_Name))
                else:
                    strList.append("{0}: {1} ({2})".format(count+1,system.System_Name, system.Station_Name))
                if system.PermitReq:
                    strList.append("**Permit**")
                strList.append("\n")
                count += 1
            
            for station in self.Sellers_List:
                strList.append("\nAt <{0}> sell:\n\t".format(station.System_Name))
                for seller in sellersPerSystem[station]:
                    if seller in self.Sellers_List:
                        strList.append(" <{0}> ".format(seller.System_Name))
                    else:
                        strList.append(" {0} ".format(seller.System_Name))
        
        #For printing alt fitness values
        elif self.Sellers_Dict is not None:
            strList.append("\t\tRoute Value:{0:.5f}\n".format(self.Fitness_Value))
            for system in self.__Route:
                if system in self.Sellers_Dict:
                    strList.append("{0}: <{1} ({2})>".format(count+1,system.System_Name, system.Station_Name))
                else:
                    strList.append("{0}: {1} ({2})".format(count+1,system.System_Name, system.Station_Name))
                if system.PermitReq:
                    strList.append("**Permit**")
                strList.append("\n")
                count += 1

            for system in self.__Route:
                if system in self.Sellers_Dict:
                    strList.append("\nAt <{0}> sell:\n\t".format(system.System_Name))
                    for seller in set(self.Sellers_Dict[system]):
                        if seller in self.Sellers_Dict:
                            strList.append(" <{0}> ".format(seller.System_Name))
                        else:
                            strList.append(" {0} ".format(seller.System_Name))

        #For just displaying the systems if they are not a good route
        else:
            strList.append("\n(Really bad)Route value:{0}\n".format(self.Fitness_Value))
            for system in self.__Route:
               strList.append('{0}\n'.format(system))

        strList.append("\nTotal distance: {0:.3f}ly".format(self.Total_Distance))
        strList.append("\nLongest jump: {0:.3f}ly".format(self.Longest_Jump))
        strList.append("\nTotal goods: {0:.2f}".format(self.Total_Supply))
        strList.append("\nCargo space req: {0}".format(self.Max_Cargo))
        strList.append("\nAvg cost: {0:.2f}".format(avgCost))
        strList.append("\nType: {0}".format(self.Route_Type.name))

        return ''.join(strList)
#------------------------------------------------------------------------------
    def __BreakingFitnessAgain(self):
        '''
        Like alt fitness except farthest
        '''
        #TODO:  Need to adjust fitvals, genetic is failing at finding good routes
        #       Maybe I have values too low??
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
        self.Longest_Jump = longestJump

        if clusterLong == 2 and (clusterLong + clusterShort) == routeLength:
           self.Route_Type = RouteType.Cluster

        if spreadJumps == routeLength:
            self.Route_Type = RouteType.Spread

        farthestSystems = {}
        for seller in self.__Route:
            farthestSystems[seller] = None
            for system in self.__Route:
                distToSystem = seller.System_Distances[system.Index]
                if distToSystem > self.__Seller_Min:
                    if farthestSystems[seller] is None:
                        farthestSystems[seller] = system
                    else:
                        currentFarthest = seller.System_Distances[farthestSystems[seller].Index]
                        if distToSystem > currentFarthest:
                            farthestSystems[seller] = system

        baseValue = 6
        fitnessScale = 1
        numUnsellable = 0
        for k,v in farthestSystems.items():
            if v is None:
                numUnsellable += 1
        sellerScale = ((routeLength-numUnsellable)/routeLength)
        sellersValue = baseValue * sellerScale
        if sellersValue == 0:
            return 0.01
        #TODO:  If sellers aren't spaced evenly -> lower val
        #       If systems aren't in a good order -> lower val
        #       If more than 2 sellers -> lower val
        #       Expand this to potentially allow for more than 2 sellers
        #       Add tracker for max cargo usage
        if sellerScale >= 1:
            sold = []
            unsold = []
            for i in range(routeLength*2):
                currentSys = self.__Route[i%routeLength];
                unsold.append(currentSys)
                toRemove = []
                numUnsold = 0
                for checkSys in unsold:
                    #Means we can sell checkSys at currentSys
                    sellableSystems = systemsBySeller[currentSys]
                    if systemsBySeller[currentSys].count(checkSys) != 0:
                        toRemove.append(checkSys)
                        sold.append(checkSys)
                    numUnsold += 1
                if numUnsold > maxSellersWaiting:
                    maxSellersWaiting = numUnsold
                if toRemove.__len__() != 0:
                    maxCargo = max(maxCargo,sum((sys.Max_Supply for sys in unsold[:-1])))
                    if self.Sellers_Dict == None:
                        self.Sellers_Dict = defaultdict(list)
                    self.Sellers_Dict[currentSys].extend(toRemove)
                for sys in toRemove:
                    unsold.remove(sys)
                if set(sold) == set(self.__Route):
                    break
            #allSellers = []
            #for system,seller in farthestSystems.items():
            #    allSellers.append(seller)
            #uniqueSellers = list(set(allSellers))
            #if uniqueSellers.__len__() != 2:
            #    return sellersValue * sellerScale * 0.75

            #seller1Position = self.__Route.index(uniqueSellers[0])
            #seller2Position = self.__Route.index(uniqueSellers[1])
            #systemJumpsApart = abs(seller1Position-seller2Position)

            #if routeLength%2 == 0 :
            #    if systemJumpsApart != math.floor(routeLength/2):
            #        sellersValue = sellersValue * 0.75
            #else:
            #    if (systemJumpsApart != math.floor(routeLength/2) and systemJumpsApart != math.ceil(routeLength/2)):
            #        sellersValue = sellersValue * 0.75
                        
            #seller1Systems = []
            #seller2Systems = []
            ##TODO: Dicts here to allow for routes with more than 2 sellers
            #sellerSystems = defaultdict(list)
            #sellerIndices = defaultdict(list)
            #for system,seller in farthestSystems.items():
            #    sellerSystems[seller].append(system)
            #    sellerIndices[seller].append(self.__Route.index(system))
            #for system,seller in farthestSystems.items():
            #    if seller == uniqueSellers[0]:
            #        seller1Systems.append(system)
            #    else:
            #        seller2Systems.append(system)
            
            #seller1Indices = sorted([self.__Route.index(system) for system in seller1Systems])
            #seller2Indices = sorted([self.__Route.index(system) for system in seller2Systems])

            #if routeLength%2 == 0 :
            #    if seller1Indices.__len__() != seller2Indices.__len__():
            #        sellersValue = sellersValue * 0.75
            #else:
            #    if abs(seller1Indices.__len__() - seller2Indices.__len__()) > 1:
            #        sellersValue = sellersValue * 0.75

            ##If difference between last and first is Indices.len-1 then we know we have a route that is in order (i think)
            ##if difference between last and first is route.len-1 then we know we need to check the values so they loop around

            #seller1SystemsInOrder = False
            #seller2SystemsInOrder = False

            #if (seller1Indices[-1] - seller1Indices[0]) == (seller1Indices.__len__() - 1):
            #    seller1SystemsInOrder = True
            #elif (seller1Indices[-1] - seller1Indices[0]) == (self.__Route.__len__() - 1):
            #    seller1SystemsInOrder = True

            #if (seller2Indices[-1] - seller2Indices[0]) == (seller2Indices.__len__() - 1):
            #    seller2SystemsInOrder = True
            #elif (seller2Indices[-1] - seller2Indices[0]) == (self.__Route.__len__() - 1):
            #    seller2SystemsInOrder = True

            #if not (seller1SystemsInOrder and seller2SystemsInOrder):
            #    sellersValue = sellersValue * 0.75
            #else:
            #    self.Sellers_Dict = { uniqueSellers[0]:seller1Systems, uniqueSellers[1]:seller2Systems }
        else:
            sellersValue = sellersValue * 0.25
        
            
        maxGoodDistance = routeLength * 100
        weightedDistance = (maxGoodDistance/self.Total_Distance) * 2
        
        minSupply = routeLength * 12
        weightedSupply = math.log(self.Total_Supply,minSupply) * 2
  
        avgCost = sum([sum(val.Cost) for val in self.__Route])/routeLength
        weightedCost = math.log(avgCost,1000)

        totalValue = (sellersValue + weightedCost + weightedDistance + weightedSupply) * sellerScale
        
        if weightedCost < 1 or weightedDistance < 2 or weightedSupply < 2:
            totalValue = totalValue * 0.5
        if sellersValue < baseValue/2:
            totalValue = totalValue * 0.25

        if longestJump > maxJumpRangeLY:
            totalValue = totalValue * 0.45
        
        
        return totalValue