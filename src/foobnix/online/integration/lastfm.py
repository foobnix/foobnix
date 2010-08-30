'''
Created on 24 Apr 2010

@author: Matik
'''

from foobnix.model.entity import CommonBean
from foobnix.thirdparty import pylast
from foobnix.thirdparty.pylast import WSError
from foobnix.util import LOG
from foobnix.util.configuration import FConfiguration
from foobnix.online.google.translate import translate
import thread
import time


API_KEY = FConfiguration().API_KEY
API_SECRET = FConfiguration().API_SECRET        
username = FConfiguration().lfm_login
password_hash = pylast.md5(FConfiguration().lfm_password)


class LastFmConnector():
    def __init__(self):
        self.network = None
        self.scrobler = None
        self.preferences_window = None
        
        thread.start_new_thread(self.init_thread, ())
    
    def init_thread(self):
        try:
            self.network = pylast.get_lastfm_network(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)
        
            """scrobler"""
            scrobler_network = pylast.get_lastfm_network(username=username, password_hash=password_hash)
            self.scrobler = scrobler_network.get_scrobbler("fbx", "1.0")
        except:
            LOG.error("Invalid last fm login or password or network problems", username, FConfiguration().lfm_password)
    
    def get_scrobler(self):
        return self.scrobler
    
    def connected(self):
        return self.network is not None
    
    def search_top_albums(self,query):
        #unicode(query, "utf-8")
        artist = self.network.get_artist(query)
        if not artist:
            return None
        try:
            albums = artist.get_top_albums()
        except WSError:
            LOG.info("No artist with that name")
            return None
        
        beans = []    
        LOG.info("Albums: ", albums)  
        
        for i, album in enumerate(albums):
            if i > 6:
                break;
            try:            
                album_txt = album.item
            except AttributeError:
                album_txt = album['item']
            
            tracks = album_txt.get_tracks()
            bean = CommonBean(name=album_txt.get_title() + " (" + album_txt.get_release_year() + ")", path="", color="GREEN", type=CommonBean.TYPE_FOLDER, parent=query);
            beans.append(bean)
            
            for track in tracks:
                bean = CommonBean(name=track, path="", type=CommonBean.TYPE_MUSIC_URL, parent=album_txt.get_title());
                beans.append(bean)
                
        return beans
    
    
    def search_tags_genre(self,query):
        query = translate(query, src="ru", to="en")
        beans = [] 
        
        tag = self.network.get_tag(query)
        bean = CommonBean(name=tag.get_name(), path="", color="GREEN", type=CommonBean.TYPE_GOOGLE_HELP, parent=None)
        beans.append(bean)
        try:
            tracks = tag.get_top_tracks()
        except:
            return None
        
        for j, track in enumerate(tracks):
            if j > 20:
                break
            try:            
                track_item = track.item
            except AttributeError:
                track_item = track['item']
            bean = CommonBean(name=track_item.get_artist().get_name() + " - " + track_item.get_title(), path="", type=CommonBean.TYPE_MUSIC_URL, parent=tag.get_name())
            beans.append(bean)
        
           
        tags = self.network.search_for_tag(query)
        LOG.info("tags")
        LOG.info(tags)
        
        
        flag = True
        
        for i, tag in enumerate(tags.get_next_page()):        
            if i == 0:
                LOG.info("we find it top", tag, query)
                continue
            
                
            
            if i < 4:
                bean = CommonBean(name=tag.get_name(), path="", color="GREEN", type=CommonBean.TYPE_GOOGLE_HELP, parent=None)
                beans.append(bean)
                
                tracks = tag.get_top_tracks()
                for j, track in enumerate(tracks):
                    if j > 10:
                        break
                    try:            
                        track_item = track.item
                    except AttributeError:
                        track_item = track['item']
                    bean = CommonBean(name=track_item.get_artist().get_name() + " - " + track_item.get_title(), path="", type=CommonBean.TYPE_MUSIC_URL, parent=tag.get_name())
                    beans.append(bean)
            else:
                if flag:
                    bean = CommonBean(name="OTHER TAGS", path="", color="#FF99FF", type=CommonBean.TYPE_FOLDER, parent=None)
                    beans.append(bean)
                    flag = False
                bean = CommonBean(name=tag.get_name(), path="", color="GREEN", type=CommonBean.TYPE_GOOGLE_HELP, parent=None)
                beans.append(bean)
                
        return beans
    
    
    
    def search_top_tracks(self, query):
        #unicode(query, "utf-8")
        artist = self.network.get_artist(query)
        if not artist:
            return None
        try:
            tracks = artist.get_top_tracks()
        except WSError:
            LOG.info("No artist with that name")
            return None
        
        beans = []    
        LOG.info("Tracks: ", tracks)
            
        for track in tracks:
            
            try:            
                track_item = track.item
            except AttributeError:
                track_item = track['item']
            
            #LOG.info(track.get_duration()
            
            bean = CommonBean(name=str(track_item), path="", type=CommonBean.TYPE_MUSIC_URL, parent=query);
            #norm_duration = track_item.get_duration() / 1000
            #LOG.info(track_item.get_duration(), norm_duration
            #bean.time = normilize_time(norm_duration)
            beans.append(bean)
            
        return beans
    
    def search_top_similar(self,query):
        #unicode(query, "utf-8")
        
        artist = self.network.get_artist(query)
        if not artist:
            return None
        
        artists = artist.get_similar(10)
        beans = []   
        for artist in artists:
            try:            
                artist_txt = artist.item
            except AttributeError:
                artist_txt = artist['item']
                
            LOG.info(artist, artist_txt)
            title = str(artist_txt)
            bean = CommonBean(name=title, path="", type=CommonBean.TYPE_FOLDER, color="GREEN", parent=query);
            beans.append(bean)
            tops = self.search_top_tracks(title)
            for top in tops:
                beans.append(top)
            
        return beans
    
    def unimplemented_search(self,query):    
        song = CommonBean(name=query, type=CommonBean.TYPE_MUSIC_URL)
        artist = song.getArtist()
        title = song.getTitle()
        track = self.network.get_track(artist, title)
        LOG.debug("Search similar songs", song.getArtist(), song.getTitle())
        
        beans = []
        if not track:
            return []
        
        
        """similar tracks"""
        try:
            similars = track.get_similar()
            
        except:
            LOG.error("Similar not found")
            return None
        beans.append(song)
        for tsong in similars:
            try:            
                tsong_item = tsong.item
            except AttributeError:
                tsong_item = tsong['item']
    
            beans.append(CommonBean(name=str(tsong_item), type=CommonBean.TYPE_MUSIC_URL, parent=query))
              
        return beans
