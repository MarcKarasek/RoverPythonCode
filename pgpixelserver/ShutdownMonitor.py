# This script should be launched into the background via root crontab at boot
# This script monitors the Spirit Rover Int1 pin. If this pin is held low
# for a certain timeout, it will cause an immediate shutdown of the Raspberry Pi

# External module imports
import RPi.GPIO as GPIO             #for access to the GPIO pin
from time import time, sleep        #for "sleep" & timestamp functions
import os                           #needed to initiate shutdown/halt

# Pin Definitons:
int1Pin = 17 # Broadcom pin 17 (P1 pin 11), Spirit pin "INT1_Pi"

# Pin Setup:
GPIO.setmode(GPIO.BCM)              # Broadcom pin-numbering scheme
GPIO.setwarnings(False)             # Disable warnings if another script has changed the pin

INT1_POWERDOWN_TIMEOUT = 0.500      #time int1 needs to be held low to initiate a power-down/halt of the Pi

try:
    while 1:
        GPIO.setup(int1Pin, GPIO.OUT)   # Pin set as output low
        GPIO.output(int1Pin, 0)
        sleep(0.05)
        GPIO.setup(int1Pin, GPIO.IN)    # Pin set as input, pull-up (PIC weak pullup also sets this high)
        GPIO.setup(int1Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        sleep(0.075)
        if (GPIO.input(int1Pin) == 0):
            print "int1 held low"
            holdStart = time()
            while (GPIO.input(int1Pin) == 0):
                sleep(0.005)
                if ((time()-holdStart) > INT1_POWERDOWN_TIMEOUT):
                    os.system('sudo wall "Spirit Shutdown Now!"')
                    os.system('sudo shutdown -h now "Spirit Shutdown Now!"')

except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    GPIO.cleanup() # cleanup all GPIO
