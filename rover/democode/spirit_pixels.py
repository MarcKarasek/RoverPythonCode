#!/usr/bin/python

import socket               # Import socket module
import sys

hue_eyes = 140
hue_wings = 200

def exceptionHandler(exception_type, exception, traceback, debug_hook=sys.excepthook):
  print "%s: %s" % (exception_type.__name__, exception)

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 20568                # Reserve a port for your service.
s.connect((host, port))


def hue_eye_up():
    global hue_eyes
    hue_eyes = hue_eyes + 20
    if hue_eyes > 360:
        hue_eyes = 20
    eyes(hue_eyes,200)

def hue_eye_down():
    global hue_eyes
    hue_eyes = hue_eyes - 20
    if hue_eyes < 0:
        hue_eyes = 340
    eyes(hue_eyes,200)

def hue_wing_up():
    global hue_wings
    hue_wings = hue_wings + 20
    if hue_wings > 360:
        hue_wings = 20

def hue_wing_down():
    global hue_wings
    hue_wings = hue_wings - 20
    if hue_wings < 0:
        hue_wings = 340

def wings_autofade(hue,bright,fall_off,over_under,streak_mode,interval):
    #global s
    animation_index = 32
    data = ''
    data = (str(animation_index) + ':' + str(hue) + ':' + str(bright) +
        ':' + str(fall_off) + ':' + str(over_under) + ":" + str(streak_mode) +
        ':' + str(interval))
    #print "data:", data
    #return data
    s.send(data)
    #s.close
    #print s.recv(1024)

def pixels_off():   #turns off all pixels
    global s
    animation_index = 2
    data = ''
    data = str(animation_index) + ':'
    #print "data:", data
    #return data
    s.send(data)
    #s.close
    #print s.recv(1024)

def eyes(hue,bright):
    global s
    animation_index = 12
    data = ''
    data = (str(animation_index) + ':' + str(hue) + ':' + str(bright))
    #print "data:", data
    #return data
    s.send(data)
    #s.close
    #print s.recv(1024)

def hue_pixel(pixel_index,hue=0,bright=0):
    global s
    animation_index = 5
    data = ''
    data = (str(animation_index) + ':' + str(pixel_index) + ':' + str(hue) + ':' + str(bright))
    #print data
    s.send(data)
