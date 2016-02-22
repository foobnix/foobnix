#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import os
from gi.repository import Gtk
import logging

from foobnix.fc.fc import FC
from foobnix.gui.model import FModel
from foobnix.helpers.window import ChildTopWindow
from foobnix.util.file_utils import file_extension, get_file_extension
from foobnix.util.list_utils import sort_by_song_name
from foobnix.util.id3_file import update_id3_wind_filtering


def get_all_music_by_paths(paths, controls):
    '''end_scanning = False
    pr_window = ProgWindow(controls)
    #pr_window.analyzed_folders += 1

    def task():
        while not end_scanning:
            time.sleep(0.5)
            GObject.idle_add(pr_window.update_window)

    thread.start_new_thread(task, ())'''
    result = []
    for path in paths:
        if path == "/":
            logging.info("Skip root folder")
            continue
        current_result = _scanner(path, None)
        result = result + current_result
    #end_scanning = True
    #GObject.idle_add(pr_window.hide)
    return result

def get_all_music_with_id3_by_path(path, with_cue_filter=None):
    beans = simple_scanner(path, None)
    all = []
    if with_cue_filter:
        for bean in beans:
            if get_file_extension(bean.path) == ".cue":
                all.append(bean)
    beans = all if all else beans
    return update_id3_wind_filtering(beans)

def _scanner(path, level):
    try:
        path = path.encode("utf-8")
    except:
        pass

    results = []
    if not os.path.exists(path):
        return
    dir = os.path.abspath(path)

    list = sort_by_name(path, os.listdir(dir))

    for file in list:
        full_path = os.path.join(path, file)

        if os.path.isfile(full_path):
            #pr_window.analyzed_files += 1
            if file_extension(file) not in FC().all_support_formats:
                continue

        if os.path.isdir(full_path):
            #pr_window.analyzed_folders += 1
            if is_dir_with_music(full_path):
                #pr_window.media_folders += 1
                b_bean = FModel(file, full_path).add_parent(level).add_is_file(False)
                results.append(b_bean)
                results.extend(_scanner(full_path, b_bean.get_level()))
        elif os.path.isfile(full_path):
            results.append(FModel(file, full_path).add_parent(level).add_is_file(True))
            #pr_window.media_files +=1

    return results

def simple_scanner(path, level):
    try:
        path = path.encode("utf-8")
    except:
        pass

    results = []
    if not os.path.exists(path):
        return
    dir = os.path.abspath(path)

    list = sort_by_name(path, os.listdir(dir))

    for file in list:
        full_path = os.path.join(path, file)

        if os.path.isfile(full_path):
            if file_extension(file) not in FC().all_support_formats:
                continue;

        if os.path.isdir(full_path):
            if is_dir_with_music(full_path):
                b_bean = FModel(file, full_path).add_parent(level).add_is_file(False)
                results.append(b_bean)
                results.extend(simple_scanner(full_path, b_bean.get_level()))
        elif os.path.isfile(full_path):
            results.append(FModel(file, full_path).add_parent(level).add_is_file(True))

    return results

def scanner(path, level):
    try:
        path = path.encode("utf-8")
    except:
        pass

    results = []
    if not os.path.exists(path):
        return
    dir = os.path.abspath(path)

    list = sort_by_name(path, os.listdir(dir))

    for file in list:
        full_path = os.path.join(path, file)

        if os.path.isfile(full_path):
            if file_extension(file) not in FC().all_support_formats:
                continue

        if os.path.isdir(full_path):
            if is_dir_with_music(full_path):
                b_bean = FModel(file, full_path).add_parent(level).add_is_file(False)
                results.append(b_bean)
                results.extend(simple_scanner(full_path, b_bean.get_level()))
        elif os.path.isfile(full_path):
            results.append(FModel(file, full_path).add_parent(level).add_is_file(True))

    return results


def sort_by_name(path, list):
    files = []
    directories = []
    for file in list:
        full_path = os.path.join(path, file)
        if os.path.isdir(full_path):
            directories.append(file)
        else:
            files.append(file)

    return sorted(directories) + sort_by_song_name(files)

def is_dir_with_music(path):
    list = None
    try:
        list = os.listdir(path)
    except OSError, e:
        logging.info("Can't get list of dir"+ str(e))

    if not list:
        return False

    for file in list:
        full_path = os.path.join(path, file)
        if os.path.isdir(full_path):
            if is_dir_with_music(full_path):
                return True
        else:
            if file_extension(file) in FC().all_support_formats:
                return True
    return False

class ProgWindow(ChildTopWindow):
    def __init__(self, controls):
        ChildTopWindow.__init__(self, "Progress", 500, 100)

        self.set_transient_for(controls.main_window)

        self.label = Gtk.Label.new("Total analyzed folders: ")
        self.label1 = Gtk.Label.new("Total analyzed files: ")
        self.label2 = Gtk.Label.new("Folders with media files found: ")
        self.label3 = Gtk.Label.new("Media files found: ")

        self.analyzed_files_label = Gtk.Label.new("0")
        self.analyzed_folders_label = Gtk.Label.new("0")
        self.media_files_label = Gtk.Label.new("0")
        self.media_folders_label = Gtk.Label.new("0")

        self.analyzed_files = 0
        self.analyzed_folders = 0
        self.media_files = 0
        self.media_folders = 0

        left_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        left_box.pack_start(self.label, False, False, 0)
        left_box.pack_start(self.label1, False, False, 0)
        left_box.pack_start(self.label2, False, False, 0)
        left_box.pack_start(self.label3, False, False, 0)

        right_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        right_box.pack_start(self.analyzed_folders_label, False, False, 0)
        right_box.pack_start(self.analyzed_files_label, False, False, 0)
        right_box.pack_start(self.media_folders_label, False, False, 0)
        right_box.pack_start(self.media_files_label, False, False, 0)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.pack_start(left_box, False, False, 0)
        box.pack_start(right_box, False, False, 0)

        self.add(box)

        self.show_all()

    def update_window(self):
        self.analyzed_folders_label.set_text(str(self.analyzed_folders))
        self.analyzed_files_label.set_text(str(self.analyzed_files))
        self.media_files_label.set_text(str(self.media_files))
        self.media_folders_label.set_text(str(self.media_folders))

