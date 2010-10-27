'''
Created on Oct 26, 2010

@author: ivan
'''
import gtk
import threading
from foobnix.regui.treeview.dm_tree import DownloadManagerTreeControl
from foobnix.util.const import DOWNLOAD_STATUS_INACTIVE, DOWNLOAD_STATUS_ACTIVE,\
    DOWNLOAD_STATUS_COMPLETED, DOWNLOAD_STATUS_DOWNLOADING, DOWNLOAD_STATUS_ALL
from foobnix.regui.treeview.dm_nav_tree import DMNavigationTreeControl
import thread
import time
from foobnix.regui.model import FDModel, FModel
from foobnix.dm.dm_dowloader import Dowloader

class DM(gtk.Window):
    def __init__(self, controls):
        self.controls = controls
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_title("Download Manager")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_geometry_hints(self, min_width=900, min_height=800)
        self.set_resizable(False)
        vbox = gtk.VBox(False,0)
         
        
        #playback = PlaybackControls(None)        
        
        paned = gtk.HPaned()
        paned.set_position(200)
        
        self.navigation = DMNavigationTreeControl().set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.navigation.append(FDModel("All").add_artist("All").add_status(DOWNLOAD_STATUS_ALL))
        self.navigation.append(FDModel("Downloading").add_artist("Downloading").add_status(DOWNLOAD_STATUS_DOWNLOADING))
        self.navigation.append(FDModel("Completed").add_artist("Completed").add_status(DOWNLOAD_STATUS_COMPLETED))
        self.navigation.append(FDModel("Active").add_artist("Active").add_status(DOWNLOAD_STATUS_ACTIVE))
        self.navigation.append(FDModel("Inactive").add_artist("Inactive").add_status(DOWNLOAD_STATUS_INACTIVE))
        
        self.dm_list = DownloadManagerTreeControl(self.navigation).set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.navigation.dm_list = self.dm_list
        paned.pack1(self.navigation.scroll)
        paned.pack2(self.dm_list.scroll)
        
        #vbox.pack_start(playback, False,True)
        vbox.pack_start(paned,True, True)
                
        self.add(vbox)
        thread.start_new_thread(self.dowloader,(self.dm_list,))
       
    
    def demo_tasks(self):
        self.append_task(FModel("Madonna - Sorry"))
        self.append_task(FModel("Madonna - Frozen"))
        
    def show(self):
        self.show_all()
    
    def append_task(self, bean):
        bean.status = DOWNLOAD_STATUS_ACTIVE
        self.dm_list.append(bean)
    
    def append_tasks(self, beans):
        for bean in beans:
            self.append_task(bean)
    
    def dowloader(self,dm_list):
        semaphore =threading.Semaphore(5)
        bean = None   
        while True:
            print "check"
            time.sleep(2)
            
            semaphore.acquire()            
            bean = dm_list.get_next_bean_to_dowload()
            if bean:                 
                vk = self.controls.vk.find_one_track(bean.get_display_name())
                bean.path = vk.path
                         
                def notify_finish():
                    self.navigation.update_statistics()
                    semaphore.release()
                    
                thread = Dowloader(dm_list.update_bean_info, bean,notify_finish)                
                thread.start()
            else:
                semaphore.release()