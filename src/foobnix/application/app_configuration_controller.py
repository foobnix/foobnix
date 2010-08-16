'''
Created on Mar 14, 2010

@author: ivan
'''
from foobnix.util.configuration import FConfiguration
from foobnix.util import LOG
class AppConfigurationCntrl():
    def __init__(self, gxMain, directoryCntr):
        self.directoryCntr = directoryCntr
        self.folderChoser = gxMain.get_widget("music_dir_filechooserbutton")
        self.folderChoser.connect("current-folder-changed", self.onChangeMusicFolder)
        
        reload_dir_button = gxMain.get_widget("reload_dir_button")
        reload_dir_button.connect("clicked", self.onChangeMusicFolder)
        
        self.vk_entry_label = gxMain.get_widget("vk_entry_login")
        self.vk_entry_passw = gxMain.get_widget("vk_entry_password")
        
        self.lfm_entry_label = gxMain.get_widget("lfm_entry_login")
        self.lfm_entry_passw = gxMain.get_widget("lfm_entry_password")
        
        """ online music folder path """
        self.online_dir = gxMain.get_widget("online_dir_filechooserbutton")
        self.online_dir.connect("current-folder-changed", self.onChangeOnline)
        self.online_dir.set_current_folder(FConfiguration().onlineMusicPath)
        self.online_dir.set_sensitive(FConfiguration().is_save_online)

        """ is save online music checkbox """
        self.save_online = gxMain.get_widget("save_online_checkbutton")
        self.save_online.connect("clicked", self.on_save_online)
        self.save_online.set_active(FConfiguration().is_save_online)
                
        self.by_first = gxMain.get_widget("radiobutton_by_first")
        self.by_popularity = gxMain.get_widget("radiobutton_by_popularity")
        self.by_time = gxMain.get_widget("radiobutton_by_time")
        
        """Random button"""
        self.randomCheckButton = gxMain.get_widget("random_checkbutton")
        self.randomCheckButton.set_active(FConfiguration().isRandom)
        self.randomCheckButton.connect("clicked", self.onRandomClicked)
        
        """Repeat button"""
        self.repeatCheckButton = gxMain.get_widget("repeat_checkbutton")
        self.repeatCheckButton.set_active(FConfiguration().isRepeat)
        self.repeatCheckButton.connect("clicked", self.onRepeatClicked)
        
        """Play on Start"""
        self.playOnStartCheckButton = gxMain.get_widget("playonstart_checkbutton")
        self.playOnStartCheckButton.set_active(FConfiguration().isPlayOnStart)
        self.playOnStartCheckButton.connect("clicked", self.onPlayOnStartClicked)
    
    def onPlayOnStartClicked(self, *args):
        FConfiguration().isPlayOnStart = self.playOnStartCheckButton.get_active()
        
    def onRepeatClicked(self, *args):
        FConfiguration().isRepeat = self.repeatCheckButton.get_active()
        
    def onRandomClicked(self, *args):
        FConfiguration().isRandom = self.randomCheckButton.get_active()
        
    def on_save_online(self, *args):
        value = self.save_online.get_active()
        if  value:
            self.online_dir.set_sensitive(True)
        else:
            self.online_dir.set_sensitive(False)
                
        FConfiguration().is_save_online = value            
    
    def onChangeOnline(self, *args):
        path = self.online_dir.get_filename()        
        LOG.info("Change music online folder", path) 
        FConfiguration().onlineMusicPath = path  
                
    """ Vkontatke"""
    def setVkLoginPass(self, login, passwrod):
        self.vk_entry_label.set_text(login)
        self.vk_entry_passw.set_text(passwrod)
        
    def getVkLogin(self): return self.vk_entry_label.get_text()    
    def getVkPassword(self): return self.vk_entry_passw.get_text()
    
    """ Last.FM"""
    def setLfmLoginPass(self, value, passwrod):
        self.lfm_entry_label.set_text(value)
        self.lfm_entry_passw.set_text(passwrod)
        
    def getLfmLogin(self): return self.lfm_entry_label.get_text()    
    def getLfmPassword(self): return self.lfm_entry_passw.get_text()

        
    def onChangeMusicFolder(self, path):                
        self.musicFolder = self.folderChoser.get_filename()        
        LOG.info("Change music folder", self.musicFolder)
                 
        self.directoryCntr.updateDirectoryByPath(self.musicFolder)                   
    
    def setMusicFolder(self, path):
        LOG.info("Set Folder", path)
        self.folderChoser.set_current_folder(path)
        
    def getMusicFolder(self):
        return self.folderChoser.get_filename()
