'''
Created on Feb 26, 2010

@author: ivan
'''

import os
import gtk
import sys
import urllib
import shutil
import thread
import logging
import threading

from subprocess import Popen
from foobnix.fc.fc import FC
from foobnix.util.const import ICON_FOOBNIX
from foobnix.helpers.textarea import ScrolledText
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name
from foobnix.helpers.dialog_entry import directory_chooser_dialog


def open_in_filemanager(path, managers=None):
    dirname = path if os.path.isdir(path) else os.path.dirname(path)
    if FC().active_manager[0] and not managers:
        managers = [FC().active_manager[1]]
    else:
        managers = FC().file_managers
    
    def search_mgr(managers, dirname):
        files = []
        for path in os.environ['PATH'].split(":"):
            if os.path.exists(path):
                files += get_files_from_folder(path)
            
        for fm in managers:
            if fm not in files:
                continue
            else:
                path = dirname
                arguments = [fm, dirname]
                if fm == 'krusader':
                    arguments.insert(-1, '--left')
                    
                logging.info("Folder " + dirname + " has been opened in " + fm)
                
                try:
                    Popen(Popen(arguments))
                except TypeError:
                    pass
                return True
            
    if not search_mgr(managers, dirname):
        if FC().active_manager[0]:
            logging.warning(FC().active_manager[1] + "not installed in system")
            logging.info("Try open other file manager")
            if not search_mgr(FC().file_managers, dirname):
                logging.warning("None file manager found")
        else:
            logging.warning("None file manager found")          

def get_files_from_folder(folder):
    return [file for file in os.listdir(folder) if not os.path.isdir(file)]
        
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
    dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
    dialog.show_all()    
    if dialog.run() == gtk.RESPONSE_ACCEPT:
        if os.path.isdir(path) or not entry_ext.get_text():
            new_path = os.path.join(os.path.dirname(path), entry.get_text())
        else:
            new_path = os.path.join(os.path.dirname(path), entry.get_text() + '.' + entry_ext.get_text()) 
        try:
            os.rename(path, new_path)
            row[index_path] = new_path
            row[index_text] = os.path.basename(new_path)
        except IOError, e:
            logging.error(e)
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
    dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
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
        try:
            for row_ref, path in zip(row_refs, paths):
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    del_dir(path)
                model.remove(get_iter_from_row_reference(row_ref))
        except IOError, e:
            logging.error(e)
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

def copy_move_files_dialog(files, dest_folder, copy=None):
    if copy == gtk.gdk.ACTION_COPY: action = _("Copy") #@UndefinedVariable
    else: action = _("Replace") 
    
    dialog = gtk.Dialog(_('%s file(s) / folder(s)') % action)
    
    ok_button = dialog.add_button(action, gtk.RESPONSE_OK)
    cancel_button = dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL) #@UnusedVariable
    
    ok_button.grab_default()
    label = gtk.Label('\n' + _("Are you really want to %s this item(s) to %s ?") % (action, dest_folder))      
    area = ScrolledText()
    area.text.set_editable(False)
    area.text.set_cursor_visible(False)
    area.buffer.set_text("\n".join([os.path.basename(path) for path in files]))
    dialog.vbox.pack_start(area.scroll)
    dialog.set_border_width(5)
    dialog.vbox.pack_start(label)
    dialog.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
    dialog.set_default_size(400, 150)
    dialog.show_all()
    if dialog.run() == gtk.RESPONSE_OK:
        dialog.destroy()
        return True
    dialog.destroy()
    return False

