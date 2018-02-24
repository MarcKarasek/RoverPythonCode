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


#run motors forward then backward
s.motors(120,120)         #can be from -255 to 255
sleep(1)                  #delay 1 second
s.motors(-120,-120)
sleep(1)
s.motors(0,0)             #stop motors

#end of script
