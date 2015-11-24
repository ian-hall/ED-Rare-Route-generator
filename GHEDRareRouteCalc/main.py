﻿__author__ = 'Ian'
from edsystem import EDSystem, DisplayLocation
from edrareroute import EDRareRoute, RouteType
from routecalc import RouteCalc
from performancecalc import PerformanceCalc
from urllib import request
import csv
import operator
import random
import itertools
import sys
import math
import re
import time
import json
import copy
from collections import Counter

#------------------------------------------------------------------------------
def __ValidateLine(currentLine, lineNum: int):
    '''
    0 - Max Cap
    1 - Supply Rate
    2 - Cost
    3 - Item
    4 - Distance
    5 - Station
    6 - System
    7 on - distance to other systems

    first/last full lines: headings

    Last 3 columns are garbage also

    '''
    supplyCap       = currentLine[0]
    avgSupply       = currentLine[1]
    itemCost        = currentLine[2]
    itemName        = currentLine[3].strip()
    distToStation   = currentLine[4]
    stationName     = currentLine[5].strip()
    systemName      = currentLine[6].strip()
    index           = lineNum-1
    distToOthers    = []
    for j in range(7,headers.__len__()-3):
        distToOthers.append(currentLine[j])
    permit = False
        
    if supplyCap == 'ND':
        supplyCap = 1
    else:
        tempMax = supplyCap.split('-')
        for i in range(0,tempMax.__len__()):
            tempMax[i] = int(re.sub("[^0-9]", "", tempMax[i]))
        supplyCap = sum(tempMax)/len(tempMax)

    if avgSupply == 'ND':
        avgSupply = 1
    else:
        tempSupply = avgSupply.split('-')
        for i in range(0,tempSupply.__len__()):
            tempSupply[i] = float(re.sub("[^0-9]", "", tempSupply[i]))
        avgSupply = sum(tempSupply)/len(tempSupply)

    itemCost = int(re.sub("[^0-9]", "", itemCost))

    #If it contains ly, convert to ls by 31,557,600 * x
    multFactor = 1;
    if 'ly' in distToStation:
        multFactor = 31557600
    distToStation = float(re.sub("[^0-9.]", "", distToStation)) * multFactor

    for i in range(0,distToOthers.__len__()):
        distToOthers[i] = float(distToOthers[i])

    #Remove '(permit)' from systems and truncate ending spaces
    if systemName.endswith('(permit)'):
        permit = True
        systemName = systemName.partition('(permit)')[0].strip()


    return EDSystem(supplyCap, avgSupply, itemCost, itemName,
                    distToStation, stationName, systemName, index,
                    distToOthers,permit)
#------------------------------------------------------------------------------
def __RunGenetic(systems, routeLength: int, popSize: int, silent: bool):
    exitTestLoop = False
    runNum = 0
    maxRuns = 20
    geneticStart = time.time()
    while not exitTestLoop and runNum < maxRuns:
        runNum += 1
        print("Run: {0}".format(runNum))
        routeTuple = RouteCalc.GeneticSolverStart(popSize,systems,routeLength,silent)
        geneticEnd = time.time()
        if routeTuple:
            bestRoute = routeTuple[0]
            print("Best route found had value {0}".format(bestRoute.Fitness_Value))
            if bestRoute.Fitness_Value >= RouteCalc.Route_Cutoff:
                print(bestRoute)
                print("Generations: {0}".format(routeTuple[1]))
                print("Time: {0}s".format((geneticEnd-geneticStart)))
                exitTestLoop = True
#------------------------------------------------------------------------------
def __RunBrute(systems, routeLength: int):
    bruteStart = time.time()
    routes = RouteCalc.Brute(systems,routeLength)
    bruteEnd = time.time()
    if routes.__len__() > 0:
        for route in routes:
            print(route)
    else:
        print("no routes =(")
    print("Routes found in {0}s".format((bruteEnd-bruteStart)))
