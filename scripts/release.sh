#!/bin/bash -e

rev=$1
version=$2

[ -n "$rev" ]
[ -n "$version" ]

# Tag the trunk revision as the released version

svn copy -m "release trunk revision $rev as sonata $version" http://svn.berlios.de/svnroot/repos/sonata/trunk/"@$rev" http://svn.berlios.de/svnroot/repos/sonata/tags/$version

# Create archive, removing:
#   - website directory

svn export http://svn.berlios.de/svnroot/repos/sonata/tags/$version sonata-$version

rm -R sonata-$version/website/

tar zcvf sonata-$version.tar.gz sonata-$version
tar jcf sonata-$version.tar.bz2 sonata-$version

rm -R sonata-$version/
