'''
Created on Feb 26, 2010

@author: ivan
'''
import os
import gtk
import urllib
import logging

from foobnix.fc.fc import FC


def open_in_filemanager(path, managers=None):
    dirname = path if os.path.isdir(path) else os.path.dirname(path)
    if FC().active_manager[0] and not managers:
        managers = [FC().active_manager[1]]
    else:
        managers = FC().file_managers
    
    def search_mgr(managers):
        if os.environ.has_key('DESKTOP_SESSION'):
            for fm in managers:
                if os.system(fm + ' \"' + dirname + '\" 2>>/dev/null'):
                    continue
                else:
                    logging.info("Folder " + dirname + " has been opened in " + fm)
                    return True
        else:
            if not os.system('explorer ' + dirname):
                logging.info("Folder " + dirname + " has been opened in explorer")
                return True
    
    if not search_mgr(managers):
        if FC().active_manager[0]:
            logging.warning(FC().active_manager[1] + "not installed in system")
            logging.info("Try open other file manager")
            if not search_mgr(FC().file_managers):
                logging.warning("None file manager found")
        else:
            logging.warning("None file manager found")          
    
def rename_file_on_disk(row, index_path, index_text):
    path = row[index_path]
    name = os.path.basename(path)
    entry = gtk.Entry()
    entry.set_width_chars(64)
    hbox = gtk.HBox()
    if os.path.isdir(path):
        entry.set_text(name)
        hbox.pack_start(entry)
        title = _('Rename folder')
    else:
        name_tuple = os.path.splitext(name)
        entry.set_text(name_tuple[0])
        entry_ext = gtk.Entry()
        entry_ext.set_width_chars(7)
        entry_ext.set_text(name_tuple[1][1:])
        hbox.pack_start(entry)
        hbox.pack_start(entry_ext)
        title = _('Rename file')
    dialog = gtk.Dialog(title, buttons=("Rename", gtk.RESPONSE_ACCEPT, "Cancel", gtk.RESPONSE_REJECT))
    dialog.vbox.pack_start(hbox)
    dialog.show_all()    
    if dialog.run() == gtk.RESPONSE_ACCEPT:
        if os.path.isdir(path) or not entry_ext.get_text():
            new_path = os.path.join(os.path.dirname(path), entry.get_text())
        else:
            new_path = os.path.join(os.path.dirname(path), entry.get_text() + '.' + entry_ext.get_text()) 
        os.rename(path, new_path)
        row[index_path] = new_path
        row[index_text] = os.path.basename(new_path)
        dialog.destroy()
        return True
    dialog.destroy()

def delete_files_from_disk(row_refs, paths, get_iter_from_row_reference):            
    for path in paths[:] :
        if os.path.isdir(path):
            for row_ref, _path in zip(row_refs[:], paths[:]):
                if path != _path and _path.startswith(path):
                    paths.remove(_path)
                    row_refs.remove(row_ref)
            
    title = _('Delete file(s) / folder(s)')
    label = gtk.Label(_('Do you really want to delete item(s) from disk?'))
    dialog = gtk.Dialog(title, buttons=("Delete", gtk.RESPONSE_ACCEPT, "Cancel", gtk.RESPONSE_REJECT))
    dialog.set_default_size(500, 200)
    dialog.set_border_width(5)
    dialog.vbox.pack_start(label)
    buffer = gtk.TextBuffer()
    text = gtk.TextView(buffer)
    text.set_editable(False)
    text.set_cursor_visible(False)
    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    scrolled_window.add(text)
    dialog.vbox.pack_start(scrolled_window)
    for path in paths:
        name = os.path.basename(path)
        buffer.insert_at_cursor('\t' + name + '\n')
    
    dialog.show_all()    
    if dialog.run() == gtk.RESPONSE_ACCEPT:
        model = row_refs[0].get_model()
        for row_ref, path in zip(row_refs, paths):
            if os.path.isfile(path):
                os.remove(path)
            else:
                del_dir(path)
            model.remove(get_iter_from_row_reference(row_ref))
            dialog.destroy()
            return True
    dialog.destroy()             

def del_dir(path): 
        list = os.listdir(path)
        if not list: return
        for item in list:
            item_abs = os.path.join(path, item)
            if os.path.isfile(item_abs):
                os.remove(item_abs)
            else:
                del_dir(item_abs)
        os.rmdir(path)

def isDirectory(path):
    return os.path.isdir(path)

"""extentsion linke .mp3, .mp4"""
def get_file_extension(fileName):    
    return os.path.splitext(fileName)[1].lower().strip()

def file_extension(file_name):
    return get_file_extension(file_name)


def get_any_supported_audio_file(full_file):    
    exists = os.path.exists(full_file)
    if exists:
        return  full_file
    
    """try to find other source"""
    ext = get_file_extension(full_file)
    nor = full_file[:-len(ext)]
    logging.info("Normalized path" + nor)
    
    for support_ext in FC().audio_formats:
        try_name = nor + support_ext
        if os.path.exists(try_name):
            return try_name
                
    return None


def get_file_path_from_dnd_dropped_uri(uri):
    path = ""
    if uri.startswith('file:\\\\\\'): # windows
        path = uri[8:] # 8 is len('file:///')
    elif uri.startswith('file://'): # nautilus, rox
        path = uri[7:] # 7 is len('file://')
    elif uri.startswith('file:'): # xffm
        path = uri[5:] # 5 is len('file:')

    path = urllib.url2pathname(path) # escape special chars
    path = path.strip('\r\n\x00') # remove \r\n and NULL

    return path
