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
            for system in allSystems:
                if system == currentSystem:
                    system.AddRares(currentSystem)
        else:
            allSystems.append(currentSystem)

    bruteSystems = []
    bruteSystems.append(allSystems[61])  #Lave
    bruteSystems.append(allSystems[63])  #Leesti
    bruteSystems.append(allSystems[78])  #Orr
    bruteSystems.append(allSystems[92])  #Usz
    bruteSystems.append(allSystems[25])  #Diso
    bruteSystems.append(allSystems[107]) #Zee
    bruteSystems.append(allSystems[0])   #39 T
    bruteSystems.append(allSystems[32])  #Fuj
    bruteSystems.append(allSystems[34])  #George
    bruteSystems.append(allSystems[69])  #Momus
    bruteSystems.append(allSystems[101]) #Witch
    bruteSystems.append(allSystems[7])   #Alt
    ''''''
    #bruteSystems.append(allSystems[90])  #Tio
    #bruteSystems.append(allSystems[20])  #Coq
    #bruteSystems.append(allSystems[31])  #Eth
    #bruteSystems.append(allSystems[12])  #Az
    #bruteSystems.append(allSystems[93])  #Utg
    #bruteSystems.append(allSystems[105]) #Yaso
    #bruteSystems.append(allSystems[80])  #Quech


    '''
    TODO: Allow users to enter the values for size/station distance.
    '''

    maxStationDistance = 1000
    systemsSubset = [system for system in allSystems if min(system.Station_Distance) <= maxStationDistance
                                                        and "permit" not in system.System_Name]
    length = 9
    popSize = 1000
    __RunGenetic(systemsSubset,length,popSize,False)
    #__RunBrute(bruteSystems,length)
    #PerformanceCalc.CheckPerformance(systemsSubset)
    #PerformanceCalc.SelectionTester(50)

    #Yaso Kondi loop
    #Indices based on live spreadsheet, no duplicates
    ykLoopList = []
    ykLoopList.append(allSystems[20])  #Coq
    ykLoopList.append(allSystems[7])   #Alt
    ykLoopList.append(allSystems[31])  #Eth
    ykLoopList.append(allSystems[12])  #Az
    ykLoopList.append(allSystems[34])  #George
    ykLoopList.append(allSystems[93])  #Utg
    ykLoopList.append(allSystems[105]) #Yaso
    ykLoopList.append(allSystems[80])  #Quech
    #print("\n\nYK Loop")
    #print(EDRareRoute(ykLoopList))

    #8 system round found by program
    #indices based on live spreadsheet, no duplicates
    bad8_1 = []
    bad8_1.append(allSystems[19]) #Chi Er
    bad8_1.append(allSystems[7])  #Alt
    bad8_1.append(allSystems[15]) #Bast
    bad8_1.append(allSystems[90]) #Tio
    bad8_1.append(allSystems[13]) #Baltah
    bad8_1.append(allSystems[48]) #Iru
    bad8_1.append(allSystems[57]) #Karsu
    bad8_1.append(allSystems[23]) #Delta P
    #print("\n\nBad 8 System route, low item cost")
    #print(EDRareRoute(bad8_1))

    good8_1 = []
    good8_1.append(allSystems[39])#Hec
    good8_1.append(allSystems[4]) #Agan
    good8_1.append(allSystems[63])#Leesti
    good8_1.append(allSystems[10])#Any
    good8_1.append(allSystems[75])#Ngur
    good8_1.append(allSystems[13])#Balt
    good8_1.append(allSystems[19])#Chi Er
    good8_1.append(allSystems[7]) #Alt
    #print("\nActually maybe a good route?")
    #print(EDRareRoute(good8_1))

    #5 system test
    bad5_1 = []
    bad5_1.append(allSystems[48]) #Iru
    bad5_1.append(allSystems[75]) #ngur
    bad5_1.append(allSystems[63]) #Leesti
    bad5_1.append(allSystems[4])  #Agan
    bad5_1.append(allSystems[7])  #Alt
    #print("\nBad 5 system route, poor systems distance")
    #print(EDRareRoute(bad5_1))


    good4_1 = []
    good4_1.append(allSystems[32])  #Fuj
    good4_1.append(allSystems[0])   #39 T
    good4_1.append(allSystems[25])  #Diso
    good4_1.append(allSystems[63])  #Leesti
    #print("\nGood 4 system route")
    #print(EDRareRoute(good4_1))

    bad11_1 = []
    bad11_1.append(allSystems[107]) #Zee
    bad11_1.append(allSystems[83])  #Rus
    bad11_1.append(allSystems[4])   #Agan
    bad11_1.append(allSystems[63])  #Leesti
    bad11_1.append(allSystems[61])  #Lave
    bad11_1.append(allSystems[75])  #Ngur
    bad11_1.append(allSystems[48])  #Iru
    bad11_1.append(allSystems[17])  #CD-75
    bad11_1.append(allSystems[90])  #Tio
    bad11_1.append(allSystems[27])  #Epsi
    bad11_1.append(allSystems[7])   #Alt
    #print("\nBad 11 system route, poor system distances")
    #print(EDRareRoute(bad11_1))

    good5_1 = []
    good5_1.append(allSystems[63])  #Leesti
    good5_1.append(allSystems[25])  #Dis
    good5_1.append(allSystems[78])  #Orr
    good5_1.append(allSystems[93])  #Utg
    good5_1.append(allSystems[86])  #Tan
    #print("\nGood 5, multiple bad sell locations")
    #print(EDRareRoute(good5_1))

    good5_2 = []
    good5_2.append(allSystems[86])  #Tan
    good5_2.append(allSystems[78])  #Orr
    good5_2.append(allSystems[25])  #Dis
    good5_2.append(allSystems[61])  #Lave
    good5_2.append(allSystems[93])  #Utg
    #print("\nProbably okay 5")
    #print(EDRareRoute(good5_2))

    bad6_1 = []
    bad6_1.append(allSystems[56])  #Kare
    bad6_1.append(allSystems[26])  #Ele
    bad6_1.append(allSystems[7])   #Alt
    bad6_1.append(allSystems[93])  #Utg
    bad6_1.append(allSystems[39])  #Hec
    bad6_1.append(allSystems[77])  #Ocho
    #print("\nShould be bad 6")
    #print(EDRareRoute(bad6_1))

    good6_1 = []
    good6_1.append(allSystems[78])  #Orr
    good6_1.append(allSystems[87])  #Tar
    good6_1.append(allSystems[86])  #Tan
    good6_1.append(allSystems[93])  #Utg
    good6_1.append(allSystems[63])  #Leesti
    good6_1.append(allSystems[61])  #Lave
    #print("Good 6, but chosen sellers could be better")
    #print(EDRareRoute(good6_1))

    #Good 'other' route
    #aeriel karsuki jaroua leesti epsilon altair

    bad5_2 = []
    bad5_2.append(allSystems[25])  #Dis
    bad5_2.append(allSystems[106]) #Zaon
    bad5_2.append(allSystems[63])  #Leesti
    bad5_2.append(allSystems[0])   #39 T
    bad5_2.append(allSystems[39])  #Hec
    #print(" \"Good\" 5, one station with bad distance")
    #print(EDRareRoute(bad5_2))