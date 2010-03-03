#!/usr/bin/env python

import sys
import gst
import time
class myPlayer ():
    def __init__(self):
        self.pipeline = gst.Pipeline()
        self.src = gst.element_factory_make("filesrc", "src")
        self.decoder = gst.element_factory_make("decodebin", "decoder")
        self.decoder.connect("new-decoded-pad", self.onNewDecodedPad)
        self.goom = gst.element_factory_make("goom")
        self.colorspace = gst.element_factory_make("ffmpegcolorspace", "color")
        self.conv = gst.element_factory_make("audioconvert", "conv")
        self.vidsink = gst.element_factory_make("autovideosink", "videosink")
        self.asink = gst.element_factory_make("autoaudiosink", "aoutput")
        self.tee = gst.element_factory_make('tee', "tee")
        self.queuea = gst.element_factory_make("queue", "queuea")
        self.queuev = gst.element_factory_make("queue", "queuev")
        self.pipeline.add(self.src, self.decoder, self.conv, self.tee, self.queuea)
        self.pipeline.add(self.asink, self.queuev, self.goom, self.colorspace, self.vidsink)
        gst.element_link_many(self.src, self.decoder)
        gst.element_link_many(self.conv, self.tee)
        self.tee.link(self.queuea)
        self.queuea.link(self.asink)
        self.tee.link(self.queuev)
        gst.element_link_many(self.queuev, self.goom, self.colorspace, self.vidsink)
    def onNewDecodedPad(self, decodebin, pad, islast):
        #link the pad to the converter
        decodebin.link(self.conv)
        
    def playfile(self, file):
        self.src.set_property('location', file)
        self.pipeline.set_state(gst.STATE_PLAYING)
        pipelinestate = self.pipeline.get_state()
        
        while pipelinestate[1] == gst.STATE_PLAYING:
            time.sleep(1)
            pipelinestate = self.pipeline.get_state()
        sys.exit()

if __name__ == '__main__':
    if (len(sys.argv) > 1):
        file = sys.argv[1]
        player = myPlayer()
        player.playfile(file)
    else:
        print "you must select a tune"
