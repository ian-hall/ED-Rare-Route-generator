import main
import routecalc
from edrareroute import EDRareRoute, FitnessType, RouteType
from edsystem import EDSystem
import unittest
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class Test_EDRareRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.All_Systems = main.ReadSystems("RareGoods.csv")
#------------------------------------------------------------------------------
    def setUp(self):
        self.System_Lists = routecalc.GenerateSystemLists(50,14,self.All_Systems)
#------------------------------------------------------------------------------
    def test_A(self):
        self.fail("should probably do this sometime")
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
#------------------------------------------------------------------------------
