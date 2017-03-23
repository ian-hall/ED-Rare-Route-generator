__author__ = 'Ian'
from collections import defaultdict
import re
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class EDSystem( object ):
#------------------------------------------------------------------------------
    def __init__(self):
        self.__Is_Initialized = False
#------------------------------------------------------------------------------
    @classmethod
    def Initialize_System(cls, item, idx, alloc, system, permit, port, illeg, cost, dst, x, y, z):
        
        if( (alloc is None) or (cost is None) or (item is None) or (dst is None) or
            (port is None) or (system is None) or (idx is None) or (permit is None) ):
            raise Exception("Values cannot be None") 
          
        newSystem = EDSystem()
        newSystem.__Supply_Numbers = [float(alloc)] if alloc is not "" else [-1]
        newSystem.__Costs = [int(cost)] if cost is not "" else [-1]
        newSystem.__Items = [item]
        newSystem.__Station_Distances = [float(dst)]
        newSystem.__Station_Names = [port]
        newSystem.__System_Name = system
        newSystem.__Index = int(idx)
        newSystem.__Permit_Req = permit 
        newSystem.__Location = dict(x=float(x), y=float(y), z=float(z))  
        #newSystem.__Distances_Dict = defaultdict(lambda: -1)
        newSystem.__Is_Initialized = True
        return newSystem  
#------------------------------------------------------------------------------
    @property
    def Total_Cost(self) -> float:
        '''
        A number that represents the total cost of buying the max number of rare goods in a system.
        '''
        total = 0
        for i in range(len(self.__Items)):
            cost = self.__Costs[i]
            supply = self.__Supply_Numbers[i]
            total += (cost * supply)
        return total
#------------------------------------------------------------------------------
    @property
    def Is_Initialized(self) -> bool:
        return self.__Is_Initialized
#------------------------------------------------------------------------------
    @property
    def Max_Supply(self) -> float:
        return sum(self.__Supply_Numbers)
#------------------------------------------------------------------------------
    @property
    def Items_Info(self) -> list:
        '''
        Returns a list with elements (item name, item cost, item supply)
        '''
        return list(zip(self.__Items,self.__Costs,self.__Supply_Numbers))
#------------------------------------------------------------------------------
    @property
    def Item_Names(self) -> list:
        return [name for name in self.__Items]
#------------------------------------------------------------------------------
    @property
    def Item_Costs(self) -> list:
        return [cost for cost in self.__Costs]
#------------------------------------------------------------------------------
    @property
    def Item_Supply_Counts(self) -> list:
        return [supply for supply in self.__Supply_Numbers]
#------------------------------------------------------------------------------
    @property
    def Station_Names(self) -> list:
        return [name for name in self.__Station_Names]
#------------------------------------------------------------------------------
    @property
    def Index(self) -> int:
        return self.__Index
#------------------------------------------------------------------------------
    @property
    def System_Name(self) -> str:
        return self.__System_Name
#------------------------------------------------------------------------------
    @property
    def Station_Distances(self) -> list:
        return [dist for dist in self.__Station_Distances]
#------------------------------------------------------------------------------
#    @property
#    def Distances_Dict(self) -> dict:
#        return dict(self.TestingDistances)
##------------------------------------------------------------------------------
#    @Distances_Dict.setter
#    def Distances_Dict(self,distances:dict):
#        self.__Distances_Dict = dict(distances)
#------------------------------------------------------------------------------
    @property
    def Location(self) -> dict:
        return dict(self.__Location)
#------------------------------------------------------------------------------
    @property
    def Needs_Permit(self) -> bool:
        return self.__Permit_Req
#------------------------------------------------------------------------------
    #Maybe not the best use of a property
    @property
    def Short_Str(self) -> str:
        strBuilder = []
        if self.__Permit_Req:
            strBuilder.append("(P) ")
        strBuilder.append("{0} (".format(self.__System_Name))
        for station in self.__Station_Names:
            strBuilder.append("{0}".format(station))
            if station != self.__Station_Names[-1]:
                strBuilder.append(", ")
        strBuilder.append(")")
        return "".join(strBuilder)
