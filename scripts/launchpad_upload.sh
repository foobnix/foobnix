#!/bin/bash
pwd
rm -rf ./build
mkdir ./build

## Global vars
PPA_NAME="ppa:foobnix-team/foobnix-player"
#PPA_NAME="ppa:popsul1993/ppa"

#export DEBFULLNAME="Ivan Ivanenko"
#export DEBEMAIL="ivan.ivanenko@gmail.com"

export DEBFULLNAME="Dmitry Kogura"
export DEBEMAIL="zavlab1@gmail.com"

#export DEBFULLNAME="Viktor Suprun"
#export DEBMAIL="popsul1993@gmail.com"

python setup.py build
#python setup.py test

echo -n "Tests finished > "

echo -n "Enter build number (default: 1): "
read BUILD
if [ -z $BUILD ] ; then BUILD=1 ; fi

pwd
source foobnix/version.py
echo $FOOBNIX_VERSION

echo "Create folder" ./build/foobnix_$FOOBNIX_VERSION
mkdir -p ./build/foobnix_$FOOBNIX_VERSION
FILES="dist docs foobnix po share test CHANGELOG COPYING README.md README Makefile *.py *.sh"
for F in $FILES ; do
    echo "copy $F..."
    cp -r ./$F ./build/foobnix_$FOOBNIX_VERSION
done

cp -r ./scripts/debian ./build/foobnix_$FOOBNIX_VERSION/debian

cd ./build

LIST=("oneiric" "natty" "maverick" "precise" "quantal" "raring")

for UBUNTU in ${LIST[@]}
do
	V_RELEASE=${RELEASE}${UBUNTU}
	echo "Deleting content of the folder", $UBUNTU
	pwd
	rm -rf foobnix_*_*
	rm -rf foobnix*.dsc
	rm -rf foobnix*.tar.gz
	rm -rf foobnix_$FOOBNIX_VERSION/debian/changelog
	cd foobnix_$FOOBNIX_VERSION/debian/
	python ../../../scripts/changelog_gen.py ${FOOBNIX_VERSION}${UBUNTU}${BUILD} $UBUNTU
	cd ../

	#dch -e

	#debuild -S -sd -kB8C27E00 # Ivan Ivanenko - old
	#debuild -S -sd -k316EC1F3 # Ivan Ivanenko
	debuild -S -sd -k707844CC # Dmitry Kogura
	#debuild -S -sd -kD4AD044A # Viktor Suprun


	#debuild -us -uc

	cd ../

	dput $PPA_NAME foobnix_${FOOBNIX_VERSION}${UBUNTU}${BUILD}_source.changes
    read text
done

cd ../
rm -rf build
echo "Done"
