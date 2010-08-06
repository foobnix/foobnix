#!/bin/bash
pwd
rm  ../../deb/*.deb
rm ../../deb/*.tar.gz
cd ../

pwd
source version

sudo python setup.py install --record files.txt
cat files.txt | sudo xargs rm -rf


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
--requires="python-mutagen, python-simplejson, python-setuptools,  gstreamer0.10-plugins-good,  gstreamer0.10-plugins-ugly, gstreamer0.10-ffmpeg, python-gst0.10" \
--maintainer="Ivan Ivanenko ivan.ivanenko@gmail.com" \
python setup.py install

pwd
cp -r . ../foobnix_$VERSION-$RELEASE
echo "Create archive"
tar cvzf ../deb/foobnix_$VERSION-$RELEASE.tar.gz ../foobnix_$VERSION-$RELEASE --exclude=.svn
rm -rf ../foobnix_$VERSION-$RELEASE

#Releas tar.gz
pwd
cd scripts

#./upload.py --summary=foobnix_$VERSION-$RELEASE.tar.gz --project=foobnix --user=ivan.ivanenko@gmail.com --labels=Featured ../../deb/foobnix_$VERSION-$RELEASE.tar.gz
#./upload.py --summary=foobnix_$VERSION-${RELEASE}_i386.deb --project=foobnix --user=ivan.ivanenko@gmail.com --labels=Featured ../../deb/foobnix_$VERSION-${RELEASE}_i386.deb
