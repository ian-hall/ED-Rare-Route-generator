import main
import routecalc
from routecalc import RouteCalc
from edsystem import EDSystem
from edrareroute import EDRareRoute, FitnessType
import unittest
import random
import operator
from collections import Counter

class Test_RouteCalc(unittest.TestCase):
#------------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.All_Systems = main.ReadSystems(useLocal=True)
#------------------------------------------------------------------------------
    def setUp(self):
        self.Pop_Size = 300
        self.Route_Length = 8
        self.Fit_Type = FitnessType.FirstOver
        
        RouteCalc.SetValidSystems(self.All_Systems)
        self.Population = [EDRareRoute(systems,self.Fit_Type) for systems in routecalc.GenerateSystemLists(self.Pop_Size,self.Route_Length,self.All_Systems)]
#------------------------------------------------------------------------------
    def test_Genetic_SelectionVals(self):
        '''
        Testing that all the values are as expected, a percentage of their value vs the total value, and that they are in increasing order
        '''
        selectVals = RouteCalc.Wrap_CalcRelativeFitness(self.Population)
        self.assertEqual(self.Pop_Size,len(selectVals))

        selectMult = RouteCalc.GetSelectionMult()
        lastVal = selectMult * self.Pop_Size
        self.assertAlmostEqual(lastVal,selectVals[-1])

        popSum = sum([route.Fitness for route in self.Population])
        firstVal = self.Population[0].Fitness/popSum * lastVal
        self.assertEqual(firstVal,selectVals[0])
        
        for i in range(500):
            with self.subTest(i=i):
                index = random.randrange(1,self.Pop_Size-1)
                randSelectVal = selectVals[index]
                randRoute = self.Population[index]
                sumToIndex = sum([route.Fitness for route in self.Population[:index+1]])
                calcVal = (sumToIndex/popSum) * lastVal
                self.assertAlmostEqual(calcVal,randSelectVal)

        self.assertListEqual(selectVals,sorted(selectVals))
#------------------------------------------------------------------------------
    def test_Genetic_Reproduce(self):
        '''
        Test that children generated by the reproduce function are not the same.
        '''
        #TODO: Will still fail sometimes if reproduce function shuffles the same way twice
        selectVals = RouteCalc.Wrap_CalcRelativeFitness(self.Population)
        for reproNum in range(self.Pop_Size):
            with self.subTest(reproNum=reproNum):
                children = RouteCalc.Wrap_Reproduce(self.Population,selectVals)
                self.assertEqual(len(children),2,"RouteCalc.Repro must create 2 children")
                self.failIfEqual(children[0],children[1],"Generated children must be different")

        #Assert removed because small route + small num valid systems + large pop = a lot of duplicates and that should not be a fail state
        #self.assertTrue(numIn <= maxNumIn,"Too many routes passing through to next generation")
#------------------------------------------------------------------------------
    def test_Genetic_Mutate(self):
        '''
        General test to make sure mutate will never return the same system list that we pass to it
        '''
        systemLists = routecalc.GenerateSystemLists(self.Pop_Size,self.Route_Length,self.All_Systems)
        for systemList in systemLists:
            with self.subTest(systemList=systemList):
                mutatedList = RouteCalc.Wrap_Mutate(systemList)
                self.failIfEqual(systemList,mutatedList)
#------------------------------------------------------------------------------
    def test_Genetic_MutateSpecial(self):
        '''
        Test the special case where number of valid systems is equal to route length
        '''
        tempValidSystems = self.All_Systems[:self.Route_Length]
        RouteCalc.SetValidSystems(tempValidSystems);
        systemLists = routecalc.GenerateSystemLists(self.Pop_Size,self.Route_Length,tempValidSystems)
        for systemList in systemLists:
            with self.subTest(systemList=systemList):
                mutatedList = RouteCalc.Wrap_Mutate(systemList)
                self.failIfEqual(systemList,mutatedList)
#------------------------------------------------------------------------------
    def test_Genetic_GenerateSystemLists(self):
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
            with self.subTest(popSize=popSize):
                for routeLen in lenRange:
                    with self.subTest(routeLen=routeLen):
                        systemLists = routecalc.GenerateSystemLists(popSize,routeLen,self.All_Systems)
                        for currList in systemLists:
                            for sys,count in Counter(currList).most_common():
                                self.assertEqual(count,1,"Multiple of a system found in route")
                        self.assertEqual(len(systemLists),popSize,"Did not generate correct number of system lists")
                        self.assertEqual(len(systemLists[0]),routeLen,"Did not generate lists of the correct length")
#------------------------------------------------------------------------------
    @unittest.expectedFailure
    def test_Genetic_StartNoArgs(self):
        RouteCalc.StartGeneticSolver()
#------------------------------------------------------------------------------
    def test_Genetic_StartBadArgs(self):
        #Assert empty system list raises exception
        with self.assertRaises(Exception):
            RouteCalc.StartGeneticSolver(500,[],20,True,self.Fit_Type)

        #Assert passing a pop size under 3 raises exception
        for popSize in range(3):
            with self.subTest(popSize=popSize):
                with self.assertRaises(Exception):
                    RouteCalc.StartGeneticSolver(popSize,self.All_Systems,6,True,self.Fit_Type)

        #Assert fail if there are more systems in the route than in the list of valid systems
        with self.assertRaises(Exception):
            RouteCalc.StartGeneticSolver(200,self.All_Systems[:self.Route_Length-1],self.Route_Length,True,self.Fit_Type)
#------------------------------------------------------------------------------
    def test_Genetic_StartBadRoutelength(self):
        #Assert passing a route length 3 or over 15 raises exception for fittype.EvenSplit
        for routeLen in range(3):
            with self.subTest(routeLen=routeLen):
                with self.assertRaises(Exception):
                    RouteCalc.StartGeneticSolver(self.Pop_Size,self.All_Systems,routeLen,True,FitnessType.EvenSplit)

        for routeLen in range(16,19):
            with self.subTest(routeLen=routeLen):
                with self.assertRaises(Exception):
                    RouteCalc.StartGeneticSolver(self.Pop_Size,self.All_Systems,routeLen,True,FitnessType.EvenSplit)

        #FirstOver should throw exception on routes under len 6 and over 35
        for routeLen in range(6):
            with self.subTest(routeLen=routeLen):
                with self.assertRaises(Exception):
                    RouteCalc.StartGeneticSolver(self.Pop_Size,self.All_Systems,routeLen,True,FitnessType.FirstOver)

        for routeLen in range(36,39):
            with self.subTest(routeLen=routeLen):
                with self.assertRaises(Exception):
                    RouteCalc.StartGeneticSolver(self.Pop_Size,self.All_Systems,routeLen,True,FitnessType.FirstOver)
#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