#------------------------------------------------------------------------------
# Main starts here
#------------------------------------------------------------------------------
if __name__ == '__main__':
    cleanedCSV = []
    allSystems = []

    
    with open('RareGoods.csv') as csvFile:
        reader = csv.reader(csvFile)
        breakout = False
        for line in reader:
            for section in line:
                if section == '':
                    breakout = True
                    break
            if not breakout:
                cleanedCSV.append(line)
            breakout = False
    '''
    target_url = 'https://docs.google.com/feeds/download/spreadsheets/Export?key=17Zv55yEjVdHrNzkH7BPnTCtXRs8GDHqchYjo9Svkyh4&exportFormat=csv&gid=0'
    csvFile = request.urlopen(target_url)
    fileToText = csvFile.read()
    usableCSV = str(fileToText).split('\\n')

    reader = csv.reader(usableCSV)
    breakout = False
    for line in reader:
        for section in line:
            if section == '':
                breakout = True
                break
        if not breakout:
            cleanedCSV.append(line)
        breakout = False
    '''
    headers = cleanedCSV[0]
    for i in range(1,cleanedCSV.__len__()-1):
        currentSystem = __ValidateLine(cleanedCSV[i],i)
        '''
        Putting all systems with multiple stations/rares/whatever into one EDSystem object
        '''   
        if allSystems.count(currentSystem) != 0:
            for system in allSystems:
                if system == currentSystem:
                    system.AddRares(currentSystem)
        else:
            allSystems.append(currentSystem)

    systemsDict = {}
    for system in allSystems:
        systemsDict[system.System_Name] = system

    #The JSON file linked to from the rareroute csv/spreadsheet. Not going to include because lol 23mb text file
    with open('edsystems.json') as jsonFile:
        jsonSystems = json.load(jsonFile)
    
    #TODO: Find which systems aren't showing, also find a better way to represent permit systems (ie remove ((permit)) from system names)
    for val in jsonSystems['systems']:
        if val['name'] in systemsDict:
            currentSystem = systemsDict[val['name']]
            currentSystem.Location['x'] = float(val['coord'][0])
            currentSystem.Location['y'] = float(val['coord'][1])
            currentSystem.Location['z'] = float(val['coord'][2])

    bruteSystems = []
    #bruteSystems.append(systemsDict['Lave'])  
    #bruteSystems.append(systemsDict['Leesti'])
    #bruteSystems.append(systemsDict['Orrere'])  
    #bruteSystems.append(systemsDict['Uszaa'])  
    #bruteSystems.append(systemsDict['Diso'])
    #bruteSystems.append(systemsDict['Zeessze']) 
    #bruteSystems.append(systemsDict['39 Tauri'])   
    #bruteSystems.append(systemsDict['Fujin'])  
    bruteSystems.append(systemsDict['George Pantazis'])  
    #bruteSystems.append(systemsDict['Momus Reach'])  
    #bruteSystems.append(systemsDict['Witchhaul']) 
    bruteSystems.append(systemsDict['Altair'])     
    #bruteSystems.append(systemsDict['Tiolce'])  
    bruteSystems.append(systemsDict['Coquim'])  
    bruteSystems.append(systemsDict['Ethgreze'])  
    bruteSystems.append(systemsDict['AZ Cancri'])  
    bruteSystems.append(systemsDict['Utgaroar'])  
    bruteSystems.append(systemsDict['Yaso Kondi']) 
    bruteSystems.append(systemsDict['Quechua'])
    '''
    TODO: Allow users to enter the values for size/station distance.
    '''
    maxStationDistance = 10000
    systemsSubset = [system for system in allSystems if min(system.Station_Distance) <= maxStationDistance
                                                        and not system.PermitReq]
    length = 4
    popSize = 500
    silent = True
    #__RunGenetic(systemsSubset,length,popSize,not silent)
    #__RunBrute(bruteSystems,length)
    #PerformanceCalc.CheckPerformance(systemsSubset)
    #PerformanceCalc.TestSystems(systemsDict)


    #TODO: Scale x/y values such that we have domain/range around 30/80
    #       Low end sticks to 0, high end use some kind of ratio
    #       Shift everything over/up to be positive
    #       Fudge values where systems have the same x or y
    longSide = 75
    shortSide = 25

    testLocs = [system for system in bruteSystems]
    xVals = [system.Location['x'] for system in testLocs]
    yVals = [system.Location['y'] for system in testLocs]

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
        print("cannot display")
    else:
        if xMax > yMax:
            for i in range(xValsNew.__len__()):
                if xValsNew[i] != 0:
                    if xValsNew[i] == xMax:
                        xValsNew[i] = longSide
                    else:
                        xValsNew[i] = round((longSide / xMax) * xValsNew[i])
                if yValsNew[i] != 0:
                    if yValsNew[i] == yMax:
                        yValsNew[i] = shortSide
                    else:
                        yValsNew[i] = round((shortSide / yMax) * yValsNew[i])
                points.append(DisplayLocation(xValsNew[i],yValsNew[i],testLocs[i].System_Name))
        else:
            #Just swap x/y to rotate the graph
            for i in range(xValsNew.__len__()):
                if xValsNew[i] != 0:
                    if xValsNew[i] == xMax:
                        xValsNew[i] = shortSide
                    else:
                        xValsNew[i] = round((shortSide / xMax) * xValsNew[i])
                if yValsNew[i] != 0:
                    if yValsNew[i] == yMax:
                        yValsNew[i] = longSide
                    else:
                        yValsNew[i] = round((longSide / yMax) * yValsNew[i])
                points.append(DisplayLocation(yValsNew[i],xValsNew[i],testLocs[i].System_Name))
        
        #Fudge numbers so we dont have same x/y points for systems, suffle on the long side first and then check again
        #before doing the fudging on the short side. L is long side, S is short side
        pointsCounter = Counter(points)
        while sum([v for k,v in pointsCounter.items() if 1 == v]) != points.__len__():
            for k,v in pointsCounter.items():
                if v > 1:
                    toChange = points.index(k)
                    if points[toChange].L + 1 < longSide:
                        points[toChange].L += 1
                    else:
                        points[toChange].L -= 1
            pointsCounter = Counter(points)

        for i in range(points.__len__()):
            for j in range(points.__len__()):
                if i != j:
                    if points[i] == points[j]:
                        print("{0} FAIL".format(points[i]))
        
        sortedPoints = sorted(points,key=lambda point : (point.S, point.L))

        for val in sortedPoints:
            print(val)

        strList = []
        for s in range(shortSide+1):
            for l in range(longSide+1):
                if DisplayLocation(l,s) in points:
                    strList.append('F')
                else:
                    strList.append('*')
            strList.append('\n')
        print(''.join(strList))