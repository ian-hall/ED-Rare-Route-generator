__author__ = 'Ian'
from edsystem import EDSystem
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

    import json
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
    bruteSystems.append(systemsDict['Lave'])  
    bruteSystems.append(systemsDict['Leesti'])
    bruteSystems.append(systemsDict['Orrere'])  
    bruteSystems.append(systemsDict['Uszaa'])  
    bruteSystems.append(systemsDict['Diso'])  
    bruteSystems.append(systemsDict['Zeessze']) 
    bruteSystems.append(systemsDict['39 Tauri'])   
    bruteSystems.append(systemsDict['Fujin'])  
    bruteSystems.append(systemsDict['George Pantazis'])  
    bruteSystems.append(systemsDict['Momus Reach'])  
    bruteSystems.append(systemsDict['Witchhaul']) 
    bruteSystems.append(systemsDict['Altair'])     
    bruteSystems.append(systemsDict['Tiolce'])  
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
    length = 8
    popSize = 500
    silent = True
    #__RunGenetic(systemsSubset,length,popSize,not silent)
    #__RunBrute(bruteSystems,length)
    #PerformanceCalc.CheckPerformance(systemsSubset)
    #PerformanceCalc.TestSystems(systemsDict)

    ykLoc = systemsDict['Yaso Kondi'].Location
    leestiLoc = systemsDict['Leesti'].Location

    testLocsX = [ykLoc['x'],leestiLoc['x']]
    testLocsY = [ykLoc['y'],leestiLoc['y']]

    xMin = min(testLocsX)
    xMax = max(testLocsX)
    yMin = min(testLocsY)
    yMax = max(testLocsY)

    xDif = xMax - xMin
    yDif = yMax - yMin

    print(xDif)
    print(yDif)