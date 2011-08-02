#!/usr/bin/env python
import os, glob
import shutil
from distutils.core import setup, Command
from test.all import run_all_tests

if os.name == 'nt':
    import py2exe #@UnresolvedImport @UnusedImport

VERSION = "2.5.21"

data_files = [
    ('share/foobnix', ['README']),
    ('share/foobnix', ['CHANGELOG']),
    ('share/applications', ['foobnix.desktop']),
    ('share/pixmaps/theme', glob.glob('foobnix/pixmaps/theme/*')),
    ('share/pixmaps', glob.glob('foobnix/pixmaps/*.png')),
    ('share/pixmaps', glob.glob('foobnix/pixmaps/*.jpg')),
    ('share/pixmaps', glob.glob('foobnix/pixmaps/*.ico')),
    ('share/pixmaps', glob.glob('foobnix/pixmaps/*.gif')),
    ('share/pixmaps', glob.glob('foobnix/pixmaps/*.svg')),
    ('share/foobnix/radio', glob.glob('radio/*')),
    ('share/man/man1', ['foobnix.1']),
]


MO_DIR = "../dist/"
if os.path.exists(MO_DIR):
        shutil.rmtree(MO_DIR)


if os.name != 'nt':
    LANGS = glob.glob("po/*.po")
    if not os.path.exists(MO_DIR):
        os.mkdir(MO_DIR)
    for lang in LANGS:
        lang = lang.replace(".po", "")
        lang = lang.replace("po/", "")
        
        if not os.path.exists(MO_DIR+'share/locale/%s/LC_MESSAGES'% lang):
            os.makedirs(MO_DIR+'share/locale/%s/LC_MESSAGES'% lang)
        
        mofile = MO_DIR+'share/locale/%s/LC_MESSAGES/foobnix.mo'% lang
        pofile = "po/" + lang + ".po"
        
        print "generating", mofile    
        os.system("msgfmt %s -o %s" % (pofile, mofile))
        data_files.append(('share/locale/%s/LC_MESSAGES' % lang, [mofile]))
        
        #data_files.append(('/usr/share/locale/%s/LC_MESSAGES' % lang, ['mo/%s/foobnix.mo' % lang]))
    
    version = file("foobnix/version.py", "wt")
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
                "foobnix.fc",
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
                "foobnix.thirdparty.mutagen",
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
