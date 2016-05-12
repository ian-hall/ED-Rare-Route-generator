__author__ = 'Ian'
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class EDSystem( object ):
    #TODO: Maybe a better way to do this?
    #      Also constructor args types don't seem to actually do any type checking, thanks python
    #      Also i never realized how bad this was with so many values being passed, but i just read from a csv file so ???
#------------------------------------------------------------------------------
    def __init__(self, supplyCap: float, avgSupply: float, itemCost: float, itemName: str, distToStation: float,
                       stationName: str, systemName: str, systemIndex: int, distToOthers: list, permit: bool):

        if( (supplyCap is None) or (avgSupply is None) or (itemCost is None) or (itemName is None) or (distToStation is None) or
            (stationName is None) or (systemName is None) or (systemIndex is None) or (distToOthers is None) or (permit is None) ):
            raise Exception("Values cannot be None") 
        
        if not isinstance(distToOthers,list):
            raise TypeError       

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
    def Items_Info(self) -> list:
        '''
        Returns a list with elements of for (item name, item cost, item supply)
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
    #TODO: Maybe a better way to get location so it can't be set
    @property
    def Location(self) -> dict:
        return self.__Location
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
        Get the distance from self to the other system. If the other system's index
        is not in the system distances list return -1
        '''
        if other.__Index < self.__System_Distances.__len__():
            return self.__System_Distances[other.__Index]
        else:
            return -1.0
#------------------------------------------------------------------------------
    def AddRares(self, other):
        '''
        Add rare goods to a system. This will add duplicates if the same good is in self and other.
        '''
        #TODO:  Change this to address the duplicates thing by looping through costs/supply/items and adding those not already in
        #           This assumes those all have the same length, which they should.
        if self.__System_Name != other.__System_Name:
            raise Exception("Can only add rares to the same system")

        for i in range(other.__Items.__len__()):
            if other.__Items[i] not in self.__Items:
                self.__Items.append(other.__Items[i])
                self.__Costs.append(other.__Costs[i])
                self.__Supply_Numbers.append(other.__Supply_Numbers[i])
                self.__Max_Supply += other.__Supply_Numbers[i]
                        
        for i in range(other.__Station_Names.__len__()):
            if other.__Station_Names[i] not in self.__Station_Names:
                self.__Station_Names.append(other.__Station_Names[i])
                self.__Station_Distances.append(other.__Station_Distances[i])

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
        Since Index refers to a system's index in the System_Distances list, this should be unique
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