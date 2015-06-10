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


headers = cleanedCSV[0]
for i in range(1,cleanedCSV.__len__()-1):
    tempSystem = []
    tempDistances = []
    tempSystem.append(cleanedCSV[i][0])
    tempSystem.append(cleanedCSV[i][1])
    tempSystem.append(cleanedCSV[i][2])
    tempSystem.append(cleanedCSV[i][3])
    tempSystem.append(cleanedCSV[i][4])
    tempSystem.append(cleanedCSV[i][5])
    tempSystem.append(cleanedCSV[i][6])
    tempSystem.append(i-1)
    for j in range (7,headers.__len__()-3):
        tempDistances.append(cleanedCSV[i][j])
    tempSystem.append(tempDistances)
    allSystems.append(EDSystem(tempSystem))

testSize = 8
totalSellers = 2
maxStationDistance = 5000
popSize = 50
gens = 100
routes = RouteCalc.GeneticSolverStart(popSize,gens,allSystems,maxStationDistance,testSize)

print("\t****GOOD ROUTES MAYBE??****")
for route in routes:
    print(route)

#Yaso-Kondi loop
#Indices based on my ed.csv file (its old)
'''
ykLoopList = []
ykLoopList.append(allSystems[104])
ykLoopList.append(allSystems[79])
ykLoopList.append(allSystems[20])
ykLoopList.append(allSystems[7])
ykLoopList.append(allSystems[31])
ykLoopList.append(allSystems[12])
ykLoopList.append(allSystems[34])
ykLoopList.append(allSystems[91])
ykLoop = EDRareRoute(ykLoopList)
print("YK Loop")
print(ykLoop)
'''

input("dont close omg")