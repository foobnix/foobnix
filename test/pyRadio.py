#
import gobject, pygst
#
pygst.require("0.10")
#
import gst
#
 
#
# create a pipeline and add [ filesrc ! tcpclientsink ]
#
pipeline = gst.Pipeline("client")
#
 
#
src = gst.element_factory_make("filesrc", "source")
#
src.set_property("location", "/home/you/song.ogg")
#
pipeline.add(src)
#
 
#
client = gst.element_factory_make("tcpclientsink", "client")
#
pipeline.add(client)
#
client.set_property("host", "72.26.204.18")
#
client.set_property("port", 6314)
#
src.link(client)
#
 
#
pipeline.set_state(gst.STATE_PLAYING)
#
 
#
# enter into a mainloop
#
loop = gobject.MainLoop()
#
loop.run()
