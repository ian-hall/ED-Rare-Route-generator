﻿from edsystem import EDSystem
from edrareroute import EDRareRoute, RouteType, FitnessType
from routecalc import RouteCalc
import time

class PerformanceCalc(object):
#------------------------------------------------------------------------------
    @classmethod
    def CheckPerformance(self,systemsList,fitType = FitnessType.Default):
        maxTests = 20

        minPopSize = 300
        maxPopSize = 400
        popSizeStep = 50
        popSizes = range(minPopSize,maxPopSize+1,popSizeStep)          

        minLength = 8
        maxLength = 8
        lengths = range(minLength,maxLength+1,1)

        
        for routeLength in lengths:
            for popSize in popSizes:
                stats = PerformanceMetrics(routeLength,popSize)
                #testNum = 0
                for testNum in range(maxTests):
                    #testNum += 1
                    #print("Test: {0}".format(testNum))
                    solved = False
                    startTime = time.time()
                    routeTuple = RouteCalc.GeneticSolverStart(popSize,systemsList,routeLength, True,fitType)
                    endTime = time.time()
                    elapsed = endTime - startTime
                    bestRoute = routeTuple[0]
                    if bestRoute.Fitness_Value >= RouteCalc.Route_Cutoff:
                        stats.Types.append(routeTuple[0].Route_Type)
                        stats.Values.append(routeTuple[0].Fitness_Value)
                        solved = True

                    stats.Times.append(elapsed)
                    stats.Solved.append(solved)
                    stats.Gens.append(routeTuple[1])

                print(stats)
