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
        goodRouteCutoff = 65

        popSize = 75
        maxStationDistance = 999999
        gens = 10000
            
        routeLen = 5
        maxRouteLen = 8

        while routeLen <= maxRouteLen:
            stats = PerformanceMetrics(routeLen,popSize)
            testNum = 0
            while testNum < maxTests:
                testNum += 1
                print("Test: {0}".format(testNum))
                solved = False
                startTime = time.time()
                routes = RouteCalc.GeneticSolverStart(popSize,gens,allSystems,maxStationDistance,routeLen, True)
                endTime = time.time()
                elapsed = endTime - startTime
                bestRoute = max(routes,key=operator.attrgetter('Fitness_Value'))
                if bestRoute.Fitness_Value >= goodRouteCutoff:
                    solved = True

                stats.Times.append(elapsed)
                stats.Solved.append(solved)
            print(stats)
            routeLen += 1
        input("wait")

class PerformanceMetrics(object):
    def __init__(self,length,popSize):
        self.Route_Length = length
        self.Pop_Size = popSize
        self.Times = []
        self.Solved = []

    def __str__(self):
        strList = []

        numSolved = 0
        totalTimeSolved = 0
        totalTimeUnsolved = 0

        numEntries = self.Solved.__len__()

        for i in range(0,self.Solved.__len__()):
            if self.Solved[i]:
                numSolved += 1
                totalTimeSolved += self.Times[i]
            else:
                totalTimeUnsolved += self.Times[i]

        percentSolved = (numSolved/numEntries) * 100
        avgTimeSolved = totalTimeSolved/numSolved
        avgTimeUnsolved = totalTimeUnsolved/(numEntries - numSolved)

        strList.append("Route Length {0}:".format(self.Route_Length))
        strList.append("\n\tPop size: {0}:".format(self.Pop_Size))
        strList.append("\n\tSolved Percentage: {0}".format(percentSolved))
        strList.append("\n\tAvg time to solve: {0}".format(avgTimeSolved))
        strList.append("\n\tAvg time for unsolved: {0}".format(avgTimeUnsolved))

        return ''.join(strList)