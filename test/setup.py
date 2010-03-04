#!/usr/bin/python

from distutils.core import setup

setup(
    name='olaf',
    scripts=['olaf'],
    py_modules=['olaf'],
    data_files=[('share/olaf', ['olaf.glade', 'unknown.png'])]
    )

