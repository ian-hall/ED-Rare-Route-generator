__author__ = 'Ian'
from edsystem import EDSystem
from edrareroute import EDRareRoute
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

cleanedCSV = []
allSystems = []

'''
with open('ed.csv') as csvFile:
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

'''
TODO: Allow users to enter the values for size/station distance.
'''

#Genetic
exitTestLoop = False
testNum = 0
maxTests = 20

goodRouteCutoff = RouteCalc.Route_Cutoff

while not exitTestLoop and testNum < maxTests:
    testNum += 1
    print("Test: {0}".format(testNum))
    routeSize = 4
    maxStationDistance = 4500
    popSize = 75
    maxGens = 20000
    routeTuple = RouteCalc.GeneticSolverStart(popSize,maxGens,allSystems,maxStationDistance,routeSize, False)
    bestRoute = routeTuple[0]
    print("Best route found had value {0}".format(bestRoute.Fitness_Value))
    if bestRoute.Fitness_Value >= goodRouteCutoff:
        print(bestRoute)
        print("\tFound after {0} generations.".format(routeTuple[1]))
        exitTestLoop = True


#Brute
#stupid slow
routeSize = 8
maxStationDistance = 5000
bruteSystems = []
bruteSystems.append(allSystems[61])  #Lave
bruteSystems.append(allSystems[63])  #Leesti
bruteSystems.append(allSystems[78])  #Orr
bruteSystems.append(allSystems[92])  #Usz
bruteSystems.append(allSystems[108]) #Zee
bruteSystems.append(allSystems[0])   #39 T
bruteSystems.append(allSystems[33])  #Fuj
bruteSystems.append(allSystems[35])  #George
bruteSystems.append(allSystems[26])  #Diso
bruteSystems.append(allSystems[69])  #Momus
bruteSystems.append(allSystems[102]) #Wolf
#routes = RouteCalc.Brute(bruteSystems,maxStationDistance,routeSize)

#print("\t****possible routes****")
#for route in routes:
#    print(route)

#Yaso Kondi loop
#Indices based on live spreadsheet, no duplicates
ykLoopList = []
ykLoopList.append(allSystems[106]) #Yaso
ykLoopList.append(allSystems[80])  #Quech
ykLoopList.append(allSystems[21])  #Coq
ykLoopList.append(allSystems[8])   #Alt
ykLoopList.append(allSystems[32])  #Eth
ykLoopList.append(allSystems[13])  #Az
ykLoopList.append(allSystems[35])  #George
ykLoopList.append(allSystems[93])  #Utg
ykLoop = EDRareRoute(ykLoopList)
print("YK Loop")
print(ykLoop)

#8 system round found by program
#indices based on live spreadsheet, no duplicates
genRoute8 = []
genRoute8.append(allSystems[20]) #Chi Er
genRoute8.append(allSystems[8])  #Alt
genRoute8.append(allSystems[16]) #Bast
genRoute8.append(allSystems[90]) #Tio
genRoute8.append(allSystems[14]) #Baltah
genRoute8.append(allSystems[49]) #Iru
genRoute8.append(allSystems[57]) #Karsu
genRoute8.append(allSystems[24]) #Delta P
goodRoute8 = EDRareRoute(genRoute8)
print("8 System route")
print(goodRoute8)

#PerformanceCalc.CheckPerformance(allSystems)