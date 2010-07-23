# -*- coding: utf-8 -*-
'''
Created on Mar 30, 2010

@author: ivan
'''

import gtk
from foobnix.util import LOG

class PrefListModel():
    POS_NAME = 0
    def __init__(self, widget, prefListMap):
        self.widget = widget
        self.prefListMap = prefListMap
        self.current_list_model = gtk.ListStore(str)
        renderer = gtk.CellRendererText()
        renderer.connect('edited', self.editRow)        
        renderer.set_property('editable', True)
        
        column = gtk.TreeViewColumn(_("My play lists"), renderer, text=0, font=2)
        column.set_resizable(True)
        widget.append_column(column)
        
        widget.set_model(self.current_list_model)
               
    
    def removeSelected(self):
        selection = self.widget.get_selection()
        selected = selection.get_selected()[1]
        if selected:                
            self.current_list_model.remove(selected)
        
    
    def editRow(self, w, event, value):
        beforeRename = unicode(self.getSelected())
        
        if value:
            i = self.getSelectedIndex()
            if i > 0 and not self.isContain(value):                                        
                self.current_list_model[i][self.POS_NAME] = value
                
                """copy songs with new name"""
                LOG.info("beforeRename ", beforeRename, self.prefListMap.keys())
                datas = self.prefListMap[beforeRename]
                LOG.info(datas)
                del self.prefListMap[beforeRename]
                self.prefListMap[value] = datas
    
    def getSelectedIndex(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected()
        if selected:
            i = model.get_string_from_iter(selected)        
            if i.find(":") == -1:
                LOG.info("Selected index is " , i)
                return int(i)
        return None
    
    def isContain(self, name):
        for i in xrange(len(self.current_list_model)):
            if str(self.current_list_model[i][self.POS_NAME]) == name:
                return True            
        return False     
        
    
    def getSelected(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected()
        
        if selected:            
            return model.get_value(selected, self.POS_NAME)
        else:
            return None
    
    def clear(self):
        self.current_list_model.clear()    
    
    def append(self, name):
        self.current_list_model.append([name])
                
