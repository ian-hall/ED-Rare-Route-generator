from edsystem import EDSystem
import unittest
import random
import string
import itertools
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class Test_EDSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.All_Systems = CreateEDSystems(500)
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
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
def CreateEDSystems(numToCreate: int) -> list:
    '''
    "Factory" whatever for making EDSystems to use in testing
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

        currentSystem = EDSystem(supplyCap,avgSupply,itemCost,itemName,distToStation,stationName,systemName,index,distToOthers,permitReq)
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