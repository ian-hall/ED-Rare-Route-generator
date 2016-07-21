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
from fuzzywuzzy import fuzz
import pandas as pd
import numpy as np
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
        bestRoute,numGenerations = RouteCalc.StartGeneticSolver(popSize,systems,routeLength,silent,fitType)
        geneticEnd = time.time()
        if bestRoute.Fitness >= RouteCalc.Route_Cutoff and stopShort:
            exitTestLoop = True
        if bestRoute.Fitness < RouteCalc.Route_Cutoff:
            print("No good route found")
        print(bestRoute)
        bestRoute.DisplayInConsole()
        print("Generations: {0}".format(numGenerations))
        print("Time since start: {0:.5f}s".format((geneticEnd-geneticStart)))
        bestRoute.DrawRoute()
#------------------------------------------------------------------------------
def __TryInt(val: str) -> bool:
    try:
        int(val)
        return True
    except:
        return False
#------------------------------------------------------------------------------
def ReadSystems(file:str = None) -> list:
    if file is None:
        file = 'https://docs.google.com/feeds/download/spreadsheets/Export?key=17Zv55yEjVdHrNzkH7BPnTCtXRs8GDHqchYjo9Svkyh4&exportFormat=csv&gid=0'
    allSystems = []
    colOffset = 7
    mainCSV = pd.read_csv(file,header=15,skipfooter=14,engine='python')
    distances = mainCSV.iloc[:,colOffset:-3]
    locations = pd.read_csv(file,header=None,skiprows=10,chunksize=3)
    for line in locations:
        locations = line.iloc[:,colOffset:-3]
        break
    systemArgs = zip(mainCSV['MAX CAP'],mainCSV['SUPPLY RATE'],mainCSV['PRICE'],mainCSV['ITEM'],mainCSV['DIST(Ls)'],mainCSV['STATION'],mainCSV['SYSTEM'])
    idx = 0
    for row in systemArgs:
        currentSystem = EDSystem.Initialize_FromCSVLine(row,idx)        
        distanceDict = {}
        for key in distances.columns:
            cleanedSystem,_ = edsystem.CleanSystemName(key)
            distanceDict[cleanedSystem] = distances[key][idx]
        currentSystem.Distances_Dict = distanceDict
        
        x,y,z = locations[colOffset+idx][0],locations[colOffset+idx][1],locations[colOffset+idx][2]
        currentSystem.Location = {'x':x,'y':y,'z':z}
        
        if currentSystem in allSystems:
            for system in allSystems:
                if system == currentSystem:
                    system.AddRares(currentSystem)
        else:
            allSystems.append(currentSystem)
        idx += 1

    return allSystems
