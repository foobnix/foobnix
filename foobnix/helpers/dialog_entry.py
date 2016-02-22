#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
from gi.repository import Gtk
import logging

from foobnix.fc.fc import FC
from foobnix.helpers.image import ImageBase
from foobnix.util.const import SITE_LOCALE, ICON_FOOBNIX
from foobnix.util.localization import foobnix_localization
from foobnix.gui.service.path_service import get_foobnix_resourse_path_by_name

foobnix_localization()

def responseToDialog(entry, dialog, response):
        dialog.response(response)

def file_selection_dialog(title, current_folder=None):
    chooser = Gtk.FileSelection(title)
    chooser.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
    chooser.set_default_response(Gtk.ResponseType.OK)
    chooser.set_select_multiple(True)
    paths = None
    if current_folder:
        chooser.set_current_folder(current_folder)
    response = chooser.run()
    if response == Gtk.ResponseType.OK:
        paths = chooser.get_selections()
    elif response == Gtk.ResponseType.CANCEL:
        logging.info('Closed, no files selected')
    chooser.destroy()
    return paths

def file_chooser_dialog(title, current_folder=None):
    chooser = Gtk.FileChooserDialog(title, action=Gtk.FileChooserAction.OPEN, buttons=(_("Open"), Gtk.ResponseType.OK))
    chooser.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
    chooser.set_default_response(Gtk.ResponseType.OK)
    chooser.set_select_multiple(True)
    paths = None
    if current_folder:
        chooser.set_current_folder(current_folder)
    response = chooser.run()
    if response == Gtk.ResponseType.OK:
        paths = chooser.get_filenames()
    elif response == Gtk.ResponseType.CANCEL:
        logging.info('Closed, no files selected')
    chooser.destroy()
    return paths

def directory_chooser_dialog(title, current_folder=None):
    chooser = Gtk.FileChooserDialog(title, action=Gtk.FileChooserAction.SELECT_FOLDER, buttons=(_("Choose"), Gtk.ResponseType.OK))
    chooser.set_default_response(Gtk.ResponseType.OK)
    chooser.set_select_multiple(True)
    paths = None
    if current_folder:
        chooser.set_current_folder(current_folder)
    response = chooser.run()
    if response == Gtk.ResponseType.OK:
        paths = chooser.get_filenames()
    elif response == Gtk.ResponseType.CANCEL:
        logging.info('Closed, no directory selected')
    chooser.destroy()
    return paths

def one_line_dialog(dialog_title, parent=None, entry_text=None, message_text1=None, message_text2=None):
        dialog = Gtk.MessageDialog(
            parent,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK,
            None)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        dialog.set_title(dialog_title)
        if message_text1:
            dialog.set_markup(message_text1)
        if message_text2:
            dialog.format_secondary_markup(message_text2)


        entry = Gtk.Entry()

        '''set last widget in action area as default widget (button OK)'''
        dialog.set_default_response(Gtk.ResponseType.OK)

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
        dialog = Gtk.MessageDialog(
            parent,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.OK,
            None)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        dialog.set_title(dialog_title)
        if message_text1:
            dialog.set_markup(message_text1)
        if message_text2:
            dialog.format_secondary_markup(message_text2)

        login_entry = Gtk.Entry()
        if entry_text1:
            login_entry.set_text(entry_text1)
        login_entry.show()

        password_entry = Gtk.Entry()
        if entry_text2:
            password_entry.set_text(entry_text2)
        password_entry.show()

        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        hbox.pack_start(login_entry, False, False, 0)
        hbox.pack_start(password_entry, False, False, 0)
        dialog.vbox.pack_start(hbox, True, True, 0)
        dialog.show_all()

        '''set last widget in action area as default widget (button OK)'''
        dialog.set_default_response(Gtk.ResponseType.OK)

        '''activate default widget after Enter pressed in entry'''
        login_entry.set_activates_default(True)
        password_entry.set_activates_default(True)

        dialog.run()
        login_text = login_entry.get_text()
        password_text = password_entry.get_text()
        dialog.destroy()
        return [login_text, password_text] if (login_text and password_text) else [None,None]

def info_dialog(title, message, parent=None):
        dialog = Gtk.MessageDialog(
            parent,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK,
            None)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        dialog.set_title(title)
        dialog.set_markup(title)
        dialog.format_secondary_markup(message)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

def info_dialog_with_link(title, version, link):
        dialog = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK,
            None)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        dialog.set_title(title)
        dialog.set_markup(title)
        dialog.format_secondary_markup("<b>" + version + "</b>")
        link = Gtk.LinkButton.new_with_label(link, link)
        link.show()
        dialog.vbox.pack_end(link, True, True, 0)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