#------------------------------------------------------------------------------
    @classmethod
    def TestSystems(self,systemsDict,fitType = FitnessType.Default):
        ykLoopList = []
        ykLoopList.append(systemsDict['Coquim'])  
        ykLoopList.append(systemsDict['Altair'])   
        ykLoopList.append(systemsDict['Ethgreze'])  
        ykLoopList.append(systemsDict['AZ Cancri'])  
        ykLoopList.append(systemsDict['George Pantazis'])  
        ykLoopList.append(systemsDict['Utgaroar'])  
        ykLoopList.append(systemsDict['Yaso Kondi']) 
        ykLoopList.append(systemsDict['Quechua'])  
        print("\n\nYK Loop")
        print(EDRareRoute(ykLoopList,fitType))
        EDRareRoute(ykLoopList,fitType).DrawRoute()

        good4_1 = []
        good4_1.append(systemsDict['Fujin'])  
        good4_1.append(systemsDict['39 Tauri'])   
        good4_1.append(systemsDict['Diso'])  
        good4_1.append(systemsDict['Leesti'])  
        print(EDRareRoute(good4_1,fitType))
       
        good5_1 = []
        good5_1.append(systemsDict['Irukama']) 
        good5_1.append(systemsDict['Ngurii']) 
        good5_1.append(systemsDict['Leesti']) 
        good5_1.append(systemsDict['Aganippe'])  
        good5_1.append(systemsDict['Altair'])  
        print(EDRareRoute(good5_1,fitType))

        good5_2 = []
        good5_2.append(systemsDict['Leesti'])  
        good5_2.append(systemsDict['Diso'])  
        good5_2.append(systemsDict['Orrere'])  
        good5_2.append(systemsDict['Utgaroar'])  
        good5_2.append(systemsDict['Tanmark'])
        print(EDRareRoute(good5_2,fitType))

        good5_3 = []
        good5_3.append(systemsDict['Tanmark'])  
        good5_3.append(systemsDict['Orrere'])  
        good5_3.append(systemsDict['Diso'])  
        good5_3.append(systemsDict['Lave'])  
        good5_3.append(systemsDict['Utgaroar'])  
        print(EDRareRoute(good5_3,fitType))

        good6_1 = []
        good6_1.append(systemsDict['Orrere'])
        good6_1.append(systemsDict['Tarach Tor'])  
        good6_1.append(systemsDict['Tanmark'])  
        good6_1.append(systemsDict['Utgaroar'])  
        good6_1.append(systemsDict['Leesti'])  
        good6_1.append(systemsDict['Lave'])  
        print(EDRareRoute(good6_1,fitType)) 
         
        good8_1 = []
        good8_1.append(systemsDict['Hecate'])
        good8_1.append(systemsDict['Aganippe']) 
        good8_1.append(systemsDict['Leesti'])
        good8_1.append(systemsDict['Any Na'])
        good8_1.append(systemsDict['Ngurii'])
        good8_1.append(systemsDict["Baltah'Sine"])
        good8_1.append(systemsDict['Chi Eridani'])
        good8_1.append(systemsDict['Altair']) 
        print(EDRareRoute(good8_1,fitType))
        
        bad6_1 = []
        bad6_1.append(systemsDict['Karetii'])
        bad6_1.append(systemsDict['Eleu'])
        bad6_1.append(systemsDict['Altair']) 
        bad6_1.append(systemsDict['Utgaroar'])
        bad6_1.append(systemsDict['Hecate'])
        bad6_1.append(systemsDict['Ochoeng'])
        print("\nNo 2 systems to sell all goods at")
        print(EDRareRoute(bad6_1,fitType))
                
        bad8_1 = []
        bad8_1.append(systemsDict['Chi Eridani']) 
        bad8_1.append(systemsDict['Altair'])  
        bad8_1.append(systemsDict['Bast']) 
        bad8_1.append(systemsDict['Tiolce']) 
        bad8_1.append(systemsDict["Baltah'Sine"]) 
        bad8_1.append(systemsDict['Irukama']) 
        bad8_1.append(systemsDict['Karsuki Ti']) 
        bad8_1.append(systemsDict['Delta Phoenicis'])
        print("\nLow item cost")
        print(EDRareRoute(bad8_1,fitType))

        bad11_1 = []
        bad11_1.append(systemsDict['Zeessze'])
        bad11_1.append(systemsDict['Rusani'])  
        bad11_1.append(systemsDict['Aganippe'])   
        bad11_1.append(systemsDict['Leesti'])  
        bad11_1.append(systemsDict['Lave'])  
        bad11_1.append(systemsDict['Ngurii'])  
        bad11_1.append(systemsDict['Irukama'])  
        bad11_1.append(systemsDict['CD-75 661'])  
        bad11_1.append(systemsDict['Tiolce'])  
        bad11_1.append(systemsDict['Epsilon Indi'])
        bad11_1.append(systemsDict['Altair'])
        print("\nPoor system distances, Bad system order")
        print(EDRareRoute(bad11_1,fitType))
        EDRareRoute(bad11_1,fitType).DrawRoute()

        altTestRoute = []
        altTestRoute.append(systemsDict['Shinrarta Dezhra'])
        altTestRoute.append(systemsDict['Leesti'])
        altTestRoute.append(systemsDict['Diso'])
        altTestRoute.append(systemsDict['Uszaa'])
        altTestRoute.append(systemsDict['Orrere'])
        altTestRoute.append(systemsDict['Lave'])
        altTestRoute.append(systemsDict['Zaonce'])
        altTestRoute.append(systemsDict['Sanuma'])
        altTestRoute.append(systemsDict['Toxandji'])
        altTestRoute.append(systemsDict['Any Na'])
        altTestRoute.append(systemsDict['Arouca'])
        altTestRoute.append(systemsDict['Deuringas'])
        altTestRoute.append(systemsDict['Neritus'])
        altTestRoute.append(systemsDict['AZ Cancri'])
        altTestRoute.append(systemsDict['Eranin'])
        altTestRoute.append(systemsDict['Ethgreze'])
        altTestRoute.append(systemsDict['Rusani'])
        altTestRoute.append(systemsDict['Damna'])
        altTestRoute.append(systemsDict['Volkhab'])
        altTestRoute.append(systemsDict['Alacarakmo'])
        altTestRoute.append(systemsDict['Rajukru'])
        altTestRoute.append(systemsDict['Kongga'])
        altTestRoute.append(systemsDict['Esuseku'])
        altTestRoute.append(systemsDict['Ochoeng'])
        altTestRoute.append(systemsDict['Karetii'])
        altTestRoute.append(systemsDict['Heike'])
        altTestRoute.append(systemsDict['Helvetitj'])
        altTestRoute.append(systemsDict['Eleu'])
        altTestRoute.append(systemsDict['Kinago'])
        altTestRoute.append(systemsDict['Vanayequi'])
        altTestRoute.append(systemsDict['Kamorin'])
        altTestRoute.append(systemsDict['Kachirigin'])
        altTestRoute.append(systemsDict['Nguna'])
        altTestRoute.append(systemsDict['HIP 10175'])
        altTestRoute.append(systemsDict['Momus Reach'])
        #altTestRoute.append(systemsDict['Wolf 1301'])
        altTestRoute.append(systemsDict['Witchhaul'])
        altTestRoute.append(systemsDict['Fujin'])
        altTestRoute.append(systemsDict['39 Tauri'])
        altTestRoute.append(systemsDict['Hecate'])
        altTestRoute.append(systemsDict['Bast'])
        altTestRoute.append(systemsDict['Zeessze'])
        altTestRoute.append(systemsDict['George Pantazis'])
        altTestRoute.append(systemsDict['Epsilon Indi'])
        altTestRoute.append(systemsDict['Altair'])
        altTestRoute.append(systemsDict['Xihe'])
        altTestRoute.append(systemsDict['Tiolce'])
        altTestRoute.append(systemsDict['Chi Eridani'])
        altTestRoute.append(systemsDict['Tanmark'])
        altTestRoute.append(systemsDict['Tarach Tor'])
        altTestRoute.append(systemsDict['Utgaroar'])
        altTestRoute.append(systemsDict['Quechua'])
        altTestRoute.append(systemsDict['Belalans'])
        altTestRoute.append(systemsDict['Aerial'])
        altTestRoute.append(systemsDict['Jaroua'])
        altTestRoute.append(systemsDict['Irukama'])
        altTestRoute.append(systemsDict['Karsuki Ti'])
        altTestRoute.append(systemsDict['Goman'])
        altTestRoute.append(systemsDict['Eshu'])
        altTestRoute.append(systemsDict['Rapa Bao'])
        altTestRoute.append(systemsDict['Wuthielo Ku'])
        altTestRoute.append(systemsDict['Kamitra'])
        altTestRoute.append(systemsDict['Delta Phoenicis'])
        altTestRoute.append(systemsDict['Coquim'])
        altTestRoute.append(systemsDict['Phiagre'])
        altTestRoute.append(systemsDict['HR 7221'])
        altTestRoute.append(systemsDict["Baltah'Sine"])
        altTestRoute.append(systemsDict['CD-75 661'])	
        #print(EDRareRoute(altTestRoute,fitType))
        #EDRareRoute(altTestRoute,fitType).DrawRoute()
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class PerformanceMetrics(object):
#------------------------------------------------------------------------------
    def __init__(self,length,popSize):
        self.Route_Length = length
        self.Pop_Size = popSize
        self.Times = []
        self.Solved = []
        self.Gens = []
        self.Types = []
        self.Values = []
