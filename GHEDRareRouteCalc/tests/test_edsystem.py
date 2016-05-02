from edsystem import EDSystem
import unittest
import random
import string
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class Test_EDSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.All_Systems = CreateEDSystems(500)
#------------------------------------------------------------------------------
    def test_System(self):
        self.fail("Not implemented")
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
        with self.assertRaises(Exception,msg="missing systemName"):
            testSystem = EDSystem(supplyCap,avgSupply,itemCost,itemName,distToStation,stationName,index,distToOthers,permitReq)
        
#------------------------------------------------------------------------------
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
