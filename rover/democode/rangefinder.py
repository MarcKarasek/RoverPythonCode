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



#display rangefinder reading in terminal window
print "Rangefinder:", s.rangefinder()

#can just print the result by calling the function by itself...
print s.rangefinder()

#can store result in a variable, then do something with it, like print it...
someVariable = s.rangefinder()
print someVariable

#end of script
