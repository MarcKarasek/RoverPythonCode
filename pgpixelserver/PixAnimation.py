# PixAnimation.py
# Author: Kevin King for Plum Geek LLC
#
# This script is included by PlumGeekPixelServer.py
# Review this file for specific animations available

import time
import math
from neopixel import *

def millis():
    return int(round(time.time() * 1000))

animation_mode = 0			        #index of which animation should be running
animation_delay = 20		        #animation delay time in ms
animation_hue = 0			        #global holder for base hue for some animations
animation_brightness = 0            #global holder for base brightness for some animations
animation_huespacing = 10	        #hue offset pixel to pixel for some animations
animation_index = 0			        #general index place-holder for some animations
animation_start_index = 0           #index to start / end automatic animations
animation_end_index = 0             #index to start / end automatic animations
over_under = 0                      #what index before/after needed to completely clear fade
animation_direction = 0             #direction for auto animations. 0=move rearward 1= move frontward
animation_timestamp = millis()      #timestamp holder to time automatic animations
timer0 = animation_timestamp        #general purpose timers, can be used to time animations
timer1 = animation_timestamp        #general purpose timers, can be used to time animations
interval0 = 0                       #holder for timing interval to update auto animations
interval1 = 0                       #holder for timing interval to update auto animations
recalculate_color = 0               #flag if a color needs to be re-calculated
redraw_pixels = 1                   #flag if pixels need to be re-drawn
new_data = 0                        #flag to indicate if incomming socket data has changed
r = 0                               #global var, used by getColorWheel to update r,g,b
g = 0
b = 0

# LED Strip Configuration:
LED_COUNT      = 27      # Number of LED pixels.
LED_PIN        = 12      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

PIXEL_STATUS        = 0    # addresses for specific pixels
PIXEL_EYERIGHT      = 1
PIXEL_EYELEFT       = 2
PIXEL_LEFTW_START   = 3
PIXEL_LEFTW_END     = 14
PIXEL_RIGHTW_START  = 15
PIXEL_RIGHTW_END    = 26

# NeoPixel code instructions here: https://learn.adafruit.com/neopixels-on-raspberry-pi/software
# Create NeoPixel object with appropriate configuration
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin() # Intialize the library (must be called once before other functions)
strip.show()  # clear any existing colors on strip, show blank strip


