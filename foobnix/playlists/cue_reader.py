# coding: utf-8

'''
Created on 7  2010

@author: ivan
'''

import chardet
import logging
import os
import re

import foobnix.util.id3_util

from foobnix.fc.fc import FC
from foobnix.gui.model import FModel
from foobnix.util import file_utils
from foobnix.util.audio import get_mutagen_audio
from foobnix.util.image_util import get_image_by_path
from foobnix.util.time_utils import convert_seconds_to_text
from foobnix.util.file_utils import get_any_supported_audio_file
from foobnix.util.id3_util import correct_encoding, update_id3

TITLE = "TITLE"
PERFORMER = "PERFORMER"
FILE = "FILE"
INDEX = "INDEX"

class CueTrack():

    def __init__(self, title, performer, index, path):
        self.title = title
        self.performer = performer
        self.index = index
        self.duration = 0
        self.path = path

    def __str__(self):
        return "Track: " + self.title + " " + self.performer + " " + self.index

    def get_start_time_str(self):
        return self.index[len("INDEX 01") + 1:]

    def get_start_time_sec(self):
        time = self.get_start_time_str()

        times = re.findall("([0-9]{1,3}):", time)

        if not times or len(times) < 2:
            return 0

        min = times[0]
        sec = times[1]
        starts = int(min) * 60 + int(sec)
        return starts

class CueFile():
    def __init__(self):
        self.title = None
        self.performer = None
        self.file = ""
        self.image = None
        self.tracks = []

    def append_track(self, track):
        self.tracks.append(track)

    def __str__(self):
        if self.title:
            logging.info("Title" + self.title)
        if self.performer:
            logging.info("Performer" + self.performer)
        if self.file:
            logging.info("File" + self.file)

        return "CUEFILE: " + self.title + " " + self.performer + " " + self.file


class CueReader():

    def __init__(self, cue_path, embedded_cue=None):
        self.cue_path = cue_path
        self.embedded_cue = embedded_cue
        self.is_valid = True
        self.cue_file = CueFile()

    def get_line_value(self, str):
        first = str.find('"') or str.find("'")
        end = str.find('"', first + 1) or str.find("'", first + 1)
        return str[first + 1:end]

    def get_full_duration (self, file):
        try:
            audio = get_mutagen_audio(file)
        except Exception, e:
            logging.warn(str(e) + " " + file)
            return

        return audio.info.length

    def normalize(self):
        duration_tracks = []
        tracks = self.cue_file.tracks

        for i in xrange(len(tracks)):
            track = tracks[i]
            full_duration = self.get_full_duration(track.path)
            if full_duration:
                if i == len(tracks) - 1: #for last track in cue
                    duration = self.get_full_duration(track.path) - track.get_start_time_sec()
                else:
                    next_track = tracks[i + 1]
                    if next_track.get_start_time_sec() > track.get_start_time_sec():
                        #for cue "one file - several tracks"
                        duration = next_track.get_start_time_sec() - track.get_start_time_sec()
                    else: #for cue  "several files - each file involve several tracks"
                        duration = self.get_full_duration(track.path) - track.get_start_time_sec()
                track.duration = duration
            else:
                track.duration = None
            if not track.path:
                track.path = self.cue_file.file

            track.path = get_any_supported_audio_file(track.path)
            duration_tracks.append(track)

        self.cue_file.tracks = duration_tracks
        return self.cue_file

    def get_common_beans(self):
        beans = []
        cue = self.parse()

        if not self.is_cue_valid():
            return []
        for i, track in enumerate(cue.tracks):
            bean = FModel(text=track.performer + " - " + track.title, path=track.path)
            bean.artist = track.performer
            bean.tracknumber = i + 1
            bean.title = track.title
            bean.album = self.cue_file.title
            bean.name = bean.text
            bean.start_sec = track.get_start_time_sec()
            bean.duration_sec = track.duration
            bean.time = convert_seconds_to_text(track.duration)
            bean.is_file = True
            try:
                bean.info = foobnix.util.id3_util.normalized_info(get_mutagen_audio(track.path).info, bean)
            except Exception, e:
                logging.warn(str(e) + " " + bean.path)
                bean.info = ""

            if not bean.title or not bean.artist:
                bean = update_id3(bean)

            beans.append(bean)

        return beans

    def is_cue_valid(self):
        logging.info("CUE VALID" + str(self.cue_path) + str(self.is_valid))
        return self.is_valid

    """detect file encoding"""
    def code_detecter(self, data):
        try:
            return chardet.detect(data)['encoding']
        except:
            return "windows-1251"

    def parse(self):
        if self.embedded_cue:
            data = self.embedded_cue
        else:
            file = open(self.cue_path, "r")
            data = file.read()

        code = self.code_detecter(correct_encoding(data))
        data = data.replace('\r\n', '\n').split('\n')
        title = ""
        performer = ""
        index = "00:00:00"
        full_file = None

        self.cue_file.image = get_image_by_path(self.cue_path)

        self.files_count = 0

        for line in data:

            if not line:
                continue

            if isinstance(line, str):
                try:
                    line = unicode(line, code)
                except:
                    logging.error("There is some problems while converting in unicode")

            line = line.strip().encode('utf-8')

            if not self.is_valid and not line.startswith(FILE):
                continue
            else:
                self.is_valid = True

            if line.startswith(TITLE):
                title = self.get_line_value(line)
                if self.files_count == 0:
                    self.cue_file.title = title

            if line.startswith(PERFORMER):
                performer = self.get_line_value(line)
                if self.files_count == 0:
                    self.cue_file.performer = performer

            if line.startswith(FILE):
                self.files_count += 1
                file = self.get_line_value(line)
                file = os.path.basename(file)

                if "/" in file:
                    file = file[file.rfind("/")+1:]
                if "\\" in file:
                    file = file[file.rfind("\\")+1:]

                dir = os.path.dirname(self.cue_path)
                full_file = os.path.join(dir, file)
                logging.debug("CUE source" + full_file)
                exists = os.path.exists(full_file)
                """if there no source cue file"""

                if not exists:
                    """try to find other source"""
                    ext = file_utils.get_file_extension(full_file)
                    nor = full_file[:-len(ext)]
                    logging.info("Normalized path" + nor)

                    find_source = False
                    for support_ext in FC().audio_formats:
                        try_name = nor + support_ext
                        if os.path.exists(try_name):
                            full_file = try_name
                            logging.debug("Found source for cue file name" + try_name)
                            find_source = True
                            break;

                    if not find_source:
                        self.is_valid = False
                        self.files_count -= 1
                        logging.warn("Can't find source for " + line + "  Check source file name")
                        continue

                if self.files_count == 0:
                    self.cue_file.file = full_file

            if line.startswith(INDEX):
                index = self.get_line_value(line)

            if line.startswith("INDEX 01"):
                cue_track = CueTrack(title, performer, index, full_file)
                self.cue_file.append_track(cue_track)

        logging.debug("CUE file parsed " + str(self.cue_file.file))
        return self.normalize()

def update_id3_for_cue(beans):
    result = []
    for bean in beans:
        if bean.path and bean.path.lower().endswith(".cue"):
                reader = CueReader(bean.path)
                cue_beans = reader.get_common_beans()
                for cue in cue_beans:
                    result.append(cue)
        else:
            result.append(bean)

    return result

