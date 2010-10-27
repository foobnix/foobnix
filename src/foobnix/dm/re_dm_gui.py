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
        actions = DMNavigationTreeControl("Actions", controls).set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        actions.append(FDModel("All").add_artist("All").add_status(DOWNLOAD_STATUS_ALL))
        actions.append(FDModel("Downloading").add_artist("Downloading").add_status(DOWNLOAD_STATUS_DOWNLOADING))
        actions.append(FDModel("Completed").add_artist("Completed").add_status(DOWNLOAD_STATUS_COMPLETED))
        actions.append(FDModel("Active").add_artist("Active").add_status(DOWNLOAD_STATUS_ACTIVE))
        actions.append(FDModel("Inactive").add_artist("Inactive").add_status(DOWNLOAD_STATUS_INACTIVE))
        
        dowlaods = DownloadManagerTreeControl(controls).set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        controls.dm = dowlaods
        paned.pack1(actions.scroll)
        paned.pack2(dowlaods.scroll)
        
        vbox.pack_start(playback, False,True)
        vbox.pack_start(paned,True, True)
        vbox.pack_start(statusbar,False, True)
        
        dowlaods.append(FDModel("Madonna - Sorry","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_INACTIVE))
        dowlaods.append(FDModel("Madonna - Frozen","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_INACTIVE))
        dowlaods.append(FDModel("Madonna - Live","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        dowlaods.append(FDModel("Madonna - GO","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_ACTIVE))
        dowlaods.append(FDModel("Madonna - Jonny","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_COMPLETED))
        dowlaods.append(FDModel("Madonna - Real","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_COMPLETED))
        dowlaods.append(FDModel("Madonna - mamba","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_DOWNLOADING))
        dowlaods.append(FDModel("Madonna - humamba","http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3").add_status(DOWNLOAD_STATUS_DOWNLOADING))
        
        dowlaods.filter(DOWNLOAD_STATUS_ACTIVE, FTreeModel().status[0])
        
        stats = dowlaods.get_status_statisctics()
        actions.update_statistics(stats)
        
        self.add(vbox)
        self.show_all()


def size2text(size):
    if size > 1024*1024*1024:
        return "%.2f Gb" % (size / (1024*1024*1024.0))
    if size > 1024*1024:
        return "%.2f Mb" % (size / (1024*1024.0))
    if size > 1024:
        return "%.2f Kb" % (size / 1024.0)
    return size

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
        
def dowload(url, to_file, callback):   
    opener = FancyURLopener()
    remote = opener.open(url)
    remote_size = 0
    
    if "Content-Length" in remote.headers:
        remote_size = int(remote.headers["Content-Length"])
    
    block_size = 4096
    block_count = 0
    
    file = open(to_file,"wb")
    
    data = True
    while data:
        data = remote.read(block_size)
        if data:
            block_count += 1
            file.write(data)
            gtk.gdk.threads_enter()
            callback.set_text(report(block_count, block_size, remote_size))
            gtk.gdk.threads_leave()
 
class DowloadTask(threading.Thread):
    def __init__(self, label, url, to):
        threading.Thread.__init__(self)
        self.label = label
        self.url  = url 
        self.to = to
    
    def run(self):
        print "go"
        collback = None
        dowload(self.url,self.to, self.label)
        
                
 
class DM_Demo(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_title("Download Manager Demo")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_geometry_hints(self, min_width=700, min_height=400)
        self.set_resizable(False)   
        
        self.label = gtk.Label("0%")
        
        self.add(self.label)
        
        self.show_all()
        
    def go(self):
        t = DowloadTask(self.label,"http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3", "/tmp/1.mp3")
        t.start()
        print "runned"
        
    def set_text(self, text):
        self.label.set_text(text)

dm = DM()
#dm.go()
gtk.threads_init()
gtk.main()        
    
#dowload("http://cs4532.vkontakte.ru/u42316445/audio/4c42a11094a2.mp3", "/tmp/1.mp3")
#dowload("http://cs1028.vkontakte.ru/u78433/audio/82c9d026c31a.mp3", "/tmp/2.mp3")