def selectAnimation(socket_data):
    #use these global variables
    global animation_mode, new_data, redraw_pixels
    global animation_index, animation_start_index, animation_end_index, animation_direction, over_under
    global animation_timestamp, timer0, timer1, interval0

    try:
        animation_mode = int(socket_data[0])
        #print "selectAnimation:", animation_mode
    except:
        print socket_data #"sock data:", socket_data[0], "animation_mode =", animation_mode

    if animation_mode == 0:
        pass #do nothing
        #off_pixels(0, LED_COUNT-1)

    elif animation_mode == 1:   #status LED (center pixel) turns off
        off_pixel(0)

    elif animation_mode == 2:  #turn off all pixels
        off_pixels(0, LED_COUNT-1)
        #hue_pixels(0, 27, 0, 0)

    elif animation_mode == 5:  #turn on a given pixel via hue_pixel function
        #print "animation_mode 5", socket_data
        pixel_index = int(socket_data[1])
        hue = int(socket_data[2])
        brightness = int(socket_data[3])
        hue_pixel(pixel_index, hue, brightness)

    elif animation_mode == 11:  #turn on a given pixel via hue_pixel function
        pixel_index = int(socket_data[1])
        hue = int(socket_data[2])
        brightness = int(socket_data[3])
        hue_pixel(pixel_index, hue, brightness)

    elif animation_mode == 12:  #eyes on
        global r,g,b
        hue = int(socket_data[1])
        brightness = int(socket_data[2])
        #getColorWheel(hue,brightness)
        hue_pixels(1, 2, hue, brightness)

    elif animation_mode == 20:  #left_wing_fade
        if new_data:            #update only if new_data flag is set
            new_data = 0        #clear new_data flag
            left_wing_fade(socket_data)

    elif animation_mode == 21:  #right_wing_fade
        if new_data:            #update only if new_data flag is set
            new_data = 0        #clear new_data flag
            right_wing_fade(socket_data)

    elif animation_mode == 22:  #both_wing_fade
        if new_data:            #update only if new_data flag is set
            new_data = 0        #clear new_data flag
            redraw_pixels = 0   #don't auto-redraw pixels
            left_wing_fade(socket_data)
            right_wing_fade(socket_data)
            strip.show()        #re-draw pixels now that both wing buffers are updated
            redraw_pixels = 1   #reset auto-redraw pixels flag

    elif animation_mode == 30:  #left_wing_fade_auto_animate
        #global interval0, over_under, animation_start_index, animation_end_index, new_data
        if new_data:            #update only if new_data flag is set
            interval0 = float(socket_data[6])
            over_under = int(socket_data[4])
            animation_direction = int(socket_data[7])
            animation_start_index = 0 - over_under
            animation_end_index = (PIXEL_LEFTW_END - PIXEL_LEFTW_START) + over_under
            new_data = 0        #clear new_data flag
        time.sleep(interval0 / 1000)
        update_pixel_index(animation_direction)
        left_wing_autofade(socket_data)     #run the animation

    elif animation_mode == 31:  #right_wing_fade_auto_animate
        #global interval0, over_under, animation_start_index, animation_end_index, new_data
        if new_data:            #update only if new_data flag is set
            interval0 = float(socket_data[6])
            over_under = int(socket_data[4])
            animation_direction = int(socket_data[7])
            animation_start_index = 0 - over_under
            animation_end_index = (PIXEL_RIGHTW_END - PIXEL_RIGHTW_START) + over_under
            new_data = 0        #clear new_data flag
        time.sleep(interval0 / 1000)
        update_pixel_index(animation_direction)
        right_wing_autofade(socket_data)    #run the animation

    elif animation_mode == 32:  #both_wing_fade_auto_animate
        #global interval0, over_under, animation_start_index, animation_end_index, new_data
        if new_data:            #update only if new_data flag is set
            interval0 = int(socket_data[6])
            over_under = int(socket_data[4])
            #animation_direction = int(socket_data[7])
            if interval0 >= 0:
                animation_direction = 0
            else:
                animation_direction = 1
            animation_start_index = 0 - over_under
            animation_end_index = (PIXEL_RIGHTW_END - PIXEL_RIGHTW_START) + over_under
            new_data = 0        #clear new_data flag
        if millis() > animation_timestamp + abs(interval0):
        #time.sleep(interval0 / 1000)
            animation_timestamp = millis()     #get new timestamp
            update_pixel_index(animation_direction)
            redraw_pixels = 0                   #don't auto-redraw pixels
            left_wing_autofade(socket_data)    #run the animation
            right_wing_autofade(socket_data)    #run the animation
            strip.show()        #re-draw pixels now that both wing buffers are updated
            redraw_pixels = 1   #reset auto-redraw pixels flag
    else:
        pass    #do nothing

    return 0 #end selectAnimation()


def right_wing_autofade(socket_data):
    global PIXEL_RIGHTW_START, PIXEL_RIGHTW_END
    global animation_index
    hue = int(socket_data[1])
    brightness = int(socket_data[2])
    falloff = int(socket_data[3])
    #animation_direction = int(socket_data[7])
    streak_mode = int(socket_data[5])

    wing_fade(hue, brightness, falloff, animation_index,
                streak_mode, PIXEL_RIGHTW_START, PIXEL_RIGHTW_END)
#end right_wing_autofade function

def left_wing_autofade(socket_data):
    global PIXEL_LEFTW_START, PIXEL_LEFTW_END
    global animation_index
    hue = int(socket_data[1])
    brightness = int(socket_data[2])
    falloff = int(socket_data[3])
    #animation_direction = int(socket_data[7])
    streak_mode = int(socket_data[5])

    wing_fade(hue, brightness, falloff, animation_index,
                streak_mode, PIXEL_LEFTW_START, PIXEL_LEFTW_END)
#end left_wing_autofade function

def update_pixel_index(animation_direction):
    global animation_index
    if animation_direction == 1:        #fade moves forward
        animation_index = animation_index - 1
        if animation_index < animation_start_index:
            animation_index = animation_end_index
        if animation_index > animation_end_index:
            animation_index = animation_end_index

    else:                               #fade moves reaward by default
        animation_index = animation_index + 1
        if animation_index < animation_start_index:
            animation_index = animation_start_index
        if animation_index > animation_end_index:
            animation_index = animation_start_index
#end update_pixel_index function

def off_pixel(pixel_index):
    strip.setPixelColorRGB(pixel_index,0,0,0)
    strip.show()

