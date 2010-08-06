#!/bin/bash
sudo apt-get remove foobnix
cd ../
sudo python setup.py install --record files.txt
cat files.txt | sudo xargs rm -rf
