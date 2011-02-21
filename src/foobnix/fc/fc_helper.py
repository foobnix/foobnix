#-*- coding: utf-8 -*-
'''
Created on 21 февр. 2011

@author: ivan
'''
from __future__ import with_statement
import os
import logging
import cPickle

CONFIG_DIR = os.path.expanduser("~") + "/.config/foobnix"
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)
COVERS_DIR = os.path.join(CONFIG_DIR , 'Covers', '');


class FCStates:    
    def save(self, fc, file):
        #if in_thread:
        #    thread.start_new_thread(FCHelper().save, (fc,))
        #else:
        FCHelper().save(fc, file)
        
    def load(self, fc, file):
        """restore from file"""
        object = FCHelper().load(file)
        if object:
            dict = object.__dict__
            keys = fc.__dict__.keys()
            for i in dict:
                try:
                    if i in keys:
                        setattr(fc, i, dict[i])
                except Exception, e:
                    logging.warn("Value not found" + str(e))
                    return False
        return True

    def info(self):
        FCHelper().print_info(self)

    def delete(self, file_path):
        FCHelper().delete(file_path)
        
class FCHelper():
    def __init__(self):
        pass

    def save(self, object, file_path):
        save_file = file(file_path, 'w')
        try:
            cPickle.dump(object, save_file)
        except Exception, e:
            logging.error("Erorr dumping pickle conf" + str(e))
        save_file.close()
        logging.debug("Config save")
        self.print_info(object);


    def load(self, file_path):
        if not os.path.exists(file_path):
            logging.debug("Config file not found" + file_path)
            return None

        with file(file_path, 'r') as load_file:
            try:
                load_file = file(file_path, 'r')
                pickled = load_file.read()

                object = cPickle.loads(pickled)
                logging.debug("Config loaded")
                self.print_info(object);
                return object
            except Exception, e:
                logging.error("Error load config" + str(e))
        return None


    def delete(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    def print_info(self, object):
        dict = object.__dict__
        for i in object.__dict__:
            logging.debug(i + str(dict[i])[:500])        
