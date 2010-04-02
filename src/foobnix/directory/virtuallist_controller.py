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
    
    def get_item_by_index(self, index):
        return self.items[index]

    def append(self, item):
        self.items.append(item)

    def getState(self):
        return self.items
    
    def setState(self, items):
        self.items = items
    
    def remove(self, index):
        if index > len(self.items):
            "INDEX TOO BIG"
            return 
        item = self.get_item_by_index(index)
        print "DELETE", item.name
        self.items.remove(item)
    
    def remove_with_childrens(self, index, parent=None):
        type = self.get_item_by_index(index).type
        print type
        if type not in [CommonBean.TYPE_FOLDER, CommonBean.TYPE_GOOGLE_HELP] :
            self.remove(index)
            return
        
        self.remove(index)
        size = len(self.items)
        for i in xrange(index, size):
            print "index" + str(i),
            print self.items[index].parent
            if self.items[index].parent == parent:
                return
            else:
                self.remove(index)
            
            
            
