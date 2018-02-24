#!/usr/bin/python

from time import sleep
import spirit_core
import spirit_pixels as pixels   #pixel functions - read over spirit_pixels.py for more info

import sys                      #basic lower level Pi system interraction
from random import randrange
s = spirit_core.Spirit()

def exceptionHandler(exception_type, exception, traceback, debug_hook=sys.excepthook):
  print "%s: %s" % (exception_type.__name__, exception)

s.i2c_process_delay(15)   #should leave this in place for all python scripts



#display bottom sensor values in terminal window
print "Surface Sensors:"
print "Left Sensors..."
print s.surf_left_0()
print s.surf_left_1()
print "Right Sensors..."
print s.surf_right_0()
print s.surf_right_1()
print "Rear Sensors..."
print s.surf_rear_0()
print s.surf_rear_1()

#end of script
