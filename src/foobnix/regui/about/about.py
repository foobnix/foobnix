# -*- coding: utf-8 -*-
'''
Created on Oct 2, 2010

@author: dimitry (zavlab1)
'''
import gtk
from foobnix.regui.service.image_service import get_foobnix_pixmap_path_by_name
from foobnix.regui.about import credits, changelog



def CreateButton_with_label_and_icon(image,label): 
    box = gtk.HBox(False, 0)
    box.set_border_width (2)
    box.pack_end (label, True, False, 0)
    box.pack_end (image, True, False, 0)
    
    button = gtk.Button()
    button.add(box)
    return button


"""""""""
Три окна about, changelog, credits имеют похожий функционал.
1) все они не изменяемого размера
2) все они прячуться при нажатии заркыть окно.
3) у всех есть тайтл

!!!Тоесть нет необходимости дублировать код создания одних и тех же окон три раза, 
а можно использовать ООП

Создать базовый класс например BaseParentWindow
который будет
1) не измеряем,
2) закрываем
3) опледелено действие скрыть
4) принимать title окна
5) принимать размер окна
6) принимать содержание.

Создать три подкласса AboutWindow, ChangelogWindow, CreditWindow
которые наслудются от главного но имеют свои особенности.

Тоесть они переиспользуют родителя с добавлением своих особенностей реализации контента.

Это важная задача на улучшение кода и понимания ООП.

"""""""""

class BaseParentWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_position(gtk.WIN_POS_CENTER)        
        self.set_resizable(False)
        
        
    def add_content(self, content):
        self.add(content)
        
class AboutWindow(BaseParentWindow):
    def __init__(self):
        BaseParentWindow.__init__(self)
        self.set_title("About Foobnix")
        self.set_size_request(200, 200)
        
        """add new content to display in parent"""
        content = gtk.Label("Hello About Label")
        self.add_content(content)     

class ChangeLogWindow(BaseParentWindow):
    def __init__(self):
        BaseParentWindow.__init__(self)
        self.set_title("Changelog")
        self.set_size_request(100, 100)        
        
        """add new content to display in parent"""
        content = gtk.Label("Hello About Changelog")
        self.add_content(content)

#........        

    
def about():
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)    
    window.set_title ("About Foobnix, every time I am creating new instance on window")
    print "About Foobnix, every time I am creating new instance on window when open it."
    window.set_position(gtk.WIN_POS_CENTER)
    window.set_border_width(5)
    window.set_geometry_hints(window, min_width=270, min_height=270)
    gtk.window_set_default_icon_from_file (get_foobnix_pixmap_path_by_name("foobnix.png"))
    window.set_resizable(False)
    
    """ get foobnix icon path"""
    foobnix_image_path = get_foobnix_pixmap_path_by_name("foobnix.png")
    
    window.set_icon_from_file (foobnix_image_path)
    
    table = gtk.Table(3, 3, False)
        
    image = gtk.image_new_from_file(foobnix_image_path);
    table.attach(image, 0, 3, 0, 1)
    
    label = gtk.Label("Foobnix")
    
    label.set_markup ("""
<big><big><b><b>Foobnix</b></b></big></big>
Playing all imaginations\n
<small>Developed by Ivan Ivanenko</small>
<small>ivan.ivanenko@gmail.com</small>\n   
<a href="http://www.foobnix.com">www.foobnix.com</a>\n""");
    
    label.set_justify(gtk.JUSTIFY_CENTER)
    table.attach(label, 0, 3, 1, 2)
    
    label = gtk.Label("Credits")
    image = gtk.image_new_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
    
    button_credits = CreateButton_with_label_and_icon(image,label)
    button_credits.set_border_width (9)
    table.attach(button_credits, 0, 1, 2, 3)
    
    label = gtk.Label("Close")
    image = gtk.image_new_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU)
    
    button_close = CreateButton_with_label_and_icon(image,label)
    button_close.set_border_width (9)
    table.attach(button_close, 2, 3, 2, 3)
    
    label = gtk.Label("Changelog")
    image = gtk.image_new_from_stock(gtk.STOCK_DND, gtk.ICON_SIZE_MENU)
    
    button_changelog = CreateButton_with_label_and_icon(image,label)
    button_changelog.set_border_width (9)
    table.attach(button_changelog, 1, 2, 2, 3)
    
    window.connect("destroy", lambda * x:window.hide())
    button_close.connect("clicked", lambda * x:window.hide())
    button_credits.connect("clicked", lambda * x:credits.credits())
    button_changelog.connect("clicked", lambda * x:changelog.changelog())
    
    button_close.grab_focus ()
    window.add(table)
    window.show_all()
    








