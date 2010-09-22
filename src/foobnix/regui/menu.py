'''
Created on Sep 22, 2010

@author: ivan
'''
import gtk
class MenuWidget():
    def __init__(self):
        top = TopMenu()
        """File menu"""
        file = top.append("File")
        file.add_image_item("Add File(s)", gtk.STOCK_OPEN)
        file.add_image_item("Add Folder(s)", gtk.STOCK_OPEN)     
        file.separator()   
        file.add_image_item("Quit", gtk.STOCK_QUIT)
        
        
        """View menu"""
        view = top.append("View")
        view.add_ckeck_item("Music Tree",True)
        view.add_ckeck_item("Search Panel",True)
        view.separator()
        view.add_ckeck_item("Lyric Panel",True)
        view.add_ckeck_item("Info Panel",False)
        view.separator()
        view.add_image_item("Preferences",gtk.STOCK_PREFERENCES)        
        
        """Playbacka menu"""
        playback = top.append("Playback")      
        order = playback.add_text_item("Order")
        linear = order.add_radio_item("Linear",None, True)
        order.add_radio_item("Random",linear, True)
        order.separator()
        order.add_image_item("Shuffle",gtk.STOCK_UNDELETE)
        
              
        repeat = playback.add_text_item("Repeat")
        all = repeat.add_radio_item("All",None, True) 
        repeat.add_radio_item("Single",all, True)
        repeat.add_radio_item("Disable",all, True)
        
        """Help menu"""
        help = top.append("Help")
        help.add_image_item("About",gtk.STOCK_ABOUT)
        help.add_image_item("Help",gtk.STOCK_HELP)
    
        self.widget = top.widget
        

class MyMenu(gtk.Menu):
    def __init__(self):
        gtk.Menu.__init__(self)
    
    def add_image_item(self, title, gtk_stock):
        item = gtk.ImageMenuItem(title)
        item.show()
        img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
        item.set_image(img) 
                
        self.append(item)
    
    def separator(self):
        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.append(separator)
    
    def add_ckeck_item(self, title,active):
        check = gtk.CheckMenuItem(title)
        check.show()
        check.set_active(active)
        self.append(check)        
    
    def add_radio_item(self, title,group, active):
        check = gtk.RadioMenuItem(group,title)
        check.show()
        check.set_active(active)
        self.append(check)
        return check
    
    def add_text_item(self, title):
        sub = gtk.MenuItem(title)
        sub.show()
        self.append(sub)
        
        menu = MyMenu()
        menu.show()        
        sub.set_submenu(menu)
        
        return menu

class TopMenu():
    def __init__(self):
        self.menu_bar = gtk.MenuBar()
        self.menu_bar.show()
       
        self.widget = self.menu_bar
        
    def append(self, title):
        menu = MyMenu()
        menu.show()
        
        file_item = gtk.MenuItem(title)
        file_item.show()
        
        file_item.set_submenu(menu)
        
        self.menu_bar.append(file_item)
        
        return menu
    
        