def info_dialog_with_link_and_donate(version):
        dialog = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK,
            None)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        dialog.set_title(_("New foobnix release avaliable"))
        dialog.set_markup(_("New foobnix release avaliable"))
        dialog.format_secondary_markup("<b>" + version + "</b>")

        card = Gtk.LinkButton.new_with_label("http://foobnix.com/%s/download.html"%SITE_LOCALE, _("Download and Donate"))
        #terminal = Gtk.LinkButton("http://www.foobnix.com/donate/eng#terminal", _("Download and Donate by Webmoney or Payment Terminal"))
        # link = Gtk.LinkButton("http://www.foobnix.com/support?lang=%s"%SITE_LOCALE, _("Download"))

        frame = Gtk.Frame(label="Please donate and download")
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.set_homogeneous(True)
        vbox.pack_start(card, True, True)
        #vbox.pack_start(terminal, True, True)
        vbox.pack_start(link, True, True)
        frame.add(vbox)

        image = ImageBase("images/foobnix-slogan.jpg")

        dialog.vbox.pack_start(image, True, True)
        dialog.vbox.pack_start(frame, True, True)
        dialog.vbox.pack_start(Gtk.Label.new(_("We hope you like the player. We will make it even better.")), True, True)
        version_check = Gtk.CheckButton.new_with_label(_("Check for new foobnix release on start"))
        version_check.set_active(FC().check_new_version)
        dialog.vbox.pack_start(version_check, True, True)

        dialog.show_all()
        dialog.run()

        FC().check_new_version = version_check.get_active()
        FC().save()
        dialog.destroy()


def show_entry_dialog(title, description):
        dialog = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.OK,
            None)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        dialog.set_markup(title)
        entry = Gtk.Entry()
        entry.connect("activate", responseToDialog, dialog, Gtk.ResponseType.OK)
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        hbox.pack_start(Gtk.Label.new("Value:"), False, 5, 5)
        hbox.pack_end(entry)
        dialog.format_secondary_markup(description)
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        dialog.run()
        text = entry.get_text()
        dialog.destroy()
        return text

def show_login_password_error_dialog(title, description, login, password):
        dialog = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            title)
        dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        dialog.set_markup(str(title))
        dialog.format_secondary_markup(description)

        login_entry = Gtk.Entry()
        login_entry.set_text(login)
        login_entry.show()

        password_entry = Gtk.Entry()
        password_entry.set_text(password)
        password_entry.set_visibility(False)
        password_entry.set_invisible_char("*")
        password_entry.show()

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.pack_start(login_entry, False, False, 0)
        vbox.pack_start(password_entry, False, False, 0)
        dialog.vbox.pack_start(vbox, True, True, 0)
        dialog.show_all()
        dialog.run()
        login_text = login_entry.get_text()
        password_text = password_entry.get_text()
        dialog.destroy()
        return [login_text, password_text]

def file_saving_dialog(title, current_folder=None):
    chooser = Gtk.FileChooserDialog(title, action=Gtk.FileChooserAction.SAVE, buttons=("document-save", Gtk.ResponseType.OK))
    chooser.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
    chooser.set_default_response(Gtk.ResponseType.OK)
    chooser.set_select_multiple(False)
    if current_folder:
        chooser.set_current_folder(current_folder)
    response = chooser.run()
    if response == Gtk.ResponseType.OK:
        paths = chooser.get_filenames()
    elif response == Gtk.ResponseType.CANCEL:
        logging.info('Closed, no files selected')
    chooser.destroy()

class FileSavingDialog(Gtk.FileChooserDialog):
    def __init__(self, title, func, args = None, current_folder=None, current_name=None):
        Gtk.FileChooserDialog.__init__(self, title, action=Gtk.FileChooserAction.SAVE, buttons=("document-save", Gtk.ResponseType.OK))
        self.set_default_response(Gtk.ResponseType.OK)
        self.set_select_multiple(False)
        self.set_do_overwrite_confirmation(True)
        self.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        if current_folder:
            self.set_current_folder(current_folder)
        if current_name:
            self.set_current_name(current_name)

        response = self.run()
        if response == Gtk.ResponseType.OK:
            filename = self.get_filename()
            folder = self.get_current_folder()
            if func:
                try:
                    if args: func(filename, folder, args)
                    else: func(filename, folder)
                except IOError, e:
                        logging.error(e)
        elif response == Gtk.ResponseType.CANCEL:
            logging.info('Closed, no files selected')
        self.destroy()

if __name__ == '__main__':
        info_dialog_with_link_and_donate("foobnix 0.2.1-8")
        Gtk.main()

