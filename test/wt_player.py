#Example 2.2 http://pygstdocs.berlios.de/pygst-tutorial/playbin.html

import wx
import gst
import os, sys

import gobject
gobject.threads_init()

class WX_Main(wx.App):
  
    def OnInit(self):
        window = wx.Frame(None)
        window.SetTitle("Video-Player")
        window.SetSize((500, 400))
        window.Bind(wx.EVT_CLOSE, self.destroy)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.entry = wx.TextCtrl(window)
        hbox.Add(self.entry, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        self.button = wx.Button(window, label="Start")
        hbox.Add(self.button, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        self.button.Bind(wx.EVT_BUTTON, self.start_stop)
        vbox.Add(hbox, 0, wx.EXPAND, 0)
        self.movie_window = wx.Panel(window)
        vbox.Add(self.movie_window, 1, wx.ALL | wx.EXPAND, 4)
        window.SetSizer(vbox)
        window.Layout()
        window.Show()
        self.SetTopWindow(window)
        
        self.player = gst.element_factory_make("playbin", "player")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect('message', self.on_message)
        bus.connect('sync-message::element', self.on_sync_message)
        
        return True

    def start_stop(self, event):
        if self.button.GetLabel() == "Start":
            filepath = self.entry.GetValue()
            if os.path.exists(filepath):
                self.button.SetLabel("Stop")
                self.player.set_property('uri', "file://" + filepath)
                self.player.set_state(gst.STATE_PLAYING)
        else:
            self.player.set_state(gst.STATE_NULL)
            self.button.SetLabel("Start")
    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.button.SetLabel("Start")
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            self.button.SetLabel("Start")

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == 'prepare-xwindow-id':
            imagesink = message.src
            imagesink.set_property('force-aspect-ratio', True)
            imagesink.set_xwindow_id(self.movie_window.GetHandle())
           
    def destroy(self, event):
        #Stop the player pipeline to prevent a X Window System error
        self.player.set_state(gst.STATE_NULL)
        event.Skip()
          
app = WX_Main()
app.MainLoop()
