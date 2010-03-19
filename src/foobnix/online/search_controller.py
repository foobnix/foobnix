'''
Created on Mar 18, 2010

@author: ivan
'''
from foobnix.model.entity import EntityBean, PlaylistBean
from foobnix.online.pylast import WSError
def search_top_albums(network, query):
    unicode(query, "utf-8")
    artist = network.get_artist(query)
    if not artist:
        return None
    try:
        albums = artist.get_top_albums()
    except WSError:
        print "No artist with that name"
        return None
    
    beans = []    
    print "Albums: ", albums  
    
    for album in albums:
        try:            
            album_txt = album.item
        except AttributeError:
            album_txt = album['item']
        
        tracks = album_txt.get_tracks()
        bean = PlaylistBean(name="===[ " + album_txt.get_title() + " ]===", path="", type=EntityBean.TYPE_FOLDER);
        beans.append(bean)
        
        for track in tracks:
            bean = PlaylistBean(name=track, path="", type=EntityBean.TYPE_MUSIC_URL);
            beans.append(bean)
            
    return beans



def search_top_tracks(network, query):
    unicode(query, "utf-8")
    artist = network.get_artist(query)
    if not artist:
        return None
    try:
        tracks = artist.get_top_tracks()
    except WSError:
        print "No artist with that name"
        return None
    
    beans = []    
    print "Tracks: ", tracks 
        
    for track in tracks:
        try:            
            track_item = track.item
        except AttributeError:
            track_item = track['item']
        bean = PlaylistBean(name=track_item, path="", type=EntityBean.TYPE_MUSIC_URL);
        beans.append(bean)
        
    return beans

def search_top_similar(network, query):
    unicode(query, "utf-8")
    
    artist = network.get_artist(query)
    if not artist:
        return None
    
    artists = artist.get_similar(10)
    beans = []   
    for artist in artists:
        try:            
            artist_txt = artist.item
        except AttributeError:
            artist_txt = artist['item']
            
        print artist, artist_txt
        title = str(artist_txt)
        bean = PlaylistBean(name="===[ " + title + " ]===", path="", type=EntityBean.TYPE_FOLDER);
        beans.append(bean)
        tops = search_top_tracks(network, title)
        for top in tops:
            beans.append(top)
        
        
            
    return beans
