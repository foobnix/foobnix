# ~*~ coding:utf-8 ~*~ #
'''
Created on Feb 26, 2010

@author: ivan
'''
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import os
import gtk
from foobnix.util.configuration import FConfiguration
from mutagen.flac import FLAC
from mutagen.apev2 import APEv2
from foobnix.util import LOG
import mutagen.mp3
from foobnix.regui.model import FModel
class CommonBean(FModel):
    TYPE_FOLDER = "TYPE_FOLDER"
    TYPE_RADIO_FOLDER = "TYPE_RADIO_FOLDER"
    TYPE_LABEL = "TYPE_LABEL"
    TYPE_GOOGLE_HELP = "TYPE_GOOGLE_HELP"
    TYPE_MUSIC_FILE = "TYPE_MUSIC_FILE"
    TYPE_MUSIC_URL = "TYPE_MUSIC_URL"
    TYPE_RADIO_URL = "TYPE_RADIO_URL"

    #Song attributes
    album = ""

    date = ""
    genre = ""
    tracknumber = ""

    def __init__(self, name=None, path=None, type=None, is_visible=True, color=None, font="normal", index= -1, parent=None, id3=None):
        FModel.__init__(self)
        self.name = name
        self.path = path
        self.type = type
        self.icon = None
        self.color = color
        self.index = index
        self.time = None
        self.is_visible = is_visible
        self.font = font
        self.parent = parent
        self.time = None
        self.album = None
        self.year = None

        self.artist = None
        self.title = None
        self.child_count = None


        self.start_at = None
        self.duration = None

        self.id3 = None
        self.image = None
        self.info = ""
        

    def set_name(self, name):
        self.artist = None;
        self.tilte = None
        self.name = name

    def getArtist(self):
        if self.artist:
            return self.artist

        s = self.name.split(" - ")
        if len(s) > 1:
            artist = self.name.split(" - ")[0]
            self.artist = ("" + artist).strip()
            return self.decode_string(self.artist)
        return ""

    def decode_string(self, str):
        try:
            return str.decode('utf-8')
        except:
            LOG.error("Error decode str", str)
            return str

    def getTitle(self):

        if self.title:
            return self.title

        s = self.name.split(" - ")
        result = ""
        if len(s) > 1:
            title = self.name.split(" - ")[1]
            result = ("" + title).strip()
        else:
            result = self.name

        for ex in FConfiguration().supportTypes:
            if result.endswith(ex):
                result = result[:-len(ex)]
        self.title = result
        return self.decode_string(result)

    def setIconPlaying(self):
        self.icon = gtk.STOCK_GO_FORWARD

    def setIconErorr(self):
        self.icon = gtk.STOCK_DIALOG_ERROR

    def setIconNone(self):
        self.icon = None

    def getTitleDescription(self):
        if self.title and self.artist and self.album:
            return self.artist + " - [" + self.album + "]  #" + self.tracknumber + " " + self.title
        else:
            if self.id3:
                return "[" + self.id3 + "] " + self.name
            else:
                return self.name

    def get_short_description(self):
        if self.title:
            return self.tracknumber + " - " + self.title
        else:
            return self.name


    def getPlayListDescription(self):
        if self.title and self.album:
            return self.name + " - " + self.title + " (" + self.album + ")" + self.parent
        return self.name

    def getMp3TagsName(self):
        audio = None

        if not self.path:
            return

        if not self.type:
            return

        if self.type != self.TYPE_MUSIC_FILE:
            return

        if not os.path.exists(self.path):
            return

        path = self.path.lower()

        if path.endswith(".flac"):
            try:
                audio = FLAC(self.path)
            except:
                return None

        elif path.endswith(".ape") or path.endswith(".mpc"):
            try:
                audio = APEv2(self.path)
            except:
                return None
        else:
            try:
                audio = MP3(self.path, ID3=EasyID3)
            except:
                return None


        artist = None
        title = None

        try:
            if audio and audio.has_key('artist'): artist = audio["artist"][0]
            if audio and audio.has_key('title'): title = audio["title"][0]
            if audio.info: self.info = audio.info.pprint()
            #if audio and audio.has_key('duration'): self.duration = audio["duration"][0]

            if artist and title:
                line = artist + " - " + title
                try:
                    decode_line = line.decode("cp866")
                    if decode_line.find(u"├") >= 0 :
                        LOG.warn("File tags encoding is very old cp866")
                        line = decode_line.replace(
                            u"\u252c", u'ё').replace(
                            u"├", "").replace(
                            u"░", u"р").replace(
                            u"▒", u"с").replace(
                            u"▓", u"т").replace(
                            u"│", u"у").replace(
                            u"┤", u"ф").replace(
                            u"╡", u"х").replace(
                            u"╢", u"ц").replace(
                            u"╖", u"ч").replace(
                            u"╕", u"ш").replace(
                            u"╣", u"щ").replace(
                            u"║", u"ъ").replace(
                            u"╗", u"ы").replace(
                            u"╝", u"ь").replace(
                            u"╜", u"э").replace(
                            u"╛", u"ю").replace(
                            u"┐", u"я")
                        #fix ёш to ё
                        line = line.replace(u'\u0451\u0448', u'\u0451')
                except:
                    pass

                self.id3, self.name = self.name, line
                return line
        except:
            LOG.error("Get song attribute error")
            pass



    def __str__(self):
        return "Common Bean :" + self.__contcat(
        "name:", self.name,
        "path:", self.path,
        "type:", self.type,
        "icon:", self.icon,
        "color:", self.color,
        "index:", self.index,
        "time:", self.time,
        "is_visible:", self.is_visible,
        "font:", self.font,
        "parent", self.parent)

    def __contcat(self, *args):
        result = ""
        for arg in args:
            result += " " + str(arg)
        return result
