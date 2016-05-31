from edsystem import EDSystem
import unittest
import random
import string
import itertools
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class Test_EDSystem(unittest.TestCase):
    #TODO: one assert per test(maybe)
#------------------------------------------------------------------------------
    #@classmethod
    ##This is causing a lot of slowdown on these tests but it should only run once?
    ##Just slamming this down into setUp
    #def setUpClass(cls):
    #    cls.Test_Params = CreateEDSystemParamList(1000)
    #    cls.Test_Systems = CreateSystemsFromParams(cls.Test_Params)
#------------------------------------------------------------------------------
    def setUp(self):
        self.Test_Args = CreateEDSystemArgsList(500)
        self.Test_Systems = CreateSystemsFromParams(self.Test_Args)
#------------------------------------------------------------------------------
    def test_System_Contructor(self):        
        systemName = "test system"
        stationName = "test station"
        index = 0
        supplyCap = 12
        avgSupply = 10
        itemCost = 400
        itemName = "test item"
        distToStation = 219
        permitReq = False
        distToOthers = [0]

        with self.assertRaises(Exception,msg="no empty constructor"):
            testSystem = EDSystem()
        with self.assertRaises(Exception,msg="missing args to constructor"):
            testSystem = EDSystem(avgSupply,itemCost,itemName,distToStation,stationName,systemName,index,distToOthers,permitReq)           
        
        wrongDistToOthers = 0
        with self.assertRaises(TypeError,msg="distToOthers needs to be a list"):
            testSystem = EDSystem(supplyCap,avgSupply,itemCost,itemName,distToStation,stationName,systemName,index,wrongDistToOthers,permitReq)
        
        with self.assertRaises(Exception,msg="no Nones allowed"):
            testSystem = EDSystem(None,avgSupply,itemCost,itemName,distToStation,stationName,systemName,index,distToOthers,permitReq)
        with self.assertRaises(Exception,msg="no Nones allowed"):
            testSystem = EDSystem(supplyCap,None,itemCost,itemName,distToStation,stationName,systemName,index,distToOthers,permitReq)
        with self.assertRaises(Exception,msg="no Nones allowed"):
            testSystem = EDSystem(supplyCap,avgSupply,None,itemName,distToStation,stationName,systemName,index,distToOthers,permitReq)
        with self.assertRaises(Exception,msg="no Nones allowed"):
            testSystem = EDSystem(supplyCap,avgSupply,itemCost,None,distToStation,stationName,systemName,index,distToOthers,permitReq)
        with self.assertRaises(Exception,msg="no Nones allowed"):
            testSystem = EDSystem(supplyCap,avgSupply,itemCost,itemName,None,stationName,systemName,index,distToOthers,permitReq)
        with self.assertRaises(Exception,msg="no Nones allowed"):
            testSystem = EDSystem(supplyCap,avgSupply,itemCost,itemName,distToStation,None,systemName,index,distToOthers,permitReq)
        with self.assertRaises(Exception,msg="no Nones allowed"):
            testSystem = EDSystem(supplyCap,avgSupply,itemCost,itemName,distToStation,stationName,None,index,distToOthers,permitReq)
        with self.assertRaises(Exception,msg="no Nones allowed"):
            testSystem = EDSystem(supplyCap,avgSupply,itemCost,itemName,distToStation,stationName,systemName,None,distToOthers,permitReq)
        with self.assertRaises(Exception,msg="no Nones allowed"):
            testSystem = EDSystem(supplyCap,avgSupply,itemCost,itemName,distToStation,stationName,systemName,index,None,permitReq)
        with self.assertRaises(Exception,msg="no Nones allowed"):
            testSystem = EDSystem(supplyCap,avgSupply,itemCost,itemName,distToStation,stationName,systemName,index,distToOthers,None)
#------------------------------------------------------------------------------
    def test_System_AddRares_Item_Names(self):
        squishedSystems = []
        for args in self.Test_Args:
            newSystem = EDSystem(**args)
            if squishedSystems.count(newSystem) != 0:
                for currentSystem in squishedSystems:
                    with self.subTest(currSystem=currentSystem):
                        if currentSystem == newSystem:
                            expected_Item_Names = currentSystem.Item_Names
                            expected_Item_Names.extend(newSystem.Item_Names)
                            currentSystem.AddRares(newSystem)
                            self.assertListEqual(expected_Item_Names,currentSystem.Item_Names)
            else:
                squishedSystems.append(newSystem)
