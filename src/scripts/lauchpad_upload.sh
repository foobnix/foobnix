#!/bin/bash
pwd
rm -rf ../../build/*.*
cd ../

python setup.py build
#python setup.py test

echo -n "Tests finished > "
read text

pwd
source foobnix/version.py
echo $FOOBNIX_VERSION

echo "Create folder" ../build/foobnix_$FOOBNIX_VERSION
cp -r . ../build/foobnix_$FOOBNIX_VERSION

export DEBFULLNAME="Ivan Ivanenko"
export DEBEMAIL="ivan.ivanenko@gmail.com"

cp -r scripts/debian ../build/foobnix_$FOOBNIX_VERSION/debian
cd ../build

#LIST=("natty" "lucid" "maverick")
LIST=("natty")

for UBUNTU in ${LIST[@]}
do
	V_RELEASE=${RELEASE}${UBUNTU:0:1}
	echo "Deleting content of the folder", $UBUNTU
	pwd
	rm -rf foobnix_*_*
	rm -rf foobnix*.dsc
	rm -rf foobnix*.tar.gz
	rm -rf foobnix_$FOOBNIX_VERSION/debian/changelog
	cd foobnix_$FOOBNIX_VERSION/debian/
	python ../../../src/scripts/changelog_gen.py ${FOOBNIX_VERSION}${UBUNTU:0:1} $UBUNTU
	cd ../
	
	#dch -e
	
	debuild -S -sd -kB8C27E00
	
	#debuild -us -uc
	
	cd ../	
	dput ppa:foobnix-player/foobnix foobnix_${FOOBNIX_VERSION}${UBUNTU:0:1}_source.changes
	#read text
done

rm -rf foobnix_*
rm -rf foobnix*.dsc
rm -rf foobnix*.tar.gz
rm -rf foobnix_$FOOBNIX_VERSION/debian/changelog
