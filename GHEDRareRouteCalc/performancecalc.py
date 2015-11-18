from edsystem import EDSystem
from edrareroute import EDRareRoute, RouteType
from routecalc import RouteCalc
import operator
import random
import itertools
import sys
import math
import time
import bisect

class PerformanceCalc(object):
    @classmethod
    def CheckPerformance(self,systemsList):
        maxTests = 10

        minPopSize = 50
        maxPopSize = 100
        popSizeStep = 50
        popSizes = range(minPopSize,maxPopSize+1,popSizeStep)          

        minLength = 7
        maxLength = 9
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
                    routeTuple = RouteCalc.GeneticSolverStart(popSize,systemsList,routeLength, True)
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
    @classmethod
    def TestSystems(self,systemsDict):
        #Yaso Kondi loop
        ykLoopList = []
        ykLoopList.append(systemsDict['Coq'])  
        ykLoopList.append(systemsDict['Alt'])   
        ykLoopList.append(systemsDict['Eth'])  
        ykLoopList.append(systemsDict['AZ C'])  
        ykLoopList.append(systemsDict['George'])  
        ykLoopList.append(systemsDict['Utg'])  
        ykLoopList.append(systemsDict['Yaso']) 
        ykLoopList.append(systemsDict['Quech'])  
        print("\n\nYK Loop")
        print(EDRareRoute(ykLoopList))

        good4_1 = []
        good4_1.append(systemsDict['Fujin'])  
        good4_1.append(systemsDict['39 T'])   
        good4_1.append(systemsDict['Diso'])  
        good4_1.append(systemsDict['Leesti'])  
        print(EDRareRoute(good4_1))
       
        good5_1 = []
        good5_1.append(systemsDict['Iru']) 
        good5_1.append(systemsDict['Ngur']) 
        good5_1.append(systemsDict['Leesti']) 
        good5_1.append(systemsDict['Agan'])  
        good5_1.append(systemsDict['Alt'])  
        print(EDRareRoute(good5_1))

        good5_2 = []
        good5_2.append(systemsDict['Leesti'])  
        good5_2.append(systemsDict['Diso'])  
        good5_2.append(systemsDict['Orr'])  
        good5_2.append(systemsDict['Utg'])  
        good5_2.append(systemsDict['Tanm'])
        print(EDRareRoute(good5_2))

        good5_3 = []
        good5_3.append(systemsDict['Tanm'])  
        good5_3.append(systemsDict['Orr'])  
        good5_3.append(systemsDict['Diso'])  
        good5_3.append(systemsDict['Lave'])  
        good5_3.append(systemsDict['Utg'])  
        print(EDRareRoute(good5_3))

        good6_1 = []
        good6_1.append(systemsDict['Orr'])
        good6_1.append(systemsDict['Tara'])  
        good6_1.append(systemsDict['Tanm'])  
        good6_1.append(systemsDict['Utg'])  
        good6_1.append(systemsDict['Leesti'])  
        good6_1.append(systemsDict['Lave'])  
        print(EDRareRoute(good6_1))   
         
        good8_1 = []
        good8_1.append(systemsDict['Hec'])
        good8_1.append(systemsDict['Agan']) 
        good8_1.append(systemsDict['Leesti'])
        good8_1.append(systemsDict['Any'])
        good8_1.append(systemsDict['Ngur'])
        good8_1.append(systemsDict['Baltah'])
        good8_1.append(systemsDict['Chi Er'])
        good8_1.append(systemsDict['Alt']) 
        print(EDRareRoute(good8_1))
        
        bad6_1 = []
        bad6_1.append(systemsDict['Kare'])  #Kare
        bad6_1.append(systemsDict['Eleu'])  #Ele
        bad6_1.append(systemsDict['Alt'])   #Alt
        bad6_1.append(systemsDict['Utg'])  #Utg
        bad6_1.append(systemsDict['Hec'])  #Hec
        bad6_1.append(systemsDict['Ocho'])  #Ocho
        print("\nNot all systems accounted for in sellers")
        print(EDRareRoute(bad6_1))
        
        bad8_1 = []
        bad8_1.append(systemsDict['Chi Er']) 
        bad8_1.append(systemsDict['Alt'])  
        bad8_1.append(systemsDict['Bast']) 
        bad8_1.append(systemsDict['Tio']) 
        bad8_1.append(systemsDict['Baltah']) 
        bad8_1.append(systemsDict['Iru']) 
        bad8_1.append(systemsDict['Karsu']) 
        bad8_1.append(systemsDict['Delta P'])
        print("\nLow item cost")
        print(EDRareRoute(bad8_1))

        bad11_1 = []
        bad11_1.append(systemsDict['Zee']) #Zee
        bad11_1.append(systemsDict['Rusa'])  #Rus
        bad11_1.append(systemsDict['Agan'])   #Agan
        bad11_1.append(systemsDict['Leesti'])  #Leesti
        bad11_1.append(systemsDict['Lave'])  #Lave
        bad11_1.append(systemsDict['Ngur'])  #Ngur
        bad11_1.append(systemsDict['Iru'])  #Iru
        bad11_1.append(systemsDict['CD-75'])  #CD-75
        bad11_1.append(systemsDict['Tio'])  #Tio
        bad11_1.append(systemsDict['Epsi'])  #Epsi
        bad11_1.append(systemsDict['Alt'])   #Alt
        print("\nPoor system distances")
        print(EDRareRoute(bad11_1))

class PerformanceMetrics(object):
    def __init__(self,length,popSize):
        self.Route_Length = length
        self.Pop_Size = popSize
        self.Times = []
        self.Solved = []
        self.Gens = []
        self.Types = []
        self.Values = []

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