from edsystem import EDSystem
from edrareroute import EDRareRoute
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
        goodRouteCutoff = RouteCalc.Route_Cutoff

        popSize = 100
        maxPopSize = 100
        maxStationDistance = 1000
            
        routeLen = 3
        maxRouteLen = 8

        while routeLen <= maxRouteLen:
            stats = PerformanceMetrics(routeLen,popSize)
            testNum = 0
            while testNum < maxTests:
                testNum += 1
                #print("Test: {0}".format(testNum))
                solved = False
                startTime = time.time()
                routeTuple = RouteCalc.GeneticSolverStart(popSize,systemsList,routeLen, True)
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

    @classmethod
    def SelectionTester(self, size: int):
        #Just copying from routecalc because i'm bad
        for run in range(0,50000):
            population = []
            for i in range(0,size):
                population.append(random.uniform(1,20))
            upperVal = math.ceil(size * 1.2)
            total = sum([val for val in population])

            selectionValues = [population[0]/total * upperVal]
            for i in range(1,population.__len__()):
                percentTotal = population[i]/total * upperVal
                selectionValues.append(percentTotal + selectionValues[i-1])

            if abs(upperVal - selectionValues[-1]) >= 0.0001:
                print("fail")

            parentsBisect = []
            parentsLoop = []
            while parentsBisect.__len__() != 2:
                value = random.uniform(0,upperVal)
                parentsBisect.append(bisect.bisect(selectionValues,value))
            
                i = 0
                while True:
                    currentSelection = None
                    if value <= selectionValues[i]:
                        parentsLoop.append(i)
                        break
                    i += 1


            if not (parentsBisect[0] == parentsLoop[0] and parentsBisect[1] == parentsLoop[1]):
                print("fail")
                print("b0: " + parentsBisect[0])
                print("l0: " + parentsLoop[0])
                print("b1: " + parentsBisect[1])
                print("b2: " + parentsLoop[1])
                

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