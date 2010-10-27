'''
Created on Oct 26, 2010

@author: ivan
'''
import gtk
from foobnix.regui.controls.status_bar import StatusbarControls
from foobnix.regui.controls.playback import PlaybackControls
from foobnix.regui.treeview.simple_tree import SimpleTreeControl
from foobnix.regui.base_controls import BaseFoobnixControls
from foobnix.regui.model import FModel, FDModel, FTreeModel
from urllib import FancyURLopener
import threading
from foobnix.regui.treeview.dm_tree import DownloadManagerTreeControl
from foobnix.util.const import DOWNLOAD_STATUS_INACTIVE, DOWNLOAD_STATUS_ACTIVE,\
    DOWNLOAD_STATUS_COMPLETED, DOWNLOAD_STATUS_DOWNLOADING, DOWNLOAD_STATUS_ALL
from foobnix.regui.treeview.dm_nav_tree import DMNavigationTreeControl
import thread

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
        
        model = FDModel("Madonna - Sorry","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_INACTIVE)
        model.persent = 66
        dm_list.append(model)
        dm_list.append(FDModel("Madonna - Frozen","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_INACTIVE))
        dm_list.append(FDModel("Madonna - Live","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        dm_list.append(FDModel("Madonna - GO","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        dm_list.append(FDModel("Madonna - Jonny","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_COMPLETED))
        dm_list.append(FDModel("Madonna - Real","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_COMPLETED))
        dm_list.append(FDModel("Madonna - mamba","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_DOWNLOADING))
        dm_list.append(FDModel("Madonna - humamba","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_DOWNLOADING))
        
        #dm_list.filter(DOWNLOAD_STATUS_ACTIVE, FTreeModel().status[0])
        
        model.persent = 30
        dm_list.update_bean_info(model)
        
        stats = dm_list.get_status_statisctics()
        navigation.update_statistics(stats)
        
        self.add(vbox)
        self.show_all()
        
        self.dowloader(model, dm_list)
    
    def dowloader(self,bean, dm_list):        
        load = Dowloader(bean, dm_list)
        load.start()
            

def report(block_count, block_size, total_size):
        """Hook function for urllib.urlretrieve()"""
        if total_size<=0:
            persent = 0.5
            total_size = "NaN"
        else:
            persent = block_count * block_size * 1.0 / total_size
            if persent > 1.0: persent = 1.0
        return  "%s = %s (%.2f%%)" % (size2text(block_count * block_size),
                                                  size2text(total_size), persent * 100)
        
class Dowloader(threading.Thread):
    def __init__(self, bean ,dm_list):
        threading.Thread.__init__(self)
        self.bean = bean
        self.dm_list = dm_list
    
    def size2text(self,size):
        if size > 1024*1024*1024:
            return "%.2f Gb" % (size / (1024*1024*1024.0))
        if size > 1024*1024:
            return "%.2f Mb" % (size / (1024*1024.0))
        if size > 1024:
            return "%.2f Kb" % (size / 1024.0)
        return size
    
    def dowload(self):   
        opener = FancyURLopener()
        remote = opener.open(self.bean.path)
        remote_size = 0
        
        if "Content-Length" in remote.headers:
            remote_size = int(remote.headers["Content-Length"])
            self.bean.size = self.size2text(remote_size) 
        
        block_size = 4096
        block_count = 0
        
        to_file = self.bean.get_display_name() + ".mp3.tmp"
        self.bean.save_to = to_file        
        file = open(to_file,"wb")
        
        data = True
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
                    self.bean.persent = persent
                    gtk.gdk.threads_enter()
                    self.dm_list.update_bean_info(self.bean)
                    gtk.gdk.threads_leave()
                
    def run(self):
        self.dowload()

dm = DM()
gtk.gdk.threads_init()
gtk.main()        
    
#dowload("http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3", "/tmp/1.mp3")
#dowload("http://cs1028.vkontakte.ru/u78433/audio/82c9d026c31a.mp3", "/tmp/2.mp3")






