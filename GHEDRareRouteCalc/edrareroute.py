from edsystem import EDSystem, DisplayLocation
from collections import Counter, defaultdict
import itertools
import math
import tkinter
import random
from enum import Enum,unique
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
@unique
class RouteType(Enum):
    Other = 0
    Cluster = 1
    Spread = 2
    FirstOver = 3
    FirstOverLong = 4
    Distance = 5
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
@unique
class FitnessType(Enum):
    EvenSplit = 0
    FirstOver = 1
    Distance = 2
    Tester = 3

#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
#TODO:  Add tracking for max_cargo to all fitness calculations
#       Need to finish adjusting the weightedCost values in the fitness functions
#           to better support routes of short lengths.
class EDRareRoute(object):
#------------------------------------------------------------------------------
    def __init__(self,systemList: list, fType: FitnessType):
        if(systemList.__len__() < 3):
            raise Exception("Routes must be 3 or more systems")
        self.__Route = systemList
        self.__Seller_Min = 160
        self.__Total_Distance = 0
        self.__Total_Cargo = sum((system.Max_Supply for system in self.__Route))
        self.__Sellers_List = None
        self.__Sellers_Dict = None
        self.__Max_Cargo = 0
        self.__Route_Type = RouteType.Other
        self.__Longest_Jump = 0
        
        self.__Fitness_Value = -1
        if fType == FitnessType.FirstOver:
            self.__Fitness_Value = self.__Fitness_FirstOver()
        elif fType == FitnessType.Tester:
            self.__Fitness_Value = self.__FitnessTester()
        elif fType == FitnessType.Distance:
            self.__Fitness_Value = self.__FitnessDistance()
        elif fType == FitnessType.EvenSplit:
            self.__Fitness_Value = self.__Fitness_EvenSplit()
        else:
            self.__Fitness_Value = self.__Fitness_FirstOver()
#------------------------------------------------------------------------------
    @property
    def Fitness(self) -> float:
        return self.__Fitness_Value
#------------------------------------------------------------------------------
    @property
    def Systems(self) -> list:
        return [system for system in self.__Route]     
#------------------------------------------------------------------------------
    @property
    def Route_Type(self) -> RouteType:
        return self.__Route_Type
#------------------------------------------------------------------------------
    @property
    def Total_Cargo(self) -> float:
        return self.__Total_Cargo
#------------------------------------------------------------------------------
    @property
    def Total_Distance(self) -> float:
        return self.__Total_Distance
#------------------------------------------------------------------------------
    @property
    def Length(self) -> int:
        return self.__Route.__len__() 
