__author__ = 'Ian'
from edsystem import EDSystem
from edrareroute import EDRareRoute
from routecalc import RouteCalc
from EDSystemPair import EDSystemPair
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
# OLD URL target_url = 'https://docs.google.com/feeds/download/spreadsheets/Export?key=1haUVaFIxFq5IPqZugJ8cfCEqBrZvFFzcA-uXB4pTfW4&exportFormat=csv&gid=0'
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
    allSystems.append(currentSystem)

'''
TODO: Allow users to enter the values for size/station distance.
'''

testSize = 4
maxStationDistance = 5000
popSize = 150
gens = 10000
routes = RouteCalc.GeneticSolverStart(popSize,gens,allSystems,maxStationDistance,testSize)

print("\t****possible routes****")
for route in routes:
    print(route)

#Yaso-Kondi loop
#Indices based on my ed.csv file with permit systems included

ykLoopList = []
ykLoopList.append(allSystems[20])
ykLoopList.append(allSystems[7])
ykLoopList.append(allSystems[31])
ykLoopList.append(allSystems[12])
ykLoopList.append(allSystems[34])
ykLoopList.append(allSystems[91])
ykLoopList.append(allSystems[104])
ykLoopList.append(allSystems[79])
ykLoop = EDRareRoute(ykLoopList)
print("YK Loop")
print(ykLoop)


input("enter to close")