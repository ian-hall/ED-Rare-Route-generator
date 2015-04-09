__author__ = 'Ian'
import re

class EDSystem( object ):
    '''
    TODO: make this not as bad
    '''
    def __init__(self, element_list: [9]):
        EDSystem.__Validate(element_list)
        self.Max_Supply = element_list[0] # Float
        self.Supply = element_list[1] # Float
        self.Cost = element_list[2] # Int
        self.Items = element_list[3] # String
        self.Station_Distance = element_list[4] # Float
        self.Station_Name = element_list[5] # String
        self.System_Name = element_list[6] # String
        self.Index = element_list[7] # Int
        self.System_Distances = element_list[8] # List of Floats

    def __Validate(element_list):
        #Max supply [0]
        if element_list[0] == 'ND':
            element_list[0] = 1
        else:
            tempMax = element_list[0].split('-')
            for i in range(0,tempMax.__len__()):
                tempMax[i] = int(re.sub("[^0-9]", "", tempMax[i]))
            element_list[0] = sum(tempMax)/len(tempMax)

        #Avg supply [1]
        if element_list[1] == 'ND':
            element_list[1] = 1
        else:
            tempSupply = element_list[1].split('-')
            for i in range(0,tempSupply.__len__()):
                tempSupply[i] = float(re.sub("[^0-9]", "", tempSupply[i]))
            element_list[1] = sum(tempSupply)/len(tempSupply)

        #Cost [2]
        element_list[2] = int(re.sub("[^0-9]", "", element_list[2]))

        #Station_Distance [4]
        #If it contains ly, convert to ls by 31,557,600 * x
        multFactor = 1;
        if 'ly' in element_list[4].lower():
            multFactor = 31557600
        element_list[4] = float(re.sub("[^0-9.]", "", element_list[4])) * multFactor

        #System_Distances [8]
        for i in range(0,element_list[8].__len__()):
            element_list[8][i] = float(element_list[8][i])

    def __str__(self):
        return str.format("{0}({1}({2}ls)): {3} @ {4}cr (~{5})", self.System_Name,self.Station_Name,self.Station_Distance,self.Items, self.Cost, self.Supply)

    def __key(self):
        '''
        Use system/station name for key because we want stations that sell
        multiple rares to be treated as one entry. 
        '''
        return (self.System_Name,self.Station_Name)
    
    def __hash__(self):
        '''
        Use the index for hash since it is unique to each entry
        '''
        return hash(self.Index)

    def __eq__(self, other):
        return self.__key() == other.__key()