#------------------------------------------------------------------------------
    def __str__(self):
        strList = []

        numSolved = 0
        totalTimeSolved = 0
        totalTimeUnsolved = 0
        totalGensSolved = 0
        totalGensUnsolved = 0

        numEntries = self.Solved.__len__()

        for i in range(0,self.Solved.__len__()):
            if self.Solved[i]:
                numSolved += 1
                totalTimeSolved += self.Times[i]
                totalGensSolved += self.Gens[i]
            else:
                totalTimeUnsolved += self.Times[i]
                totalGensUnsolved += self.Gens[i]

        percentSolved = (numSolved/numEntries) * 100
        avgSolvedValue = sum(self.Values)/self.Values.__len__() if numSolved > 0 else 0
        avgTimeSolved = totalTimeSolved/numSolved if numSolved > 0 else 0
        avgTimeUnsolved = totalTimeUnsolved/(numEntries - numSolved) if (numEntries-numSolved) > 0 else 0
        avgGensSolved = totalGensSolved/numSolved if numSolved > 0 else 0 
        avgGensUnsolved = totalGensUnsolved/(numEntries - numSolved) if (numEntries-numSolved) > 0 else 0  

        strList.append("\nRoute Length {0}, Pop Size {1}".format(self.Route_Length,self.Pop_Size))
        strList.append("\n\tSolved {0}%".format(percentSolved))
        if numSolved > 0:
            strList.append("\n\tAvg solved value: {0}".format(avgSolvedValue))
            strList.append("\n\tAvg time(solved): {0}".format(avgTimeSolved))
            strList.append("\n\tAvg generations(solved): {0}".format(avgGensSolved))
            strList.append("\n\tSolution Types:")
            strList.append("\n\t\t{0}: {1}".format(RouteType.Other.name,self.Types.count(RouteType.Other)))
            strList.append("\n\t\t{0}: {1}".format(RouteType.Spread.name,self.Types.count(RouteType.Spread)))
            strList.append("\n\t\t{0}: {1}".format(RouteType.Cluster.name,self.Types.count(RouteType.Cluster)))
        if numSolved != self.Solved.__len__():
            strList.append("\n\tAvg time(fail): {0}".format(avgTimeUnsolved))
            strList.append("\n\tAvg generations(fail): {0}".format(avgGensUnsolved))

        return ''.join(strList)