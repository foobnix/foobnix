#!/usr/bin/env python
import os, glob
import shutil
from distutils.core import setup, Command
from test.all import run_all_tests

VERSION = "0.2.3"
RELEASE = "1"
LANGS = ('ru', 'zh_CN', "es", "it")

if not os.path.exists("mo/"):
    os.mkdir("mo/")
for lang in LANGS:
    pofile = "po/" + lang + ".po"
    mofile = "mo/" + lang + "/foobnix.mo"
    if not os.path.exists("mo/" + lang + "/"):
        os.mkdir("mo/" + lang + "/")
    print "generating", mofile    
    os.system("msgfmt %s -o %s" % (pofile, mofile))
    
    


version = file("foobnix/version.py", "wt")
version.write("""
FOOBNIX_VERSION="%(VERSION)s-%(RELEASE)s"
VERSION="%(VERSION)s"
RELEASE="%(RELEASE)s"
""" % {'RELEASE':RELEASE, 'VERSION':VERSION})
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
                "foobnix.cue",
                "foobnix.dm",
                "foobnix.eq",
                "foobnix.helpers",
                "foobnix.preferences",
                "foobnix.preferences.configs",
                "foobnix.regui",
                "foobnix.regui.about",
                "foobnix.regui.controls",
                "foobnix.regui.engine",
                "foobnix.regui.model",
                "foobnix.regui.notetab",
                "foobnix.regui.service",
                "foobnix.regui.treeview",
                "foobnix.thirdparty",
                "foobnix.thirdparty.google",
                "foobnix.util",
                ],
        scripts=['foobnix/foobnix'],
        cmdclass={"test": test_cmd},
        data_files=[
                    ('share/foobnix', ['README']),
                    ('share/foobnix', ['CHANGELOG']),
                    ('share/applications', ['foobnix.desktop']),
                    ('share/pixmaps/theme', glob.glob('foobnix/pixmaps/theme/*')),
                    ('share/pixmaps', glob.glob('foobnix/pixmaps/*.png')),
                    ('share/pixmaps', glob.glob('foobnix/pixmaps/*.jpg')),
                    ('share/pixmaps', glob.glob('foobnix/pixmaps/*.gif')),
                    ('share/pixmaps', glob.glob('foobnix/pixmaps/*.svg')),
                    ('share/foobnix/radio', glob.glob('radio/*')),
                    ('share/man/man1', ['foobnix.1']),
                    ('/usr/share/locale/ru/LC_MESSAGES', ['mo/ru/foobnix.mo']),
                    ('/usr/share/locale/es/LC_MESSAGES', ['mo/es/foobnix.mo']),
                    ('/usr/share/locale/it/LC_MESSAGES', ['mo/it/foobnix.mo']),
                    ('/usr/share/locale/zh_CN/LC_MESSAGES', ['mo/zh_CN/foobnix.mo'])                   
                    ]
        )

os.remove("foobnix/foobnix")
if os.path.exists("mo"):
    shutil.rmtree("mo")
if os.path.exists("build"):
    shutil.rmtree("build")
