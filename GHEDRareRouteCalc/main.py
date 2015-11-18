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

    first/last line: headings

    Last 3 columns are garbage also

    '''
    supplyCap       = currentLine[0]
    avgSupply       = currentLine[1]
    itemCost        = currentLine[2]
    itemName        = currentLine[3]
    distToStation   = currentLine[4]
    stationName     = currentLine[5]
    systemName      = currentLine[6]
    index           = lineNum-1
    distToOthers    = []
    for j in range(7,headers.__len__()-3):
        distToOthers.append(currentLine[j])
        
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

    return EDSystem(supplyCap, avgSupply, itemCost, itemName,
                    distToStation, stationName, systemName, index,
                    distToOthers)

def __RunGenetic(systems: 'list of EDSystem instance', routeLength: int, popSize: int, silent: bool):
    exitTestLoop = False
    testNum = 0
    maxTests = 20
    geneticStart = time.time()
    while not exitTestLoop and testNum < maxTests:
        testNum += 1
        print("Test: {0}".format(testNum))
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

def __RunBrute(systems: 'list of EDSystem instance', routeLength: int):
    bruteStart = time.time()
    routes = RouteCalc.Brute(systems,routeLength)
    bruteEnd = time.time()
    if routes.__len__() > 0:
        for route in routes:
            print(route)
    else:
        print("no routes =(")
    print("Routes found in {0}s".format((bruteEnd-bruteStart)))

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

    commonSystems = {}
    commonSystems['Lave']   = allSystems[61]
    commonSystems['Leesti'] = allSystems[63]
    commonSystems['Orr']    = allSystems[78]
    commonSystems['Usz']    = allSystems[92]
    commonSystems['Diso']   = allSystems[25]
    commonSystems['Zee']    = allSystems[107]
    commonSystems['39 T']   = allSystems[0]
    commonSystems['Fujin']  = allSystems[32]
    commonSystems['George'] = allSystems[34]
    commonSystems['Momus']  = allSystems[69]
    commonSystems['Witch']  = allSystems[101]
    commonSystems['Alt']    = allSystems[7]
    commonSystems['Tio']    = allSystems[90]
    commonSystems['Coq']    = allSystems[20]
    commonSystems['Eth']    = allSystems[31]
    commonSystems['AZ C']   = allSystems[12]
    commonSystems['Utg']    = allSystems[93]
    commonSystems['Yaso']   = allSystems[105]
    commonSystems['Quech']  = allSystems[80]
    commonSystems['Chi Er'] = allSystems[19]
    commonSystems['Bast']   = allSystems[15]
    commonSystems['Baltah'] = allSystems[13]
    commonSystems['Iru']    = allSystems[48]
    commonSystems['Karsu']  = allSystems[57]
    commonSystems['Delta P']= allSystems[23]
    commonSystems['Hec']    = allSystems[39]
    commonSystems['Agan']   = allSystems[4]
    commonSystems['Any']    = allSystems[10]
    commonSystems['Ngur']   = allSystems[75]
    commonSystems['Tanm']   = allSystems[86]  
    commonSystems['Tara']   = allSystems[87]
    commonSystems['Zoan']   = allSystems[106]
    commonSystems['Kare']   = allSystems[56]
    commonSystems['Eleu']   = allSystems[26]
    commonSystems['Ocho']   = allSystems[77] 
    commonSystems['Rusa']   = allSystems[83]  
    commonSystems['CD-75']  = allSystems[17] 
    commonSystems['Epsi']   = allSystems[27]


    bruteSystems = []
    bruteSystems.append(commonSystems['Lave'])  
    bruteSystems.append(commonSystems['Leesti'])
    bruteSystems.append(commonSystems['Orr'])  
    bruteSystems.append(commonSystems['Usz'])  
    bruteSystems.append(commonSystems['Diso'])  
    bruteSystems.append(commonSystems['Zee']) 
    bruteSystems.append(commonSystems['39 T'])   
    bruteSystems.append(commonSystems['Fujin'])  
    bruteSystems.append(commonSystems['George'])  
    bruteSystems.append(commonSystems['Momus'])  
    bruteSystems.append(commonSystems['Witch']) 
    bruteSystems.append(commonSystems['Alt'])  
    
    #bruteSystems.append(commonSystems[90])  #Tio
    #bruteSystems.append(commonSystems[20])  #Coq
    #bruteSystems.append(commonSystems[31])  #Eth
    #bruteSystems.append(commonSystems[12])  #Az
    #bruteSystems.append(commonSystems[93])  #Utg
    #bruteSystems.append(commonSystems[105]) #Yaso
    #bruteSystems.append(commonSystems[80])  #Quech

    '''
    TODO: Allow users to enter the values for size/station distance.
          Better way to pick out systems used in bruteSystems and lists below
    '''

    maxStationDistance = 100000
    systemsSubset = [system for system in allSystems if min(system.Station_Distance) <= maxStationDistance
                                                        and "permit" not in system.System_Name]
    length = 6
    popSize = 50
    silent = True
    #__RunGenetic(systemsSubset,length,popSize,not silent)
    __RunBrute(bruteSystems,length)
    #PerformanceCalc.CheckPerformance(systemsSubset)
    #PerformanceCalc.TestSystems(commonSystems)