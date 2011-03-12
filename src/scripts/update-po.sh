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

POF=`pwd`/po/POTFILES.in

rm $POF
touch $POF

LIST=(
"foobnix"
"foobnix.cue"
"foobnix.dm"
"foobnix.eq"
"foobnix.fc"
"foobnix.helpers"
"foobnix.preferences"
"foobnix.preferences.configs"
"foobnix.regui"
"foobnix.regui.about"
"foobnix.regui.controls"
"foobnix.regui.engine"
"foobnix.regui.model"
"foobnix.regui.notetab"
"foobnix.regui.service"
"foobnix.regui.treeview"
"foobnix.thirdparty"
"foobnix.thirdparty.google"
"foobnix.util"
)


for NAME in ${LIST[@]}
do
	writelines $POF ./${NAME//.//}/
done

writelines $POF ./foobnix/util/


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
