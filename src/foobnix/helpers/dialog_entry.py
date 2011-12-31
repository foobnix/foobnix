#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
import logging

from foobnix.fc.fc import FC
from foobnix.helpers.image import ImageBase
from foobnix.util.const import SITE_LOCALE, ICON_FOOBNIX
from foobnix.util.localization import foobnix_localization
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name

foobnix_localization()

def responseToDialog(entry, dialog, response):
        dialog.response(response)
        
def file_chooser_dialog(title, current_folder=None):
    chooser = gtk.FileChooserDialog(title, action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    chooser.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
    chooser.set_default_response(gtk.RESPONSE_OK)
    chooser.set_select_multiple(True)
    paths = None
    if current_folder:
        chooser.set_current_folder(current_folder)
    response = chooser.run()
    if response == gtk.RESPONSE_OK:
        paths = chooser.get_filenames()
    elif response == gtk.RESPONSE_CANCEL:
        logging.info('Closed, no files selected')
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
        logging.info('Closed, no directory selected')
    chooser.destroy()
    return paths

def one_line_dialog(dialog_title, parent=None, entry_text=None, message_text1=None, message_text2=None):
        dialog = gtk.MessageDialog(
            parent,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_OK,
            None)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        dialog.set_title(dialog_title)
        if message_text1:
            dialog.set_markup(message_text1)
        if message_text2:
            dialog.format_secondary_markup(message_text2)     
        
        
        entry = gtk.Entry()
        
        '''set last widget in action area as default widget (button OK)'''
        dialog.set_default_response(gtk.RESPONSE_OK) 
        
        '''activate default widget after Enter pressed in entry'''
        entry.set_activates_default(True)
        
        if entry_text:
            entry.set_text(entry_text)
        dialog.vbox.pack_start(entry, True, True, 0)
        dialog.show_all()
        
        dialog.run()
        text = entry.get_text()
        
        dialog.destroy()    
        return text if text else None
    
def two_line_dialog(dialog_title, parent=None, message_text1=None,
                    message_text2=None, entry_text1="", entry_text2=""):
        dialog = gtk.MessageDialog(
            parent,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        dialog.set_title(dialog_title)
        if message_text1:
            dialog.set_markup(message_text1)
        if message_text2:
            dialog.format_secondary_markup(message_text2)
        
        login_entry = gtk.Entry()
        if entry_text1:
            login_entry.set_text(entry_text1)
        login_entry.show()
        
        password_entry = gtk.Entry()
        if entry_text2:
            password_entry.set_text(entry_text2)
        password_entry.show()
        
        hbox = gtk.VBox()
        hbox.pack_start(login_entry, False, False, 0)
        hbox.pack_start(password_entry, False, False, 0)
        dialog.vbox.pack_start(hbox, True, True, 0)
        dialog.show_all()
        
        '''set last widget in action area as default widget (button OK)'''
        dialog.set_default_response(gtk.RESPONSE_OK) 
        
        '''activate default widget after Enter pressed in entry'''
        login_entry.set_activates_default(True)
        password_entry.set_activates_default(True)
        
        dialog.run()
        login_text = login_entry.get_text()
        password_text = password_entry.get_text()
        dialog.destroy()
        return [login_text, password_text] if (login_text and password_text) else [None,None]     

def info_dialog(title, message):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_OK,
            None)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        dialog.set_title(title)
        dialog.set_markup(title)
        dialog.format_secondary_markup(message)        
        dialog.show_all()
        dialog.run()
        dialog.destroy()      
        
def info_dialog_with_link(title, version, link):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_OK,
            None)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
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
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        dialog.set_title(_("New foobnix release avaliable"))
        dialog.set_markup(_("New foobnix release avaliable"))
        dialog.format_secondary_markup("<b>" + version + "</b>")
        
        
        
        card = gtk.LinkButton("http://www.foobnix.com/support?lang=%s"%SITE_LOCALE, _("Download and Donate"))
        #terminal = gtk.LinkButton("http://www.foobnix.com/donate/eng#terminal", _("Download and Donate by Webmoney or Payment Terminal"))
        link = gtk.LinkButton("http://www.foobnix.com/support?lang=%s"%SITE_LOCALE, _("Download"))
        
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
        version_check = gtk.CheckButton(_("Check for new foobnix release on start"))
        version_check.set_active(FC().check_new_version)
        dialog.vbox.pack_start(version_check, True, True)
        
        dialog.show_all()
        dialog.run()
        
        FC().check_new_version = version_check.get_active()
        FC().save()
        dialog.destroy()           
    

def show_entry_dialog(title, description):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK,
            None)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
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
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
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
    chooser.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
    chooser.set_default_response(gtk.RESPONSE_OK)
    chooser.set_select_multiple(False)
    if current_folder:
        chooser.set_current_folder(current_folder)
    response = chooser.run()
    if response == gtk.RESPONSE_OK:
        paths = chooser.get_filenames()
    elif response == gtk.RESPONSE_CANCEL:
        logging.info('Closed, no files selected')
    chooser.destroy()
    
class FileSavingDialog(gtk.FileChooserDialog):
    def __init__(self, title, func, args = None, current_folder=None, current_name=None):
        gtk.FileChooserDialog.__init__(self, title, action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        self.set_default_response(gtk.RESPONSE_OK)
        self.set_select_multiple(False)
        self.set_do_overwrite_confirmation(True)
        self.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        if current_folder:
            self.set_current_folder(current_folder)
        if current_name:
            self.set_current_name(current_name)
        
        response = self.run()
        if response == gtk.RESPONSE_OK:
            filename = self.get_filename()
            folder = self.get_current_folder()
            if func:
                try:
                    if args: func(filename, folder, args)
                    else: func(filename, folder)
                except IOError, e:
                        logging.error(e)
        elif response == gtk.RESPONSE_CANCEL:
            logging.info('Closed, no files selected')
        self.destroy()
   
if __name__ == '__main__':
        info_dialog_with_link_and_donate("foobnix 0.2.1-8")
        gtk.main()        

