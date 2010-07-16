#!/bin/sh
cd ../

python setup.py install --record files.txt
cat files.txt | sudo xargs rm -rf
rm files.txt
