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
gens = 10
#routes = RouteCalc.GeneticSolverStart(popSize,gens,allSystems,maxStationDistance,testSize)

#print("\t****GOOD ROUTES MAYBE??****")
#for route in routes:
#    print(route)

#Yaso-Kondi loop
#Indices based on my ed.csv file (its old)
ykLoopList = []
ykLoopList.append(allSystems[104])
ykLoopList.append(allSystems[79])
ykLoopList.append(allSystems[7])
ykLoopList.append(allSystems[20])
ykLoopList.append(allSystems[12])
ykLoopList.append(allSystems[31])
ykLoopList.append(allSystems[34])
ykLoopList.append(allSystems[91])
ykLoop = EDRareRoute(ykLoopList)
print(ykLoop)
#tempRoute = ykLoop.GetRoute()

#print("\n\nShortest Paths")
#tempRoute = ykLoop.GetRoute()
#for system in tempRoute:
#    vertices = [system]
#    edges = []

#    while set(vertices) != set(tempRoute):
#        nextMinEdge = sys.maxsize
#        vertexToAdd = None
#        lastVertex = vertices[-1]
#        for newVertex in tempRoute:
#            if lastVertex.System_Distances[newVertex.Index] < nextMinEdge and vertices.count(newVertex) == 0:
#                nextMinEdge = lastVertex.System_Distances[newVertex.Index]
#                vertexToAdd = newVertex        
#        vertices.append(vertexToAdd)
#        edges.append(EDSystemPair(lastVertex,vertexToAdd,nextMinEdge))
#    #Need to add the distance from last to first
#    edges.append(EDSystemPair(vertices[-1],vertices[0],vertices[-1].System_Distances[vertices[0].Index]))

#    print("\t***")
#    for edge in edges:
#        print(edge)
#    print("Total Distance: ",sum([edge.Distance for edge in edges]))

input("dont close omg")

'''
sellingDistance = 140
sellersPerStation = {}
for system in tempRoute:
    tempSellers = []
    for distToCheck in tempRoute:
        if system.System_Distances[distToCheck.Index] >= sellingDistance:
            tempSellers.append(distToCheck)
    sellersPerStation[system] = tempSellers

combosWithAllSystems = []
for combo in itertools.combinations(tempRoute,2):
    #If sellers can't sell to eachother we know the combo is bad
    if combo[0].System_Distances[combo[1].Index] < sellingDistance:
        continue
    sellersPerCombo = []
    for obj in combo:
        sellersPerCombo += [val for val in sellersPerStation[obj]]
    if set(sellersPerCombo).__len__() == tempRoute.__len__():
        combosWithAllSystems.append(combo)

combosToRemove = []
for combo in combosWithAllSystems:
    numSellers = sellersPerStation[combo[0]].__len__()
    badCombo = False
    for system in combo:
        numToCheck = sellersPerStation[system].__len__()
        leftOver = math.fabs(numSellers - numToCheck)
        #If leftOver > 1, that means seller lists are not going to give good routes
        #We still might want to keep these because we don't neccisarily want to throw
        #away the route if it's our only one...
        if leftOver > 1:
            badCombo = True
    if badCombo:
        combosToRemove.append(combo)

for combo in combosToRemove:
    combosWithAllSystems.remove(combo)            

if combosWithAllSystems.__len__() == 0:
    print("No suitable sellers")
for combo in combosWithAllSystems:
    strList = ["\nFor combo: {"]
    for system in combo:
        strList.append(" ({0}) ".format(system.System_Name))
    strList.append("}\n")

    for system in combo:
        strList.append("\n{0} ->".format(system.System_Name))
        for seller in sellersPerStation[system]:
            strList.append(" ({0}) ".format(seller.System_Name))
    print(''.join(strList))

systemPairings = {}
uniqueSystems = []
for combo in combosWithAllSystems:
    for system in combo:
        if uniqueSystems.count(system) == 0:
            uniqueSystems.append(system)

for system in uniqueSystems:
    systemPairings[system] = []
    for combo in combosWithAllSystems:
        if combo.count(system) != 0:
            for value in combo:
                if value != system:
                    systemPairings[system].append(value)


#Need to try it with each node to start since we will get different routes
#Also need to fudge this to look for stations where distances are all close together

sellPoints = math.floor(tempRoute.__len__()/totalSellers)
allRoutes = []
checkedSystems = []
for system in uniqueSystems:
    for pair in systemPairings[system]:
        checkedSystems.append(system)
        vertices = [system]
        edges = []

        while set(vertices) != set(tempRoute):
            nextMinEdge = sys.maxsize
            vertexToAdd = None
            lastVertex = vertices[-1]
            for newVertex in tempRoute:
                if vertices.__len__() % sellPoints == 0:
                    vertexToAdd = pair
                    nextMinEdge = lastVertex.System_Distances[pair.Index]
                    continue
                if lastVertex.System_Distances[newVertex.Index] < nextMinEdge and vertices.count(newVertex) == 0:
                    nextMinEdge = lastVertex.System_Distances[newVertex.Index]
                    vertexToAdd = newVertex        
            vertices.append(vertexToAdd)
            edges.append(EDSystemPair(lastVertex,vertexToAdd,nextMinEdge))
        #Need to add the distance from last to first
        edges.append(EDSystemPair(vertices[-1],vertices[0],vertices[-1].System_Distances[vertices[0].Index]))

        print("\t***")
        for edge in edges:
            print(edge)
        print("Total Distance: ",sum([edge.Distance for edge in edges]))
'''
