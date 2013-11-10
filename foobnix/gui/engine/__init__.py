from foobnix.gui.model.signal import FControl

class MediaPlayerStatus():
    def __init__(self):
        self.setStop()

    def setPlay(self):
        self.isPlay = True
        self.isPause = False
        self.isStop = False

    def setPause(self):
        self.isPlay = False
        self.isPause = True
        self.isStop = False

    def setStop(self):
        self.isPlay = False
        self.isPause = False
        self.isStop = True


class MediaPlayerEngine(FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        self.status = MediaPlayerStatus()

    def state_play(self):
        pass

    def state_pause(self):
        pass

    def state_stop(self):
        pass

    def play(self, path):
        pass

    def state_play_pause(self):
        pass

    #0-100
    def volume_up(self, value):
        pass

    #0-100
    def volume_down(self, value):
        pass



