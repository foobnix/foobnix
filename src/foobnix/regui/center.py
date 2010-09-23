'''
Created on Sep 23, 2010

@author: ivan
'''
import gtk
class PlaylistControls():
    def __init__(self):
        notebook = gtk.Notebook()
        notebook.append_page(gtk.Button("1"), gtk.Label("1"))
        notebook.append_page(gtk.Button("2"), gtk.Label("2"))
        
        self.widget = notebook


class InfoPanelWidget():
    def __init__(self):        
        self.widget= gtk.Button("right")    
