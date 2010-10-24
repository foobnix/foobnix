#-*- coding: utf-8 -*-
'''
Created on 24 окт. 2010

@author: ivan
'''
import gtk
from foobnix.eq.eq_controller import EqController

if __name__ == '__main__':
    
    
    eq = EqController()
    eq.on_load()
    
    gtk.main()
