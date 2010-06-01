#!/bin/sh
cd ../

python setup.py install --record files.txt
cat files.txt | sudo xargs rm -rf

VERSION=0.1.5
RELEASE=1

checkinstall \
-y \
--install=no \
--deldoc=yes \
--pkgname=foobnix \
--pkgversion=$VERSION \
--pkgrelease=$RELEASE  \
--pkglicense=GPL \
--pkggroup=foobnix \
--pkgsource=. \
--pakdir=../deb \
--deldoc=yes \
--deldesc=yes \
--delspec=yes \
--backup=no \
--requires="python-mutagen, python-simplejson, python-setuptools" \
--maintainer="Ivan Ivanenko ivan.ivanenko@gmail.com" \
python setup.py install

tar cvzf ../deb/foobnix_$VERSION-$RELEASE.tar.gz ../src/ --exclude=.svn