#------------------------------------------------------------------------------
    def test_System_AddRares_Item_Costs(self):
        squishedSystems = []
        for args in self.Test_Args:
            newSystem = EDSystem(**args)
            if squishedSystems.count(newSystem) != 0:
                for currentSystem in squishedSystems:
                    with self.subTest(currSystem=currentSystem):
                        if currentSystem == newSystem:
                            expected_Item_Costs = currentSystem.Item_Costs
                            expected_Item_Costs.extend(newSystem.Item_Costs)
                            currentSystem.AddRares(newSystem)
                            self.assertListEqual(expected_Item_Costs,currentSystem.Item_Costs)
            else:
                squishedSystems.append(newSystem)
#------------------------------------------------------------------------------
    def test_System_AddRares_Station_Names(self):
        squishedSystems = []
        for args in self.Test_Args:
            newSystem = EDSystem(**args)
            if squishedSystems.count(newSystem) != 0:
                for currentSystem in squishedSystems:
                    with self.subTest(currSystem=currentSystem):
                        if currentSystem == newSystem:
                            expected_Station_Names = currentSystem.Station_Names
                            expected_Station_Names.extend(newSystem.Station_Names)
                            currentSystem.AddRares(newSystem)
                            self.assertListEqual(expected_Station_Names,currentSystem.Station_Names)
            else:
                squishedSystems.append(newSystem)
#------------------------------------------------------------------------------
    def test_System_AddRares_Station_Distances(self):
        squishedSystems = []
        for args in self.Test_Args:
            newSystem = EDSystem(**args)
            if squishedSystems.count(newSystem) != 0:
                for currentSystem in squishedSystems:
                    with self.subTest(currSystem=currentSystem):
                        if currentSystem == newSystem:
                            expected_Station_Distances = currentSystem.Station_Distances
                            expected_Station_Distances.extend(newSystem.Station_Distances)
                            currentSystem.AddRares(newSystem)
                            self.assertListEqual(expected_Station_Distances,currentSystem.Station_Distances)
            else:
                squishedSystems.append(newSystem)
#------------------------------------------------------------------------------
    def test_System_AddRares_Total_Cost(self):
        squishedSystems = []
        for args in self.Test_Args:
            newSystem = EDSystem(**args)
            if squishedSystems.count(newSystem) != 0:
                for currentSystem in squishedSystems:
                    with self.subTest(currSystem=currentSystem):
                        if currentSystem == newSystem:
                            expected_Total = currentSystem.Total_Cost + newSystem.Total_Cost
                            currentSystem.AddRares(newSystem)
                            self.assertAlmostEqual(expected_Total,currentSystem.Total_Cost)
            else:
                squishedSystems.append(newSystem)
#------------------------------------------------------------------------------
    def test_System_Total_Cost(self):
        '''
        Test that we are getting back the expected total cost of items sold in a system
        '''
        for system in self.Test_Systems:
            with self.subTest(sysName=system.System_Name):
                expectedCosts = self.__PullValsForArg(self.Test_Args,"itemCost",system.System_Name)
                expectedSupplyNums = self.__PullValsForArg(self.Test_Args,"supplyCap",system.System_Name)
                self.assertEqual(expectedCosts.__len__(),expectedSupplyNums.__len__())
                expectedTotal = 0
                for cost,supply in zip(expectedCosts,expectedSupplyNums):
                    expectedTotal += (cost * supply)
                self.assertAlmostEqual(expectedTotal,system.Total_Cost)
#------------------------------------------------------------------------------
    def test_System_Item_Costs(self):
        '''
        Test that we get back the expected list of costs for items sold in a system
        '''
        for system in self.Test_Systems:
            with self.subTest(sysName=system.System_Name):
                expectedItemCosts = self.__PullValsForArg(self.Test_Args,"itemCost",system.System_Name)
                self.assertListEqual(expectedItemCosts,system.Item_Costs)
#------------------------------------------------------------------------------
    def test_System_Item_Names(self):
        #TODO:  Test failed once with item lists of different length
        #           Same item appeared twice in system list but only once in args list
        for system in self.Test_Systems:
            with self.subTest(sysName=system.System_Name):
                expectedItemNames = self.__PullValsForArg(self.Test_Args,"itemName",system.System_Name)
                self.assertListEqual(expectedItemNames,system.Item_Names)
#------------------------------------------------------------------------------
    def test_System_Item_Counts(self):
        for system in self.Test_Systems:
            with self.subTest(sysName=system.System_Name):
                expectedItemCounts = self.__PullValsForArg(self.Test_Args,"avgSupply",system.System_Name)
                self.assertListEqual(expectedItemCounts,system.Item_Supply_Counts)
#------------------------------------------------------------------------------
    def test_System_Items(self):
        '''
        Test that item info in a system maintains form when pulling it back out
        '''
        for system in self.Test_Systems:
            with self.subTest(sysName=system.System_Name):
                sameSystems = [args for args in self.Test_Args if args["systemName"] == system.System_Name]
                for args in sameSystems:
                    with self.subTest(i=args["systemIndex"]):
                        itemInfo = (args["itemName"],args["itemCost"],args["avgSupply"],args["supplyCap"])
                        self.assertIn(itemInfo,system.Items_Info)