#------------------------------------------------------------------------------
def __ReadUserInput(systemsDict:dict) -> tuple:
    '''
    Gets the user input for running the genetic. Tuple will have form (bool,int,list).
    bool will be true if the input gathered was valid.
    int will be the choice selected
    list will either be a list of args to run the genetic with [max station dist, route len, permit status] or a list of systems to run it with.
    '''
    readyToRun = False
    argsOrSystems = []
    sb = []
    sb.append("Please select an option:\n")
    sb.append("\t1) Generate route by length\n")
    sb.append("\t2) Generate route by system list\n")
    sb.append("\t3) Exit")
    print(''.join(sb))
    optionChoice = input("Your choice: ")
    numChoices = 3
    while not( __TryInt(optionChoice) and not (int(optionChoice) < 1 or int(optionChoice) > numChoices) ):
        print("Invalid entry")
        optionChoice = input("Your choice: ")
    
    if int(optionChoice) == 1:
        argsToUse = []      
        stationDist = input("Max distance to station (ly): ")
        while not (__TryInt(stationDist) and int(stationDist) >= 1):
            print("Please enter a number between 1 and whatever")
            stationDist = input("Max distance to station (ly): ")
        
        routeLen = input("Route length [6-35]: ")
        while not (__TryInt(routeLen) and not (int(routeLen) < 6 or int(routeLen) > 35)):
            print("Please enter a length from 6 up to and including 35.")
            routeLen = input("Route length [6-35]: ")

        validPermitEntry = False
        permitsStr = input("Allow permit systems [Y/N]? ")
        if permitsStr.__len__() == 1 and (permitsStr == 'N' or permitsStr == 'Y'):
            validPermitEntry = True
        while not validPermitEntry:
            print("Please enter just Y or N")
            permitsStr = input("Allow permit systems [Y/N]? ")
            if permitsStr.__len__() == 1 and (permitsStr == 'N' or permitsStr == 'Y'):
                validPermitEntry = True
        
        permitVal = (permitsStr == "Y")

        argsToUse = [int(stationDist),int(routeLen),permitVal]
        argsOrSystems = argsToUse
        readyToRun = True
    
        
    elif int(optionChoice) == 2:
        #Maybe have this be a selection list of all known systems
        systemsToUse = []
        count = 0
        stopReadLoop = False
        minSystems = 6;
        print("Please enter at least {0} systems.".format(minSystems))
        print("Type \"stop\" to...stop")
        print("Note: All systems you enter will be used.")
        while not stopReadLoop:
            count += 1
            checkSystem = input("\t{0}) ".format(count))
            #If they type exit, we exit
            if checkSystem.lower() == "stop":
                stopReadLoop = True
                continue
            if checkSystem in systemsDict:
                #If the system is in the systems dict, meaning its spelled exactly the same, we add to the list of systems
                if systemsDict[checkSystem] not in systemsToUse:
                    systemsToUse.append(systemsDict[checkSystem])
                else:
                    print("System already in list, try another.")
                    count -= 1
            else:
                #Otherwise, we use fuzz to check for similar strings and give spelling suggestions
                possibleSysNames = []
                for k,v in systemsDict.items():
                    if fuzz.ratio(checkSystem,k) >= 60:
                        possibleSysNames.append(k)
                if possibleSysNames.__len__() == 0:
                    print("No system with that name found. Please try another")
                elif possibleSysNames.__len__() == 1:
                    print("Did you mean \"{0}\"?".format(possibleSysNames[0]))
                else:
                    print("Did you mean one of these?")
                    print("\t{0}".format(' '.join(possibleSysNames)))
                count -= 1
        
        if systemsToUse.__len__() < minSystems:
            print("Not enough systems entered. Exiting.")
        else:
            readyToRun = True
            argsOrSystems = systemsToUse

    elif int(optionChoice) == 3:
        print("Goodbye")

    return (readyToRun,int(optionChoice),argsOrSystems)
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Main starts here
#------------------------------------------------------------------------------
if __name__ == '__main__':
    csvFile = "RareGoods.csv"
    #allSystems = ReadSystems(csvFile);
    allSystems = ReadSystems(csvFile)

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

    prompt = False    
    if prompt:
        ready,runType,userArgs = __ReadUserInput(systemsDict)
        if ready:
            if runType == 1:
                maxStationDistance = userArgs[0]
                length = userArgs[1]
                allowPermits = userArgs[2]
                systemsSubset = []
                if allowPermits:
                    systemsSubset = [system for system in allSystems if min(system.Station_Distances) <= maxStationDistance]
                else:
                    systemsSubset = [system for system in allSystems if min(system.Station_Distances) <= maxStationDistance and not system.Needs_Permit]
                __RunGenetic(systemsSubset,length,500,fitType=FitnessType.FirstOver,silent=False,stopShort=True)
            if runType == 2:
                userSystems = userArgs
                routeLen = userSystems.__len__()
                __RunGenetic(userSystems,routeLen,500,fitType=FitnessType.FirstOver,silent=False,stopShort=True)       
    else:
        maxStationDistance = 5000
        systemsSubset = [system for system in allSystems if min(system.Station_Distances) <= maxStationDistance and not system.Needs_Permit]
        length = 20
        popSize = 2500
        fitType = FitnessType.Distance
        silenceOutput = False
        stopShort = True
        __RunGenetic(systemsSubset,length,popSize,fitType,silenceOutput,stopShort)

        #PerformanceCalc.CheckPerformance(systemsSubset,fitType=FitnessType.EvenSplit)
        #PerformanceCalc.CheckPerformance(systemsSubset,fitType=FitnessType.FirstOver)
        #PerformanceCalc.CheckPerformance(systemsSubset,fitType=FitnessType.Distance)
        #PerformanceCalc.CheckPerformance(systemsSubset,fitType=FitnessType.Tester)

        #PerformanceCalc.CheckTestSystems(systemsDict,FitnessType.EvenSplit)

        #fullRoute = EDRareRoute(allSystems,FitnessType.FirstOver)
        #print(fullRoute)
        #fullRoute.DisplayInConsole()
        #fullRoute.DrawRoute(showLines=False)
#------------------------------------------------------------------------------