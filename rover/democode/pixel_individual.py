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



# use this to set any pixel to any hue and brightness
# pass pixel number (beginning with 0), pixel hue, and pixel brightness

pixels.hue_pixel(14,150,20)  #turn on some pixels
sleep(0.1)
pixels.hue_pixel(24,150,20)
sleep(1)
pixels.hue_pixel(14,150,0)   #set brightness to 0 to turn them off
sleep(0.1)
pixels.hue_pixel(24,150,0)




#end of script
