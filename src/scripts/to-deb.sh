#!/bin/sh
pwd
rm  ../../deb/*.deb
rm ../../deb/*.tar.gz
cd ../

sudo python setup.py install --record files.txt
cat files.txt | sudo xargs rm -rf

VERSION=0.1.8
RELEASE=3

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
--requires="python-mutagen, python-simplejson, python-setuptools,  gstreamer0.10-plugins-good,  gstreamer0.10-plugins-ugly, gstreamer0.10-ffmpeg" \
--maintainer="Ivan Ivanenko ivan.ivanenko@gmail.com" \
python setup.py install

tar cvzf ../deb/foobnix_$VERSION-$RELEASE.tar.gz ../src/ --exclude=.svn

#Releas tar.gz
pwd
cd scripts

./upload.py --summary=foobnix_$VERSION-$RELEASE.tar.gz --project=foobnix --user=ivan.ivanenko@gmail.com --labels=Featured ../../deb/foobnix_$VERSION-$RELEASE.tar.gz
./upload.py --summary=foobnix_$VERSION-2_i386.deb --project=foobnix --user=ivan.ivanenko@gmail.com --labels=Featured ../../deb/foobnix_$VERSION-3_i386.deb
