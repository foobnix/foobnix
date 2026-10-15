Foobnix music player
=====================
Foobnix is a free music player written on Python 3

http://www.foobnix.com

CUE, wv and iso.wv support, probably the best among Linux music players
Supports MP3, MP4, AAC, CD Audio, WMA, OGG, FLAC, WavPack, WAV, Musepack and many more formats
Online Music Search and Listen for Free
5000+ Internet Radio Stations

## Main features

  * CUE, wv and iso.wv support, probably the best among Linux music players
  * Supports MP3, MP4, AAC, CD Audio, WMA, OGG, FLAC, WavPack, WAV, Musepack and many more formats
  * 10-band equalizer with presets support
  * Last.FM integration: search in related songs, artists, covers and other
  * vk.com also supported: your and your friends' music, songs search and playback
  * Lyrics search by lyricsmania.com and megalyrics.ru

## Gentoo

Community-maintained **amd64** packages are available in the
[vitaly-zdanevich overlay](https://github.com/vitaly-zdanevich/gentoo-overlay).
Run the repository setup and installation commands as root:

```bash
emerge --ask app-eselect/eselect-repository dev-vcs/git
eselect repository add vitaly-zdanevich-overlay git https://github.com/vitaly-zdanevich/gentoo-overlay.git
emaint sync -r vitaly-zdanevich-overlay
```

The release ebuild uses the `~amd64` testing keyword. Add this entry to
`/etc/portage/package.accept_keywords`, or to a file inside that directory:

```text
media-sound/foobnix::vitaly-zdanevich-overlay ~amd64
```

Install the release from source:

```bash
emerge --ask media-sound/foobnix::vitaly-zdanevich-overlay
```

For the prepackaged release, replace `media-sound/foobnix` with
`media-sound/foobnix-bin` in both the keyword entry and the install command.
This variant repackages deb-multimedia's Debian package and still uses system
Python and GTK. The source and binary packages cannot be installed together.

To build the latest Git checkout instead, add this keyword entry:

```text
=media-sound/foobnix-9999::vitaly-zdanevich-overlay **
```

Then install the live version:

```bash
emerge --ask '=media-sound/foobnix-9999::vitaly-zdanevich-overlay'
```

Both packages enable translations with the `nls` USE flag by default. The `X`
flag pulls in Keybinder for global keyboard shortcuts; the source package
also offers `test` to run its offline tests. If Portage requests additional
keyword or USE changes for dependencies, follow Gentoo's
[keyword guide](https://wiki.gentoo.org/wiki/Knowledge_Base:Accepting_a_keyword_for_a_single_package)
and [USE flag guide](https://wiki.gentoo.org/wiki/USE_flag). See the
[repository guide](https://wiki.gentoo.org/wiki/Eselect-repository) for overlay
configuration details.

Launch Foobnix from the application menu or run `foobnix` as your normal user.
Local playback is tested; legacy Last.fm and VK integrations may not work.

## Depends

  Python 3+
  Gtk 3+
	python-simplejson, python-mutagen, python-pylast

## Run:
    
    python foobnix.py

## To restore default settings:
  
    rm -f ~$USER/.config/foobnix-3/foobnix_conf.pkl

