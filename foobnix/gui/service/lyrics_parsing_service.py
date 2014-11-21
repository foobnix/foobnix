'''
Created on Sep 1, 2012

@author: zavlab1
'''

import urllib
import logging
from HTMLParser import HTMLParser


class LyricsFinder(HTMLParser):
    def __init__(self, tagname=None, attr=None, attr_value=None):
        HTMLParser.__init__(self)
        self.data = []
        self.needed_tag = 0
        self.tagname = tagname
        self.attr = attr
        self.attr_value = attr_value

    def get_lyrics_from_lyricsmania(self, artist, title):
        base = "http://www.lyricsmania.com/"
        self.tagname = 'div'
        self.attr = 'id'
        self.attr_value = 'songlyrics_h'
        title = title.encode('utf-8').strip().replace(" ", "_").replace("/", "-")
        title = urllib.quote(title)
        artist = artist.encode('utf-8').strip().replace(" ", "_").replace("/", "-")
        artist = urllib.quote(artist)
        result = urllib.urlopen(base + title + "_lyrics_" + artist + ".html").read()
        result = result.replace('&#039;', '!apostrophe!')
        self.feed(result)
        return "\n".join(self.data).replace('!apostrophe!', '&#039;')

    def get_lyrics_from_megalyrics(self, artist, title):
        base = "http://megalyrics.ru/lyric/"
        self.tagname = 'div'
        self.attr = 'class'
        self.attr_value = 'text_inner'
        title = title.replace(" ", "-").replace("/", "-")
        title = urllib.quote(title)
        artist = artist.replace(" ", "-").replace("/", "-")
        artist = urllib.quote(artist)
        result = urllib.urlopen(base + artist + "/" + title + ".html").read()
        result = result.replace("&#39;", '!apostrophe!').replace('<br /><br />', '<br />\n<br />')
        self.feed(result)
        return "\n".join(self.data).replace('!apostrophe!', "\'")

    def handle_starttag(self, tag, attrs):
        if tag == self.tagname:
            for name, value in attrs:
                if name == self.attr and value == self.attr_value:
                    self.needed_tag = 1

    def handle_endtag(self, tag):
        if tag == self.tagname and self.needed_tag:
            self.needed_tag = 0

    def handle_data(self, data):
        if self.needed_tag:
            self.data.append(data.strip())


def get_lyrics_by_parsing(artist, title):
    if not artist or not title:
        return ""

    if "lyrics_finder" not in globals():
        global lyrics_finder
        lyrics_finder = LyricsFinder()
    artist = artist.encode('utf-8').strip()
    title = title.encode('utf-8').strip()
    lyrics_finder.data = []
    text = None
    try:
        logging.debug("Try to get lyrics from lyricsmania.com")
        text = lyrics_finder.get_lyrics_from_lyricsmania(artist, title)
    except:
        logging.info("Error occurred when getting lyrics from lyricsmania.com")

    if not text:
        try:
            logging.debug("Try to get lyrics from megalyrics.ru")
            text = lyrics_finder.get_lyrics_from_megalyrics(artist, title)
        except Exception, e:
            import sys
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            logging.info("Error occurred when getting lyrics from megalyrics.ru")

    lyrics_finder.reset()
    return text


if __name__ == '__main__':
    print get_lyrics_by_parsing("aBBA", " honey, Honey ")