'''
Created on Nov 9, 2013

@author: ivan
'''
import unittest
from foobnix.thirdparty import pylast
from foobnix.fc.fc_base import FCBase
from foobnix.thirdparty.pylast import Artist

API_KEY = FCBase().API_KEY
API_SECRET = FCBase().API_SECRET
username = FCBase().lfm_login
password_hash = pylast.md5(FCBase().lfm_password)

class Test(unittest.TestCase):

    def test_pylast(self):
        network = pylast.get_lastfm_network(api_key=API_KEY,
                                                     api_secret=API_SECRET,
                                                     username=username,
                                                     password_hash=password_hash)
        artist = network.get_artist("Madonna");
        summary = artist.get_bio_summary()
        print "========="
        print summary

