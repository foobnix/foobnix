import gtk

class Icon():
    PLAYING = gtk.STOCK_GO_FORWARD
    ERROR = gtk.STOCK_DIALOG_ERROR
    PAUSE = gtk.STOCK_MEDIA_PAUSE
    STOP = gtk.STOCK_MEDIA_STOP
    SAVE = gtk.STOCK_SAVE
    CONNECT = gtk.STOCK_CONNECT
    HOME = gtk.STOCK_HOME
    NONE = None

class LineType():
    SIMPLE_LINE = {"color":None}
    TITLE_LINE = {"color":"GREEN"}
    INFO_LINE = {"color":"YELLOW"}
    RED_LINE = {"color":"RED"}
    CLICK_LINE = {"color":"BLUE"}

class Model():
    POS_ICON = 0;
    POS_TEXT = 1;
    POS_TIME = 2;
    
    POS_ID = 3;
    POS_BG_COLOR = 4;
    POS_ICON_STATUS = 5;
    
    def __init__(self, widget):
        self.widget = widget
        self.model = gtk.ListStore(str,str,str, str,str,str)
        widget.set_model(self.model)
        self.create_columns(widget)
        self.index = 0
    
    def append(self, id, text, time,line_type=LineType.SIMPLE_LINE):
        self.index += 1
        if line_type["color"] == None:
            bg_color = self.get_background_colour(self.index)
        else:
            bg_color = line_type["color"]
            
        self.model.append([None, text,time,id,bg_color, None])
    
    def set_song_icon(self, uuid, icon):
        self._get_line_by_uuid(uuid)[self.POS_ICON] =  icon    
   
    def set_status_icon(self, uuid, icon):
        self._get_line_by_uuid(uuid)[self.POS_ICON_STATUS] =  icon

    def _get_line_by_uuid(self, uuid):
        for line in self.model:
            if line[self.POS_ID] == uuid:
                return line
        return None
    
    
    def clear_all_icons(self):
        for line in self.model:
            line[self.POS_ICON] = Icon.NONE
        
    
    def get_selected_id(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected()
        if selected:            
            return model.get_value(selected, self.POS_ID)
        return None
        
    def create_columns(self, treeView):
        
        cellpb = gtk.CellRendererPixbuf()
        icon_column = gtk.TreeViewColumn('    ', cellpb, stock_id=self.POS_ICON, cell_background=self.POS_BG_COLOR)
            
        treeView.append_column(icon_column)
        
    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Artist - Title", rendererText, text=self.POS_TEXT, background=self.POS_BG_COLOR)
        treeView.append_column(column)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_expand(True)
        
        cellpb = gtk.CellRendererPixbuf()
        icon_column = gtk.TreeViewColumn('    ', cellpb, stock_id=self.POS_ICON_STATUS, cell_background=self.POS_BG_COLOR)
        treeView.append_column(icon_column)

        
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Time", rendererText, text=self.POS_TIME, background=self.POS_BG_COLOR)
        treeView.append_column(column)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column.set_expand(False)
   
    def get_background_colour(self, i):
        if i % 2 :
            return "#F2F2F2"
        else:
            return "#FFFFE5"

class BaseCntr():
    def __init__(self, widget):
        widget.connect("button-press-event", self.on_button_press)
        widget.connect("key-release-event", self.on_key_release_event)
        widget.connect("drag-end", self.on_drag_end)
    
    def on_key_release_event(self, *args):
        pass
    
    def on_drag_end(self, *args):
        self.on_drag()
    
    def on_button_press(self,w,e):
        if self._is_double_click(e):
            self.on_duble_click()
    
    def on_drag(self):
        pass
    
    def on_duble_click(self):
        pass
    
    def get_state(self):        
        return self.state
    
    def set_state(self, state):
        self.state = state
    
    def _is_double_click(self,event):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            return True
        else:
            return False        
                    

class Cntrl(gtk.Window, BaseCntr, Model): 
    def __init__(self):        
        super(Cntrl, self).__init__()
        
        self.set_size_request(350, 250)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", gtk.main_quit)
        self.set_title("Demo list")

        treeView = gtk.TreeView()
        BaseCntr.__init__(self, treeView)
        Model.__init__(self, treeView)
       
        self.logic()
        
        vbox = gtk.VBox(False, 8)
        vbox.pack_start(treeView, True, True, 0)
        self.add(vbox)
        self.show_all()
    
    def on_duble_click(self):
        uuid = self.get_selected_id()
        self.set_song_icon(uuid, Icon.PLAYING)
        self.set_status_icon(uuid, Icon.HOME)
        
        print "Selected id", self.get_selected_id()
    
    def logic(self):
        i ="0"
        self.append("uuid"+i,i+" Madonna - like1","3:1"+i, LineType.TITLE_LINE)
        i = "a"
        self.append("uuid"+i,i+" Madonna - like1","3:1"+i, LineType.RED_LINE)
        for i in "12345679":
            self.append("uuid"+i,i+" Madonna - like1","3:1"+i)
        

Cntrl()
gtk.main()
