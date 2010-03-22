'''
Created on Mar 14, 2010

@author: ivan
'''
class AppConfigurationCntrl():
    def __init__(self, gxMain, directoryCntr):
        self.directoryCntr = directoryCntr
        self.folderChoser = gxMain.get_widget("music_dir_filechooserbutton")
        self.folderChoser.connect("current-folder-changed", self.onChangeMusicFolder)
        
        self.vk_entry_label = gxMain.get_widget("vk_entry_login")
        self.vk_entry_passw = gxMain.get_widget("vk_entry_password")
        
        self.lfm_entry_label = gxMain.get_widget("lfm_entry_login")
        self.lfm_entry_passw = gxMain.get_widget("lfm_entry_password")
        
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
        print "Change music folder",self.musicFolder 
        self.directoryCntr.updateDirectoryByPath(self.musicFolder)                   
    
    def setMusicFolder(self, path):
        print "Set Folder", path
        self.folderChoser.set_current_folder(path)
        
    def getMusicFolder(self):
        return self.folderChoser.get_filename()