import main
import routecalc
from edrareroute import EDRareRoute, FitnessType, RouteType
from edsystem import EDSystem
import unittest
import random
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class Test_EDRareRoute(unittest.TestCase):
    #TODO: one assert per test
#------------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.All_Systems = main.ReadSystems("RareGoods.csv")
        cls.System_Lists = routecalc.GenerateSystemLists(100,15,cls.All_Systems)
#------------------------------------------------------------------------------
    def test_Route_Not_Eq(self):
        '''
        Test that routes with the same systems, same order, different fitness types are not equal
                                  same systems, different order, same fitness types are not equal
        '''
        sysList1 = random.choice(self.System_Lists)
        sysList2 = [system for system in sysList1]
        random.shuffle(sysList2)

        #Make sure these aren't equal, but I think shuffle will never return the same list??
        self.assertNotEqual(sysList1,sysList2,"shuffle didn't shuffle")

        splitRoute1 = EDRareRoute(sysList1,FitnessType.EvenSplit)
        firstRoute1 = EDRareRoute(sysList1,FitnessType.FirstOver)

        self.assertNotEqual(splitRoute1,firstRoute1)
        self.assertNotEqual(firstRoute1,splitRoute1)


        splitRoute2 = EDRareRoute(sysList2,FitnessType.EvenSplit)
        firstRoute2 = EDRareRoute(sysList2,FitnessType.FirstOver)

        self.assertNotEqual(splitRoute1,splitRoute2)
        self.assertNotEqual(firstRoute1,firstRoute2)
#------------------------------------------------------------------------------
    def test_Route_Eq(self):
        '''
        Test that routes with the same systems and fit type are equal
        '''
        sysList = random.choice(self.System_Lists)
        sysListCopy = [system for system in sysList]
        
        for name,fType in FitnessType.__members__.items():
            with self.subTest(fType=fType):
                testRoute1 = EDRareRoute(sysList,fType)
                testRoute2 = EDRareRoute(sysListCopy,fType)
                self.assertEqual(testRoute1,testRoute2)
#------------------------------------------------------------------------------
    def test_Route_Distance(self):
        '''
        Make sure all fitvals are calculating the expected total distance of a route
        '''
        sysList = random.choice(self.System_Lists)
        routeLen = sysList.__len__()   
        expectedDistance = 0
        for i in range(routeLen):
            currSys = sysList[i%routeLen]
            nextSys = sysList[(i+1)%routeLen]
            expectedDistance += currSys.GetDistanceTo(nextSys)

        for name,fType in FitnessType.__members__.items():
            with self.subTest(fType=fType):
                testRoute = EDRareRoute(sysList,fType)
                self.assertAlmostEqual(expectedDistance,testRoute.Total_Distance)          
#------------------------------------------------------------------------------
    def test_Route_Cargo_Totals(self):
        '''
        Test that the correct total cargo is being calculated
        '''
        sysList = random.choice(self.System_Lists)
        routeLen = sysList.__len__()
        expectedCargo = 0
        for i in range(routeLen):
            currSys = sysList[i]
            expectedCargo += currSys.Max_Supply

        for name,fType in FitnessType.__members__.items():
            with self.subTest(fType=fType):
                testRoute = EDRareRoute(sysList,fType)
                self.assertAlmostEqual(expectedCargo,testRoute.Total_Cargo)    
#------------------------------------------------------------------------------
    def test_Route_Bad_Constructor(self):
        '''
        Make sure we are unable to create routes under length 3
        '''
        for i in range(3):
            sysList = random.choice(self.System_Lists)
            shortList = sysList[:i]
            with self.subTest(i=i):
                for name,fType in FitnessType.__members__.items():
                    with self.subTest(fType=fType):
                        with self.assertRaises(Exception):
                            testRoute = EDRareRoute(shortList,fType)   