def hue_pixel(pixel_index, hue, brightness):
    print "PixAnimation.py: hue_pixel", pixel_index, hue, brightness
    global r,g,b            #use global r,g,b values - will be updated by getColorWheel()
    getColorWheel(hue,brightness)
    print "PixAnimation.py: hue_pixel", pixel_index, hue, brightness, r, g, b
    strip.setPixelColorRGB(pixel_index,r,g,b)
    strip.show()

def off_pixels(pixel_index_start, pixel_index_end):
    local_index = pixel_index_start
    while local_index <= pixel_index_end:
        strip.setPixelColorRGB(local_index,0,0,0)
        local_index = local_index + 1
    strip.show()

def hue_pixels(pixel_index_start, pixel_index_end, hue, brightness):
    global r,g,b            #use global r,g,b values - will be updated by getColorWheel()
    getColorWheel(hue,brightness)
    local_index = pixel_index_start
    while local_index <= pixel_index_end:
        strip.setPixelColorRGB(local_index,r,g,b)
        local_index = local_index + 1
    strip.show()

def right_wing_fade(socket_data):
    global PIXEL_RIGHTW_START
    global PIXEL_RIGHTW_END
    hue = int(socket_data[1])
    brightness = int(socket_data[2])
    falloff = int(socket_data[3])
    index_base = int(socket_data[4])
    streak_mode = int(socket_data[5])
    wing_fade(hue, brightness, falloff, index_base,
                streak_mode, PIXEL_RIGHTW_START, PIXEL_RIGHTW_END)

def left_wing_fade(socket_data):
    global PIXEL_LEFTW_START
    global PIXEL_LEFTW_END
    hue = int(socket_data[1])
    brightness = int(socket_data[2])
    falloff = int(socket_data[3])
    index_base = int(socket_data[4])
    streak_mode = int(socket_data[5])
    wing_fade(hue, brightness, falloff, index_base,
                streak_mode, PIXEL_LEFTW_START, PIXEL_LEFTW_END)

def wing_fade(hue, brightness, falloff, index_base, streak_mode, pix_first, pix_last):
    global redraw_pixels    #use global redraw pixels flag
    global r,g,b            #use global r,g,b values - will be updated by getColorWheel()

    falloff_percent = float(falloff)/100
    index_base = index_base + pix_first #int(socket_data[4]) + PIXEL_RIGHTW_START
    #print hue, brightness, falloff_percent, index_base

    getColorWheel(hue,brightness)
    #print "Staring RGB:", r,g,b

    if (index_base >= pix_first) and (index_base <= pix_last):
        #print "fade from:", index_base
        strip.setPixelColorRGB(index_base,r,g,b)

    for x in range(1,12):
        r = int(float(r) * (1-falloff_percent))
        g = int(float(g) * (1-falloff_percent))
        b = int(float(b) * (1-falloff_percent))
        up_pix = index_base + x
        down_pix = index_base - x
        #print "up", up_pix, "down", down_pix, r,g,b
        if streak_mode == 0 or streak_mode == 2:          #streak reaward in modes 0 or 2
            if (up_pix >= pix_first) and (up_pix <= pix_last):
                #print "up:", up_pix
                strip.setPixelColorRGB(up_pix,r,g,b)
        else:
            if (up_pix >= pix_first) and (up_pix <= pix_last):
                #print "zero'd up", up_pix
                strip.setPixelColorRGB(up_pix,0,0,0)
        if streak_mode == 0 or streak_mode == 1:          #streak reaward in modes 0 or 1
            if (down_pix >= pix_first) and (down_pix <= pix_last):   #if (down_pix >= 15):
                strip.setPixelColorRGB(down_pix,r,g,b)
                #print "down:", down_pix
        else:
            if (down_pix >= pix_first) and (down_pix <= pix_last):   #if (down_pix >= 15):
                #print "zero'd down", down_pix
                strip.setPixelColorRGB(down_pix,0,0,0)

    if redraw_pixels:   #redraw pixels if the global redraw_pixels flag is set
        strip.show()    #this flag is usually set, but may be cleared temporarily
                        #by some animations that do multiple strip buffer updates
                        #before finally calling strip.show() to update all pixels
                        #in one shot
# end wing_fade function