def create_folder_dialog(path):
    dirname = path if os.path.isdir(path) else os.path.dirname(path)
    dialog = gtk.Dialog(_("Make folder dialog"))
    ok_button = dialog.add_button(_("Create folder"), gtk.RESPONSE_OK)
    label1 = gtk.Label(_("You want to create subfolder in folder") + " " + os.path.basename(dirname))
    label2 = gtk.Label(_("Enter new folder's name:"))
    entry = gtk.Entry()
    dialog.set_border_width(5)
    dialog.vbox.pack_start(label1)
    dialog.vbox.pack_start(label2)
    dialog.vbox.pack_start(entry)
    dialog.show_all()
    ok_button.grab_default()
    def task():
        if dialog.run() == gtk.RESPONSE_OK:
            folder_name = entry.get_text()
            if folder_name:
                full_path = os.path.join(dirname, folder_name)
                try:
                    os.mkdir(full_path)
                except OSError, e:
                    logging.error(e)
                    if str(e).startswith("[Errno 17]"):
                        er_message = _("So folder already exists")
                    else:
                        er_message = str(e)
                    warning = gtk.MessageDialog(parent=dialog, flags=gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_ERROR, message_format=er_message)
                    if warning.run() == gtk.RESPONSE_DELETE_EVENT:
                        warning.destroy()
                    full_path = task()
                return full_path
    full_path = task()
    dialog.destroy()
    return full_path
     
def isDirectory(path):
    return os.path.isdir(path)

"""extentsion linke .mp3, .mp4"""
def get_file_extension(fileName):
    if fileName and fileName.startswith("http"):
        return None    
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

def get_dir_size(dirpath):
    folder_size = 0
    for (path, dirs, files) in os.walk(dirpath): #@UnusedVariable
        for file in files:
            filename = os.path.join(path, file)
            folder_size += os.path.getsize(filename)
    return folder_size

def get_full_size(path_list):
    size = 0
    for path in path_list:
        if os.path.exists(path):
            if os.path.isdir(path):
                size += get_dir_size(path)
            else:
                size += os.path.getsize(path)
    return size

def copy_move_with_progressbar(pr_window, src, dst_folder, move=False, symlinks=False, ignore=None):
    '''changed shutil.copytree(src, dst, symlinks, ignore)'''
    if sys.version_info < (2, 6):
        logging.warning("your python version is too old")
        return
    else:
        from multiprocessing import Process
    def copy_move_one_file(src, dst_folder):
        
        m = Process(target=func, args=(src, dst_folder))
        m.start()
        def task():
            try:
                name_begin = pr_window.label_from.get_text().split()[0]
                pr_window.label_from.set_text(name_begin + " " + os.path.basename(src) + "\n")
                pr_window.progress(src, dst_folder)
            except threading.ThreadError:
                m.terminate()
                os.remove(os.path.join(dst_folder, os.path.basename(src)))
        thread.start_new_thread(task, ())
        if m.is_alive():
            m.join()
        return
    
    func = shutil.move if move else shutil.copy2
    if os.path.isfile(src):
        copy_move_one_file(src, dst_folder)
        return
    """Recursively copy a directory tree using copy2().

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    try:
        names = os.listdir(src)
    except OSError, why:
        logging.error(why)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()
    
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    subfolder = os.path.join(dst_folder, os.path.basename(src))
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(subfolder, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copy_move_with_progressbar(pr_window, srcname, subfolder, move, symlinks, ignore)
            else:
                copy_move_one_file(srcname, subfolder)
              
                # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
    if move:
        os.rmdir(src)
    else:
        try:
            shutil.copystat(src, dst_folder)
        except OSError, why:
            errors.extend((src, dst_folder, str(why)))
    
def copy_to(old_paths):
        destinations = directory_chooser_dialog(_("Choose Folder"), FC().last_dir)
        if not destinations:
            return
        from foobnix.helpers.window import CopyProgressWindow
        pr_window = CopyProgressWindow(_("Progress"), old_paths, 300, 100)
        pr_window.label_to.set_text(_("To: ") + destinations[0] + "\n")
        if destinations:
            for old_path in old_paths:
                if not os.path.exists(old_path):
                    logging.warning("File " + old_path + " not exists")
                    continue
                pr_window.label_from.set_text(_("Copying: ") + os.path.dirname(old_path))
                def task():
                    copy_move_with_progressbar(pr_window, old_path, destinations[0])
                    pr_window.response(gtk.RESPONSE_OK)
                t = threading.Thread(target=task)
                t.start()
                if pr_window.run() == gtk.RESPONSE_REJECT:
                    pr_window.exit = True
                    t.join()
        pr_window.destroy()