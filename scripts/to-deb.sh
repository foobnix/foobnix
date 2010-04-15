#!/bin/sh
cd ../

checkinstall \
-y \
--install=no \
--deldoc=yes \
--pkgname=foobnix \
--pkgversion=0.1.0 \
--pkgrelease=1  \
--pkglicense=GPL \
--pkggroup=foobnix \
--pkgsource=. \
--pakdir=../deb \
--deldoc=yes \
--deldesc=yes \
--delspec=yes \
--backup=no \
--requires="python-mutagen, python-simplejson" \
--maintainer="Ivan Ivanenko ivan.ivanenko@gmail.com" \
python setup.py install