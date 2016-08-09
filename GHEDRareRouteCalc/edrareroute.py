from edsystem import EDSystem, DisplayLocation
from collections import Counter, defaultdict
import itertools
import math
import tkinter
import random
import numpy as np
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
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
#TODO:  
#       Need to finish adjusting the weightedCost values in the fitness functions
#           to better support routes of short lengths.
class EDRareRoute(object):
#------------------------------------------------------------------------------
    def __init__(self,systemList: list, fType: FitnessType):
        if(systemList.__len__() < 3):
            raise Exception("Routes must be 3 or more systems")
        self.__Route = systemList
        self.__Route_Loop = (systemList + systemList)
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
        elif fType == FitnessType.Distance:
            self.__Fitness_Value = self.__FitnessDistance()
        elif fType == FitnessType.EvenSplit:
            self.__Fitness_Value = self.__Fitness_EvenSplit()
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
        only works with short ( < 16 ) routes
        '''
        routeLength = self.__Route.__len__()
        self.__Total_Distance = 0
        self.__Route_Type = RouteType.Other

        overallScale = 1
        baseValue = 6
        maxJumpDistance = 200
        clusterLoDistance = 45
        clusterHiDistance = 140
        spreadMaxDistance = 120
        numClusterLoJumps = 0
        numClusterHiJumps = 0
        numSpreadJumps = 0
        currentLongestJump = -1
        overMaxJump = False
        systemsBySeller = {}
        for i in range(routeLength):
            current = self.__Route[i]
            next = self.__Route[(i+1)%routeLength]
            distance = current.GetDistanceTo(next)
            self.__Total_Distance += distance
            currentLongestJump = max(currentLongestJump,distance)
            if distance > maxJumpDistance:
                overMaxJump = True
            if distance <= clusterLoDistance:
                numClusterLoJumps += 1
            if distance >= clusterHiDistance:
                numClusterHiJumps += 1
            if distance <= spreadMaxDistance:
                numSpreadJumps +=1

            systemsBySeller[current] = []
            for system in self.__Route:
                if current.GetDistanceTo(system) >= self.__Seller_Min:
                    systemsBySeller[current].append(system)
        self.__Longest_Jump = currentLongestJump

        if numClusterHiJumps == 2 and (numClusterHiJumps + numClusterLoJumps) == routeLength:
           self.__Route_Type = RouteType.Cluster
        if numSpreadJumps == routeLength:
            self.__Route_Type = RouteType.Spread
        
        numSellable = 0
        numSellableScale = -1
        for seller1,seller2 in itertools.combinations(systemsBySeller,2):
            sellableSystems = set(systemsBySeller[seller1] + systemsBySeller[seller2])
            numSellable = max(numSellable,sellableSystems.__len__())
            numSellableScale = max(numSellableScale,(numSellable/routeLength * baseValue))
            seller1Idx = self.__Route.index(seller1)
            seller2Idx = self.__Route.index(seller2)
            systemJumpsApart = abs(seller1Idx-seller2Idx)
            #continue if things aren't evenly spaced
            if (systemJumpsApart != math.floor(routeLength/2) and systemJumpsApart != math.ceil(routeLength/2)):
                continue
            #continue if number of sellers per system isnt off by at most 1
            if abs(systemsBySeller[seller1].__len__() - systemsBySeller[seller2].__len__()) > 1:
                continue
            #Maybe faster than converting route to a set and checking equality
            allSellable = True
            for system in self.__Route:
                if system not in sellableSystems:
                    allSellable = False
                    break
            if allSellable:
                self.__Sellers_Dict = None
                self.__Max_Cargo = 0
                systemsSoldDiff = -1
                mostSystemsSold = -1
                leastSystemsSold = routeLength + 1                
                sold = []
                unsold = []
                for currentSys in self.__Route_Loop:
                    unsold.append(currentSys)
                    toRemove = []
                    if currentSys == seller1 or currentSys == seller2:
                        for checkSys in unsold:
                            if checkSys.GetDistanceTo(currentSys) >= self.__Seller_Min:
                                toRemove.append(checkSys)
                                sold.append(checkSys)
                    if toRemove.__len__() != 0:
                        self.__Max_Cargo = max(self.__Max_Cargo,sum((sys.Max_Supply for sys in unsold[:-1])))
                        if self.__Sellers_Dict == None:
                            self.__Sellers_Dict = defaultdict(list)
                        self.__Sellers_Dict[currentSys].extend(toRemove)
                    numSold = 0
                    for sys in toRemove:
                        unsold.remove(sys)
                        numSold = numSold + 1
                    mostSystemsSold = max(mostSystemsSold,numSold)
                    leastSystemsSold = min(leastSystemsSold,numSold)

        if self.__Sellers_Dict is None:
            overallScale = 0.25

        maxGoodDistance = routeLength * 100
        weightedDistance = (maxGoodDistance/self.__Total_Distance) * 2
        if overMaxJump:
            weightedDistance = weightedDistance * 0.5
        
        minSupply = routeLength * 10
        weightedSupply = math.log(self.__Total_Cargo,minSupply) * 2
  
        totalGoodsCost = sum([system.Total_Cost for system in self.__Route])
        #Base this on an average purchase price of 1x000cr per system   
        weightedCost = totalGoodsCost/(routeLength * 15000)
        
        totalValue = (numSellableScale + weightedCost + weightedDistance + weightedSupply) * overallScale
        
        if weightedCost < 1 or weightedDistance < 2 or weightedSupply < 2:
            totalValue = totalValue * 0.5
        if numSellableScale < baseValue/2:
            totalValue = totalValue * 0.25

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

        overallScale = 1
        baseValue = 6
        longestGoodJump = 120
        maxJumpDistance = 195
        currentLongestJump = -1
        overGoodJump = False

        systemsBySeller = {}
        for i in range(routeLength):
            current = self.__Route[i]
            next = self.__Route[(i+1)%routeLength]
            distance = current.GetDistanceTo(next)
            if distance > longestGoodJump:
                overGoodJump = True
                self.__Route_Type = RouteType.FirstOverLong
            currentLongestJump = max(currentLongestJump,distance)
            self.__Total_Distance += distance
            systemsBySeller[current] = []
            for system in self.__Route:
                if current.GetDistanceTo(system) >= self.__Seller_Min:
                    systemsBySeller[current].append(system)
        self.__Longest_Jump = currentLongestJump

        numSellableSystems = routeLength
        for system in systemsBySeller:
            if systemsBySeller[system].__len__() == 0:
                numSellableSystems -= 1
        numSellableScale = numSellableSystems/routeLength * baseValue
        
        #Skip this part if we already know we can't sell all goods
        self.__Max_Cargo = 0
        systemsSoldDiff = -1
        mostSystemsSold = -1
        leastSystemsSold = routeLength + 1
        if numSellableScale >= baseValue:
            sold = []
            unsold = []
            #Go through at most twice, since if a systems doesnt sell by then it won't sell
            for currentSys in self.__Route_Loop:
                unsold.append(currentSys)
                toRemove = []
                for checkSys in unsold:
                    #Means we can sell checkSys at currentSys
                    sellableSystems = systemsBySeller[currentSys]
                    if systemsBySeller[currentSys].count(checkSys) != 0:
                        toRemove.append(checkSys)
                        sold.append(checkSys)
                if toRemove.__len__() != 0:
                    self.__Max_Cargo = max(self.__Max_Cargo,sum((sys.Max_Supply for sys in unsold[:-1])))
                    if self.__Sellers_Dict == None:
                        self.__Sellers_Dict = defaultdict(list)
                    self.__Sellers_Dict[currentSys].extend(toRemove)
                numSold = 0
                for sys in toRemove:
                    unsold.remove(sys)
                    numSold = numSold + 1
                mostSystemsSold = max(mostSystemsSold,numSold)
                leastSystemsSold = min(leastSystemsSold,numSold)
                systemsSoldDiff = mostSystemsSold - leastSystemsSold
        else:
            #Scale overall value down
            overallScale = 0.5

        maxGoodDistance = routeLength * longestGoodJump
        weightedDistance = (maxGoodDistance/self.__Total_Distance) * 2
        
        minSupply = routeLength * 10
        weightedSupply = math.log(self.__Total_Cargo,minSupply) * 2
  
        totalGoodsCost = sum([system.Total_Cost for system in self.__Route])
        #Base this on an average purchase price of 1x000cr per system   
        weightedCost = totalGoodsCost/(routeLength * 15000)
        
        totalValue = (numSellableScale + weightedCost + weightedDistance + weightedSupply) * overallScale
        
        if weightedCost < 1 or weightedDistance < 2 or weightedSupply < 2:
            totalValue = totalValue * 0.5
        if numSellableScale < baseValue/2:
            totalValue = totalValue * 0.25

        if overGoodJump and routeLength < 16:
            totalValue = totalValue * 0.8
        if self.__Longest_Jump > maxJumpDistance:
            totalValue = totalValue * 0.45
        
        #TODO: Scale here, larger allowance for sellersDifference on longer routes.... maybe like ceil(len/5) or something  with a min of 1? 
        if systemsSoldDiff is not None:
            totalValue = (totalValue * 0.5 ) if (systemsSoldDiff > 4) else totalValue

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
        return weightedDistance * 11
#------------------------------------------------------------------------------
    #TODO: Add a better way to represent large routes than first letter of system, too many duplicates
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
        #TODO: Add color to seller locations on mouseover
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

        #TODO: maybe this still loops forever sometimes
        overlapping = CheckOverlappingPoints(points,ovalRad)
        split = 10
        loops = 0
        flip = False
        visited = []
        while overlapping.__len__() > 1:
            for point,conflicts in overlapping.items():
                for badPoint in conflicts:
                    if loops % split == 0:                 
                        if flip:
                            badPoint.Row += 6
                        else:
                            badPoint.Row -= 6
                    else:
                        if flip:
                            badPoint.Col += 6
                        else:
                            badPoint.Col -= 6
                    flip = not flip
            visited = []
            overlapping = CheckOverlappingPoints(points,ovalRad)
            loops += 1

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
        return self.__Fitness_Value
#------------------------------------------------------------------------------
    def __hash__(self):
        return hash(self.__Fitness_Value)
#------------------------------------------------------------------------------
    def __eq__(self,other):
        return self.__key() == other.__key()
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
def CheckOverlappingPoints(points,ovalRad):
    '''
    Checks if there will be any overlapping ovals with the given points and oval radius
    '''
    #TODO: Change this to be by system instead of by pair
    overlapping = defaultdict(list)
    for p1 in points:
        for p2 in points:
            if p1 == p2:
                continue
            if abs(p1.Col-p2.Col) <= ovalRad and abs(p1.Row-p2.Row) <= ovalRad:
                overlapping[p1].append(p2)
    return overlapping