#------------------------------------------------------------------------------
    def test_Route_RouteType_Split(self):
        '''
        Test that we are getting only the expected RouteTypes back from certain FitnessTypes
        '''
        fType = FitnessType.EvenSplit
        expectedRouteTypes = [RouteType.Cluster, RouteType.Spread, RouteType.Other]
        for sysList in self.System_Lists:
            currRoute = EDRareRoute(sysList,fType)
            self.assertIn(currRoute.Route_Type,expectedRouteTypes)
#------------------------------------------------------------------------------
    def test_Route_RouteType_First(self):
        '''
        Test that we are getting only the expected RouteTypes back from certain FitnessTypes
        '''
        fType = FitnessType.FirstOver
        expectedRouteTypes = [RouteType.FirstOver, RouteType.FirstOverLong]
        for sysList in self.System_Lists:
            currRoute = EDRareRoute(sysList,fType)
            self.assertIn(currRoute.Route_Type,expectedRouteTypes)
#------------------------------------------------------------------------------
    def test_Route_Systems(self):
        '''
        Test that we get back the same systems from a route that we put in
        '''
        for systemList in self.System_Lists:
            for name,fType in FitnessType.__members__.items():
                with self.subTest(fType=fType):
                    testRoute = EDRareRoute(systemList,fType)
                    self.assertListEqual(testRoute.Systems,systemList)   
#------------------------------------------------------------------------------
    def test_Route_Length(self):
        '''
        Test that we get the expected length back from a route
        '''
        for systemList in self.System_Lists:
            expectedLength = random.randint(3,15)
            tempList = systemList[:expectedLength]
            with self.subTest(expectedLength=expectedLength):
                for name,fType in FitnessType.__members__.items():
                    with self.subTest(fType=fType):
                        testRoute = EDRareRoute(tempList,fType)
                        self.assertEqual(testRoute.Length,expectedLength)
#------------------------------------------------------------------------------
    def test_Route_Properties(self):
        '''
        Test that properties cannot be set
        '''
        testRoute = EDRareRoute(self.System_Lists[0],FitnessType.FirstOver)
        
        with self.assertRaises(AttributeError):
            testRoute.Fitness = 99
        
        with self.assertRaises(AttributeError):
            testRoute.Length = 13
        
        with self.assertRaises(AttributeError):
            testRoute.Route_Type = RouteType.Cluster
        
        with self.assertRaises(AttributeError):
            testRoute.Systems = []
        
        with self.assertRaises(AttributeError):
            testRoute.Total_Cargo = -1
        
        with self.assertRaises(AttributeError):
            testRoute.Total_Distance = -1
#------------------------------------------------------------------------------
    def test_Route_Systems_Unchanged(self):
        '''
        Test that getting the systems of a route and modifying the list does
        not change the systems of the route indirectly
        '''
        for systemList in self.System_Lists:
            for name,fType in FitnessType.__members__.items():
                with self.subTest(fType=fType):
                    testRoute = EDRareRoute(systemList,fType)
                    changedSystems = testRoute.Systems
                    random.shuffle(changedSystems)
                    self.assertNotEqual(testRoute.Systems,changedSystems,msg="EDRareRoute systems indirectly changed")
#------------------------------------------------------------------------------
    def test_Route_Fitness_SysOrderEqual(self):
        '''
        Routes should always have the same fitness value when given systems in the same order
        but with different positions in the system list.
        '''
        #TODO:  Regularly fails with EvenSplit fitness types
        #           Most likely because of the use of itertools.combos to find sellers,
        #           Different route order means different seller selection order and the first will be chosen
        #           Maybe can't do anything about this
        import collections
        for systemList in self.System_Lists:
            for name,fType in FitnessType.__members__.items():
                with self.subTest(fType=fType):
                    sysDQ = collections.deque(systemList)
                    numToRotate = random.randrange(systemList.__len__())
                    sysDQ.rotate(numToRotate)
                    rotatedList = list(sysDQ)
                    route = EDRareRoute(systemList,fType)
                    rotatedRoute = EDRareRoute(rotatedList,fType)
                    self.assertAlmostEqual(route.Fitness,rotatedRoute.Fitness)
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------