#!/bin/bash
if [ "$(whoami)" != "root" ]; then
	echo "Sorry, you are not root. try 'sudo uninstall.sh'"
	exit 1
fi

python setup.py install --record files.txt
cat files.txt | xargs rm -rf
rm files.txt
