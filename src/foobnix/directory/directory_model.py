'''
Created on Mar 11, 2010

@author: ivan
'''
import gtk
import gobject
from foobnix.model.entity import CommonBean

class DirectoryModel():
    POS_NAME = 0
    POS_PATH = 1
    POS_FONT = 2
    POS_VISIBLE = 3
    POS_TYPE = 4
    POS_INDEX = 5
    POS_PARENT = 6
    POS_FILTER_CHILD_COUNT = 7
    
    def __init__(self, widget):
        self.widget = widget
        self.current_list_model = gtk.TreeStore(str, str, str, gobject.TYPE_BOOLEAN, str, int, str, str)
        renderer = gtk.CellRendererText()
        #renderer.connect('edited', self.editRow)
        
        #renderer.set_property('editable', True)

        
        print "ATTTR", renderer.get_property("attributes")
        
        
        column = gtk.TreeViewColumn(_("Title"), renderer, text=0, font=2)
        column.set_resizable(True)
        widget.append_column(column)

                
        filter = self.current_list_model.filter_new()
        filter.set_visible_column(self.POS_VISIBLE)
        widget.set_model(filter)
        
    
    
        
    def editRow(self, w, event, value):
        if value:
            selection = self.widget.get_selection()
            model, selected = selection.get_selected()
            print "VAlue", value          
            print selected
            i = model.get_string_from_iter(selected)
            print "I ", i
            if i.find(":") == -1:
                print i
                self.current_list_model[int(i)][self.POS_NAME] = value
           
        
    def append(self, level, bean):
        return self.current_list_model.append(level, [bean.name, bean.path, bean.font, bean.is_visible, bean.type, bean.index, bean.parent, bean.child_count])
        
    def clear(self):
        self.current_list_model.clear() 
    def getModel(self):
        return self.current_list_model
    
    def setModel(self, model):
        self.current_list_model = model
        
    def get_selected_bean(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected()
        return self._getBeanByIter(model, selected)   
    
    def deleteSelected(self):
        model, iter = self.widget.get_selection().get_selected()
        if iter:             
            model.remove(iter)

    def _getBeanByIter(self, model, iter):
        if iter:
            bean = CommonBean()
            bean.name = model.get_value(iter, self.POS_NAME)
            bean.path = model.get_value(iter, self.POS_PATH)            
            bean.font = model.get_value(iter, self.POS_FONT)
            bean.visible = model.get_value(iter, self.POS_VISIBLE)
            bean.type = model.get_value(iter, self.POS_TYPE)
            bean.index = model.get_value(iter, self.POS_INDEX)
            bean.parent = model.get_value(iter, self.POS_PARENT)
            bean.child_count = model.get_value(iter, self.POS_FILTER_CHILD_COUNT)                  
            return bean
        return None
    
    def getBeenByPosition(self, position):
        bean = CommonBean()        
        
        bean.name = self.current_list_model[position][ self.POS_NAME]
        bean.path = self.current_list_model[position][ self.POS_PATH]
        bean.type = self.current_list_model[position][ self.POS_TYPE]
        bean.visible = self.current_list_model[position][ self.POS_VISIBLE]
        bean.font = self.current_list_model[position][ self.POS_FONT]
        bean.parent = self.current_list_model[position][self.POS_PARENT]
        bean.child_count = self.current_list_model[position][self.POS_FILTER_CHILD_COUNT]
        return bean

    def getAllSongs(self):
        result = []
        for i in xrange(len(self.current_list_model)):
            been = self.getBeenByPosition(i)
            
            if been.type in [CommonBean.TYPE_MUSIC_FILE, CommonBean.TYPE_MUSIC_URL, CommonBean.TYPE_RADIO_URL]:                
                result.append(been)
        return result
        

    def getChildSongBySelected(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected()
        n = model.iter_n_children(selected)
        iterch = model.iter_children(selected)
        
        results = []
        
        for i in xrange(n):
            song = self._getBeanByIter(model, iterch)
            if song.type != CommonBean.TYPE_FOLDER:  
                results.append(self._getBeanByIter(model, iterch))
            iterch = model.iter_next(iterch)
        
        return results
        
        
    def filterByName(self, query):        
        if len(query.strip()) > 0:
            query = query.strip().decode("utf-8").lower()
            
            for line in self.current_list_model:
                name = str(line[self.POS_NAME]).lower()

                if name.find(query) >= 0:
                    print "FIND PARENT:", name, query
                    line[self.POS_VISIBLE] = True                    
                else:
                    find = False
                    child_count = 0;
                    for child in line.iterchildren():
                        name = str(child[self.POS_NAME]).decode("utf-8").lower()
                        if name.find(query) >= 0:
                            child_count += 1
                            print "FIND CHILD :", name, query
                            child[self.POS_VISIBLE] = True
                            line[self.POS_VISIBLE] = True
                            line[self.POS_FILTER_CHILD_COUNT] = child_count 
                            find = True
                            
                        else:
                            child[self.POS_VISIBLE] = False
                    if not find:
                        line[self.POS_VISIBLE] = False
                    else:
                        self.widget.expand_all()
                    
                        
        else:
            self.widget.collapse_all()
            for line in self.current_list_model:                
                line[self.POS_VISIBLE] = True
                for child in line.iterchildren():
                    child[self.POS_VISIBLE] = True
                
    

