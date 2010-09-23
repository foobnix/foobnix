'''
Created on Sep 23, 2010

@author: ivan
'''
import gtk
class PlaylistControls():
    def __init__(self):
        notebook = gtk.Notebook()
        notebook.append_page(gtk.Button("1"), gtk.Label("Madonna"))
        notebook.append_page(gtk.Button("2"), gtk.Label("Scorpions"))
        
        self.widget = notebook


class InfoPanelWidget():    
    def __init__(self): 
        info_frame = gtk.Frame("Madonna - Album (2009)")        
        vbox = gtk.VBox(False,0)
        

        
        """image and similar artists"""
        ibox = gtk.HBox(False,0)
        image =gtk.Image()
        image.set_from_stock(gtk.STOCK_NEW, 100)
        artists =gtk.Button("Similar Artists")
        
        ibox.pack_start(image, True, True)
        ibox.pack_start(artists, True, True)
        
        vbox.pack_start(ibox,True,True)
        
        """image and similar artists"""
        sbox = gtk.HBox(False,0)
        songs =gtk.Button("Similar Songs")
        tags =gtk.Button("Smilar Tags")
        
        sbox.pack_start(songs, True, True)
        sbox.pack_start(tags, True, True)
        
        vbox.pack_start(sbox,True,True)
        
                
        info_frame.add(vbox)
        

        
        info_frame.show_all()
               
        self.widget= info_frame