#------------------------------------------------------------------------------
    def __Fitness_EvenSplit(self):
        '''
        Fitness value based on having a roughly even number of systems between sellers
        '''
        #TODO:  Add tracking for max cargo used
        #       Try again without itertools combos maybe and instead do only check values that are evenly spaced out like we want
        #           Actually looks like I already do this because I continue if routes arent split???
        routeLength = self.Length
        self.__Total_Distance = 0     
       
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
            jumpDistance = currentSystem.GetDistanceTo(nextSystem)
            self.__Total_Distance += jumpDistance
            longestJump = jumpDistance if jumpDistance > longestJump else longestJump
            if jumpDistance <= clusterShortLY:
                clusterShort += 1
            if jumpDistance >= clusterLongLY and jumpDistance <= maxJumpRangeLY:
                clusterLong += 1 
            if jumpDistance <= spreadMaxLY:
                spreadJumps += 1 
        self.__Longest_Jump = longestJump
        #Route has 2 groups of systems separated by a long jump
        if clusterLong == 2 and (clusterLong + clusterShort) == routeLength:
           self.__Route_Type = RouteType.Cluster

        #Route has fairly evenly spaced jumps
        if spreadJumps == routeLength:
            self.__Route_Type = RouteType.Spread

        pairValue = -999
        goodPair = 6

        for systemPair in itertools.combinations(self.__Route,2):
            system1 = systemPair[0]
            system2 = systemPair[1]
            allSystemsSellable = [0 for i in range(routeLength)]

            system1Index = self.__Route.index(system1)
            system2Index = self.__Route.index(system2)
            systemJumpsApart = abs(system1Index-system2Index)

            #if routeLength%2 == 0 :
            #    if systemJumpsApart != math.floor(routeLength/2):
            #        continue
            #else:
            if (systemJumpsApart != math.floor(routeLength/2) and systemJumpsApart != math.ceil(routeLength/2)):
                continue

            #TODO: Fix spacing
            #      I don't even remember what the heck this is supposed to be
            system1Sellers = []
            system1LastIndex = -999
            system2Sellers = []
            system2LastIndex = -999
            for i in range(1,routeLength):
                system1IndexToCheck = (i + system1Index) % routeLength
                currentSystem = self.__Route[system1IndexToCheck]
                if system1.GetDistanceTo(currentSystem) >= self.__Seller_Min:
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
                if system2.GetDistanceTo(currentSystem) >= self.__Seller_Min:
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
                        self.__Sellers_List = systemPair
                        pairValue = goodPair
                        break
                else:
                    if pairValue < sum(allSystemsSellable) / 5:
                        pairValue = sum(allSystemsSellable) / 5
                        self.__Sellers_List = systemPair
            else:
                if pairValue < sum(allSystemsSellable)/ 15:
                    pairValue = sum(allSystemsSellable) / 15
                    self.__Sellers_List = systemPair
            
        #If no combo of systems yields good seller spacing, or not all systems accounted for in the best pair(?), return here
        if self.__Sellers_List is None:
            return 0.01
        
        #Special case for shorter routes
        maxGoodDistance = routeLength * 100
        if routeLength < 6:
            maxGoodDistance = maxGoodDistance * 1.2
        #Less total distance needs to give a higher value
        weightedDistance = (maxGoodDistance/self.__Total_Distance) * 2
        
        minSupply = routeLength * 10
        weightedSupply = math.log(self.__Total_Cargo,minSupply) * 2
  
        totalGoodsCost = sum([system.Total_Cost for system in self.__Route])
        weightedCost = totalGoodsCost/(routeLength * 15000)

        totalValue = (((pairValue/goodPair) * pairValue) + weightedCost + weightedDistance + weightedSupply)
        if weightedCost < 1 or weightedDistance < 2 or weightedSupply < 2:
            totalValue = totalValue * 0.5
        if longestJump > maxJumpRangeLY:
            totalValue = totalValue * 0.7

        return totalValue