#------------------------------------------------------------------------------
    def test_System_Total_Supply(self):
        for system in self.Test_Systems:
            with self.subTest(sysName=system.System_Name):
                expectedTotal = sum(self.__PullValsForArg(self.Test_Args,"supplyCap",system.System_Name))
                self.assertAlmostEqual(expectedTotal,system.Max_Supply)
#------------------------------------------------------------------------------
    def test_System_Permit(self):
        for system in self.Test_Systems:
            with self.subTest(sysName = system.System_Name):
                #Only check the first instance of the system in the args list, adding items does not change the permit req for a system
                expectedPermitReq = self.__PullValsForArg(self.Test_Args,"permit",system.System_Name)[0]
                self.assertTrue(system.Needs_Permit == expectedPermitReq)                
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#Test properties cannot be set
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    def assertSystemsEqual(self,system1,system2):
        '''
        Custom assert to test system equality on the following:
        system name, station names, item names, item costs, item supplies, total cost

        ignoring system distances and station distances because if all else is equal we can figure
        out and wrongness by looking in game.
        '''
        #TODO:  Decide if this should be here and fail on first assert, or return a custom assert message with no specifics, or have a real long/ugly thing going on with subtests
        #       Maybe this isn't even needed?
        self.assertEqual(system1.System_Name,system2.System_Name)
        self.assertSetEqual(set(system1.Station_Names),set(system2.Station_Names))
        self.assertSetEqual(set(system1.Item_Names),set(system2.Item_Names))
        self.assertSetEqual(set(system1.Item_Costs),set(system2.Item_Costs))
        self.assertSetEqual(set(system1.Item_Supply_Counts),set(system2.Item_Supply_Counts))
        self.assertAlmostEqual(system1.Total_Cost,system2.Total_Cost)
#------------------------------------------------------------------------------
    def __PullValsForArg(self,argsDictList,argToPull,systemName):
        '''
        Return a list of values representing the type of argToPull from all args for systems with systemName
        '''
        return [args[argToPull] for args in argsDictList if args["systemName"] == systemName]
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
def CreateEDSystemArgsList(numToCreate: int) -> list:
    '''
    Returns dicts of valid arguments for creating an EDSystem
    '''
    validSystemNames,validStationNames,validItemNames = [],[],[]

    with open("systems.txt") as systemNames:
        validSystemNames = systemNames.read().split()
    with open("stations.txt") as stationNames:
        validStationNames = stationNames.read().split()
    with open("items.txt") as itemNames:
        validItemNames = itemNames.read().split()
        
    argsDictList = []
    for i in range(numToCreate):
        systemName = ' '.join(random.choice(validSystemNames) for _ in range(random.randint(1,2)))
        stationName = ' '.join(random.choice(validStationNames) for _ in range(2))
        index = i
        supplyCap = random.randint(1,15)
        avgSupply = supplyCap
        itemCost = random.randrange(7000)
        itemName = ' '.join(random.choice(validItemNames) for _ in range(random.randint(2,3)))
        distToStation = random.randrange(10000)
        permitReq = (random.randrange(100)%10 == 0)

        #TODO: Maybe at some point have this actually have values instead of 0 all
        distToOthers = [0 for _ in range(numToCreate)]

        #Check for and remove/come up with another station name if a given name is already in a system
        stationsForSystem = [args["stationName"] for args in argsDictList if args["systemName"] == systemName]
        while stationName in stationsForSystem:
            stationName = ' '.join(random.choice(validStationNames) for _ in range(2))
        
        argsDict = {"supplyCap":supplyCap,
                     "avgSupply":avgSupply,
                     "itemCost":itemCost,
                     "itemName":itemName,
                     "distToStation":distToStation,
                     "stationName":stationName,
                     "systemName":systemName,
                     "systemIndex":index,
                     "distToOthers":distToOthers,
                     "permit":permitReq}
        argsDictList.append(argsDict)
    
    return argsDictList
#------------------------------------------------------------------------------
def CreateSystemsFromParams(paramsList: list) -> list:
    '''
    "Factory" whatever for making EDSystems to use in testing
    '''
    generatedSystems = []
    for args in paramsList:
        currentSystem = EDSystem(**args)
        if generatedSystems.count(currentSystem) != 0:
            for system in generatedSystems:
                if system == currentSystem:
                    system.AddRares(currentSystem)
        else:
            generatedSystems.append(currentSystem)
    return generatedSystems
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()