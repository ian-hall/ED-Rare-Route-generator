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


def __ValidateLine(currentLine, lineNum):
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

if __name__ == '__main__':
    cleanedCSV = []
    allSystems = []

    
    with open('ED2.csv') as csvFile:
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
        If a system/station is already in the allSystems list we will simply add
        the rare items from the found station to the station in the list. The found
        station is then NOT added to the list.
        '''   
        if allSystems.count(currentSystem) != 0:
            dupes = []
            for system in allSystems:
                if system == currentSystem:
                    system.AddRares(currentSystem)
                    dupes.append(system)
        else:
            allSystems.append(currentSystem)

    bruteSystems = []
    bruteSystems.append(allSystems[62])  #Lave
    bruteSystems.append(allSystems[64])  #Leesti
    bruteSystems.append(allSystems[79])  #Orr
    bruteSystems.append(allSystems[93])  #Usz
    bruteSystems.append(allSystems[108]) #Zee
    bruteSystems.append(allSystems[0])   #39 T
    bruteSystems.append(allSystems[33])  #Fuj
    bruteSystems.append(allSystems[35])  #George
    bruteSystems.append(allSystems[26])  #Diso
    bruteSystems.append(allSystems[70])  #Momus
    bruteSystems.append(allSystems[102]) #Witch
    bruteSystems.append(allSystems[8])   #Alt
    bruteSystems.append(allSystems[91])  #Tio
    bruteSystems.append(allSystems[21])  #Coq
    bruteSystems.append(allSystems[32])  #Eth
    bruteSystems.append(allSystems[13])  #Az
    bruteSystems.append(allSystems[94])  #Utg
    bruteSystems.append(allSystems[106]) #Yaso
    bruteSystems.append(allSystems[81])  #Quech

    
    '''
    TODO: Allow users to enter the values for size/station distance.
    '''

    maxStationDistance = 4500
    systemsSubset = [system for system in allSystems if system.Station_Distance <= maxStationDistance
                                                        and "permit" not in system.System_Name]
    routeSize = 4
    
    #Genetic
    exitTestLoop = False
    testNum = 0
    maxTests = 20
    popSize = 100
    geneticStart = time.time()
    while not exitTestLoop and testNum < maxTests:
        testNum += 1
        print("Test: {0}".format(testNum))
        routeTuple = RouteCalc.GeneticSolverStart(popSize,systemsSubset,routeSize, False)
        geneticEnd = time.time()
        bestRoute = routeTuple[0]
        print("Best route found had value {0}".format(bestRoute.Fitness_Value))
        if bestRoute.Fitness_Value >= RouteCalc.Route_Cutoff:
            print(bestRoute)
            print("Generations: {0}".format(routeTuple[1]))
            print("Time: {0}s".format((geneticEnd-geneticStart)))
            exitTestLoop = True
    
    '''
    #Brute
    bruteStart = time.time()
    routes = RouteCalc.Brute(bruteSystems,routeSize)
    bruteEnd = time.time()
    if routes.__len__() > 0:
        for route in routes:
            print(route)
    else:
        print("no routes =(")
    print("Routes found in {0}s".format((bruteEnd-bruteStart)))
    '''
    #PerformanceCalc.CheckPerformance(systemsSubset)
    #PerformanceCalc.SelectionTester(5000)

    #Yaso Kondi loop
    #Indices based on live spreadsheet, no duplicates
    ykLoopList = []
    ykLoopList.append(allSystems[21])  #Coq
    ykLoopList.append(allSystems[8])   #Alt
    ykLoopList.append(allSystems[32])  #Eth
    ykLoopList.append(allSystems[13])  #Az
    ykLoopList.append(allSystems[35])  #George
    ykLoopList.append(allSystems[94])  #Utg
    ykLoopList.append(allSystems[106]) #Yaso
    ykLoopList.append(allSystems[81])  #Quech
    #print("\n\nYK Loop")
    #print(EDRareRoute(ykLoopList))

    #8 system round found by program
    #indices based on live spreadsheet, no duplicates
    genRoute8 = []
    genRoute8.append(allSystems[20]) #Chi Er
    genRoute8.append(allSystems[8])  #Alt
    genRoute8.append(allSystems[16]) #Bast
    genRoute8.append(allSystems[91]) #Tio
    genRoute8.append(allSystems[14]) #Baltah
    genRoute8.append(allSystems[49]) #Iru
    genRoute8.append(allSystems[58]) #Karsu
    genRoute8.append(allSystems[24]) #Delta P
    #print("\n\nBad 8 System route, low item cost")
    #print(EDRareRoute(genRoute8))

    test8 = []
    test8.append(allSystems[40])#Hec
    test8.append(allSystems[5]) #Agan
    test8.append(allSystems[64])#Leesti
    test8.append(allSystems[11])#Any
    test8.append(allSystems[76])#Ngur
    test8.append(allSystems[14])#Balt
    test8.append(allSystems[20])#Chi Er
    test8.append(allSystems[8]) #Alt
    #print("\nBad 8 system route, poor seller spacing")
    #print(EDRareRoute(test8))

    #5 system test
    test5 = []
    test5.append(allSystems[49]) #Iru
    test5.append(allSystems[76]) #ngur
    test5.append(allSystems[64]) #Leesti
    test5.append(allSystems[5])  #Agan
    test5.append(allSystems[8])  #Alt
    #print("\nBad 5 system route, poor systems distance")
    #print(EDRareRoute(test5))


    test4 = []
    test4.append(allSystems[33])  #Fuj
    test4.append(allSystems[0])   #39 T
    test4.append(allSystems[26])  #Diso
    test4.append(allSystems[64])  #Leesti
    #print("\nGood 4 system route")
    #print(EDRareRoute(test4))

    systems11_1 = []
    systems11_1.append(allSystems[108]) #Zee
    systems11_1.append(allSystems[84])  #Rus
    systems11_1.append(allSystems[5])   #Agan
    systems11_1.append(allSystems[64])  #Leesti
    systems11_1.append(allSystems[62])  #Lave
    systems11_1.append(allSystems[76])  #Ngur
    systems11_1.append(allSystems[49])  #Iru
    systems11_1.append(allSystems[18])  #CD-75
    systems11_1.append(allSystems[91])  #Tio
    systems11_1.append(allSystems[28])  #Epsi
    systems11_1.append(allSystems[8])   #Alt
    #print("\nBad 11 system route, poor system distances")
    #print(EDRareRoute(systems11_1))

    another5 = []
    another5.append(allSystems[64])  #Leesti
    another5.append(allSystems[26])  #Dis
    another5.append(allSystems[79])  #Orr
    another5.append(allSystems[94])  #Utg
    another5.append(allSystems[87])  #Tan
    #print("\nGood 5, multiple bad sell locations")
    #print(EDRareRoute(another5))

    #Orr Usz Witch 39 Hec Lee 

    #pathetic attempt at multithreading
    #Can only map around 20,000,000 before memory cap
    '''
    from multiprocessing import Pool
    from multiprocessing.dummy import Pool as ThreadPool
    poolSize = 3
    
    t1Start = time.time()
    routePerms = itertools.permutations(bruteSystems,routeSize)
    with ThreadPool(poolSize) as p:
        results = p.map(RouteCalc.T_Helper,routePerms)
    results = [val for val in results if val]
    sortedResults = sorted(results,key=operator.attrgetter('Fitness_Value'))
    t1End = time.time()
    for route in sortedResults:
        print(route)
    '''