__author__ = 'Ian'
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class EDSystem( object ):
#------------------------------------------------------------------------------
    '''
    TODO:  Getters/Setters instead of public whatevers
    '''
    def __init__(self, supplyCap: float, avgSupply: float, itemCost: float, itemName: str, distToStation: float,
                       stationName: str, systemName: str, stationIndex: int, distToOthers: list, permit: bool):
        self.Max_Supply = supplyCap # Float
        self.Supply_Numbers = [avgSupply] # Float
        self.Costs = [itemCost] # Int
        self.Items = [itemName] # String
        self.Station_Distances = [distToStation] # Float
        self.Station_Names = [stationName] # String
        self.System_Name = systemName # String
        self.Index = stationIndex # Int
        self.System_Distances = distToOthers # List of Floats
        self.Location = dict(x=0, y=0, z=0)
        self.PermitReq = permit
#------------------------------------------------------------------------------
    def AddRares(self, other):
        self.Supply_Numbers.extend(other.Supply_Numbers)
        self.Costs.extend(other.Costs)
        self.Items.extend(other.Items)
        self.Max_Supply += other.Max_Supply
        if self.Station_Names != other.Station_Names:
            self.Station_Names.extend(other.Station_Names)
            self.Station_Distances.extend(other.Station_Distances)
#------------------------------------------------------------------------------
    def __str__(self):
        strBuilder = []
        if self.PermitReq:
            #return str.format("(P){0}({1}): {2} @ {3}cr (~{4})", self.System_Name,''.join(self.Station_Names),self.Items, self.Costs, self.Max_Supply)
            strBuilder.append("(P)")
        
        strBuilder.append("{0}(".format(self.System_Name))
        for station in self.Station_Names:
            strBuilder.append("{0}".format(station))
            if station != self.Station_Names[-1]:
                strBuilder.append(", ")
        strBuilder.append("): {")
        for i in range(self.Items.__len__()):
            strBuilder.append("{0} - {1}cr".format(self.Items[i],self.Costs[i]))
            if i != self.Items.__len__() - 1:
                strBuilder.append(", ")
        strBuilder.append("}} (~{0})".format(self.Max_Supply))
            
        #else:
        #    return str.format("{0}({1}): {2} @ {3}cr (~{4})", self.System_Name,''.join(self.Station_Names),self.Items, self.Costs, self.Max_Supply)
        return ''.join(strBuilder)
        
#------------------------------------------------------------------------------
    def __key(self):
        '''
        All stations/rares in a system will count as one EDSystems
        '''
        return self.System_Name
#------------------------------------------------------------------------------  
    def __hash__(self):
        '''
        Use the index for hash since it is unique to each entry
        '''
        return hash(self.Index)
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
