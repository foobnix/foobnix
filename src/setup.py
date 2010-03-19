#!/usr/bin/env python

from distutils.core import setup
import glob
import os

setup(name='FoobNix',
      version='1.0',
      description='Nice Music Player',
      author='Ivan Ivanenko',
      author_email='ivan.ivanenko@gmail.com',
      url='http://code.google.com/p/foobnix/',
      package_data={'foobnix': ['glade/*.glade']},

      packages=[".",
                "foobnix", 
                "foobnix.application",
                "foobnix.directory",
                "foobnix.glade",
                "foobnix.model",                
                "foobnix.online",
                "foobnix.player",
                "foobnix.playlist",
                "foobnix.preferences",
                "foobnix.radio",
                "foobnix.tryicon",
                "foobnix.util",
                "foobnix.window",
                ],  
        scripts = ['foobnix.py'],
        py_modules=[".",
                "foobnix", 
                "foobnix.application",
                "foobnix.directory",
                "foobnix.glade",
                "foobnix.model",                
                "foobnix.online",
                "foobnix.player",
                "foobnix.playlist",
                "foobnix.preferences",
                "foobnix.radio",
                "foobnix.tryicon",
                "foobnix.util",
                "foobnix.window",
                ]    
     )


