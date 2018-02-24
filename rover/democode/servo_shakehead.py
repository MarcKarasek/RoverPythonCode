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



#servo commands to make robot shake head
s.servo_speed(3000)     #set servo speed in degrees per second (3000 is max)
s.servo_pan(30)         #0 is center, plus or minus 90 from there to rotate head
sleep(0.25)             #short delay
s.servo_pan(-30)
sleep(0.25)
s.servo_pan(0)          #0 sets servo back to center

#end of script
