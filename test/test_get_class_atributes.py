'''
Created on Mar 14, 2010

@author: ivan
'''
class GetAttributes:
    special = "special"
    def __init__(self):
        self.a = "A1"
        self.b = "B1"
    
attr = GetAttributes()
print attr.a
print attr.b
print attr.special
print dir(attr)
print getattr(attr, "a")

for i in dir(attr):
    if not i.startswith("__"):
        print i, getattr(attr,i)