#------------------------------------------------------------------------------
    def __Fitness_FirstOver(self):
        '''
        Alternative fitness value based on just accounting for all systems in a route without
        regard to system positions in the route.
        Based on selling to the first system next on the route over the __Seller_Min distance
        Also a lot faster than the original __CalcFitness.
        '''
        #TODO: 
        #       Add a check for the amount of jumps a system stays in before it is sold and scale if over some value
        routeLength = self.__Route.__len__()
        self.__Total_Distance = 0
        self.__Route_Type = RouteType.FirstOver
        sellerScale = 1
        baseValue = 6
        longJumpDistance = 135
        maxJumpDistance = 200
        longestJump = -1
        overLongJump = False
        for i in range(0,routeLength):
            currentSystem = self.__Route[i]
            nextSystem = self.__Route[(i+1)%routeLength]
            jumpDistance = currentSystem.GetDistanceTo(nextSystem)
            if jumpDistance > longestJump:
                longestJump = jumpDistance
            
            if jumpDistance > longJumpDistance:
                overLongJump = True
                self.__Route_Type = RouteType.FirstOverLong
            self.__Total_Distance += jumpDistance

        self.__Longest_Jump = longestJump
        systemsBySeller = {}
        for seller in self.__Route:
            systemsBySeller[seller] = []
            for system in self.__Route:
                if seller.GetDistanceTo(system) >= self.__Seller_Min:
                    systemsBySeller[seller].append(system)
        ableToSell = routeLength
        for k,v in systemsBySeller.items():
            if v.__len__() == 0:
                ableToSell -= 1
        sellersValue = ableToSell/routeLength * baseValue
        
        #Skip this part if we already know we can't sell all goods
        maxCargo = 0
        sellersDifference = None
        mostSellers = -1
        leastSellers = routeLength
        if sellersValue >= baseValue:
            #sellersUsed = []
            sold = []
            unsold = []
            #Go through at most twice, since if a systems doesnt sell by then it won't sell
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
                if toRemove.__len__() != 0:
                    maxCargo = max(maxCargo,sum((sys.Max_Supply for sys in unsold[:-1])))
                    if self.__Sellers_Dict == None:
                        self.__Sellers_Dict = defaultdict(list)
                    self.__Sellers_Dict[currentSys].extend(toRemove)
                numSold = 0
                for sys in toRemove:
                    unsold.remove(sys)
                    numSold = numSold + 1
                mostSellers = max(mostSellers,numSold)
                leastSellers = min(leastSellers,numSold)
                if set(sold) == set(self.__Route):
                    sellersDifference = mostSellers - leastSellers
                    break
        else:
            #Scale overall value down
            sellerScale = 0.25

        maxGoodDistance = routeLength * longJumpDistance
        weightedDistance = (maxGoodDistance/self.__Total_Distance) * 2
        
        minSupply = routeLength * 10
        weightedSupply = math.log(self.__Total_Cargo,minSupply) * 2
  
        totalGoodsCost = sum([system.Total_Cost for system in self.__Route])
        #Base this on an average purchase price of 1x000cr per system   
        weightedCost = totalGoodsCost/(routeLength * 15000)
        
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
        
        #TODO: Scale here, larger allowance for sellersDifference on longer routes.... maybe like ceil(len/5) or something  with a min of 1? 
        if sellersDifference is not None:
            totalValue = (totalValue * 0.5 ) if (sellersDifference > 4) else totalValue
        
        self.__Max_Cargo = maxCargo
        return totalValue
#------------------------------------------------------------------------------
    def __FitnessDistance(self):
        self.__Route_Type = RouteType.Distance
        routeLength = self.Length
        self.__Total_Distance = 0
        for i in range(0,routeLength):
            currentSystem = self.__Route[i]
            nextSystem = self.__Route[(i+1)%routeLength]
            jumpDistance = currentSystem.GetDistanceTo(nextSystem)
            self.__Total_Distance += jumpDistance
        
        maxGoodDistance = routeLength * 100
        weightedDistance = (maxGoodDistance/self.__Total_Distance)
        if weightedDistance < 0.75:
            return weightedDistance * 6
        else:
            return weightedDistance * 10
