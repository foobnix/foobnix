Foobnix music player
=====================

What is Foobnix?
----------------
Foobnix is a free music player written on Python.

Main features
-------------
  * CUE, wv and iso.wv support, probably the best among Linux music players
  * Supports MP3, MP4, AAC, CD Audio, WMA, OGG, FLAC, WavPack, WAV, Musepack and many more formats
  * 10-band equalizer with presets support
  * Last.FM integration: search in related songs, artists, covers and other
  * vk.com also supported: your and your friends' music, songs search and playback
  * Lyrics search by lyricsmania.com and megalyrics.ru

Installation
------------

To install from deb or tar.gz please visit https://launchpad.net/~foobnix-team/+archive/foobnix-player/+packages

To install from Ubuntu PPA:

    sudo add-apt-repository ppa:foobnix-team/foobnix-player
    sudo apt-get update
    sudo apt-get install foobnix

To install from sources:

    sudo python setup.py install
    # or
    sudo make install
    # or
    ./install

To uninstall:

    sudo make uninstall
    # or
    ./uninstall

To restore default settings:

    rm -f ~$USER/.config/foobnix/foobnix_conf.pkl

Depends

	python-chardet, python-gi, python-simplejson, python-mutagen, gstreamer1.0-plugins-good, gir1.2-gstreamer-1.0, gir1.2-gtk-3.0, gir1.2-webkit-3.0, gir1.2-soup-2.4, gir1.2-keybinder-3.0, gir1.2-notify-0.7, gettext

Recommends:
 
	gstreamer1.0-plugins-bad, gstreamer1.0-plugins-ugly, gstreamer1.0-libav, gstreamer1.0-alsa, python-setuptools, fuseiso, python-notify, libmp3lame0, libfaac0, python-keybinder, ffmpeg

