#!/usr/bin/env python
import sys
import datetime

VERSION = sys.argv[1]
RELEASE = sys.argv[2]
UBUNTU = sys.argv[3]

"""begin"""
dt = datetime.datetime.today()
TIME = dt.strftime("%a, %d %b %Y %H:%M:%S +0200")
BUG_NUM = "1000" + RELEASE[:1]

template = """foobnix (%(VERSION)s-%(RELEASE)s) %(UBUNTU)s; urgency=low

  * Initial release (Closes: #%(BUG_NUM)s)  Upload new release %(VERSION)s-%(RELEASE)s
  
 -- Ivan Ivanenko <ivan.ivanenko@gmail.com>  %(TIME)s
""" % {'UBUNTU':UBUNTU, 'VERSION':VERSION, 'RELEASE':RELEASE, "TIME":TIME, "BUG_NUM":BUG_NUM}

file = open("changelog", "w")
file.write(template)
file.close()

print template




