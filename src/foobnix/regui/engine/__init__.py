from foobnix.regui.model.signal import FControl

class MediaPlayerEngine(FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
    
    def state_play(self):
        pass
    
    def state_pause(self):
        pass
    
    def state_stop(self):
        pass
    
    def play(self, path):
        pass
    
    #0-100
    def volume_up(self, value):
        pass
    
    #0-100
    def volume_down(self, value):
        pass
    
    
        
