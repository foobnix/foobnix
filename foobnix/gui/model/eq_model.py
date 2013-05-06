'''
Created on Oct 25, 2010

@author: ivan
'''
class EqModel():
    def __init__(self, id, name, preamp, values):
        self.id = id
        self.name = name
        self.preamp = preamp
        self.values = values
    
    def set_preamp(self, preamp):
        self.preamp = preamp
    
    def set_values(self, values):
        self.values = values