'''
Created on Oct 27, 2010

@author: ivan
'''
import threading
from foobnix.util import LOG
from urllib import FancyURLopener
from foobnix.util.const import DOWNLOAD_STATUS_COMPLETED, \
    DOWNLOAD_STATUS_DOWNLOADING, DOWNLOAD_STATUS_INACTIVE
import os
from foobnix.util.time_utils import size2text
from foobnix.util.fc import FC
from foobnix.util.file_utils import get_file_extension

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
            LOG.error(e)
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
        
        if bean.artist:
            path = FC().online_save_to_folder + "/" + bean.artist 
            to_file = os.path.join(path, bean.get_display_name() + ext)            
        else:
            path = FC().online_save_to_folder
            to_file = os.path.join(path, bean.get_display_name() + ext)        
        
        if not os.path.exists(path):
            os.makedirs(path)
        
        to_file_tmp = to_file + ".tmp"
        
        if os.path.exists(to_file_tmp):
            bean.status = DOWNLOAD_STATUS_INACTIVE
            bean.to_file = to_file
            update(bean)
            return  None
        
        if os.path.exists(to_file):
            bean.status = DOWNLOAD_STATUS_COMPLETED
            bean.to_file = to_file
            update(bean)
            return None
        
        bean.save_to = to_file        
        file = open(to_file_tmp, "wb")
        
        data = True
        
        """begin download"""
        self.bean.status = DOWNLOAD_STATUS_DOWNLOADING
        self.update(self.bean)
        
        
        while data:
            data = remote.read(block_size)
            if data:
                block_count += 1
                file.write(data)
                #time.sleep(0.1)
                persent = block_count * block_size * 100.0 / remote_size
                if block_count % 50 == 0:
                    bean.persent = persent
                    update(bean)
                    
        """update file info on finish"""                    
        
        os.rename(to_file_tmp, to_file)
        bean.status = DOWNLOAD_STATUS_COMPLETED
        bean.to_file = to_file
        bean.persent = 100
        update(bean)
