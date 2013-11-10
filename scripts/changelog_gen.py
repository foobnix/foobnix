#!/usr/bin/env python
import sys
import datetime
print sys.argv
VERSION = sys.argv[1]
UBUNTU = sys.argv[2]

"""begin"""
dt = datetime.datetime.today()
TIME = dt.strftime("%a, %d %b %Y %H:%M:%S +0200")
BUG_NUM = "1000" + VERSION

template = """foobnix (%(VERSION)s) %(UBUNTU)s; urgency=low

  * Initial release (Closes: #%(BUG_NUM)s)  Upload new release %(VERSION)s
  
 -- Ivan Ivanenko <ivan.ivanenko@gmail.com>  %(TIME)s
""" % {'UBUNTU':UBUNTU, 'VERSION':VERSION, "TIME":TIME, "BUG_NUM":BUG_NUM}

file = open("changelog", "w")
file.write(template)
file.close()

print template




