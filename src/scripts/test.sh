#!/bin/bash
LIST=(
"foobnix"
"foobnix.cue"
"foobnix.util"
)


for NAME in ${LIST[@]}
do
	echo +${NAME}+
done
