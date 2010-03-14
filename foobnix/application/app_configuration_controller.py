'''
Created on Mar 14, 2010

@author: ivan
'''
class AppConfigurationCntrl():
    def __init__(self, gxMain, directoryCntr):
        self.directoryCntr = directoryCntr
        self.folderChoser = gxMain.get_widget("music_dir_filechooserbutton")
        self.folderChoser.connect("current-folder-changed", self.onChangeMusicFolder)
        
    def onChangeMusicFolder(self, path):                
        self.musicFolder = self.folderChoser.get_filename()        
        print "Change music folder",self.musicFolder 
        self.directoryCntr.updateDirectoryByPath(self.musicFolder)                   
    
    def setMusicFolder(self, path):
        print "Set Folder", path
        self.folderChoser.set_current_folder(path)
        
    def getMusicFolder(self):
        return self.folderChoser.get_filename()