#
# Makefile for Foobnix
#
PYVER=`python -c "import sys; print sys.version[:3]"`
PREFIX ?= /usr/local
DESTDIR ?= ./

all:
	python setup.py build

test:
	python setup.py test
	
tarball:
	python setup.py sdist
	mv dist/foobnix-*.tar.gz $(DESTDIR)

install:
	python setup.py install --prefix=$(PREFIX)

clean:
	python setup.py clean
	rm -rf ./build
	find . -name *.pyc -exec rm {} \;

uninstall:
	-rm $(PREFIX)/bin/foobnix
	-rm -r $(PREFIX)/lib/python${PYVER}/dist-packages/foobnix
	-rm -r $(PREFIX)/lib/python${PYVER}/dist-packages/foobnix-*.egg-info
	-rm -r $(PREFIX)/share/foobnix
	-find ${PREFIX}/share/locale -name foobnix.mo -exec rm {} \;
	-rm $(PREFIX)/share/applications/foobnix.desktop
	-rm $(PREFIX)/share/pixmaps/foobnix*
	-rm $(PREFIX)/share/man/man1/foobnix*