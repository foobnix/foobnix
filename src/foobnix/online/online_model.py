'''
Created on Mar 16, 2010

@author: ivan
'''
from random import randint
from foobnix.util import LOG
import random
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
    
    POS_START_AT = 9
    POS_DURATION = 10
    POS_ID3 = 11
    POS_IMAGE = 12
    
    def __init__(self, widget):
        self.widget = widget
        self.current_list_model = gtk.ListStore(str, str, str, str, str, int, str, str, str, str, str, str, str)
               
        cellpb = gtk.CellRendererPixbuf()
        cellpb.set_property('cell-background', 'yellow')
        iconColumn = gtk.TreeViewColumn(None, cellpb, stock_id=0, cell_background=4)
        iconColumn.set_fixed_width(5)
        
        descriptionColumn = gtk.TreeViewColumn(_('Artist - Title'), gtk.CellRendererText(), text=self.POS_NAME, background=self.POS_COLOR)
        descriptionColumn.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        descriptionColumn.set_resizable(True)
        descriptionColumn.set_expand(True)
        
        number_column = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=self.POS_TRACK_NUMBER, background=self.POS_COLOR)
        number_column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        
        
        timeColumn = gtk.TreeViewColumn(_('Time'), gtk.CellRendererText(), text=self.POS_TIME, background=self.POS_COLOR)
        timeColumn.set_fixed_width(5)
        timeColumn.set_min_width(5)
        
        #empty = gtk.TreeViewColumn(None, gtk.CellRendererText(), text= -1, background=self.POS_COLOR)
                
        widget.append_column(iconColumn)
        widget.append_column(number_column)
        widget.append_column(descriptionColumn)
        widget.append_column(timeColumn)
        #widget.append_column(empty)
        
        widget.set_model(self.current_list_model)
    def get_size(self):
        return len(self.current_list_model)
    
    def get_all_beans(self):
        beans = []
        for i in xrange(self.get_size()):
            beans.append(self.getBeenByPosition(i))
        return beans
    
    def getBeenByPosition(self, position):
        if position < 0:
            position = 0
        if position >= self.get_size():
            position = 0
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
        bean.start_at = self.current_list_model[position][ self.POS_START_AT]
        bean.duration = self.current_list_model[position][ self.POS_DURATION]
        bean.id3 = self.current_list_model[position][ self.POS_ID3]
        bean.image = self.current_list_model[position][ self.POS_IMAGE]
        return bean  
    
    
    def get_random_bean(self):
        index = randint(0, self.get_size() - 1)
        return self.getBeenByPosition(index) 
    
    def getModel(self):
        return self.current_list_model

    def get_selected_bean(self):
        selection = self.widget.get_selection()
        model, paths = selection.get_selected_rows()

        if not paths:
            return None
        
        return self._get_bean_by_path(paths[0])
    
    def get_all_selected_beans(self):
        selection = self.widget.get_selection()
        model, paths = selection.get_selected_rows()
        if not paths:
            return None
        beans = []
        for path in paths:       
            selection.select_path(path)     
            bean = self._get_bean_by_path(path)
            beans.append(bean)
        return beans    
    
    def _get_bean_by_path(self, path):
        model = self.current_list_model
        iter = model.get_iter(path)
        if iter:
            bean = CommonBean()
            bean.icon = model.get_value(iter, self.POS_ICON)
            bean.tracknumber = model.get_value(iter, self.POS_TRACK_NUMBER)
            bean.name = model.get_value(iter, self.POS_NAME)
            bean.path = model.get_value(iter, self.POS_PATH)
            bean.color = model.get_value(iter, self.POS_COLOR)
            bean.index = model.get_value(iter, self.POS_INDEX)
            bean.type = model.get_value(iter, self.POS_TYPE)
            bean.parent = model.get_value(iter, self.POS_PARENT)
            bean.time = model.get_value(iter, self.POS_TIME)
            bean.start_at = model.get_value(iter, self.POS_START_AT)
            bean.duration = model.get_value(iter, self.POS_DURATION)
            bean.id3 = model.get_value(iter, self.POS_ID3)
            bean.image = model.get_value(iter, self.POS_IMAGE)
            return bean
        return None
                
    
    def clear(self):
        self.current_list_model.clear()
    
    def remove_selected(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected_rows()
        iters = [model.get_iter(path) for path in selected]
        LOG.debug("REMOVE:", iters)
        for iter in iters:
            model.remove(iter)
    
    def append(self, bean):
        """teplorary disable colors"""        
        self.current_list_model.append([bean.icon, bean.tracknumber, bean.name, bean.path, bean.color, bean.index, bean.type, bean.parent, bean.time, bean.start_at, bean.duration, bean.id3, bean.image])

    def __del__(self, *a):
        LOG.info("del")
        
        
    def get_selected_index(self):
        
        selection = self.widget.get_selection()
        #model, selected = selection.get_selected()
        model, selected = selection.get_selected_rows()
        if not selected:
            return None
        iter = self.current_list_model.get_iter(selected[0])
        if iter:
            i = model.get_string_from_iter(iter)  
            #LOG.info("!!I", i      
            #if i.find(":") == -1:
            #return int(i)
            return int(i)
        return None    

    def repopulate(self, played_index, shuffle=False):
        LOG.info("Selected index", played_index)
        list = self.get_all_beans()
        
        if shuffle:
            random.shuffle(list)

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
        """temp no color"""
        return None
        if i % 2 :
            return "#F2F2F2"
        else:
            return "#FFFFE5"        
