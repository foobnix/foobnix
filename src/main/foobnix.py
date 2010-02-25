#!/usr/bin/env python
import thread, time
import gtk.glade
import gst
import os

class FoobNIX:


        def __init__(self):
                    
                #Set the Glade file
                self.gladefile = "foobnix.glade"  
                self.wTree = gtk.glade.XML(self.gladefile, "mainWindow")
                 
                    
                #Create our dictionay and connect it
                dic = {
               "on_mainWindow_destroy" : gtk.main_quit,
               "on_AddWine" : self.OnAddWine,
               "on_filechooserbutton1_file_set": self.onFileSelect,
               "on_button1_clicked":self.onPlayButton,
               "on_button2_clicked":self.onPauseButton,
               "on_button3_clicked":self.onStopButton,
               "on_hscale2_change_value": self.onVolumeChange,
               "on_hscale1_change_value": self.onSeekChange,
               "on_treeview1_button_press_event":self.onSlectRow
               }
                self.wTree.signal_autoconnect(dic)
                
                self.dialog = gtk.FileChooserDialog(
                                                    title=None,
                                                    parent=None,
                                                    action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                                    buttons=None,
                                                    backend=None)
                
                self.dialog.set_default_response(gtk.RESPONSE_OK)

                
                #Here are some variables that can be reused later
                self.cWine = 0
                self.cWinery = 1
                self.cGrape = 2
                self.cYear = 3
                
                self.sWine = "Wine"
                self.sWinery = "Winery"
                self.sGrape = "Grape"
                self.sYear = "Year"                
                                
                #Get the treeView from the widget Tree
                self.wineView = self.wTree.get_widget("wineView")
                self.wineFile = self.wTree.get_widget("filechooserbutton1")                
                self.wineText = self.wTree.get_widget("entry1")
                self.time_label = self.wTree.get_widget("label7")                
                
                self.wineVolume = self.wTree.get_widget("hscale2")
                self.wineSeek = self.wTree.get_widget("hscale1")
                
                self.treeview1 = self.wTree.get_widget("treeview1")
                self.treeview2 = self.wTree.get_widget("treeview2")
                
                
                self.wineText.set_text("/home/ivan/Music/22.mp3")
                
                #self.player = gst.element_factory_make("playbin2", "my-player")                
                
                self.player = gst.Pipeline("player")
                source = gst.element_factory_make("filesrc", "file-source")
                decoder = gst.element_factory_make("mad", "mp3-decoder")
                conv = gst.element_factory_make("audioconvert", "converter")
                sink = gst.element_factory_make("alsasink", "alsa-output")
                
                
                volume = gst.element_factory_make("volume", "volume")
                
                self.time_format = gst.Format(gst.FORMAT_TIME)
                
                
        
                self.player.add(source, decoder, conv, volume, sink)
                gst.element_link_many(source, decoder, volume, conv, sink)
                
                
                self.time_format = gst.Format(gst.FORMAT_TIME)
                

                 
                #player = gst.Pipeline("player")   
                #self.volume = gst.element_factory_make("volume", "volume")
                #self.level = gst.element_factory_make("level", "volume-level")            

                #Add all of the List Columns to the wineView
                self.AddWineListColumn(self.sWine, self.cWine)
                self.AddWineListColumn(self.sWinery, self.cWinery)
                self.AddWineListColumn(self.sGrape, self.cGrape)
                self.AddWineListColumn(self.sYear, self.cYear)
    
                #Create the listStore Model to use with the wineView
                self.wineList = gtk.ListStore(str, str, str, str)
                #Attache the model to the treeView
                self.wineView.set_model(self.wineList)
                
                
                self.play_thread_id = None
                self.player.set_state(gst.STATE_NULL)                
                self.time_label.set_text("00:00 / 00:00")
                
                bus = self.player.get_bus()
                bus.add_signal_watch()
                bus.connect("message", self.on_message)
                
                
                #TABLE
                
                self.column = gtk.TreeViewColumn("Title", gtk.CellRendererText()
                    , text=0)
                self.column.set_resizable(True)                
                self.column.set_sort_column_id(0)
                self.treeview1.append_column(self.column)
                
                #Create the listStore Model to use with the wineView
                self.treeList = gtk.TreeStore(str)
                #append1 = self.treeList.append(None, ["a"])
                #self.treeList.append(append1, ["1a" ])
                
                path = "/home/ivan/Music/ELO"
                level = None;
                self.go_recursive(path, level)
                
                self.treeview1.set_model(self.treeList)                                 
        
        print "some"    
        
        def go_recursive(self, path, level):
            
            dir = os.path.abspath(path)    
            print "absolut", dir
            list = os.listdir(dir)
        
            for file in list:
                
                sub = self.treeList.append(level, [file])
                
                full_path = path +"/"+ file        
                if os.path.isdir(full_path):            
                    print "dir", file                    
                    self.go_recursive(full_path,sub) 
                else:
                    print "file", file
                    
                
        def AddWineListColumn(self, title, columnId):
                """This function adds a column to the list view.
                First it create the gtk.TreeViewColumn and then set
                some needed properties"""
                                                
                column = gtk.TreeViewColumn(title, gtk.CellRendererText()
                    , text=columnId)
                column.set_resizable(True)                
                column.set_sort_column_id(columnId)
                self.wineView.append_column(column)
                
        def OnAddWine(self, widget):
                """Called when the use wants to add a wine"""
                #Cteate the dialog, show it, and store the results
                wineDlg = wineDialog();                
                result, newWine = wineDlg.run()
                
                if (result == gtk.RESPONSE_OK):
                    """The user clicked Ok, so let's add this
                    wine to the wine list"""
                    self.wineList.append(newWine.getList())
        
        def onFileSelect(self, widget):
            print "set file"
            file_name = self.wineFile.get_filename()
            print file_name
            self.wineText.set_text(file_name)
        
        def onPlayButton(self, widget):
            print "Play" 
            file_name = self.wineFile.get_filename()
            if not file_name:
                file_name = self.wineText.get_text()
                print "set file name", file_name                                                    
            #self.player.set_property("uri", "file://" + file_name)
            self.player.get_by_name("file-source").set_property("location", file_name)
            self.player.set_state(gst.STATE_PLAYING)
            self.play_thread_id = thread.start_new_thread(self.play_thread, ())
            

                        
        def onPauseButton(self, widget):
            print "Pause"
            self.player.set_state(gst.STATE_PAUSED)
        def onStopButton(self, widget):
            print "Stop"
            self.player.set_state(gst.STATE_NULL)
            self.time_label.set_text("00:00 / 00:00")
            
        def onVolumeChange(self, widget, obj3, ojb4):
            val = ojb4 / 100            
            print val    
            self.player.get_by_name("volume").set_property('volume', val)
        
        def onSlectRow(self,widget,event):
            print "select"
            
        def onSeekChange(self, widget, obj3, obj4):            
            time.sleep(0.2)          
                        
                        
            pos_current = self.player.query_position(self.time_format, None)[0]
            pos_max = self.player.query_duration(self.time_format, None)[0]            
            
            print "Current", pos_current, pos_max
            seek_ns = pos_max * obj4 / 100;
            print "Set position", seek_ns
                        
            self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, seek_ns)
            #self.play_thread_id = thread.start_new_thread(self.play_thread, ())
        
        def play_thread(self):
            print "Thread Start"
            play_thread_id = self.play_thread_id
            gtk.gdk.threads_enter() #@UndefinedVariable
            self.time_label.set_text("00:00 / 00:00")
            gtk.gdk.threads_leave() #@UndefinedVariable
    
            while play_thread_id == self.play_thread_id:
                try:
                    time.sleep(0.2)
                    dur_int = self.player.query_duration(self.time_format, None)[0]
                    dur_str = self.convert_ns(dur_int)
                    gtk.gdk.threads_enter() #@UndefinedVariable
                    self.time_label.set_text("00:00 / " + dur_str)
                    gtk.gdk.threads_leave() #@UndefinedVariable
                    break
                except:
                    pass
                    
            time.sleep(0.2)
            while play_thread_id == self.play_thread_id:
                pos_int = self.player.query_position(self.time_format, None)[0]
                pos_str = self.convert_ns(pos_int)
                if play_thread_id == self.play_thread_id:
                    gtk.gdk.threads_enter() #@UndefinedVariable
                    self.time_label.set_text(pos_str + " / " + dur_str)
                    
                    self.wineSeek.set_value(100 * pos_int / dur_int)
                    
                    gtk.gdk.threads_leave() #@UndefinedVariable
                time.sleep(1)

        def convert_ns(self, time_int):
            time_int = time_int / 1000000000
            time_str = ""
            if time_int >= 3600:
                _hours = time_int / 3600
                time_int = time_int - (_hours * 3600)
                time_str = str(_hours) + ":"
            if time_int >= 600:
                _mins = time_int / 60
                time_int = time_int - (_mins * 60)
                time_str = time_str + str(_mins) + ":"
            elif time_int >= 60:
                _mins = time_int / 60
                time_int = time_int - (_mins * 60)
                time_str = time_str + "0" + str(_mins) + ":"
            else:
                time_str = time_str + "00:"
            if time_int > 9:
                time_str = time_str + str(time_int)
            else:
                time_str = time_str + "0" + str(time_int)
                
            return time_str          
    
        def on_message(self, bus, message):
            t = message.type
            if t == gst.MESSAGE_EOS:
                self.play_thread_id = None
                self.player.set_state(gst.STATE_NULL)
                self.button.set_label("Start")
                self.time_label.set_text("00:00 / 00:00")
            elif t == gst.MESSAGE_ERROR:
                err, debug = message.parse_error()
                print "Error: %s" % err, debug
                self.play_thread_id = None
                self.player.set_state(gst.STATE_NULL)
                self.button.set_label("Start")
                self.time_label.set_text("00:00 / 00:00")
                                               
       
    
        
                                
