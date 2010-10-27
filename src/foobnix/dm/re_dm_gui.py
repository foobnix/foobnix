'''
Created on Oct 26, 2010

@author: ivan
'''
import gtk
from foobnix.regui.controls.status_bar import StatusbarControls
from foobnix.regui.controls.playback import PlaybackControls
from foobnix.regui.base_controls import BaseFoobnixControls
from urllib import FancyURLopener
import threading
from foobnix.regui.treeview.dm_tree import DownloadManagerTreeControl
from foobnix.util.const import DOWNLOAD_STATUS_INACTIVE, DOWNLOAD_STATUS_ACTIVE,\
    DOWNLOAD_STATUS_COMPLETED, DOWNLOAD_STATUS_DOWNLOADING, DOWNLOAD_STATUS_ALL
from foobnix.regui.treeview.dm_nav_tree import DMNavigationTreeControl
import thread
import time
from foobnix.regui.model import FDModel

class DM(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_title("Download Manager")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_geometry_hints(self, min_width=900, min_height=800)
        self.set_resizable(False)
        
        vbox = gtk.VBox(False,0)
        
        controls = BaseFoobnixControls() 
        
        playback = PlaybackControls(controls)        
        statusbar = StatusbarControls(controls)
        
        paned = gtk.HPaned()
        paned.set_position(200)
        navigation = DMNavigationTreeControl("navigation", controls).set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        navigation.append(FDModel("All").add_artist("All").add_status(DOWNLOAD_STATUS_ALL))
        navigation.append(FDModel("Downloading").add_artist("Downloading").add_status(DOWNLOAD_STATUS_DOWNLOADING))
        navigation.append(FDModel("Completed").add_artist("Completed").add_status(DOWNLOAD_STATUS_COMPLETED))
        navigation.append(FDModel("Active").add_artist("Active").add_status(DOWNLOAD_STATUS_ACTIVE))
        navigation.append(FDModel("Inactive").add_artist("Inactive").add_status(DOWNLOAD_STATUS_INACTIVE))
        
        dm_list = DownloadManagerTreeControl(controls).set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        controls.dm = dm_list
        paned.pack1(navigation.scroll)
        paned.pack2(dm_list.scroll)
        
        vbox.pack_start(playback, False,True)
        vbox.pack_start(paned,True, True)
        vbox.pack_start(statusbar,False, True)
        
        dm_list.append(FDModel("Madonna - Sorry","/home/ivan/b515c44700b4.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        dm_list.append(FDModel("Madonna - Frozen","/home/ivan/b515c44700b4.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        dm_list.append(FDModel("Madonna - Live","/home/ivan/b515c44700b4.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        dm_list.append(FDModel("Madonna - GO","/home/ivan/b515c44700b4.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        dm_list.append(FDModel("Madonna - Jonny","/home/ivan/b515c44700b4.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        dm_list.append(FDModel("Madonna - Real","/home/ivan/b515c44700b4.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        dm_list.append(FDModel("Madonna - mamba","/home/ivan/b515c44700b4.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        dm_list.append(FDModel("Madonna - humamba","/home/ivan/b515c44700b4.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        
        stats = dm_list.get_status_statisctics()
        print stats
        #navigation.update_statistics(stats)
        
        self.add(vbox)
        self.show_all()
        
        thread.start_new_thread(self.dowloader,(dm_list,))
        #self.dowloader(dm_list)
    
    def dowloader(self,dm_list):
        semaphore =threading.Semaphore(2)
        bean = True   
        while True:
            print "check"
            time.sleep(1)
            bean = dm_list.get_next_bean_to_dowload()
            if bean:
                semaphore.acquire()            
                func = dm_list.update_bean_info
                def task():
                    dowload(func, bean, semaphore)
                thread.start_new_thread(task,())
    
def size2text(size):
    if size > 1024*1024*1024:
        return "%.2f Gb" % (size / (1024*1024*1024.0))
    if size > 1024*1024:
        return "%.2f Mb" % (size / (1024*1024.0))
    if size > 1024:
        return "%.2f Kb" % (size / 1024.0)
    return size
    
def dowload(func, bean, semaphore):  
    if not bean:
        return None
     
    opener = FancyURLopener()
    remote = opener.open(bean.path)
    remote_size = 0
    
    if "Content-Length" in remote.headers:
        remote_size = int(remote.headers["Content-Length"])
        bean.size = size2text(remote_size) 
    
    block_size = 4096
    block_count = 0
    
    to_file = bean.get_display_name() + ".mp3.tmp"
    bean.save_to = to_file        
    file = open(to_file,"wb")
    
    data = True
    bean.status = DOWNLOAD_STATUS_DOWNLOADING
    while data:
        data = remote.read(block_size)
        if data:
            block_count += 1
            file.write(data)
            
            #dm_list.set_text(report(block_count, block_size, remote_size))
            persent = block_count * block_size * 1.0 / remote_size
            persent = persent * 100
            if int(persent) % 2 == 0:
                print persent 
                bean.persent = persent
                gtk.gdk.threads_enter()                    
                func(bean)
                gtk.gdk.threads_leave()
    
    bean.status = DOWNLOAD_STATUS_COMPLETED
    func(bean)
    print "finished"
    semaphore.release()

dm = DM()
gtk.gdk.threads_init()
gtk.main()