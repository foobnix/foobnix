'''
Created on Mar 11, 2010

@author: ivan
'''
from foobnix.model.entity import SongBean, EntityBean
class VirturalLIstCntr():    
    def __init__(self):
        self.items = []
        self.items.append(SongBean("Demo", "path", type=EntityBean.TYPE_MUSIC_URL))        
                       
    def get_items(self):
        return self.items

    def append(self, item):
        self.items.append(item)