#------------------------------------------------------------------------------
    #TODO: Maybe do some kind of ratio between oldX/newX to squish xVals so the route doesn't look so wide
    #       Add a better way to represent large routes than first letter of system, too many duplicates
    def DisplayInConsole(self):
        '''
        prints the route with the power of the console
        '''
        maxCols = 53
        maxRows = 20

        xVals = [system.Location['x'] for system in self.__Route]
        yVals = [system.Location['y'] for system in self.__Route]

        xMin = min(xVals)
        yMin = min(yVals)

        if xMin < 0:
            xValsNew = [abs(xMin) + x for x in xVals]
        else:
            xValsNew = [x - xMin for x in xVals]
        if yMin < 0:
            yValsNew = [abs(yMin) + y for y in yVals]
        else:
            yValsNew = [y - yMin for y in yVals]

        xMax = max(xValsNew)
        yMax = max(yValsNew)
        points = []

        #Everything is shifted so mins are 0 and max() is the difference between points
        #Round stuff to graph it
        if xMax == 0 and yMax == 0:
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
    def DrawRoute(self,showLines:bool=True):
        '''
        Draws the route using tkinter
        '''
        #TODO:  Find why zoom jumps all over the place
        #       Add color to seller locations on mouseover
        routeLength = self.__Route.__len__()

        cWidth = 900
        cHeight = 600
        ovalRad = 12
        border = 20

        maxCols = cWidth - (2*border)
        maxRows = cHeight - (2*border)

        xVals = [system.Location['x'] for system in self.__Route]
        yVals = [system.Location['y'] for system in self.__Route]
        zVals = [system.Location['z'] for system in self.__Route]

        xMin = min(xVals)
        yMin = min(yVals)
        zMin = min(zVals)

        if xMin < border:
            xValsNew = [abs(xMin) + x + border for x in xVals]
        else:
            xValsNew = [x - xMin for x in xVals]
        if yMin < border:
            yValsNew = [abs(yMin) + y + border for y in yVals]
        else:
            yValsNew = [y - yMin for y in yVals]

        xMax = max(xValsNew)
        yMax = max(yValsNew)
        zMax = max(zVals)
        points = []

        if xMax == 0 and yMax == 0:
            print("Unable to draw route")
            return

        for i in range(xValsNew.__len__()):
            if xValsNew[i] != 0:
                if xValsNew[i] == xMax:
                    xValsNew[i] = maxCols
                else:
                    xValsNew[i] = round((maxCols / xMax) * xValsNew[i])
            else:
                xValsNew[i] = border
            if yValsNew[i] != 0:
                if yValsNew[i] == yMax:
                    yValsNew[i] = maxRows
                else:
                    yValsNew[i] = round((maxRows / yMax) * yValsNew[i])
            else:
                yValsNew[i] = border

        xMax = max(xValsNew)
        yMax = max(yValsNew)
        #flip yvals around and add border size to all
        yValsNew = [(yMax - y) + border for y in yValsNew]

        for i in range(xValsNew.__len__()):
            points.append(DisplayLocation(row=yValsNew[i],col=xValsNew[i],depth=zVals[i],name=self.__Route[i].System_Name))


        #TODO: Maybe have this shuffle based on ovalRad so we dont have overlapping ovals
        #      Instead of doing counter(points), need to go through the point list and check which points are within
        #      ovalRad of eachother
        pointsCounter = Counter(points)
        split = 10
        loops = 0
        while sum([v for k,v in pointsCounter.items() if v == 1]) != points.__len__():
            for k,v in pointsCounter.items():
                if v > 1:
                    toChange = points.index(k)
                    if loops%split == split-1:
                        if points[toChange].Row + ovalRad < maxRows:
                            points[toChange].Row += ovalRad
                        else:
                            points[toChange].Row -= ovalRad
                    else:
                        if points[toChange].Col + ovalRad < maxCols:
                            points[toChange].Col += ovalRad
                        else:
                            points[toChange].Col -= ovalRad
            loops += 1
            pointsCounter = Counter(points)

        for i in range(points.__len__()):
            for j in range(points.__len__()):
                if i != j:
                    if points[i] == points[j]:
                        print("Unable to draw route")
                        return

        zValsNew = [z + abs(zMin) for z in zVals]
        zMax = max(zValsNew)
        #Red -> low, Green -> high
        fillColors = ["#FF0000", "#FF6000", "#FFBF00", "#DFFF00", "#80FF00", "#20FF00", "#00FF40"]
        colorStep = (zMax / (fillColors.__len__())) + 0.1

        root = tkinter.Tk()
        bgColor = "#666666"
        systemLabel = tkinter.Label(root)
        systemLabel.pack(fill=tkinter.BOTH)

        def clearSystemLabel(event):
            systemLabel.config(text="")


        canvas = tkinter.Canvas(root,width=cWidth,height=cHeight,bg=bgColor)

        if showLines:
            for i in range(routeLength):
                currSys = self.__Route[i%routeLength]
                nextSys = self.__Route[(i+1)%routeLength]
                jumpDistance = currSys.GetDistanceTo(nextSys)
                #gross
                #also doesnt look as good as I thought
                if( (self.__Sellers_Dict is not None and nextSys in self.__Sellers_Dict) or 
                    (self.__Sellers_List is not None and nextSys in self.__Sellers_List) ):
                    currLine = canvas.create_line(points[i%routeLength].Col,points[i%routeLength].Row,
                                                  points[(i+1)%routeLength].Col,points[(i+1)%routeLength].Row,
                                                  arrow="last",arrowshape=(20,30,20),width=4)
                else:
                    currLine = canvas.create_line(points[i%routeLength].Col,points[i%routeLength].Row,
                                                  points[(i+1)%routeLength].Col,points[(i+1)%routeLength].Row,
                                                  width=4)

                canvas.tag_bind(currLine,"<Motion>", lambda e, i=i, jumpDist=jumpDistance: systemLabel.config(text="{0} -> {1}: {2:.2F}ly".format(points[i%routeLength].System_Name,
                                                                                                                     points[(i+1)%routeLength].System_Name,
                                                                                                                     jumpDist)))

        currSysInd = 0
        for point in points:
            currSys = self.__Route[currSysInd]
            colorIndex = int((point.Depth + abs(zMin))//colorStep)
            fill = fillColors[colorIndex]
            sysOval = canvas.create_oval(point.Col - ovalRad,point.Row - ovalRad,point.Col + ovalRad,point.Row + ovalRad, fill=fill)
            canvas.tag_bind(sysOval,"<Motion>",lambda e, currSys=currSys,sysInd=currSysInd: systemLabel.config(text="{0}: {1}".format(sysInd+1,currSys)))
            currSysInd += 1

        def scaleCanv(event):
            #thanks snackoverflow
            #TODO: Make zoom zoom more better
            if (event.delta > 0):
                canvas.scale("all", canvas.winfo_width()/2, canvas.winfo_height()/2, 1.1, 1.1)
            elif (event.delta < 0):
                canvas.scale("all", canvas.winfo_width()/2, canvas.winfo_height()/2, 0.9, 0.9)
            canvas.configure(scrollregion = canvas.bbox("all"))
        
        canvas.bind("<MouseWheel>",lambda e: scaleCanv(e))    
        canvas.bind("<Button-1>",lambda e: canvas.scan_mark(e.x,e.y))
        canvas.bind("<B1-Motion>",lambda e: canvas.scan_dragto(e.x,e.y,gain=1))
        canvas.bind("<Button-3>",lambda e: clearSystemLabel(e)) 
        canvas.pack(fill=tkinter.BOTH)
        
        root.wm_title("a route")
        root.mainloop()
#------------------------------------------------------------------------------
    def __str__(self):
        totalCost = sum([system.Total_Cost for system in self.__Route])
        strList = []
        count = 0

        #For printing split fitness values
        #TODO:  Flag systems that can be sold at either seller
        #       Add helper function to change sellers_list to sellers_dict so we can get rid of this
        if self.__Sellers_List is not None:
            sellersPerSystem = {}
            for system in self.__Route:
                tempSellers = []
                for distToCheck in self.__Route:
                    if system.GetDistanceTo(distToCheck) >= self.__Seller_Min:
                        tempSellers.append(distToCheck)
                sellersPerSystem[system] = tempSellers
            strList.append("\t\tRoute Value:{0:.5f}\n".format(self.__Fitness_Value))
            for system in self.__Route:
                if system in self.__Sellers_List:
                    strList.append("{0}: <{1}>".format(count+1,system.Short_Str))
                else:
                    strList.append("{0}: {1}".format(count+1,system.Short_Str))
                strList.append("\n")
                count += 1
            
            for station in self.__Sellers_List:
                strList.append("\nAt <{0}> sell:\n\t".format(station.System_Name))
                for seller in sellersPerSystem[station]:
                    if seller in self.__Sellers_List:
                        strList.append(" <{0}> ".format(seller.System_Name))
                    else:
                        strList.append(" {0} ".format(seller.System_Name))
        
        #For printing alt fitness values
        elif self.__Sellers_Dict is not None:
            strList.append("\t\tRoute Value:{0:.5f}\n".format(self.__Fitness_Value))
            for system in self.__Route:
                if system in self.__Sellers_Dict:
                    strList.append("{0}: <{1}>".format(count+1,system.Short_Str))
                else:
                    strList.append("{0}: {1}".format(count+1,system.Short_Str))
                strList.append("\n")
                count += 1

            for system in self.__Route:
                if system in self.__Sellers_Dict:
                    strList.append("\nAt <{0}> sell:\n\t".format(system.System_Name))
                    for seller in set(self.__Sellers_Dict[system]):
                        if seller in self.__Sellers_Dict:
                            strList.append(" <{0}> ".format(seller.System_Name))
                        else:
                            strList.append(" {0} ".format(seller.System_Name))

        #For just displaying the systems if we dont have a sellers list/dict
        else:
            strList.append("\nRoute value:{0}\n".format(self.__Fitness_Value))
            for system in self.__Route:
               strList.append('{0}\n'.format(system))

        strList.append("\nTotal distance: {0:.3f}ly".format(self.__Total_Distance))
        strList.append("\nLongest jump: {0:.3f}ly".format(self.__Longest_Jump))
        strList.append("\nTotal cargo purchased: {0:.2f}T".format(self.__Total_Cargo))
        strList.append("\nRequired cargo space: {0}T".format(self.__Max_Cargo))
        strList.append("\nRequired credits: {0:.2f}cr".format(totalCost))
        strList.append("\nType: {0}".format(self.__Route_Type.name))

        return ''.join(strList)
#------------------------------------------------------------------------------
    def __key(self):
        return (self.__Route,self.__Fitness_Value)
#------------------------------------------------------------------------------
    def __eq__(self,other):
        return self.__key() == other.__key()
#------------------------------------------------------------------------------
    def __FitnessTester(self):
        '''
        Another attempt at making the EvenSplit type routes calculate faster
        '''
        #TODO Changing this garbage again
        #Going to try to make it like alt fitness, except instead of checking
        #if we hit a system over seller_min, we check if the system is
        #one of a pair of systems that accounts for all rare goods to be sold
        #the systems which can be sold to with the overall lowest cargo requirement
        #between sells should be favored
        # EX: 1,2,3,4 -> 5; 5,6,7,8 -> 1 OR 1,2,3,4 -> 7; 5,6,7,8 -> 3
        # would favor (5,1) over (7,3) because less holdover between sellers
        # 6,7,8,1 -> 3; 2,3,4,5 -> 7 would be for spread/other routes, above for cluster
        #           Jump        Held                Sold
        #           1           {1}                 {}
        #           2           {1,2}               {}
        #           3           {2,3}               {1}
        #           4           {2,3,4}             {1}
        #           5           {2,3,4,5}           {1}
        #           6           {2,3,4,5,6}         {1}
        #           7           {6,7}               {1,2,3,4,5}
        #           8           {6,7,8}             {1,2,3,4,5}
        #           9           {6,7,8,1}           {1,2,3,4,5}
        #          10           {6,7,8,1,2}         {1,2,3,4,5}
        #          11           {2,3}               {1,2,3,4,5,6,7,8,1} ##ALL SOLD
        routeLength = self.Length
        self.__Total_Distance = 0     
        sellerScale = 1
        clusterShortLY = 50
        clusterLongLY = 145
        spreadMaxLY = 110
        maxJumpRangeLY = 200
        clusterShort = 0
        clusterLong = 0
        spreadJumps = 0
        longestJump = -999
        baseValue = 6

        for i in range(0,routeLength):
            currentSystem = self.__Route[i]
            nextSystem = self.__Route[(i+1)%routeLength]
            jumpDistance = currentSystem.GetDistanceTo(nextSystem)
            self.__Total_Distance += jumpDistance
            longestJump = jumpDistance if jumpDistance > longestJump else longestJump
            if jumpDistance <= clusterShortLY:
                clusterShort += 1
            if jumpDistance >= clusterLongLY and jumpDistance <= maxJumpRangeLY:
                clusterLong += 1 
            if jumpDistance <= spreadMaxLY:
                spreadJumps += 1 
        self.__Longest_Jump = longestJump
        #Route has 2 groups of systems separated by a long jump
        if clusterLong == 2 and (clusterLong + clusterShort) == routeLength:
           self.__Route_Type = RouteType.Cluster

        #Route has fairly evenly spaced jumps
        if spreadJumps == routeLength:
            self.__Route_Type = RouteType.Spread
        
        systemsBySeller = {}
        for seller in self.__Route:
            systemsBySeller[seller] = []
            for system in self.__Route:
                if seller.GetDistanceTo(system) >= self.__Seller_Min:
                    systemsBySeller[seller].append(system)
        ableToSell = 0
        goodPairs = []
        #TODO: Do a stupid thing where I actually check that all systems are accounted for in systemsBySeller
        for seller1,seller2 in itertools.combinations(systemsBySeller,2):
            sellableSystems = set(systemsBySeller[seller1] + systemsBySeller[seller2])
            ableToSell = max(ableToSell,sellableSystems.__len__())
            if sellableSystems == set(self.__Route):
                goodPairs.append((seller1,seller2))
        sellersValue = min(ableToSell,routeLength)/routeLength * baseValue
        maxCargo = 0

        if sellersValue >= baseValue:
            for seller1,seller2 in goodPairs:
                seller1Idx = self.__Route.index(seller1)
                seller2Idx = self.__Route.index(seller2)
                systemJumpsApart = abs(seller1Idx-seller2Idx)
                #continue if things aren't evenly spaced
                if (systemJumpsApart != math.floor(routeLength/2) and systemJumpsApart != math.ceil(routeLength/2)):
                    continue
                #continue if number of sellers per system isnt off by at most 1
                if abs(systemsBySeller[seller1].__len__() - systemsBySeller[seller2].__len__()) > 1:
                    continue
                #TODO: Actually need to do this to calculate maxCargo
                sold = []
                unsold = []
                self.__Sellers_Dict = None
                for i in range(routeLength*2):
                    currentSys = self.__Route[i%routeLength];
                    unsold.append(currentSys)
                    toRemove = []
                    numUnsold = 0
                    if currentSys == seller1 or currentSys == seller2:
                        for rareSys in unsold:
                            #Means we can sell checkSys at currentSys
                            sellableSystems = systemsBySeller[currentSys]
                            if rareSys in sellableSystems:
                                toRemove.append(rareSys)
                                sold.append(rareSys)
                            numUnsold += 1
                    if toRemove.__len__() != 0:
                        maxCargo = max(maxCargo,sum((sys.Max_Supply for sys in unsold[:-1])))
                        if self.__Sellers_Dict == None:
                            self.__Sellers_Dict = defaultdict(list)
                        self.__Sellers_Dict[currentSys].extend(toRemove)
                    numSold = 0
                    for sys in toRemove:
                        unsold.remove(sys)
                        numSold = numSold + 1
                    #We know that each pair represents two sellers that can represent the selling of all rares in the route
                    #We can just check the length here instead of doing a check on members of sold and route
                    if sold.__len__() >= self.__Route.__len__():
                        #We have every system accounted for in sold, exit the for loop
                        break
                if self.__Sellers_Dict is not None:
                    break
        if self.__Sellers_Dict is None:
            sellerScale = 0.25

        maxGoodDistance = routeLength * 100
        weightedDistance = (maxGoodDistance/self.__Total_Distance) * 2
        
        minSupply = routeLength * 10
        weightedSupply = math.log(self.__Total_Cargo,minSupply) * 2
  
        totalGoodsCost = sum([system.Total_Cost for system in self.__Route])
        #Base this on an average purchase price of 1x000cr per system   
        weightedCost = totalGoodsCost/(routeLength * 15000)
        
        totalValue = (sellersValue + weightedCost + weightedDistance + weightedSupply) * sellerScale
        
        if weightedCost < 1 or weightedDistance < 2 or weightedSupply < 2:
            totalValue = totalValue * 0.5
        if sellersValue < baseValue/2:
            totalValue = totalValue * 0.25
        
        self.__Max_Cargo = maxCargo
        return totalValue
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------