#!/bin/bash
if [ "$(whoami)" != "root" ]; then
	echo "Sorry, you are not root. try 'sudo install.sh'"
	exit 1
fi

python setup.py install
