#-*- coding: utf-8 -*-
'''
Created on 27 сент. 2010

@author: ivan
'''

import time
import thread
import logging
import datetime

from foobnix.fc.fc import FC
from foobnix.fc.fc_base import FCBase
from foobnix.gui.model import FModel
from foobnix.thirdparty.pylast import WSError, Tag
from foobnix.thirdparty import pylast

API_KEY = FCBase().API_KEY
API_SECRET = FCBase().API_SECRET


class Cache():
    def __init__(self, network):
        self.network = network
        self.cache_tracks = {}
        self.cache_albums = {}
        self.cache_images = {}

    def get_key(self, artist, title):
        return artist + "-" + title

    def get_track(self, artist, title):
        if not artist or not title:
            return None
        if self.get_key(artist, title) in self.cache_tracks:
            track = self.cache_tracks[self.get_key(artist, title)]
            logging.debug("Get track from cache " + str(track))
            return track
        else:
            track = self.network.get_track(artist, title)
            self.cache_tracks[self.get_key(artist, title)] = track
            return track

    def get_album(self, artist, title):
        if not artist or not title:
            return None
        track = self.get_track(artist, title)
        if track:
            if self.get_key(artist, title) in self.cache_albums:
                logging.debug("Get album from cache" + str(track))
                return self.cache_albums[self.get_key(artist, title)]
            else:
                album = track.get_album()
                if album:
                    self.cache_albums[self.get_key(artist, title)] = album
                    return album
        return None

    def get_album_image_url(self, artist, title, size=pylast.COVER_LARGE):
        if not artist or not title:
            return None
        if self.get_key(artist, title) in self.cache_images:
            logging.info("Get image from cache")
            return self.cache_images[self.get_key(artist, title)]
        else:
            album = self.get_album(artist, title)
            if album:
                image = album.get_cover_image(size)
                self.cache_images[self.get_key(artist, title)] = image
                return image


