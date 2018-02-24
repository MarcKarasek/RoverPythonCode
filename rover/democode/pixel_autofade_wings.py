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



#start automated wing fade

#pixels.wings_autofade(hue,wings_brightness,wings_fall_off,
#    wings_over_under, fade_direction, wing_swoop_speed)
pixels.wings_autofade(250,50,7,5,1,10)
sleep(1.5)
pixels.wings_autofade(120,20,7,5,1,20)
sleep(1.5)
pixels.pixels_off()
#end of script
