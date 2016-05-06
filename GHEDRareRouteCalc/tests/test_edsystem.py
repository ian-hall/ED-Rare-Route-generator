from edsystem import EDSystem
import unittest
import random
import string
import itertools
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class Test_EDSystem(unittest.TestCase):
    #TODO: one assert per test
#------------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.Test_Systems = CreateEDSystems(500)
#------------------------------------------------------------------------------
    def setUp(self):
        self.Test_Params = CreateEDSystemParamList(100)
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
    def test_System_AddRares(self):
        systemName1 = "test system 1"
        stationName1 = "test station 1"
        index1 = 0
        supplyCap1 = 12
        avgSupply1 = 10
        itemCost1 = 400
        itemName1 = "test item 1"
        distToStation1 = 219

        systemName2 = "test system 2"
        stationName2 = "test station 2"
        index2 = 1
        supplyCap2 = 7
        avgSupply2 = 4
        itemCost2 = 1400
        itemName2 = "test item 2"
        distToStation2 = 420

        distToOthers = [0]
        permitReq = False

        origSystem = EDSystem(supplyCap1,avgSupply1,itemCost1,itemName1,distToStation1,stationName1,systemName1,index1,distToOthers,permitReq)
        testSys_Same_SysName = EDSystem(supplyCap2,avgSupply2,itemCost2,itemName2,distToStation2,stationName2,systemName1,index2,distToOthers,permitReq)
        origSystem.AddRares(testSys_Same_SysName)
        testSys_Same_SysName.AddRares(origSystem)

        expectedTotalCost = itemCost1 + itemCost2
        self.assertIn(itemName2,origSystem.Item_Names)
        self.assertIn(itemCost2,origSystem.Item_Costs)
        self.assertAlmostEqual(origSystem.Total_Cost,expectedTotalCost)
        self.assertIn(stationName2,origSystem.Station_Names)
        self.assertIn(distToStation2,origSystem.Station_Distances)

        origSystem = EDSystem(supplyCap1,avgSupply1,itemCost1,itemName1,distToStation1,stationName1,systemName1,index1,distToOthers,permitReq)
        testSys_Diff_SysName = EDSystem(supplyCap2,avgSupply2,itemCost2,itemName2,distToStation2,stationName2,systemName2,index2,distToOthers,permitReq)
        with self.assertRaises(Exception):
            origSystem.AddRares(testSys_Diff_SysName)
#------------------------------------------------------------------------------
    def test_System_AddRares_Item_Names(self):
        '''
        Test that AddRares is actually... adding rares to a system
        '''
        squishedSystems = []
        for args in self.Test_Params:
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
        '''
        Test that AddRares is actually... adding rares to a system
        '''
        squishedSystems = []
        for args in self.Test_Params:
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
        '''
        Test that AddRares is actually... adding rares to a system
        '''
        squishedSystems = []
        for args in self.Test_Params:
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
        '''
        Test that AddRares is actually... adding rares to a system
        '''
        squishedSystems = []
        for args in self.Test_Params:
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
        '''
        Test that AddRares is actually... adding rares to a system
        '''
        squishedSystems = []
        for args in self.Test_Params:
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
    def test_System_TotalCost(self):
        '''
        Test that we are getting back the expected total cost of items sold in a system
        '''
        for system in self.Test_Systems:
            with self.subTest(system=system):
                expectedTotal = sum(system.Item_Costs)
                self.assertAlmostEqual(expectedTotal,system.Total_Cost)
#------------------------------------------------------------------------------
    def test_System_ItemCosts(self):
        '''
        Test that we get back the expected list of costs for items sold in a system
        '''
        pass
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
def CreateEDSystemParamList(numToCreate: int) -> list:
    '''
    Returns dicts of valid paramaters for creating an EDSystem
    '''
    validSystemNames,validStationNames,validItemNames = [],[],[]

    with open("systems.txt") as systemNames:
        validSystemNames = systemNames.read().split()
    with open("stations.txt") as stationNames:
        validStationNames = stationNames.read().split()
    with open("items.txt") as itemNames:
        validItemNames = itemNames.read().split()
        
    paramsList = []
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
        paramDict = {"supplyCap":supplyCap,
                     "avgSupply":avgSupply,
                     "itemCost":itemCost,
                     "itemName":itemName,
                     "distToStation":distToStation,
                     "stationName":stationName,
                     "systemName":systemName,
                     "systemIndex":index,
                     "distToOthers":distToOthers,
                     "permit":permitReq}
        paramsList.append(paramDict)
    
    return paramsList
#------------------------------------------------------------------------------
def CreateEDSystems(numToCreate: int) -> list:
    '''
    "Factory" whatever for making EDSystems to use in testing
    '''
    '''
    validSystemNames,validStationNames,validItemNames = [],[],[]

    with open("systems.txt") as systemNames:
        validSystemNames = systemNames.read().split()
    with open("stations.txt") as stationNames:
        validStationNames = stationNames.read().split()
    with open("items.txt") as itemNames:
        validItemNames = itemNames.read().split()
        
    generatedSystems = []
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
    '''
    generatedSystems = []
    paramsList = CreateEDSystemParamList(numToCreate)
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