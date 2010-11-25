#!/usr/bin/env python
import sys
import datetime

VERSION = sys.argv[1]
RELEASE = sys.argv[2]
UBUNTU = sys.argv[3]

"""begin"""
dt = datetime.datetime.today()
TIME = dt.strftime("%a, %d %b %Y %H:%M:%S +0200")

template = """foobnix (%(VERSION)s-%(RELEASE)s) %(UBUNTU)s; urgency=low

  * Initial release (Closes: #%(RELEASE)s)  Upload new release %(VERSION)s-%(RELEASE)s
  
 -- Ivan Ivanenko <ivan.ivanenko@gmail.com>  %(TIME)s
""" % {'UBUNTU':UBUNTU, 'VERSION':VERSION, 'RELEASE':RELEASE, "TIME":TIME}

file = open("changelog", "w")
file.write(template)
file.close()

print template