class wineDialog:
    """This class is used to show wineDlg"""
    
    def __init__(self, wine="", winery="", grape="", year=""):
    
                #setup the glade file
                self.gladefile = "pywine.glade"
                #setup the wine that we will return
                self.wine = Wine(wine, winery, grape, year)
                
    def run(self):
                """This function will show the wineDlg"""    
                
                #load the dialog from the glade file      
                self.wTree = gtk.glade.XML(self.gladefile, "wineDlg") 
                #Get the actual dialog widget
                self.dlg = self.wTree.get_widget("wineDlg")
                #Get all of the Entry Widgets and set their text
                self.enWine = self.wTree.get_widget("enWine")
                self.enWine.set_text(self.wine.wine)
                self.enWinery = self.wTree.get_widget("enWinery")
                self.enWinery.set_text(self.wine.winery)
                self.enGrape = self.wTree.get_widget("enGrape")
                self.enGrape.set_text(self.wine.grape)
                self.enYear = self.wTree.get_widget("enYear")
                self.enYear.set_text(self.wine.year)    
    
                #run the dialog and store the response                
                self.result = self.dlg.run()
                #get the value of the entry fields
                self.wine.wine = self.enWine.get_text()
                self.wine.winery = self.enWinery.get_text()
                self.wine.grape = self.enGrape.get_text()
                self.wine.year = self.enYear.get_text()
                
                #we are done with the dialog, destory it
                self.dlg.destroy()
                
                #return the result and the wine
                return self.result, self.wine
                

class Wine:
    """This class represents all the wine information"""
    
    def __init__(self, wine="", winery="", grape="", year=""):
                
                self.wine = wine
                self.winery = winery
                self.grape = grape
                self.year = year
                
    def getList(self):
                """This function returns a list made up of the 
                wine information.  It is used to add a wine to the 
                wineList easily"""
                return [self.wine, self.winery, self.grape, self.year]                
                
if __name__ == "__main__":
    
    player = FoobNIX()
    gtk.gdk.threads_init() #@UndefinedVariable
    gtk.main()
