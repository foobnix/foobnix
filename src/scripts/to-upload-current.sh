#!/bin/bash
source /home/ivan/password
cd ../
pwd
LANG=en
#REV=$(svnversion 2>/dev/null)
REV='today'
echo "REVISION" 
echo $REV
svn info > svn_info.txt
date >> svn_info.txt


rm -rf ../deb/*.*

cp -r . ../foobnix_$REV
tar cvzf ../deb/foobnix_$REV.tar.gz ../foobnix_$REV --exclude=.svn --exclude=*.pyc 
rm -rf ../foobnix_$REV


#python scripts/upload.py --summary=foobnix_$REV.tar.gz --project=foobnix --user=ivan.ivanenko@gmail.com --password=$PASSWORD ../deb/foobnix_$REV.tar.gz
#rm -rf ../deb/foobnix_$REV.tar.gz

rm  svn_info.txt

cd ../deb
svn commit (c) ../deb/foobnix_$REV.tar.gz 

