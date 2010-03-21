'''
Created on Mar 11, 2010

@author: ivan
'''
from foobnix.model.entity import CommonBean
class VirturalLIstCntr():    
    def __init__(self):
        self.items = []
                       
    def get_items(self):
        return self.items

    def append(self, item):
        self.items.append(item)

    def getState(self):
        return self.items
    
    def setState(self,items):
        self.items = items