class LastFmService():
    def __init__(self, controls):
        self.connection = None
        self.network = None
        self.scrobbler = None
        self.preferences_window = None
        self.controls = controls
        thread.start_new_thread(self.init_thread, ())

    def connect(self):
        if self.network and self.scrobbler:
            return True
        return self.init_thread()

    def init_thread(self):
        time.sleep(5)
        if not self.controls.net_wrapper.is_internet():
            return None

        logging.debug("RUN INIT LAST.FM")
        username = FCBase().lfm_login
        password_hash = pylast.md5(FCBase().lfm_password)
        self.cache = None
        try:
            self.network = pylast.get_lastfm_network(api_key=API_KEY,
                                                     api_secret=API_SECRET,
                                                     username=username,
                                                     password_hash=password_hash)
            self.cache = Cache(self.network)

            """scrobbler"""
            scrobbler_network = pylast.get_lastfm_network(username=username, password_hash=password_hash)
            self.scrobbler = scrobbler_network.get_scrobbler("fbx", "1.0")
        except:
            self.network = None
            self.scrobbler = None
            self.controls.statusbar.set_text("Error last.fm connection with %s/%s" % (username, FCBase().lfm_password))
            logging.error("Either invalid last.fm login or password or network problems")
            """
            val = show_login_password_error_dialog(_("Last.fm connection error"), _("Verify user and password"), username, FC().lfm_password)
            if val:
                FC().lfm_login = val[0]
                FC().lfm_password = val[1]
            return False
            """
        return True

    def get_network(self):
        return self.network

    def get_user(self, username):
        return self.network.get_user(username)

    def get_authenticated_user(self):
        return self.network.get_authenticated_user()

    def get_loved_tracks(self, username, limit=50):
        lfm_tracks = self.get_user(username).get_loved_tracks(limit=limit)
        return self.sub_tracks_to_models(lfm_tracks, 'track')

    def get_recent_tracks(self, username, unused_limit=10):
        lfm_tracks = self.get_user(username).get_recent_tracks(limit=20)
        return self.sub_tracks_to_models(lfm_tracks, 'track')

    def get_top_tracks(self, username, unused):
        lfm_tracks = self.get_user(username).get_top_tracks()
        return self.sub_tracks_to_models(lfm_tracks, 'item')

    def get_top_artists(self, username, unused):
        lfm_tracks = self.get_user(username).get_top_artists()
        return self.sub_artist_to_models(lfm_tracks, 'item')

    def get_recommended_artists(self, username, limit=50):
        lfm_artists = self.get_authenticated_user().get_recommended_artists(limit=limit)
        return self.artists_to_models(lfm_artists)

    def get_events(self, username, limit=50):
        lfm_events = self.get_authenticated_user().get_upcoming_events()
        return self.events_to_models(lfm_events)

    def get_friends(self, username, unused):
        lfm_tracks = self.get_user(username).get_friends()
        list = self.get_sub_childs(lfm_tracks, 'name')
        result = []
        for item in list:
            result.append(FModel(item))
        return result

    def get_neighbours(self, username, unused):
        lfm_tracks = self.get_user(username).get_neighbours()
        list = self.get_sub_childs(lfm_tracks, 'name')
        result = []
        for item in list:
            parent = FModel(item)
            result.append(parent)
        return result

    def get_scrobbler(self):
        return self.scrobbler

    def report_now_playing(self, bean):
        if not FC().enable_music_scrobbler:
            logging.debug("Last.fm scrobbler not enabled")
            return None
        if not self.get_scrobbler():
            logging.warn("no last.fm scrobbler")
            return None

        def task(bean):
            if bean.artist and bean.title:
                try:
                    bean.artist, bean.title = bean.artist, bean.title
                    self.get_scrobbler().report_now_playing(bean.artist, bean.title)
                    logging.debug("notify %s %s" % (bean.artist, bean.title))
                except Exception, e:
                    logging.error(str(e) + "Error reporting now playing last.fm" + str(bean.artist) + str(bean.title))
            else:
                logging.debug("Bean title or artist not defined")

        thread.start_new_thread(task, (bean,))

    def report_scrobbled(self, bean, start_time, duration_sec):
        if not FC().enable_music_scrobbler:
            logging.debug("Last.fm scrobbler not enabled")
            return None

        if not self.get_scrobbler():
            return None

        def task(bean):
            if bean.artist and bean.title:
                try:
                    bean.artist, bean.title = bean.artist.encode("utf-8"), bean.title.encode("utf-8")
                    if bean.album:
                        bean.album = bean.album.encode("utf-8")
                    self.get_scrobbler().scrobble(bean.artist, bean.title, start_time, "P", "", int(duration_sec), bean.album or "")
                    logging.debug("Song Scrobbled " + str(bean.artist) + " " + str(bean.title) + " " + str(start_time) + " P: " + str(int(duration_sec)))
                except Exception, e:
                    logging.error(str(e) + "Error reporting now playing last.fm " + str(bean.artist) + " " + str(bean.title) + " A: " + str(bean.album))
            else:
                logging.debug("Bean title or artist not defined")

        thread.start_new_thread(task, (bean,))

    def connected(self):
        return self.network is not None

    def search_top_albums(self, aritst_name):
        if not self.connect():
            return None
        artist = self.network.get_artist(aritst_name)
        if not artist:
            return None
        try:
            albums = artist.get_top_albums()
        except WSError:
            logging.info("No artist with that name")
            return None

        albums_info = []
        for album in albums:
            try:
                album_txt = album.item
            except AttributeError:
                album_txt = album['item']

            name = album_txt.get_name()
            year = album_txt.get_release_year()
            albums_info.append((name, year))

        beans = []
        for album in sorted(albums_info, key=lambda x: x[1]):
            (name, year) = album
            if year:
                bean = FModel(name + " (" + year + ")").add_album(name).add_artist(aritst_name).add_year(year)
            else:
                bean = FModel(name).add_album(name).add_artist(aritst_name).add_year(year)

            beans.append(bean)
        return beans

    """some parent linke LoveTrack"""
    def sub_tracks_to_models(self, love_tracks, key='track'):
        tracks = []
        for love_track in love_tracks:
            try:
                track = getattr(love_track, key)
            except AttributeError:
                track = love_track[key]
            tracks.append(track)

        return self.tracks_to_models(tracks)

    def get_sub_childs(self, list, key='name'):
        result = []
        for item in list:
            try:
                artist = getattr(item, key)
            except AttributeError:
                artist = item[key]
            result.append(artist)
        return result

    def sub_artist_to_models(self, topartists, key='item'):
        artists = []
        for love_track in topartists:
            try:
                artist = getattr(love_track, key)
            except AttributeError:
                artist = love_track[key]
            artists.append(artist)

        return self.artists_to_models(artists)

    def tracks_to_models(self, tracks):
        results = []
        for track in tracks:
            artist = track.get_artist().get_name()
            title = track.get_title()
            bean = FModel(artist + " - " + title).add_artist(artist).add_title(title)
            results.append(bean)
        return results

    def artists_to_models(self, artists):
        results = []
        for track in artists:
            artist = track.get_name()
            bean = FModel(artist).add_artist(artist)
            results.append(bean)
        return results

    def events_to_models(self, events):
        results = []
        for event in events:
            try:
                name = event.get_title()
                event_model = FModel(name).add_is_file(False).add_font("bold")
                results.append(event_model)
                artists = event.get_artists()
                for artist in artists:
                    bean = FModel(artist.get_name()).parent(event_model).add_artist(artist.get_name()).add_is_file(True)
                    results.append(bean)
            except Exception as e:
                pass
        return results

    def search_album_tracks(self, artist_name, album_name):
        if not artist_name or not album_name:
            logging.warn("search_album_tracks artist and album is empty")
            return []
        if not self.connect():
            return None
        album = self.network.get_album(artist_name, album_name)
        tracks = album.get_tracks()
        return self.tracks_to_models(tracks)

    def search_top_tags(self, tag):

        logging.debug("Search tag " + tag)
        if not self.connect():
            return None
        if not tag:
            logging.warn("search_top_tags TAG is empty")
            return []
        beans = []
        tags = self.network.search_for_tag(tag)
        for tag in tags.get_next_page():
                tag_name = tag.get_name()
                bean = FModel(tag_name).add_genre(tag_name)
                beans.append(bean)
        return beans

    def search_top_tag_tracks(self, tag_name):
        logging.warn("search_top_tag tracks"+tag_name)
        if not self.connect():
            return None
        if not tag_name:
            logging.warn("search_top_tags TAG is empty")
            return []

        tag = Tag(tag_name, self.network)
        tracks = tag.get_top_tracks()

        beans = []

        for track in tracks:

            try:
                track_item = track.item
            except AttributeError:
                track_item = track['item']

            #LOG.info(track_item.get_duration())

            #bean = CommonBean(name=str(track_item), path="", type=CommonBean.TYPE_MUSIC_URL, parent=query);
            artist = track_item.get_artist().get_name()
            title = track_item.get_title()
            text = artist + " - " + title
            bean = FModel(text).add_artist(artist).add_title(title)
            beans.append(bean)

        return beans

    def search_top_tracks(self, artist_name):
        if not self.connect():
            return None
        artist = self.network.get_artist(artist_name)
        if not artist:
            return []
        try:
            tracks = artist.get_top_tracks()
        except WSError:
            logging.info("No artist with that name")
            return []

        beans = []

        for track in tracks:

            try:
                track_item = track.item
            except AttributeError:
                track_item = track['item']

            #LOG.info(track_item.get_duration())

            #bean = CommonBean(name=str(track_item), path="", type=CommonBean.TYPE_MUSIC_URL, parent=query);
            artist = track_item.get_artist().get_name()
            title = track_item.get_title()
            text = artist + " - " + title
            bean = FModel(text).add_artist(artist).add_title(title)
            beans.append(bean)

        return beans

    def search_top_similar_artist(self, artist_name, count=45):
        if not self.connect():
            return None
        if not artist_name:
            logging.warn("search_top_similar_artist, Artist name is empty")
            return []

        artist = self.network.get_artist(artist_name)
        if not artist:
            return []

        artists = artist.get_similar(count)
        beans = []
        for artist in artists:
            try:
                artist_txt = artist.item
            except AttributeError:
                artist_txt = artist['item']

            artist_name = artist_txt.get_name()
            bean = FModel(artist_name).add_artist(artist_name).add_is_file(True)

            beans.append(bean)
        return beans

    def search_top_similar_tracks(self, artist, title):
        if not self.connect():
            return None

        if not artist or not title:
            logging.warn("search_top_similar_tags artist or title is empty")
            return []

        track = self.cache.get_track(artist, title)
        if not track:
            logging.warn("search_top_similar_tracks track not found")
            return []

        similars = track.get_similar()
        beans = []
        for tsong in similars:
            try:
                tsong_item = tsong.item
            except AttributeError:
                tsong_item = tsong['item']

            artist = tsong_item.get_artist().get_name()
            title = tsong_item.get_title()
            model = FModel(artist + " - " + title).add_artist(artist).add_title(title).add_is_file(True)
            beans.append(model)

        return beans

    def search_top_similar_tags(self, artist, title):
        if not self.connect():
            return None

        if not artist or not title:
            logging.warn("search_top_similar_tags artist or title is empty")
            return []

        track = self.cache.get_track(artist, title)

        if not track:
            logging.warn("search_top_similar_tags track not found")
            return []

        tags = track.get_top_tags()
        beans = []
        for tag in tags:
            try:
                tag_item = tag.item
            except AttributeError:
                tag_item = tag['item']

            tag_name = tag_item.get_name()
            model = FModel(tag_name).add_genre(tag_name).add_is_file(True)
            beans.append(model)
        return beans

    def get_album_name(self, artist, title):
        if not self.connect():
            return None
        album = self.cache.get_album(artist, title)
        if album:
            return album.get_name()

    def get_album_year(self, artist, title):
        if not self.connect():
            return None
        album = self.cache.get_album(artist, title)
        if album:
            st_date = str(album.get_release_date())
            try:
                dt = datetime.datetime.strptime(st_date, "%d %b %Y, %H:%M")
            except:
                if st_date:
                    i = st_date.find(",")
                    return st_date[i - 4:i]
                else:
                    return st_date
            return str(dt.year)

    def get_album_image_url(self, artist, title, size=pylast.COVER_LARGE):
        if not self.connect():
            return None
        return self.cache.get_album_image_url(artist, title)

    def love(self, bean):
        track = self.cache.get_track(bean.artist, bean.title)
        track.love()
        logging.debug("I love this track %s-%s" % (bean.artist, bean.title))
