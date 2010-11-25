#!/bin/bash
pwd
rm -rf ../../build/*.*
cd ../

#python setup.py build

pwd
source foobnix/version.py
echo $FOOBNIX_VERSION

echo "Create folder" ../build/foobnix_$FOOBNIX_VERSION
cp -r . ../build/foobnix_$FOOBNIX_VERSION

export DEBFULLNAME="Ivan Ivanenko"
export DEBEMAIL="ivan.ivanenko@gmail.com"

cp -r scripts/debian ../build/foobnix_$FOOBNIX_VERSION/debian
cd ../build


LIST=("lucid" "maverick" "natty")

for UBUNTU in ${LIST[@]}
do
	rm -rf foobnix*_source*
	rm -rf foobnix*.dsc
	rm -rf foobnix*.tar.gz
	cd foobnix_$FOOBNIX_VERSION/debian
	python ../../../src/scripts/changelog_gen.py $VERSION $RELEASE $UBUNTU
	cd ../
	
	#dch -e
	
	debuild -S -sd -kD2628E50
	
	#debuild -us -uc
	
	cd ../	
	dput ppa:foobnix-player/foobnix foobnix_${FOOBNIX_VERSION}_source.changes
done