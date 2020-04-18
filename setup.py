#!/usr/bin/env python

import os
import glob
import shutil

from distutils.core import setup, Command
from test.all import run_all_tests

if os.name == 'nt':
    import py2exe   #@UnresolvedImport @UnusedImport

from foobnix.version import FOOBNIX_VERSION
VERSION = FOOBNIX_VERSION

data_files = [
    ('share/applications', glob.glob('share/applications/*.desktop')),
    ('share/pixmaps', glob.glob('share/pixmaps/*.*')),
    ('share/foobnix/images', glob.glob('share/foobnix/images/*.*')),
    ('share/foobnix/images/theme', glob.glob('share/foobnix/images/theme/*.*')),
    ('share/foobnix/radio', glob.glob('share/foobnix/radio/*.*')),
    ('share/man/man1', glob.glob('docs/*')),
]

MO_DIR = "dist/"
if os.path.exists(MO_DIR):
    shutil.rmtree(MO_DIR)

if os.name != 'nt':
    LANGS = glob.glob("po/*.po")
    if not os.path.exists(MO_DIR):
        os.mkdir(MO_DIR)
    for lang in LANGS:
        lang = lang.replace(".po", "")
        lang = lang.replace("po/", "")

        if not os.path.exists(MO_DIR + 'share/locale/%s/LC_MESSAGES' % lang):
            os.makedirs(MO_DIR + 'share/locale/%s/LC_MESSAGES' % lang)

        mofile = MO_DIR + 'share/locale/%s/LC_MESSAGES/foobnix.mo' % lang
        pofile = "po/" + lang + ".po"

        os.system("msgfmt %s -o %s" % (pofile, mofile))
        data_files.append(('share/locale/%s/LC_MESSAGES' % lang, [mofile]))

        #data_files.append(('/usr/share/locale/%s/LC_MESSAGES' % lang, ['mo/%s/foobnix.mo' % lang]))

    version = open("foobnix/version.py", "wt")
    version.write("FOOBNIX_VERSION='%s'" % VERSION)
    version.close()

shutil.copyfile("foobnix.py", "foobnix/foobnix")


class test_cmd(Command):
    description = "run automated tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if not run_all_tests():
            raise SystemExit("Test failures are listed above.")


setup(name='foobnix',
      version=VERSION,
      license="GNU GPLv3",
      description='Foobnix GTK+ music player',
      author='Ivan Ivanenko',
      author_email='ivan.ivanenko@gmail.com',
      url='www.foobnix.com',
      classifiers=[
          'Development Status ::  Beta',
          'Environment :: X11 Applications',
          'Intended Audience :: End Users/Desktop',
          'License :: GNU General Public License (GPL)',
          'Operating System :: Linux',
          'Programming Language :: Python',
          'Topic :: Multimedia :: Sound :: Players',
      ],
      packages=[
          "foobnix",
          "foobnix.dm",
          "foobnix.eq",
          "foobnix.fc",
          "foobnix.helpers",
          "foobnix.playlists",
          "foobnix.preferences",
          "foobnix.preferences.configs",
          "foobnix.gui",
          "foobnix.gui.about",
          "foobnix.gui.controls",
          "foobnix.gui.engine",
          "foobnix.gui.model",
          "foobnix.gui.notetab",
          "foobnix.gui.perspectives",
          "foobnix.gui.service",
          "foobnix.gui.treeview",
          "foobnix.thirdparty",
          "foobnix.util",
      ],
      scripts=['foobnix/foobnix'],
      cmdclass={"test": test_cmd},
      data_files=data_files,
      windows=[
          {
              "script": "foobnix.py",
              "icon_resources": [(0, os.path.join('foobnix', 'pixmaps', 'foobnix.ico'))]
          }],
      options={
          'py2exe': {
              'includes': ('cairo, pango, pangocairo, atk, gio, pygst, gst, simplejson, chardet')
          }
      }
)

if os.name != 'nt':
    os.remove("foobnix/foobnix")
    if os.path.exists("build"):
        shutil.rmtree("build")
