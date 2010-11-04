'''
Created on 7  2010

@author: ivan
'''
from __future__ import with_statement
from foobnix.regui.model import FModel
import os
from foobnix.util.time_utils import normilize_time
from foobnix.util import LOG, file_utils
import chardet
import re
from foobnix.util.image_util import get_image_by_path
'''
Created on 4

@author: ivan
'''

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

        times = re.findall("([0-9]{1,2}):", time)

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
            LOG.info("Title", self.title)
        if self.performer:
            LOG.info("Performer", self.performer)
        if self.file:
            LOG.info("File", self.file)

        return "CUEFILE: " + self.title + " " + self.performer + " " + self.file

class CueReader():

    def __init__(self, cue_file):
        self.cue_file = cue_file
        self.is_valid = True

    def get_line_value(self, str):
        first = str.find('"') or str.find("'")
        end = str.find('"', first + 1) or str.find("'", first + 1)
        return str[first + 1:end]

    def normalize(self, cue_file):
        duration_tracks = []
        tracks = cue_file.tracks
        for i in xrange(len(tracks) - 1):
            track = tracks[i]
            next_track = tracks[i + 1]
            duration = next_track.get_start_time_sec() - track. get_start_time_sec()
            track.duration = duration
            if not track.path:
                track.path = cue_file.file
            duration_tracks.append(track)

        cue_file.tracks = duration_tracks
        return cue_file

    def get_common_beans(self):
        beans = []
        cue = self.parse()
        for i, track  in enumerate(cue.tracks):
            #bean = CommonBean(name=track.performer + " - " + track.title, path=track.path, type=CommonBean.TYPE_MUSIC_FILE)
            bean = FModel(text=track.performer + " - " + track.title, path=track.path)
            bean.artist = track.performer
            bean.tracknumber = i + 1
            bean.title = track.title
            bean.name = bean.text
            bean.start_sec = track.get_start_time_sec()
            bean.duration_sec = track.duration
            bean.time = normilize_time(track.duration)
            bean.is_file = True
            #bean.parent = cue.performer + " - " + cue.title
            #bean.image = cue.image

            beans.append(bean)


        return beans

    def is_cue_valid(self):
        self.parse()
        LOG.info("CUE VALID", self.cue_file, self.is_valid)
        return self.is_valid

    """detect file encoding"""
    def code_detecter(self, filename):
        with open(filename) as codefile:
            data = codefile.read()

        return chardet.detect(data)['encoding']


    def parse(self):
        file = open(self.cue_file, "r")
        code = self.code_detecter(self.cue_file);
        LOG.debug("File encoding is", code)

        is_title = True
        cue_file = CueFile()

        title = ""
        performer = ""
        index = "00:00:00"
        full_file = None

        cue_file.image = get_image_by_path(self.cue_file)

        self.files_count = 0

        for line in file:

            try:
                line = unicode(line, code)
            except:
                LOG.error("File encoding is too strange", code)
                pass

            line = str(line).strip()



            if not line:
                continue

            if line.startswith(TITLE):
                title = self.get_line_value(line)
                if is_title:
                    cue_file.title = title


            if line.startswith(PERFORMER):
                performer = self.get_line_value(line)
                if is_title:
                    cue_file.performer = performer

            if line.startswith(FILE):
                self.files_count += 1

                if self.files_count > 1:
                        self.is_valid = False
                        return cue_file

                file = self.get_line_value(line)
                dir = os.path.dirname(self.cue_file)
                full_file = os.path.join(dir, file)
                LOG.debug("CUE source", full_file)
                exists = os.path.exists(full_file)
                """if there no source cue file"""

                if not exists:
                    """try to find other source"""
                    ext = file_utils.get_file_extenstion(full_file)
                    nor = full_file[:-len(ext)]
                    LOG.info("Normilized path", nor)
                    if os.path.exists(nor + ".ape"):
                        full_file = nor + ".ape"
                    elif os.path.exists(nor + ".flac"):
                        full_file = nor + ".flac"
                    elif os.path.exists(nor + ".wav"):
                        full_file = nor + ".wav"
                    elif os.path.exists(nor + ".mp3"):
                        full_file = nor + ".mp3"
                    else:
                        self.is_valid = False
                        return cue_file

                if is_title:
                    cue_file.file = full_file


            if line.startswith(INDEX):
                index = self.get_line_value(line)

            if line.startswith("TRACK") and line.find("AUDIO"):
                if not is_title:
                    cue_track = CueTrack(title, performer, index, full_file)
                    cue_file.append_track(cue_track)

                is_title = False

        return self.normalize(cue_file)