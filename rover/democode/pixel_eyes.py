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



#set eyes to given hue and brightness
pixels.eyes(200,100)    #sets hue 200 (0 to 360, color wheel) brightness 100 (0 to 255)
sleep(0.5)              #short delay
pixels.eyes(225,100)    #new hue
sleep(0.5)              #short delay
pixels.eyes(250,100)    #new hue
sleep(0.5)              #short delay
pixels.eyes(275,100)    #new hue
sleep(0.5)              #short delay
pixels.eyes(300,100)    #new hue
sleep(0.5)              #short delay
pixels.eyes(300,0)      #brightness of 0 turns eyes off

#end of script
