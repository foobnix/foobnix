'''
Created on Sep 1, 2012

@author: zavlab1
'''

import urllib
from HTMLParser import HTMLParser


class LyricsFinder(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []
        self.needed_tag = 0
    
    def get_lyrics(self, artist, title):
        base = "http://www.lyricsmania.com/"
        title = title.encode('utf-8').strip().replace(" ", "_")
        title = urllib.quote(title)
        artist = artist.encode('utf-8').strip().replace(" ", "_")
        artist = urllib.quote(artist)
        result = urllib.urlopen(base + title + "_lyrics_" + artist + ".html").read()
        self.feed(result)
        return "\n".join(self.data)
    
    def handle_starttag(self, tag, attrs):
        if tag == "div":
            for name, value in attrs:
                if name == 'id' and value == "songlyrics_h":
                    self.needed_tag = 1
                   
    def handle_endtag(self, tag):
        if tag == 'div' and self.needed_tag:
            self.needed_tag = 0

    def handle_data(self, data):
        if self.needed_tag:
            self.data.append(data.strip())

def get_lyrics_from_lyricsmania(artist, title):
    if not globals().has_key("lyrics_finder"):
        global lyrics_finder
        lyrics_finder = LyricsFinder()
    lyric = lyrics_finder.get_lyrics(artist, title)
    lyrics_finder.reset()
    return lyric

if __name__ == '__main__':  
    print get_lyrics_from_lyricsmania("aBBA", " honey, Honey ")

