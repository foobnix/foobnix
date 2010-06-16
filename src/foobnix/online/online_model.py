'''
Created on Mar 16, 2010

@author: ivan
'''
from random import randint
from foobnix.util import LOG
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
'''
Created on Mar 11, 2010

@author: ivan
'''
import gtk
from foobnix.model.entity import CommonBean
class OnlineListModel:
    POS_ICON = 0
    POS_TRACK_NUMBER = 1
    POS_NAME = 2
    POS_PATH = 3
    POS_COLOR = 4
    POS_INDEX = 5
    POS_TYPE = 6
    POS_PARENT = 7
    POS_TIME = 8
    
    def __init__(self, widget):
        self.widget = widget
        self.current_list_model = gtk.ListStore(str, str, str, str, str, int, str, str,str)
               
        cellpb = gtk.CellRendererPixbuf()
        cellpb.set_property('cell-background', 'yellow')
        iconColumn = gtk.TreeViewColumn(_('Icon'), cellpb, stock_id=0, cell_background=4)
        iconColumn.set_fixed_width(5)
        
        descriptionColumn = gtk.TreeViewColumn(_('Artist - Title'), gtk.CellRendererText(), text=self.POS_NAME, background=self.POS_COLOR)
        descriptionColumn.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        descriptionColumn.set_resizable(True)
        
        timeColumn = gtk.TreeViewColumn(_('Time'), gtk.CellRendererText(), text=self.POS_TIME, background=self.POS_COLOR)
        timeColumn.set_fixed_width(5)
        timeColumn.set_min_width(5)
        
        empty = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=-1, background=self.POS_COLOR)
                
        widget.append_column(iconColumn)
        #widget.append_column(numbetColumn)
        widget.append_column(descriptionColumn)
        widget.append_column(timeColumn)
        widget.append_column(empty)
        
        widget.set_model(self.current_list_model)
    def get_size(self):
        return len(self.current_list_model)
    
    def get_all_beans(self):
        beans  =[]
        for i in xrange(self.get_size()):
            beans.append(self.getBeenByPosition(i))
        return beans
    
    def getBeenByPosition(self, position):
        bean = CommonBean()
        bean.icon = self.current_list_model[position][ self.POS_ICON]
        bean.tracknumber = self.current_list_model[position][ self.POS_TRACK_NUMBER]
        bean.name = self.current_list_model[position][ self.POS_NAME]
        bean.path = self.current_list_model[position][ self.POS_PATH]
        bean.color = self.current_list_model[position][ self.POS_COLOR]
        bean.index = self.current_list_model[position][ self.POS_INDEX]
        bean.type = self.current_list_model[position][ self.POS_TYPE]
        bean.parent = self.current_list_model[position][ self.POS_PARENT]
        bean.time = self.current_list_model[position][ self.POS_TIME]
        return bean  
    
    
    def get_random_bean(self):
        index = randint(0,self.get_size())
        return self.getBeenByPosition(index) 
    
    def getModel(self):
        return self.current_list_model

    def getSelectedBean(self):
        print self.widget
        selection = self.widget.get_selection()
        print selection
        model, selected = selection.get_selected()
        print model, selected
        if selected:
            bean = CommonBean()
            bean.icon = model.get_value(selected, self.POS_ICON)
            bean.tracknumber = model.get_value(selected, self.POS_TRACK_NUMBER)
            bean.name = model.get_value(selected, self.POS_NAME)
            bean.path = model.get_value(selected, self.POS_PATH)
            bean.color = model.get_value(selected, self.POS_COLOR)
            bean.index = model.get_value(selected, self.POS_INDEX)
            bean.type = model.get_value(selected, self.POS_TYPE)
            bean.parent = model.get_value(selected, self.POS_PARENT)
            bean.time = model.get_value(selected, self.POS_TIME)
            return bean                
    
    def clear(self):
        self.current_list_model.clear()
    
    def remove_selected(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected()
        self.current_list_model.remove(selected)
    
    def append(self, bean):   
        self.current_list_model.append([bean.icon, bean.tracknumber, bean.name, bean.path, bean.color, bean.index, bean.type, bean.parent, bean.time])

    def __del__(self, *a):
        print "del"
        
        
    def get_selected_index(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected()
        if selected:
            i = model.get_string_from_iter(selected)  
            #print "!!I", i      
            #if i.find(":") == -1:
            #return int(i)
            return int(i)
        return None    

    def repopulate(self, played_index):
        LOG.info("Selected index", played_index)
        list = self.get_all_beans()
        self.clear()        
        for i in xrange(len(list)):
            songBean = list[i]

            if not songBean.color:
                songBean.color = self.get_bg_color(i)

            songBean.name = songBean.getPlayListDescription()
            songBean.index = i

            if i == played_index:
                songBean.setIconPlaying()
                self.append(songBean)
            else:
                songBean.setIconNone()
                self.append(songBean)

    def get_bg_color(self, i):
        if i % 2 :
            return "#F2F2F2"
        else:
            return "#FFFFE5"        
