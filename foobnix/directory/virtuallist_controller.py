'''
Created on Mar 11, 2010

@author: ivan
'''
from foobnix.model.entity import CommonBean
class VirturalLIstCntr():    
    def __init__(self):
        self.items = []
        self.items.append(CommonBean("Demo", "path", type=CommonBean.TYPE_MUSIC_URL))        
                       
    def get_items(self):
        return self.items

    def append(self, item):
        self.items.append(item)
