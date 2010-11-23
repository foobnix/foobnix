#!/bin/bash

#debuild -us -uc
debuild -S -sd -kD2628E50
#dh_make -c gpl -s -b -p foobnix-0.2.2-3
dput ppa:foobnix-player/foobnix foobnix_0.2.2-3_source.changes
