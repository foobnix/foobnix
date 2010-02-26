#!/usr/bin/env python
import thread, time
import gtk.glade
import gst
import os
from player.mouse_utils import is_double_click




class FoobNIX:
        def __init__(self):
                    
                #Set the Glade file
                self.gladefile = "foobnix.glade"  
                self.wTree = gtk.glade.XML(self.gladefile, "mainWindow")
                    
                #Create our dictionay and connect it
                dic = {
               "on_mainWindow_destroy" : gtk.main_quit,
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
                
                self.musicTree = self.wTree.get_widget("treeview1")
                self.treeview2 = self.wTree.get_widget("treeview2")
                
                
                self.wineText.set_text("/home/ivan/Music/CD1")
                
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
                

                
                
                self.play_thread_id = None
                self.player.set_state(gst.STATE_NULL)                
                self.time_label.set_text("00:00 / 00:00")
                
                bus = self.player.get_bus()
                bus.add_signal_watch()
                bus.connect("message", self.on_message)
                
                #################
                #TABLE
                #################
                
                self.column = gtk.TreeViewColumn("Title", gtk.CellRendererText()
                    , text=0)
                self.column.set_resizable(True)                
                self.column.set_sort_column_id(0)
                self.musicTree.append_column(self.column)
                
                
                self.musicTreeModel = gtk.TreeStore(str,str)
                
                
                path = "/home/ivan/Music/nightwish"
                level = None;
                self.go_recursive(path, level)
                
                self.musicTree.set_model(self.musicTreeModel)                                 
        
        print "some"    
        
        def go_recursive(self, path, level):
            
            dir = os.path.abspath(path)    
            print "absolut", dir
            list = os.listdir(dir)
        
            for file in list:
                
                full_path = path + "/" + file        
                sub = self.musicTreeModel.append(level, [file, full_path])                
                
                if os.path.isdir(full_path):            
                    print "dir", file                    
                    self.go_recursive(full_path, sub) 
                else:
                    print "file", file
                    
               
                     
                
        
        
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
        
        def onSlectRow(self, widget, event):        
                 
            #left double click
     
            if is_double_click(event):
                selection = self.musicTree.get_selection()
                model, selected = selection.get_selected()
                if selected:
                    song_path = model.get_value(selected, 1)
                    print song_path
                    self.wineText.set_text(song_path)
                
 
            
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
                
if __name__ == "__main__":
    
    player = FoobNIX()
    gtk.gdk.threads_init() #@UndefinedVariable
    gtk.main()
