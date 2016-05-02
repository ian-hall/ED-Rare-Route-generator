__author__ = 'Ian'
import edsystem
from edsystem import EDSystem, DisplayLocation
from edrareroute import EDRareRoute, RouteType, FitnessType
from routecalc import RouteCalc
from performancecalc import PerformanceCalc
import csv
import re
import time
from urllib import request

#------------------------------------------------------------------------------
def __ValidateLine(currentLine: list, lineNum: int) -> EDSystem:
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
    itemName        = currentLine[3].strip().replace("\\'","\'")
    distToStation   = currentLine[4]
    stationName     = currentLine[5].strip().replace("\\'","\'")
    systemName      = currentLine[6].strip().replace("\\'","\'")
    index           = lineNum-1
    distToOthers    = []
    for j in range(7,currentLine.__len__()-3):
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

    if supplyCap == 1 or avgSupply == 1:
        supplyCap = max([supplyCap,avgSupply])
        avgSupply = supplyCap


    return EDSystem(supplyCap, avgSupply, itemCost, itemName,
                    distToStation, stationName, systemName, index,
                    distToOthers, permit)
#------------------------------------------------------------------------------
def __RunGenetic(systems: list, routeLength: int, popSize: int, fitType: FitnessType, silent: bool, stopShort: bool):
    exitTestLoop = False
    runNum = 0
    maxRuns = 5
    geneticStart = time.time()
    bestRoute = None
    while not exitTestLoop and runNum < maxRuns:
        runNum += 1
        print("Run: {0}".format(runNum))
        routeTuple = RouteCalc.GeneticSolverStart(popSize,systems,routeLength,silent,fitType)
        geneticEnd = time.time()
        if routeTuple:
            bestRoute = routeTuple[0]
            if bestRoute.Fitness >= RouteCalc.Route_Cutoff and stopShort:
                exitTestLoop = True
            if bestRoute.Fitness < RouteCalc.Route_Cutoff:
                print("No good route found".format(bestRoute.Fitness))
            print(bestRoute)
            print("Generations: {0}".format(routeTuple[1]))
            print("Time since start: {0:.5f}s".format((geneticEnd-geneticStart)))
            bestRoute.PrintRoute()
    if bestRoute is not None:
        bestRoute.DrawRoute()
#------------------------------------------------------------------------------
def __TryFloat(val: str) -> bool:
    try:
        float(val)
        return True
    except:
        return False
#------------------------------------------------------------------------------
def ReadSystems(file:str = None) ->list:
    cleanedCSV = []
    allSystems = []
    coordLists = {}

    if file is not None:
        with open(file) as csvFile:
            reader = csv.reader(csvFile)
            breakout = False
            for line in reader:
                for section in line:
                    if section == '':
                        breakout = True
                        continue
                    if section == 'x' or section == 'y' or section == 'z':
                        temp = [float(val) for val in line if __TryFloat(val)]
                        coordLists[section] = temp
                        breakout = True
                        break
                if not breakout:
                    cleanedCSV.append(line)
                breakout = False
    else:
        target_url = 'https://docs.google.com/feeds/download/spreadsheets/Export?key=17Zv55yEjVdHrNzkH7BPnTCtXRs8GDHqchYjo9Svkyh4&exportFormat=csv&gid=0'
        with request.urlopen(target_url) as csvFile:
            fileToText = csvFile.read()
            usableCSV = str(fileToText).split('\\n')
            reader = csv.reader(usableCSV)
            breakout = False
            for line in reader:
                for section in line:
                    if section == '':
                        breakout = True
                        continue
                    if section == 'x' or section == 'y' or section == 'z':
                        temp = [float(val) for val in line if __TryFloat(val)]
                        coordLists[section] = temp
                        breakout = True
                        break
                if not breakout:
                    cleanedCSV.append(line)
                breakout = False

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

    for system in allSystems:
        system.Location['x'] = coordLists['x'][system.Index]
        system.Location['y'] = coordLists['y'][system.Index]
        system.Location['z'] = coordLists['z'][system.Index]

    return allSystems

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Main starts here
#------------------------------------------------------------------------------
if __name__ == '__main__':
    csvFile = "RareGoods.csv"
    allSystems = ReadSystems(csvFile);

    systemsDict = {}
    for system in allSystems:
        systemsDict[system.System_Name] = system

    commonSystems = []
    commonSystems.append(systemsDict['Lave'])  
    commonSystems.append(systemsDict['Leesti'])
    commonSystems.append(systemsDict['Orrere'])  
    commonSystems.append(systemsDict['Uszaa'])  
    commonSystems.append(systemsDict['Diso'])
    commonSystems.append(systemsDict['Zeessze']) 
    commonSystems.append(systemsDict['39 Tauri'])   
    commonSystems.append(systemsDict['Fujin'])  
    commonSystems.append(systemsDict['George Pantazis'])  
    commonSystems.append(systemsDict['Momus Reach'])  
    commonSystems.append(systemsDict['Witchhaul']) 
    commonSystems.append(systemsDict['Altair'])     
    commonSystems.append(systemsDict['Tiolce'])  
    commonSystems.append(systemsDict['Coquim'])  
    commonSystems.append(systemsDict['Ethgreze'])  
    commonSystems.append(systemsDict['AZ Cancri'])  
    commonSystems.append(systemsDict['Utgaroar'])  
    commonSystems.append(systemsDict['Yaso Kondi']) 
    commonSystems.append(systemsDict['Quechua'])

    '''
    TODO: Allow users to enter the values for length/station distance.
    '''
    maxStationDistance = 5000
    systemsSubset = [system for system in allSystems if min(system.Station_Distances) <= maxStationDistance and not system.Needs_Permit]
    length = 11
    popSize = 333
    __RunGenetic(systemsSubset,length,popSize,fitType=FitnessType.FirstOver,silent=False,stopShort=True)

    #PerformanceCalc.CheckPerformance(systemsSubset,fitType=FitnessType.EvenSplit)
    #PerformanceCalc.CheckPerformance(systemsSubset,fitType=FitnessType.FirstOver)
    #PerformanceCalc.CheckPerformance(systemsSubset,fitType=FitnessType.Farthest)

    #PerformanceCalc.TestSystems(systemsDict,FitnessType.EvenSplit)

    #fullRoute = EDRareRoute(allSystems,FitnessType.FirstOver)
    #print(fullRoute)
    #fullRoute.PrintRoute()
    #fullRoute.DrawRoute(showLines=False)
#------------------------------------------------------------------------------