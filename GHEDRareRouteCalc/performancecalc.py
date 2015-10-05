from edsystem import EDSystem
from edrareroute import EDRareRoute
from routecalc import RouteCalc
import operator
import random
import itertools
import sys
import math
import time

class PerformanceCalc(object):
    @classmethod
    def CheckPerformance(self,allSystems):
        maxTests = 10
        goodRouteCutoff = RouteCalc.Route_Cutoff

        popSize = 300
        maxPopSize = 300
        maxStationDistance = 999999
            
        routeLen = 7
        maxRouteLen = 8

        while routeLen <= maxRouteLen:
            stats = PerformanceMetrics(routeLen,popSize)
            testNum = 0
            while testNum < maxTests:
                testNum += 1
                #print("Test: {0}".format(testNum))
                solved = False
                startTime = time.time()
                routeTuple = RouteCalc.GeneticSolverStart(popSize,allSystems,maxStationDistance,routeLen, True)
                endTime = time.time()
                elapsed = endTime - startTime
                bestRoute = routeTuple[0]
                if bestRoute.Fitness_Value >= goodRouteCutoff:
                    solved = True

                stats.Times.append(elapsed)
                stats.Solved.append(solved)
                stats.Gens.append(routeTuple[1])

            print(stats)
            #popSize += 10
            routeLen += 1

class PerformanceMetrics(object):
    def __init__(self,length,popSize):
        self.Route_Length = length
        self.Pop_Size = popSize
        self.Times = []
        self.Solved = []
        self.Gens = []

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
        avgTimeSolved = totalTimeSolved/numSolved if numSolved > 0 else 0
        avgTimeUnsolved = totalTimeUnsolved/(numEntries - numSolved) if (numEntries-numSolved) > 0 else 0
        avgGensSolved = totalGensSolved/numSolved if numSolved > 0 else 0 
        avgGensUnsolved = totalGensUnsolved/(numEntries - numSolved) if (numEntries-numSolved) > 0 else 0  

        strList.append("Route Length {0}:".format(self.Route_Length))
        strList.append("\nPop size {0}".format(self.Pop_Size))
        strList.append("\n\tSolved Percentage: {0}".format(percentSolved))
        strList.append("\n\tAvg time to solve: {0}".format(avgTimeSolved))
        strList.append("\n\tAvg generations to solve: {0}".format(avgGensSolved))
        strList.append("\n\tAvg time for unsolved: {0}".format(avgTimeUnsolved))
        strList.append("\n\tAvg generations for unsolved: {0}".format(avgGensUnsolved))

        return ''.join(strList)