def right_wing_fadedown_bak(socket_data):
    global new_data
    global r,g,b    #use global r,g,b values - will be updated by getColorWheel()
    if new_data:
        new_data = 0    #clear the "new data" flag
        #print "right_wing_fadedown", socket_data[3]

        hue = int(socket_data[1])
        brightness = int(socket_data[2])
        falloff_percent = float(socket_data[3])/100
        index_base = int(socket_data[4]) + PIXEL_RIGHTW_START
        streak_mode = int(socket_data[5])
        #print hue, brightness, falloff_percent, index_base
        getColorWheel(hue,brightness)
        #print "Staring RGB:", r,g,b

        if (index_base >= PIXEL_RIGHTW_START) and (index_base <= PIXEL_RIGHTW_END):
            #print "base addr:", index_base
            strip.setPixelColorRGB(index_base,r,g,b)

        for x in range(1,12):
            r = int(float(r) * (1-falloff_percent))
            g = int(float(g) * (1-falloff_percent))
            b = int(float(b) * (1-falloff_percent))
            up_pix = index_base + x
            down_pix = index_base - x
            #print "up", up_pix, "down", down_pix, r,g,b
            if streak_mode == 0 or streak_mode == 2:          #streak reaward in modes 0 or 2
                if (up_pix >= PIXEL_RIGHTW_START) and (up_pix <= PIXEL_RIGHTW_END):
                    #print "up:", up_pix
                    strip.setPixelColorRGB(up_pix,r,g,b)
            else:
                if (up_pix >= PIXEL_RIGHTW_START) and (up_pix <= PIXEL_RIGHTW_END):
                    #print "zero'd up", up_pix
                    strip.setPixelColorRGB(up_pix,0,0,0)
            if streak_mode == 0 or streak_mode == 1:          #streak reaward in modes 0 or 1
                if (down_pix >= PIXEL_RIGHTW_START) and (down_pix <= PIXEL_RIGHTW_END):   #if (down_pix >= 15):
                    strip.setPixelColorRGB(down_pix,r,g,b)
                    #print "down:", down_pix
            else:
                if (down_pix >= PIXEL_RIGHTW_START) and (down_pix <= PIXEL_RIGHTW_END):   #if (down_pix >= 15):
                    #print "zero'd down", down_pix
                    strip.setPixelColorRGB(down_pix,0,0,0)

        if redraw_pixels:   #redraw pixels if the global redraw_pixels flag is set
            strip.show()    #this flag is usually set, but may be cleared temporarily
                            #by some animations that do multiple strip buffer updates
                            #before finally calling strip.show() to update all pixels
                            #in one shot
    # end if newdata:


def getColorWheel(h, bright):

    '''
    Convert a given hue and brightness to RGB(Red Green Blue) and populate the
    global variables red, green, and blue with the result which can be directly
    sent to the pixels via setPixelRGB() and the like.
    This function will automatically "unwrap" full rotations.
    h is hue value, integer between 0 and 360
    bright is the brightness value between 0 and 255
    Based on code by Chris Hulbert, found at: http://splinter.com.au/blog/?p=29
    :param h:
        h is hue value, integer between 0 and 360
    :param bright:
        bright is the brightness value between 0 and 255
    :return:
        list of red, green, blue values 0-255, ready for sending direct to NeoPixels
    '''
    global r
    global g
    global b
    #make sure value passed falls within 0 and 360
    if (h > 359):
        while (h > 359):
            h = h - 359  # subtract full rotations until within range

    if (h < 0):
        while (h < 0):
            h = h + 359  # add full rotations until within range
        h = 359 - h


    #this is the algorithm to convert from RGB to HSV
    r = 0
    g = 0
    b = 0
    s = 1
    bright = float(bright)  #turn bright into float, otherwise python assumes int and rounds it
    v = bright / 255
    i = int(h/60.0)
    f = h/60.0 - i
    pv = v * (1 - s)
    qv = v * (1 - s*f)
    tv = v * (1 - s * (1 - f))

    if i == 0:
        r = v
        g = tv
        b = pv

    elif i == 1:
        r = qv
        g = v
        b = pv

    elif i == 2:
        r = pv
        g = v
        b = tv

    elif i == 3:
        r = pv
        g = qv
        b = v

    elif i == 4:
        r = tv
        g = pv
        b = v

    elif i == 5:
        r = v
        g = pv
        b = qv
    else:
        r = 0
        g = 0
        b = 0

    r = int(255 * r)
    g = int(255 * g)
    b = int(255 * b)

    rgb = r,g,b
    return rgb
