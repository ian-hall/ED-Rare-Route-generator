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
def __TryInt(val: str) -> bool:
    try:
        int(val)
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
def __GetUserInput(systemsDict:dict) -> tuple:
    '''
    Gets the user input for running the genetic. Tuple will have form (bool,int,list).
    bool will be true if the input gathered was valid.
    int will be the choice selected
    list will either be a list of args to run the genetic with [max station dist, route len, permit status] or a list of systems to run it with.
    '''
    #Using try float so I 
    readyToRun = False
    argsOrSystems = []
    sb = []
    sb.append("Please select an option:\n")
    sb.append("\t1) generate route by length\n")
    sb.append("\t2) generate route by system list\n")
    sb.append("\t3) exit")
    print(''.join(sb))
    optionChoice = input("Your choice: ")
    numChoices = 3
    while not( __TryInt(optionChoice) and not (int(optionChoice) < 1 or int(optionChoice) > numChoices) ):
        print("Invalid entry")
        optionChoice = input("Your choice: ")
    
    if float(optionChoice) == 1:
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
        
        permitVal = 1 if (permitsStr == "Y") else 0

        argsToUse = [int(stationDist),int(routeLen),permitVal]
        argsOrSystems = argsToUse
        readyToRun = True
    
        
    elif float(optionChoice) == 2:
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

    elif float(optionChoice) == 3:
        print("Goodbye")

            
    

    return (readyToRun,int(optionChoice),argsOrSystems)
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

    prompt = False
    
    if prompt:
        userInput = __GetUserInput(systemsDict)
        ready = userInput[0]
        if ready:
            runType = userInput[1]
            if runType == 1:
                maxStationDistance = userInput[2][0]
                length = userInput[2][1]
                allowPermits = (userInput[2][2] == 1)
                systemsSubset = []
                if allowPermits:
                    systemsSubset = [system for system in allSystems if min(system.Station_Distances) <= maxStationDistance]
                else:
                    systemsSubset = [system for system in allSystems if min(system.Station_Distances) <= maxStationDistance and not system.Needs_Permit]
                __RunGenetic(systemsSubset,length,500,fitType=FitnessType.FirstOver,silent=False,stopShort=True)
            if runType == 2:
                userSystems = userInput[2]
                routeLen = userSystems.__len__()
                __RunGenetic(userSystems,routeLen,500,fitType=FitnessType.FirstOver,silent=False,stopShort=True)
        
    else:
        maxStationDistance = 5000
        systemsSubset = [system for system in allSystems if min(system.Station_Distances) <= maxStationDistance and not system.Needs_Permit]
        length = 8
        popSize = 500
        fitType = FitnessType.FirstOver
        silenceOutput = False
        stopShort = True
        #__RunGenetic(commonSystems,length,popSize,fitType,silenceOutput,stopShort)

        #PerformanceCalc.CheckPerformance(systemsSubset,fitType=FitnessType.EvenSplit)
        #PerformanceCalc.CheckPerformance(systemsSubset,fitType=FitnessType.FirstOver)

        PerformanceCalc.TestSystems(systemsDict,FitnessType.EvenSplit)

        #fullRoute = EDRareRoute(allSystems,FitnessType.FirstOver)
        #print(fullRoute)
        #fullRoute.PrintRoute()
        #fullRoute.DrawRoute(showLines=False)
#------------------------------------------------------------------------------