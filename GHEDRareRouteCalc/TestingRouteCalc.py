import unittest
from routecalc import RouteCalc
from edsystem import EDSystem
from edrareroute import EDRareRoute, FitnessType
import main
import random
import operator
from collections import Counter

class Test_TestingRouteCalc(unittest.TestCase):
#------------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.All_Systems = main.ReadSystems('RareGoods.csv')
#------------------------------------------------------------------------------
    def setUp(self):
        self.Pop_Size = 300
        self.Route_Length = 15
        self.Fit_Type = FitnessType.FirstOver
        
        RouteCalc.SetValidSystems(self.All_Systems)
        self.Population = [EDRareRoute(systems,self.Fit_Type) for systems in RouteCalc.GenerateSystemLists(self.Pop_Size,self.Route_Length,self.All_Systems)]
#------------------------------------------------------------------------------
    def test_SelectionVals(self):
        '''
        Testing that all the values are as expected, a percentage of their value vs the total value, and that they are in increasing order
        '''
        selectVals = RouteCalc.WrapRelativeFitness(self.Population)
        self.assertEqual(self.Pop_Size,selectVals.__len__())

        selectMult = RouteCalc.GetSelectionMult()
        lastVal = selectMult * self.Pop_Size
        self.assertAlmostEqual(lastVal,selectVals[-1])

        popSum = sum([val.GetFitValue() for val in self.Population])
        firstVal = self.Population[0].GetFitValue()/popSum * lastVal
        self.assertEqual(firstVal,selectVals[0])
        
        for i in range(500):
            with self.subTest(i==i):
                index = random.randrange(1,self.Pop_Size-1)
                randSelectVal = selectVals[index]
                randRoute = self.Population[index]
                sumToIndex = sum([val.GetFitValue() for val in self.Population[:index+1]])
                calcVal = (sumToIndex/popSum) * lastVal
                self.assertAlmostEqual(calcVal,randSelectVal)

        self.assertListEqual(selectVals,sorted(selectVals))
#------------------------------------------------------------------------------
    def test_Reprodudce(self):
        '''
        Test that the majority of children generated are not already in the population
        Reproduce returns a tuple of lists, but we turn these into EDRareRoutes for comparison
        '''
        #TODO: Potential failure risk when popsize is larger than the number of total combos of validsystems with len routelen
        maxNumIn = self.Pop_Size * 0.05
        numIn = 0
        selectVals = RouteCalc.WrapRelativeFitness(self.Population)
        for i in range(self.Pop_Size):
            with self.subTest(i==i):
                children = RouteCalc.WrapReproduce(self.Population,selectVals)
                self.assertEqual(children.__len__(),2)
                self.failIfEqual(children[0],children[1])
                for child in (EDRareRoute(val,self.Fit_Type) for val in children):
                    if child in self.Population:
                        numIn += 1

        self.assertTrue(numIn <= maxNumIn)
#------------------------------------------------------------------------------
    def test_Mutate(self):
        '''
        General test to make sure mutate will never return the same system list that we pass to it
        '''
        systemLists = RouteCalc.GenerateSystemLists(self.Pop_Size,self.Route_Length,self.All_Systems)
        for systemList in systemLists:
            with self.subTest(systemList==systemList):
                mutatedList = RouteCalc.WrapMutate(systemList)
                self.failIfEqual(systemList,mutatedList)
#------------------------------------------------------------------------------
    def test_Mutate_Special(self):
        '''
        Test the special case where number of valid systems is equal to route length
        '''
        tempValidSystems = self.All_Systems[:self.Route_Length]
        RouteCalc.SetValidSystems(tempValidSystems);
        systemLists = RouteCalc.GenerateSystemLists(self.Pop_Size,self.Route_Length,tempValidSystems)
        for systemList in systemLists:
            with self.subTest(systemList==systemList):
                mutatedList = RouteCalc.WrapMutate(systemList)
                self.failIfEqual(systemList,mutatedList)
#------------------------------------------------------------------------------
    def test_GeneratedSystems(self):
        '''
        Make sure RouteCalc.GenerateSystemLists generates lists of systems without duplicates
        '''
        initPop = 5
        popIncreases = 10
        popRange = ((initPop ** i for i in range(1,popIncreases)))
        initRouteLen = 3
        routeLenIncreases = 10
        lenRange = ((initRouteLen * i * 2 for i in range(1,routeLenIncreases)))

        for popSize in popRange:
            with self.subTest(popSize == popSize):
                for routeLen in lenRange:
                    with self.subTest(routeLen==routeLen):
                        systemLists = RouteCalc.GenerateSystemLists(popSize,routeLen,self.All_Systems)
                        for systemList in systemLists:
                            for sys,count in Counter(systemList).most_common():
                                self.assertEqual(count,1)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
