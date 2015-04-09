from edsystem import EDSystem
class EDSystemPair(object):
    def __init__(self,s1: EDSystem,s2: EDSystem,distance: float):
        self.S1 = s1
        self.S2 = s2
        self.Distance = distance
   
    def __str__(self):
        return "{{{0},{1}}} -> {2:8G}".format(self.S1.System_Name,self.S2.System_Name,self.Distance)


