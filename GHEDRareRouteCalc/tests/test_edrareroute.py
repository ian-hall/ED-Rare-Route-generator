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
        sysList2 = [val for val in sysList1]
        random.shuffle(sysList2)

        #Make sure these aren't equal, but I think shuffle will never return the same list??
        self.assertNotEqual(sysList1,sysList2,"shuffle didn't shuffle")

        splitRoute1 = EDRareRoute(sysList1,FitnessType.EvenSplit)
        farRoute1 = EDRareRoute(sysList1,FitnessType.Farthest)
        firstRoute1 = EDRareRoute(sysList1,FitnessType.FirstOver)

        self.assertNotEqual(splitRoute1,farRoute1)
        self.assertNotEqual(splitRoute1,firstRoute1)
        self.assertNotEqual(farRoute1,firstRoute1)


        splitRoute2 = EDRareRoute(sysList2,FitnessType.EvenSplit)
        farRoute2 = EDRareRoute(sysList2,FitnessType.Farthest)
        firstRoute2 = EDRareRoute(sysList2,FitnessType.FirstOver)

        self.assertNotEqual(splitRoute1,splitRoute2)
        self.assertNotEqual(farRoute1,farRoute2)
        self.assertNotEqual(firstRoute1,firstRoute2)
#------------------------------------------------------------------------------
    def test_Route_Eq(self):
        '''
        Test that routes with the same systems and fit type are equal
        '''
        sysList = random.choice(self.System_Lists)
        sysListCopy = [val for val in sysList]
        
        for name,fType in FitnessType.__members__.items():
            with self.subTest(fType=fType):
                testRoute1 = EDRareRoute(sysList,fType)
                testRoute2 = EDRareRoute(sysListCopy,fType)
                self.assertEqual(testRoute1,testRoute2)

        #splitRoute1 = EDRareRoute(sysList,FitnessType.EvenSplit)
        #splitRoute2 = EDRareRoute(sysListCopy,FitnessType.EvenSplit)
        #farRoute1 = EDRareRoute(sysList,FitnessType.Farthest)
        #farRoute2 = EDRareRoute(sysListCopy,FitnessType.Farthest)
        #firstRoute1 = EDRareRoute(sysList,FitnessType.FirstOver)
        #firstRoute2 = EDRareRoute(sysListCopy,FitnessType.FirstOver)

        #self.assertEqual(splitRoute1,splitRoute2)
        #self.assertEqual(farRoute1,farRoute2)
        #self.assertEqual(firstRoute1,firstRoute2)
#------------------------------------------------------------------------------
    def test_Route_Distance(self):
        sysList = random.choice(self.System_Lists)   
        self.fail("Not implemented")    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
