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
