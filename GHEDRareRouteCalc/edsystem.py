__author__ = 'Ian'
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class EDSystem( object ):
#------------------------------------------------------------------------------
    def __init__(self, supplyCap: float, avgSupply: float, itemCost: float, itemName: str, distToStation: float,
                       stationName: str, systemName: str, systemIndex: int, distToOthers: list, permit: bool):
        
        self.__Max_Supply = supplyCap # Float
        self.__Supply_Numbers = [avgSupply] # Float
        self.__Costs = [itemCost] # Int
        self.__Items = [itemName] # String
        self.__Station_Distances = [distToStation] # Float
        self.__Station_Names = [stationName] # String
        self.__System_Name = systemName # String
        self.__Index = systemIndex # Int
        self.__System_Distances = distToOthers # List of Floats
        self.__Permit_Req = permit 
        self.__Location = dict(x=0, y=0, z=0)
#------------------------------------------------------------------------------
    @property
    def Total_Cost(self) -> int:
        return sum(self.__Costs)
#------------------------------------------------------------------------------
    @property
    def Max_Supply(self) -> float:
        return self.__Max_Supply
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
    #TODO: Maybe a better way to get location so it can't be set
    @property
    def Location(self) -> dict:
        return self.__Location
#------------------------------------------------------------------------------
    @property
    def Needs_Permit(self) -> bool:
        return self.__Permit_Req
#------------------------------------------------------------------------------
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
    def GetDistanceTo(self, next) -> float:
        return self.__System_Distances[next.__Index]
#------------------------------------------------------------------------------
    def AddRares(self, other):
        self.__Supply_Numbers.extend(other.__Supply_Numbers)
        self.__Costs.extend(other.__Costs)
        self.__Items.extend(other.__Items)
        self.__Max_Supply += other.Max_Supply
        if self.__Station_Names != other.__Station_Names:
            self.__Station_Names.extend(other.__Station_Names)
            self.__Station_Distances.extend(other.__Station_Distances)
#------------------------------------------------------------------------------
    def __str__(self):
        strBuilder = []
        if self.__Permit_Req:
            strBuilder.append("(P)")
        
        strBuilder.append("{0}(".format(self.__System_Name))
        for station in self.__Station_Names:
            strBuilder.append("{0}".format(station))
            if station != self.__Station_Names[-1]:
                strBuilder.append(", ")
        strBuilder.append("): {")
        for i in range(self.__Items.__len__()):
            strBuilder.append("{0} - {1}cr".format(self.__Items[i],self.__Costs[i]))
            if i != self.__Items.__len__() - 1:
                strBuilder.append(", ")
        strBuilder.append("}} ({0}T)".format(self.__Max_Supply))

        return ''.join(strBuilder)
        
#------------------------------------------------------------------------------
    def __key(self):
        '''
        All stations/rares in a system will count as one EDSystems
        '''
        return self.__System_Name
#------------------------------------------------------------------------------  
    def __hash__(self):
        '''
        Use the index for hash since it is unique to each entry
        '''
        return hash(self.__Index)
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
        return "{0:>17}: ({1},{2})".format(self.System_Name,self.Col,self.Row)
#------------------------------------------------------------------------------
    def __eq__(self, other):
        return (self.Col == other.Col) and (self.Row == other.Row)
#------------------------------------------------------------------------------
    def __hash__(self):
        return hash((self.Col,self.Row))
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
