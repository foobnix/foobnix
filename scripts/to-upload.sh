#!/bin/bash
pwd
source ../version
source /home/ivan/password


FILE_PATH=../../deb/

FILE_TAR_GZ=foobnix_$VERSION-$RELEASE.tar.gz
FILE_DEB_32=foobnix_$VERSION-${RELEASE}_i386.deb 
FILE_DEB_64=foobnix_$VERSION-${RELEASE}_amd64.deb

LIST=($FILE_TAR_GZ $FILE_DEB_32 $FILE_DEB_64) 


for FILE_NAME in ${LIST[@]}
do
	if [ -f ${FILE_PATH}${FILE_NAME} ]
	then
		echo file exists ${FILE_PATH}${FILE_NAME}
		echo ./upload.py --summary=${FILE_NAME} --project=foobnix --user=ivan.ivanenko@gmail.com --password=$PASSWORD --labels=Featured ${FILE_PATH}${FILE_NAME}
		./upload.py --summary=${FILE_NAME} --project=foobnix --user=ivan.ivanenko@gmail.com --password=$PASSWORD --labels=Featured ${FILE_PATH}${FILE_NAME}
	fi
done

