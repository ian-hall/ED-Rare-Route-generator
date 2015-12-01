__author__ = 'Ian'
class EDSystem( object ):
#------------------------------------------------------------------------------
    '''
    TODO:  pretty printing so you don't see the braces around the lists
    '''
    def __init__(self, supplyCap, avgSupply, itemCost, itemName, distToStation,
                       stationName, systemName, stationIndex, distToOthers: [], permit: bool):
        self.Max_Supply = supplyCap # Float
        self.Supply = [avgSupply] # Float
        self.Cost = [itemCost] # Int
        self.Items = [itemName] # String
        self.Station_Distance = [distToStation] # Float
        self.Station_Name = [stationName] # String
        self.System_Name = systemName # String
        self.Index = stationIndex # Int
        self.System_Distances = distToOthers # List of Floats
        self.Location = dict(x=0, y=0, z=0)
        self.PermitReq = permit
#------------------------------------------------------------------------------
    def __str__(self):
        return str.format("{0}({1}): {2} @ {3}cr (~{4})", self.System_Name,self.Station_Name,self.Items, self.Cost, self.Max_Supply)
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
    def AddRares(self, newRares: 'EDSystem'):
        self.Supply.extend(newRares.Supply)
        self.Cost.extend(newRares.Cost)
        self.Items.extend(newRares.Items)
        self.Max_Supply += newRares.Max_Supply
        if self.Station_Name != newRares.Station_Name:
            self.Station_Name.extend(newRares.Station_Name)
            self.Station_Distance.extend(newRares.Station_Distance)
#------------------------------------------------------------------------------
###############################################################################
#------------------------------------------------------------------------------
class DisplayLocation(object):
#------------------------------------------------------------------------------
    def __init__(self, col, row, name = None):
        self.Col = col
        self.Row = row
        self.System_Name = name
#------------------------------------------------------------------------------
    def __eq__(self, other):
        return (self.Col == other.Col) and (self.Row == other.Row)
#------------------------------------------------------------------------------
    def __str__(self):
        return "{0:>17}: ({1},{2})".format(self.System_Name,self.Col,self.Row)
#------------------------------------------------------------------------------
    def __hash__(self):
        return hash((self.Col,self.Row))
