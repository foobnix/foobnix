'''
Created on May 28, 2010

@author: ivan
'''
import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import os
from google.appengine.ext.webapp import template
import pylast
from configuration import FConfiguration
from vk import Vkontakte
from pylast import WSError

API_KEY = FConfiguration().API_KEY
API_SECRET = FConfiguration().API_SECRET

username = FConfiguration().lfm_login
password_hash = pylast.md5(FConfiguration().lfm_password)
network = pylast.get_lastfm_network(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)
vkontakte = Vkontakte(FConfiguration().vk_login, FConfiguration().vk_password)

def search_top_tracks(query):    
    artist = network.get_artist(query)
    if not artist:
        return None
    try:
        tracks = artist.get_top_tracks()
    except WSError:        
        return None
    
    songs = []    
    for track in tracks:
        
        try:            
            track_item = track.item
        except AttributeError:
            track_item = track['item']
        
        song = Song(name=str(track_item));
        songs.append(song)
        
    return songs


class Song():
    def __init__(self,  name="",path="",type=""):
        self.path = path
        self.name = name
        self.type = type
        
        
class SourcePath(webapp.RequestHandler):
    def get(self):
        query = self.request.get('query')
        song = vkontakte.find_most_relative_song(query)
        self.redirect(song.path)
        
class SearchPage(webapp.RequestHandler):
    def get(self):       
        
        song = self.request.get('song')
        
        if song:
            songs = search_top_tracks(song)
        else:
            songs = []
        
        template_values = {           
            'song': song.capitalize(),
            'songs': songs
            }        
        path = os.path.join(os.path.dirname(__file__), 'search.html')
        self.response.out.write(template.render(path, template_values))        


application = webapp.WSGIApplication(
                                     [('/', SearchPage),
                                     ('/search', SearchPage),
                                     ('/source', SourcePath)],
                                     debug=True)
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()