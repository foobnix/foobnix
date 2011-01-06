'''
Created on Feb 26, 2010

@author: ivan
'''


def size2text(size):
    if size > 1024*1024*1024:
        return "%.2f Gb" % (size / (1024*1024*1024.0))
    if size > 1024*1024:
        return "%.2f Mb" % (size / (1024*1024.0))
    if size > 1024:
        return "%.2f Kb" % (size / 1024.0)
    return size

def convert_seconds_to_text(time_sec):
        time_sec = int(time_sec)

        hours = time_sec / (60*60)
        time_sec = time_sec - (hours * 60*60)

        mins = time_sec / 60
        time_sec = time_sec - (mins * 60)

        secs = time_sec
        if hours > 0:
            return "{0}:{1:0>2}:{2:0>2}".format(hours, mins, secs)
        else:
            return "{0:0>2}:{1:0>2}".format(mins, secs)

def normalize_time(length):
    convert_seconds_to_text(length)