'''
Created on Oct 27, 2010

@author: ivan
'''

from __future__ import with_statement

import os
import time
import logging
import threading
from foobnix.fc.fc import FC
from urllib import FancyURLopener
from foobnix.util.time_utils import size2text
from foobnix.util.file_utils import get_file_extension
from foobnix.util.bean_utils import get_bean_download_path
from foobnix.util.const import DOWNLOAD_STATUS_COMPLETED, \
    DOWNLOAD_STATUS_DOWNLOADING, DOWNLOAD_STATUS_INACTIVE


class Dowloader(threading.Thread):
    def __init__(self, update, bean, notify_finish):
        threading.Thread.__init__(self)
        self.update = update
        self.bean = bean
        self.notify_finish = notify_finish
    
    def run(self):
        try:
            self.download()
        except Exception, e:
            self.bean.status = DOWNLOAD_STATUS_INACTIVE
            self.update(self.bean)
            logging.error(e)
        finally:
            self.notify_finish() 
    
    def download(self):
        bean = self.bean 
        update = self.update 
        if not bean or not bean.path:            
            return None
         
        opener = FancyURLopener()
        remote = opener.open(bean.path)
        remote_size = 0
        
        if "Content-Length" in remote.headers:
            remote_size = int(remote.headers["Content-Length"])
            bean.size = size2text(remote_size) 
        
        block_size = 4096
        block_count = 0
        
        ext = get_file_extension(bean.path)
        
        path = FC().online_save_to_folder
        if not os.path.isdir(path):
            os.makedirs(path)
            
        if bean.save_to:
            to_file = os.path.join(bean.save_to, bean.text + ".mp3") 
        else:            
            to_file = get_bean_download_path(bean, FC().online_save_to_folder)
        
        if not os.path.exists(os.path.dirname(to_file)):
                os.makedirs(os.path.dirname(to_file))        
        
        to_file_tmp = to_file + ".tmp"
        
        if os.path.exists(to_file_tmp):
            bean.status = DOWNLOAD_STATUS_INACTIVE
            bean.to_file = to_file
            update(bean)
            return None
        
        if os.path.exists(to_file):
            bean.status = DOWNLOAD_STATUS_COMPLETED
            bean.to_file = to_file
            update(bean)
            return None
        
        bean.save_to = to_file        
        with file(to_file_tmp, "wb") as tmp_file:
            data = True
            
            """begin download"""
            self.bean.status = DOWNLOAD_STATUS_DOWNLOADING
            self.bean.path = to_file
            self.update(self.bean)

            while data:
                data = remote.read(block_size)
                if data:
                    block_count += 1
                    tmp_file.write(data)
                    #time.sleep(0.1)
                    persent = block_count * block_size * 100.0 / remote_size
                    if block_count % 50 == 0:
                        bean.persent = persent
                        update(bean)
        time.sleep(0.5)           
        """update file info on finish"""                    
        logging.debug("rename %s - %s" % (to_file_tmp, to_file))
        os.rename(to_file_tmp, to_file)
        bean.status = DOWNLOAD_STATUS_COMPLETED
        bean.to_file = to_file
        bean.persent = 100
        update(bean)