#------------------------------------------------------------------------------
    def GetDistanceTo(self, other) -> float:
        '''
        Calculate the distance to another system based on the x,y,z values.
        '''
        #TODO: Maybe have main calculate all distances when reading in the systems
        #      There is noticeable slow down doing this, of course
        import numpy as np
        localValues = np.array([self.__Location['x'], self.__Location['y'], self.__Location['z']])
        otherValues = np.array([other.__Location['x'], other.__Location['y'], other.__Location['z']])
        return np.linalg.norm(localValues-otherValues)
#------------------------------------------------------------------------------
    def AddRares(self, other):
        '''
        Add rare goods to a system. This will add duplicates if the same item is in self and other.
        '''
        if self.__System_Name != other.__System_Name:
            raise Exception("Can only add rares to the same system")

        for i in range(len(other.__Items)):
            if other.__Items[i] not in self.__Items:
                self.__Items.append(other.__Items[i])
                self.__Costs.append(other.__Costs[i])
                self.__Supply_Numbers.append(other.__Supply_Numbers[i])
                        
        for i in range(len(other.__Station_Names)):
            if other.__Station_Names[i] not in self.__Station_Names:
                self.__Station_Names.append(other.__Station_Names[i])
                self.__Station_Distances.append(other.__Station_Distances[i])
#------------------------------------------------------------------------------
    def CalculateDistances(self,systemList):
        #TODO: Maybe have main call this to set all distances at once into a dict
        import numpy as np
        localValues = np.array([self.__Location['x'], self.__Location['y'], self.__Location['z']])
        for other in systemList:
            distanceTo = np.array([other.__Location['x'], other.__Location['y'], other.__Location['z']])
            temp = np.linalg.norm(localValues-distanceTo)
            #print("{0} to {1} -> {2}".format(self.__System_Name, other.__System_Name,temp))           
#------------------------------------------------------------------------------
    def __str__(self):
        #TODO:  Mark stations/Items to identify where stuff is bought, or maybe group them together when printing.
        #           In game this doesn't matter much because rares are flagged in each station but for this it might be good
        strBuilder = []
        if self.__Permit_Req:
            strBuilder.append("(P)")
        
        strBuilder.append("{0} (".format(self.__System_Name))
        for station in self.__Station_Names:
            strBuilder.append("{0}".format(station))
            if station != self.__Station_Names[-1]:
                strBuilder.append(", ")
        strBuilder.append("): {")
        for i in range(len(self.__Items)):
            strBuilder.append("{0} - {1}cr".format(self.__Items[i],self.__Costs[i]))
            if i != len(self.__Items) - 1:
                strBuilder.append(", ")
        strBuilder.append("}} ({0}T)".format(self.Max_Supply))

        return ''.join(strBuilder)       
#------------------------------------------------------------------------------
    def __key(self):
        '''
        All stations/rares in a system will count as one EDSystems
        '''
        return self.__System_Name
#------------------------------------------------------------------------------  
    def __hash__(self):
        return hash(self.__key())
#------------------------------------------------------------------------------
    def __eq__(self, other):
        return self.__key() == other.__key()
#------------------------------------------------------------------------------    
###############################################################################
#------------------------------------------------------------------------------
class DisplayLocation(object):
#------------------------------------------------------------------------------
    def __init__(self, row, col, depth = 0, name = ""):
        self.Row = row
        self.Col = col
        self.Depth = depth
        self.System_Name = name
#------------------------------------------------------------------------------
    def __str__(self):
        return "{0:>17}: (c{1},r{2})".format(self.System_Name,self.Col,self.Row)
#------------------------------------------------------------------------------
    def __eq__(self, other):
        return (self.Col == other.Col) and (self.Row == other.Row) and (self.Depth == other.Depth)
#------------------------------------------------------------------------------
    def __hash__(self):
        return hash((self.Col,self.Row))
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
def TryFloat(val: str) -> bool:
    try:
        float(val)
        return True
    except:
        return False
#------------------------------------------------------------------------------