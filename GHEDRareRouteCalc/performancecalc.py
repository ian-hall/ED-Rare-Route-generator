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

        minPopSize = 500
        maxPopSize = 500
        popSizeStep = 50
        popSizes = range(minPopSize,maxPopSize+1,popSizeStep)          

        minLength = 8
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