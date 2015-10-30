﻿__author__ = 'Ian'
import re

class EDSystem( object ):
    '''
    TODO:  pretty printing so you don't see the braces around the lists
    '''
    def __init__(self, supplyCap, avgSupply, itemCost, itemName, distToStation,
                       stationName, systemName, stationIndex, distToOthers: []):
        self.Max_Supply = supplyCap # Float
        self.Supply = [avgSupply] # Float
        self.Cost = [itemCost] # Int
        self.Items = [itemName] # String
        self.Station_Distance = [distToStation] # Float
        self.Station_Name = [stationName] # String
        self.System_Name = systemName # String
        self.Index = stationIndex # Int
        self.System_Distances = distToOthers # List of Floats

    def __str__(self):
        return str.format("{0}({1}): {2} @ {3}cr (~{4})", self.System_Name,self.Station_Name,self.Items, self.Cost, self.Max_Supply)

    def __key(self):
        '''
        Use system/station name for key because we want stations that sell
        multiple rares to be treated as one entry. 
        '''
        return self.System_Name
    
    def __hash__(self):
        '''
        Use the index for hash since it is unique to each entry
        '''
        return hash(self.Index)

    def __eq__(self, other):
        return self.__key() == other.__key()
    
    def AddRares(self, newRares):
        self.Supply.extend(newRares.Supply)
        self.Cost.extend(newRares.Cost)
        self.Items.extend(newRares.Items)
        self.Max_Supply += newRares.Max_Supply
        if self.Station_Name != newRares.Station_Name:
            self.Station_Name.extend(newRares.Station_Name)
            self.Station_Distance.extend(newRares.Station_Distance)