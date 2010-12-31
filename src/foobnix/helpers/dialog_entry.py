#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.util import LOG
from foobnix.util.localization import foobnix_localization
from foobnix.helpers.image import ImageBase

foobnix_localization()

def responseToDialog(entry, dialog, response):
        dialog.response(response)
        
def file_chooser_dialog(title, current_folder=None):
    chooser = gtk.FileChooserDialog(title, action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    chooser.set_default_response(gtk.RESPONSE_OK)
    chooser.set_select_multiple(True)
    paths = None
    if current_folder:
        chooser.set_current_folder(current_folder)
    response = chooser.run()
    if response == gtk.RESPONSE_OK:
        paths = chooser.get_filenames()
    elif response == gtk.RESPONSE_CANCEL:
        LOG.info('Closed, no files selected')
    chooser.destroy()
    return paths

def directory_chooser_dialog(title, current_folder=None):
    chooser = gtk.FileChooserDialog(title, action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    chooser.set_default_response(gtk.RESPONSE_OK)
    chooser.set_select_multiple(True)
    paths = None
    if current_folder:
        chooser.set_current_folder(current_folder)
    response = chooser.run()
    if response == gtk.RESPONSE_OK:
        paths = chooser.get_filenames()
    elif response == gtk.RESPONSE_CANCEL:
        LOG.info('Closed, no directory selected')
    chooser.destroy()
    return paths

def one_line_dialog(dialog_title, text=None):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_OK,
            None)
        dialog.set_title(dialog_title)
        dialog.set_markup(dialog_title)        
        entry = gtk.Entry()
        
        if text:
            entry.set_text(text)
        dialog.vbox.pack_end(entry, True, True, 0)
        dialog.show_all()
        
        dialog.run()
        text = entry.get_text()
        
        dialog.destroy()    
        return text
def two_line_dialog(title, description, line1, line2):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            title)
        dialog.set_markup(title)
        dialog.format_secondary_markup(description)
        
        login_entry = gtk.Entry()
        login_entry.set_text(line1)
        login_entry.show()
        
        password_entry = gtk.Entry()
        password_entry.set_text(line2)
        password_entry.show()
        
        hbox = gtk.VBox()
        hbox.pack_start(login_entry, False, False, 0)
        hbox.pack_start(password_entry, False, False, 0)
        dialog.vbox.pack_start(hbox, True, True, 0)
        dialog.show_all()
        dialog.run()
        login_text = login_entry.get_text()
        password_text = password_entry.get_text()
        dialog.destroy()
        return [login_text, password_text]      
        
        
def info_dialog_with_link(title, version, link):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_OK,
            None)
        dialog.set_title(title)
        dialog.set_markup(title)
        dialog.format_secondary_markup("<b>" + version + "</b>")
        link = gtk.LinkButton(link, link)
        link.show()
        dialog.vbox.pack_end(link, True, True, 0)
        dialog.show_all()
        dialog.run()
        dialog.destroy()      
        
def info_dialog_with_link_and_donate(version):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_OK,
            None)
        dialog.set_title(_("New foobnix release avaliable"))
        dialog.set_markup(_("New foobnix release avaliable"))
        dialog.format_secondary_markup("<b>" + version + "</b>")
        
        
        
        card = gtk.LinkButton("http://www.foobnix.com/donate/eng", _("Download and Donate"))
        #terminal = gtk.LinkButton("http://www.foobnix.com/donate/eng#terminal", _("Download and Donate by Webmoney or Payment Terminal"))
        link = gtk.LinkButton(_("http://www.foobnix.com/download/eng"), _("Download"))
        
        frame = gtk.Frame("Please donate and download")
        vbox = gtk.VBox(True, 0)
        vbox.pack_start(card, True, True)
        #vbox.pack_start(terminal, True, True)
        vbox.pack_start(link, True, True)
        frame.add(vbox)
        
        image = ImageBase("foobnix-slogan.jpg")
        
        dialog.vbox.pack_start(image, True, True)
        dialog.vbox.pack_start(frame, True, True)
        dialog.vbox.pack_start(gtk.Label(_("We hope you like the player. We will make it even better.")), True, True)
        
        dialog.show_all()
        dialog.run()
        dialog.destroy()           
    

def show_entry_dialog(title, description):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)
        dialog.set_markup(title)
        entry = gtk.Entry()
        entry.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Value:"), False, 5, 5)
        hbox.pack_end(entry)
        dialog.format_secondary_markup(description)
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        dialog.run()
        text = entry.get_text()
        dialog.destroy()
        return text
    
def show_login_password_error_dialog(title, description, login, password):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR,
            gtk.BUTTONS_OK,
            title)
        dialog.set_markup(str(title))
        dialog.format_secondary_markup(description)
        
        login_entry = gtk.Entry()
        login_entry.set_text(login)
        login_entry.show()
        
        password_entry = gtk.Entry()
        password_entry.set_text(password)
        password_entry.set_visibility(False)
        password_entry.set_invisible_char("*")
        password_entry.show()
        
        hbox = gtk.VBox()
        hbox.pack_start(login_entry, False, False, 0)
        hbox.pack_start(password_entry, False, False, 0)
        dialog.vbox.pack_start(hbox, True, True, 0)
        dialog.show_all()
        dialog.run()
        login_text = login_entry.get_text()
        password_text = password_entry.get_text()
        dialog.destroy()
        return [login_text, password_text]    

def file_saving_dialog(title, current_folder=None):
    chooser = gtk.FileChooserDialog(title, action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_OK))
    chooser.set_default_response(gtk.RESPONSE_OK)
    chooser.set_select_multiple(False)
    if current_folder:
        chooser.set_current_folder(current_folder)
    response = chooser.run()
    if response == gtk.RESPONSE_OK:
        paths = chooser.get_filenames()
    elif response == gtk.RESPONSE_CANCEL:
        LOG.info('Closed, no files selected')
    chooser.destroy()
    
    
if __name__ == '__main__':
        info_dialog_with_link_and_donate("foobnix 0.2.1-8")
        gtk.main()        

