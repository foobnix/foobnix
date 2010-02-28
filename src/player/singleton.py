'''
Created on Feb 28, 2010

@author: ivan
'''
from confguration import FoobNixConf

FoobNixConf().mediaLibraryPath="/Book"
FoobNixConf().save()
print FoobNixConf().mediaLibraryPath 
