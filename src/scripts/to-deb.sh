#!/bin/sh
cd ../

python setup.py install --record files.txt
cat files.txt | sudo xargs rm -rf

checkinstall \
-y \
--install=no \
--deldoc=yes \
--pkgname=foobnix \
--pkgversion=0.1.0 \
--pkgrelease=2  \
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