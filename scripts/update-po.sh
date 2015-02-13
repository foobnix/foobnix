#!/bin/bash

writelines() {
   cd $2
   for i in *.py
     do
       echo $2${i} >> $1
    done
    cd -
}

cd ../
BASE=`pwd`
echo $BASE

cd $BASE
rm -rf po
bzr branch lp:foobnix po

POF=`pwd`/po/POTFILES.in

rm $POF
touch $POF

LIST=(
"foobnix"
"foobnix.dm"
"foobnix.eq"
"foobnix.fc"
"foobnix.helpers"
"foobnix.preferences"
"foobnix.preferences.configs"
"foobnix.gui"
"foobnix.gui.about"
"foobnix.gui.controls"
"foobnix.gui.engine"
"foobnix.gui.model"
"foobnix.gui.notetab"
"foobnix.gui.perspectives"
"foobnix.gui.service"
"foobnix.gui.treeview"
"foobnix.util"
)

for NAME in ${LIST[@]}
do
	writelines $POF ./${NAME//.//}/
done

cd $BASE/po

intltool-update -p
mv untitled.pot foobnix.pot

for i in *.po
  do
  if [ "$i" = "messages.po" ]
    then
    continue
  fi
  echo Updating ${i}...
  intltool-update "${i%*.po}"
  echo
done

echo Cleaning up...
rm untitled.pot

cd $BASE/po
echo Launchpad commit to lp:foobnix

bzr whoami
bzr commit -m "Update foobnix.po"
bzr push lp:foobnix

rm -rf $BASE/po
cd $BASE
echo Get Last transtations
bzr branch lp:~foobnix-team/+junk/foobnix po
