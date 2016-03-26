import unittest
from routecalc import RouteCalc
from edsystem import EDSystem
from edrareroute import EDRareRoute
import main

class Test_TestingRouteCalc(unittest.TestCase):
    def setUp(self):
        self.All_Systems = main.ReadSystems('RareGoods.csv')
        return super().setUp()

    def test_2(self):
        self.assertEqual(2,2)

if __name__ == '__main__':
    unittest.main()
