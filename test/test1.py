'''
Created on Mar 2, 2010

@author: ivan
'''
class User:
    def __init__(self):
        self.name = "Gp"
    
    def _get_name(self):
        return self.name
    
    def some(self, name):
        assert type(name) in (long, str)
        
    
    kane = property(_get_name)


u = User()
print u.kane

list = [1, 2, 4, 8, 2]
list1 = [3, 4, 1, 2]


print sorted(list) + sorted(list1) 

