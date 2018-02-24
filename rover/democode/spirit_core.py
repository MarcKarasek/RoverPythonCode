#!/usr/bin/python

from time import sleep          #needed for "sleep" function
from time import time
import smbus
import spidev                   #SPI interface to talk between Pi and Arduino processor

PIC_I2C_ADDRESS = 0x32
PIC_CYCLE_DURATION = 0.020
SPI_SPEED = 75000 #400000              #SPI transmit speed in Hz.
SPI_PAYLOAD_MAX_LENGTH = 9             #max usable SPI data bytes (not including checksum & tail byte)
                                       #allows 1 target register plus 8 usable bytes of data
SERVO_CENTER_TILT = 75  #actual value (0-127 degrees) sent to PIC to center this servo
SERVO_CENTER_PAN = 90   #actual value (0-127 degrees) sent to PIC to center this servo
SERVO_CENTER_GRIP = 10  #actual value (0-127 degrees) sent to PIC to center this servo

class Spirit(object):

    '''
    Functions for communicating via SPI with Arduino processor on Spirit Mainboard
    '''

    def motors(self,left,right):
        #print left, right
        spi_register = 130  #register key Arduino is looking for to process received data
        left = self.clamp(left,-255,255)    #clamp values to within expected limits
        right = self.clamp(right,-255,255)   #
        #print left, right
        left = (int(left/2))+128            #convert to format expected by Arduino SPI receiver
        right = (int(right/2))+128          #
        #print left, right
        self.spi_transfer([spi_register,left,right])    #send it

    '''
    Status Registers, Important Inputs, and PIC Comparators
    '''

    ''' PIC_ReadStatus, Register 1 '''
    def current_warning_int(self):
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return self.currentWarningInt
        resp = self.PIC_ReadStatus()
        return self.currentWarningInt

    def voltage_warning_int(self):
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return self.voltageWarningInt
        resp = self.PIC_ReadStatus()
        return self.voltageWarningInt

    def shutdown_now_int(self):
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return self.shutdownNowInt
        resp = self.PIC_ReadStatus()
        return self.shutdownNowInt

    def motor_stop_int(self):
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return self.motorStopInt
        resp = self.PIC_ReadStatus()
        return self.motorStopInt

    def surface_sense_int(self):
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return self.surfaceSenseInt
        resp = self.PIC_ReadStatus()
        return self.surfaceSenseInt

    def power_sense_int(self):
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return self.powerSenseInt
        resp = self.PIC_ReadStatus()
        return self.powerSenseInt

    def range_sense_int(self):
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return self.rangeSenseInt
        resp = self.PIC_ReadStatus()
        return self.rangeSenseInt

    def amb_sense_int(self):
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return self.ambSenseInt
        resp = self.PIC_ReadStatus()
        return self.ambSenseInt

    def uart_rx_thresh_int(self):
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return self.UARTRxThreshInt
        resp = self.PIC_ReadStatus()
        return self.UARTRxThreshInt

    def uart_rx_null_int(self):
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return self.UARTRxNullInt
        resp = self.PIC_ReadStatus()
        return self.UARTRxNullInt

    def uart_tx_in_prog(self):
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return self.UARTTxInProg
        resp = self.PIC_ReadStatus()
        return self.UARTTxInProg

    def PIC_ReadStatus(self):
        #reply with cached data if less than one PIC cycle has passed
        if ((time()-self._time_status_reg) < PIC_CYCLE_DURATION):
            return (self.statusBank0, self.statusBank1)
        #else, query fresh data from PIC via i2c
        register = 1
        length = 3
        pause = 0.0016
        sleep(pause)    #make sure we're clear of any prev transaction
        i2c_reply = self.i2cRead(register,length,pause)
        if (i2c_reply < 0):
            return i2c_reply
        #mark time this read was sucessful
        self._time_status_reg = time()
        #load variables based on i2c reply packet
        self.statusBank0 = i2c_reply[1]
        self.statusBank1 = i2c_reply[2]
        self.currentWarningInt = (statusBank0 >> 0) & 1
        self.voltageWarningInt = (statusBank0 >> 1) & 1
        self.shutdownNowInt = (statusBank0 >> 2) & 1
        self.motorStopInt = (statusBank0 >> 3) & 1
        self.surfaceSenseInt = (statusBank0 >> 4) & 1
        self.powerSenseInt = (statusBank0 >> 5) & 1
        self.rangeSenseInt = (statusBank0 >> 6) & 1
        self.ambSenseInt = (statusBank0 >> 7) & 1
        self.UARTRxThreshInt = (statusBank1 >> 0) & 1
        self.UARTRxNullInt = (statusBank1 >> 1) & 1
        self.UARTTxInProg = (statusBank1 >> 2) & 1
        return (self.statusBank0, self.statusBank1)

    ''' PIC_ReadInputs, Register 5 '''
    def button(self):
        if ((time()-self._time_inputs) < PIC_CYCLE_DURATION):
            return self.button
        resp = self.PIC_ReadInputs()
        return self.button

    def button_power(self):
        if ((time()-self._time_inputs) < PIC_CYCLE_DURATION):
            return self.buttonPower
        resp = self.PIC_ReadInputs()
        return self.buttonPower

    def accel_int1(self):
        if ((time()-self._time_inputs) < PIC_CYCLE_DURATION):
            return self.accelInt1
        resp = self.PIC_ReadInputs()
        return self.accelInt1

    def gyro_int1(self):
        if ((time()-self._time_inputs) < PIC_CYCLE_DURATION):
            return self.gyroInt1
        resp = self.PIC_ReadInputs()
        return self.gyroInt1

    def gyro_int2(self):
        if ((time()-self._time_inputs) < PIC_CYCLE_DURATION):
            return self.gyroInt2
        resp = self.PIC_ReadInputs()
        return self.gyroInt2

    def chg_present(self):
        if ((time()-self._time_inputs) < PIC_CYCLE_DURATION):
            return self.chgPresent
        resp = self.PIC_ReadInputs()
        return self.chgPresent

    def chg_in_prog(self):
        if ((time()-self._time_inputs) < PIC_CYCLE_DURATION):
            return self.chgInProg
        resp = self.PIC_ReadInputs()
        return self.chgInProg

    def xbee_assoc(self):
        if ((time()-self._time_inputs) < PIC_CYCLE_DURATION):
            return self.xbeeAssoc
        resp = self.PIC_ReadInputs()
        return self.xbeeAssoc

    def PIC_ReadInputs(self):
        #reply with cached data if less than one PIC cycle has passed
        if ((time()-self._time_inputs) < PIC_CYCLE_DURATION):
            return (self.picInputs)
        #else, query fresh data from PIC via i2c
        register = 5
        length = 2
        pause = 0.0016
        sleep(pause)    #make sure we're clear of any prev transaction
        i2c_reply = self.i2cRead(register,length,pause)
        if (i2c_reply < 0):
            return i2c_reply
        #mark time this read was sucessful
        self._time_inputs = time()
        #load variables based on i2c reply packet
        self.picInputs = i2c_reply[1]
        self.button = (picInputs >> 0) & 1
        self.buttonPower = (picInputs >> 1) & 1
        self.accelInt1 = (picInputs >> 2) & 1
        self.gyroInt1 = (picInputs >> 3) & 1
        self.gyroInt2 = (picInputs >> 4) & 1
        self.chgPresent = (picInputs >> 5) & 1
        self.chgInProg = (picInputs >> 6) & 1
        self.xbeeAssoc = (picInputs >> 7) & 1
        return (self.picInputs)

    ''' PIC_ReadComparators, Register 6 '''
    def current_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.currentComparator
        resp = self.PIC_ReadComparators()
        return self.currentComparator

    def voltage_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.voltageComparator
        resp = self.PIC_ReadComparators()
        return self.voltageComparator

    def left_outer_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.leftOuterComparator
        resp = self.PIC_ReadComparators()
        return self.leftOuterComparator

    def left_inner_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.leftInnerComparator
        resp = self.PIC_ReadComparators()
        return self.leftInnerComparator

    def right_outer_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.rightOuterComparator
        resp = self.PIC_ReadComparators()
        return self.rightOuterComparator

    def right_inner_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.rightInnerComparator
        resp = self.PIC_ReadComparators()
        return self.rightInnerComparator

    def rear_outer_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.rearOuterComparator
        resp = self.PIC_ReadComparators()
        return self.rearOuterComparator

    def rear_inner_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.rearInnerComparator
        resp = self.PIC_ReadComparators()
        return self.rearInnerComparator

    def rangefinder_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.rangefinderComparator
        resp = self.PIC_ReadComparators()
        return self.rangefinderComparator

    def amb_left_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.ambLeftComparator
        resp = self.PIC_ReadComparators()
        return self.ambLeftComparator

    def amb_right_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.ambRightComparator
        resp = self.PIC_ReadComparators()
        return self.ambRightComparator

    def amb_rear_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.ambRearComparator
        resp = self.PIC_ReadComparators()
        return self.ambRearComparator

    def wall_power_comp(self):
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return self.wallPowerComparator
        resp = self.PIC_ReadComparators()
        return self.wallPowerComparator

    def PIC_ReadComparators(self):
        #reply with cached data if less than one PIC cycle has passed
        if ((time()-self._time_comparators) < PIC_CYCLE_DURATION):
            return (self.thresholdComparators1, self.thresholdComparators2)
        #else, query fresh data from PIC via i2c
        register = 6
        length = 3
        pause = 0.0016
        sleep(pause)    #make sure we're clear of any prev transaction
        i2c_reply = self.i2cRead(register,length,pause)
        if (i2c_reply < 0):
            return i2c_reply
        #mark time this read was sucessful
        self._time_comparators = time()
        #load variables based on i2c reply packet
        self.thresholdComparators1 = i2c_reply[1]
        self.thresholdComparators2 = i2c_reply[2]
        self.currentComparator = (thresholdComparators1 >> 0) & 1
        self.voltageComparator = (thresholdComparators1 >> 1) & 1
        self.leftOuterComparator = (thresholdComparators1 >> 2) & 1
        self.leftInnerComparator = (thresholdComparators1 >> 3) & 1
        self.rightOuterComparator = (thresholdComparators1 >> 4) & 1
        self.rightInnerComparator = (thresholdComparators1 >> 5) & 1
        self.rearOuterComparator = (thresholdComparators1 >> 6) & 1
        self.rearInnerComparator = (thresholdComparators1 >> 7) & 1
        self.rangefinderComparator = (thresholdComparators2 >> 0) & 1
        self.ambLeftComparator = (thresholdComparators2 >> 1) & 1
        self.ambRightComparator = (thresholdComparators2 >> 2) & 1
        self.ambRearComparator = (thresholdComparators2 >> 3) & 1
        self.wallPowerComparator = (thresholdComparators2 >> 4) & 1
        return (self.thresholdComparators1, self.thresholdComparators2)

    '''
    Power Status
    '''

    ''' PIC_ReadPower, Register 21 '''
    def power_voltage(self):
        if ((time()-self._time_power) < PIC_CYCLE_DURATION):
            return self.powerVoltage
        resp = self.PIC_ReadPower()
        return self.powerVoltage

    def power_current(self):
        if ((time()-self._time_power) < PIC_CYCLE_DURATION):
            return self.powerCurrent
        resp = self.PIC_ReadPower()
        return self.powerCurrent

    def PIC_ReadPower(self):
        #reply with cached data if less than one PIC cycle has passed
        if ((time()-self._time_power) < PIC_CYCLE_DURATION):
            return (self.powerVoltage, self.powerCurrent)
        #else, query fresh data from PIC via i2c
        register = 21
        length = 5
        pause = 0.0016
        sleep(pause)    #make sure we're clear of any prev transaction
        i2c_reply = self.i2cRead(register,length,pause)
        if (i2c_reply < 0):
            return i2c_reply
        #mark time this read was sucessful
        self._time_power = time()
        #load variables based on i2c reply packet
        self.powerVoltage = i2c_reply[1]<<8 | i2c_reply[2]
        self.powerCurrent = i2c_reply[3]<<8 | i2c_reply[4]
        self.powerVoltage = float(self.powerVoltage) / 1000
        self.powerCurrent = float(self.powerCurrent) / 1000
        return (self.powerVoltage, self.powerCurrent)

    ''' PIC_ReadPowerAverages, Register 26 '''
    def power_voltage_avg(self):
        if ((time()-self._time_power_average) < PIC_CYCLE_DURATION):
            return self.powerVoltageAverage
        resp = self.PIC_ReadPowerAverages()
        return self.powerVoltageAverage

    def power_current_avg(self):
        if ((time()-self._time_power_average) < PIC_CYCLE_DURATION):
            return self.powerCurrentAverage
        resp = self.PIC_ReadPowerAverages()
        return self.powerCurrentAverage

    def PIC_ReadPowerAverages(self):
        #reply with cached data if less than one PIC cycle has passed
        if ((time()-self._time_power_average) < PIC_CYCLE_DURATION):
            return (self.powerVoltageAverage, self.powerCurrentAverage)
        #else, query fresh data from PIC via i2c
        register = 26
        length = 5
        pause = 0.0025  #pause = 0.0016
        sleep(pause)    #make sure we're clear of any prev transaction
        i2c_reply = self.i2cRead(register,length,pause)
        if (i2c_reply < 0):
            return i2c_reply
        #mark time this read was sucessful
        self._time_power_average = time()
        #load variables based on i2c reply packet
        self.powerVoltageAverage = i2c_reply[1]<<8 | i2c_reply[2]
        self.powerCurrentAverage = i2c_reply[3]<<8 | i2c_reply[4]
        self.powerVoltageAverage = float(self.powerVoltageAverage) / 1000
        self.powerCurrentAverage = float(self.powerCurrentAverage) / 1000
        return (self.powerVoltageAverage, self.powerCurrentAverage)

    '''
    Ambient Sensors
    '''

    ''' PIC_ReadAllAmbientSensors, Register 32 '''
    def amb_left(self):
        if ((time()-self._time_ambient) < PIC_CYCLE_DURATION):
            return self.ambLeft
        resp = self.PIC_ReadAllAmbientSensors()
        return self.ambLeft

    def amb_right(self):
        if ((time()-self._time_ambient) < PIC_CYCLE_DURATION):
            return self.ambRight
        resp = self.PIC_ReadAllAmbientSensors()
        return self.ambRight

    def amb_rear(self):
        if ((time()-self._time_ambient) < PIC_CYCLE_DURATION):
            return self.ambRear
        resp = self.PIC_ReadAllAmbientSensors()
        return self.ambRear

    def PIC_ReadAllAmbientSensors(self):
        #reply with cached data if less than one PIC cycle has passed
        if ((time()-self._time_ambient) < PIC_CYCLE_DURATION):
            return (self.ambLeft, self.ambRight, self.ambRear)
        #else, query fresh data from PIC via i2c
        register = 32
        length = 7
        pause = 0.0016
        sleep(pause)    #make sure we're clear of any prev transaction
        i2c_reply = self.i2cRead(register,length,pause)
        if (i2c_reply < 0):
            return i2c_reply
        #mark time this read was sucessful
        self._time_ambient = time()
        #load variables based on i2c reply packet
        self.ambLeft = i2c_reply[1]<<8 | i2c_reply[2]
        self.ambRight = i2c_reply[3]<<8 | i2c_reply[4]
        self.ambRear = i2c_reply[5]<<8 | i2c_reply[6]
        return (self.ambLeft, self.ambRight, self.ambRear)

    ''' PIC_ReadAllAmbientAverages, Register 35 '''
    def amb_left_avg(self):
        if ((time()-self._time_ambient_average) < PIC_CYCLE_DURATION):
            return self.ambLeftAverage
        resp = self.PIC_ReadAllAmbientAverages()
        return self.ambLeftAverage

    def amb_right_avg(self):
        if ((time()-self._time_ambient_average) < PIC_CYCLE_DURATION):
            return self.ambRightAverage
        resp = self.PIC_ReadAllAmbientAverages()
        return self.ambRightAverage

    def amb_rear_avg(self):
        if ((time()-self._time_ambient_average) < PIC_CYCLE_DURATION):
            return self.ambRearAverage
        resp = self.PIC_ReadAllAmbientAverages()
        return self.ambRearAverage

    def PIC_ReadAllAmbientAverages(self):
        #reply with cached data if less than one PIC cycle has passed
        if ((time()-self._time_ambient_average) < PIC_CYCLE_DURATION):
            return (self.ambLeftAverage, self.ambRightAverage, self.ambRearAverage)
        #else, query fresh data from PIC via i2c
        register = 35
        length = 7
        pause = 0.0016
        sleep(pause)    #make sure we're clear of any prev transaction
        i2c_reply = self.i2cRead(register,length,pause)
        if (i2c_reply < 0):
            return i2c_reply
        #mark time this read was sucessful
        self._time_ambient_average = time()
        #load variables based on i2c reply packet
        self.ambLeftAverage = i2c_reply[1]<<8 | i2c_reply[2]
        self.ambRightAverage = i2c_reply[3]<<8 | i2c_reply[4]
        self.ambRearAverage = i2c_reply[5]<<8 | i2c_reply[6]
        return (self.ambLeftAverage, self.ambRightAverage, self.ambRearAverage)

    '''
    Surface Sensors
    '''

    ''' PIC_ReadAllSurfaceSensors, Register 31 '''
    def surf_left_0(self):
        if ((time()-self._time_surface) < PIC_CYCLE_DURATION):
            return self.surfLeft0
        resp = self.PIC_ReadAllSurfaceSensors()
        return self.surfLeft0

    def surf_left_1(self):
        if ((time()-self._time_surface) < PIC_CYCLE_DURATION):
            return self.surfLeft1
        resp = self.PIC_ReadAllSurfaceSensors()
        return self.surfLeft1

    def surf_right_0(self):
        if ((time()-self._time_surface) < PIC_CYCLE_DURATION):
            return self.surfRight0
        resp = self.PIC_ReadAllSurfaceSensors()
        return self.surfRight0

    def surf_right_1(self):
        if ((time()-self._time_surface) < PIC_CYCLE_DURATION):
            return self.surfRight1
        resp = self.PIC_ReadAllSurfaceSensors()
        return self.surfRight1

    def surf_rear_0(self):
        if ((time()-self._time_surface) < PIC_CYCLE_DURATION):
            return self.surfRear0
        resp = self.PIC_ReadAllSurfaceSensors()
        return self.surfRear0

    def surf_rear_1(self):
        if ((time()-self._time_surface) < PIC_CYCLE_DURATION):
            return self.surfRear1
        resp = self.PIC_ReadAllSurfaceSensors()
        return self.surfRear1

    def PIC_ReadAllSurfaceSensors(self):
        #reply with cached data if less than one PIC cycle has passed
        if ((time()-self._time_surface) < PIC_CYCLE_DURATION):
            return (self.surfLeft1,self.surfLeft0,self.surfRight0,
                    self.surfRight1,self.surfRear0,self.surfRear1)
        #else, query fresh data from PIC via i2c
        register = 31
        length = 13
        pause = 0.0017
        sleep(pause)    #make sure we're clear of any prev transaction
        i2c_reply = self.i2cRead(register,length,pause)
        if (i2c_reply < 0):
            return i2c_reply
        #mark time this read was sucessful
        self._time_surface = time()
        #load variables based on i2c reply packet
        self.surfLeft0 = i2c_reply[1]<<8 | i2c_reply[2]
        self.surfRight0 = i2c_reply[3]<<8 | i2c_reply[4]
        self.surfRear0 = i2c_reply[5]<<8 | i2c_reply[6]
        self.surfLeft1 = i2c_reply[7]<<8 | i2c_reply[8]
        self.surfRight1 = i2c_reply[9]<<8 | i2c_reply[10]
        self.surfRear1 = i2c_reply[11]<<8 | i2c_reply[12]
        return (self.surfLeft1,self.surfLeft0,self.surfRight0,
                self.surfRight1,self.surfRear0,self.surfRear1)

    ''' PIC_ReadAllSurfaceAverages, Register 36 '''
    def surf_left_0_avg(self):
        if ((time()-self._time_surface_average) < PIC_CYCLE_DURATION):
            return self.surfLeft0Average
        resp = self.PIC_ReadAllSurfaceAverages()
        return self.surfLeft0Average

    def surf_left_1_avg(self):
        if ((time()-self._time_surface_average) < PIC_CYCLE_DURATION):
            return self.surfLeft1Average
        resp = self.PIC_ReadAllSurfaceAverages()
        return self.surfLeft1Average

    def surf_right_0_avg(self):
        if ((time()-self._time_surface_average) < PIC_CYCLE_DURATION):
            return self.surfRight0Average
        resp = self.PIC_ReadAllSurfaceAverages()
        return self.surfRight0Average

    def surf_right_1_avg(self):
        if ((time()-self._time_surface_average) < PIC_CYCLE_DURATION):
            return self.surfRight1Average
        resp = self.PIC_ReadAllSurfaceAverages()
        return self.surfRight1Average

    def surf_rear_0_avg(self):
        if ((time()-self._time_surface_average) < PIC_CYCLE_DURATION):
            return self.surfRear0Average
        resp = self.PIC_ReadAllSurfaceAverages()
        return self.surfRear0Average

    def surf_rear_1_avg(self):
        if ((time()-self._time_surface_average) < PIC_CYCLE_DURATION):
            return self.surfRear1Average
        resp = self.PIC_ReadAllSurfaceAverages()
        return self.surfRear1Average

    def PIC_ReadAllSurfaceAverages(self):
        #reply with cached data if less than one PIC cycle has passed
        if ((time()-self._time_surface_average) < PIC_CYCLE_DURATION):
            return (self.surfLeft1Average,self.surfLeft0Average,self.surfRight0Average,
                    self.surfRight1Average,self.surfRear0Average,self.surfRear1Average)
        #else, query fresh data from PIC via i2c
        register = 36
        length = 13
        pause = 0.0017
        sleep(pause)    #make sure we're clear of any prev transaction
        i2c_reply = self.i2cRead(register,length,pause)
        if (i2c_reply < 0):
            return i2c_reply
        #mark time this read was sucessful
        self._time_surface_average = time()
        #load variables based on i2c reply packet
        self.surfLeft0Average = i2c_reply[1]<<8 | i2c_reply[2]
        self.surfRight0Average = i2c_reply[3]<<8 | i2c_reply[4]
        self.surfRear0Average = i2c_reply[5]<<8 | i2c_reply[6]
        self.surfLeft1Average = i2c_reply[7]<<8 | i2c_reply[8]
        self.surfRight1Average = i2c_reply[9]<<8 | i2c_reply[10]
        self.surfRear1Average = i2c_reply[11]<<8 | i2c_reply[12]
        return (self.surfLeft1Average,self.surfLeft0Average,self.surfRight0Average,
                self.surfRight1Average,self.surfRear0Average,self.surfRear1Average)


    '''
    Servo Controls
    '''

    def servo_speed(self, speed_dps):   #set servo speed in degrees per second
        register = 51
        pause = 0.0015
        self.servoSpeed = int(speed_dps)
        self.servoSpeed = self.clamp(self.servoSpeed, 1, 3000)
        data = [((self.servoSpeed >> 8) & 0xFF), (self.servoSpeed & 0xFF)]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def servo_tilt(self, position):    #set servo position
        register = 52
        pause = 0.0015
        self.servoTilt = int(position)
        self.servoTilt = self.clamp(self.servoTilt, -90, 90)
        servoSetpoint = self.servoTilt + SERVO_CENTER_TILT
        data = [servoSetpoint]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def servo_tilt_move(self, offset):   #move servo to relative position vs current position
        register = 52
        pause = 0.0015
        offset = int(offset)
        self.servoTilt = self.servoTilt + offset
        self.servoTilt = self.clamp(self.servoTilt, -90, 90)
        servoSetpoint = self.servoTilt + SERVO_CENTER_TILT
        data = [servoSetpoint]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def servo_pan(self, position):       #set servo position
        register = 53
        pause = 0.0015
        self.servoPan = int(position)
        self.servoPan = self.clamp(self.servoPan, -90, 90)
        servoSetpoint = self.servoPan + SERVO_CENTER_PAN
        data = [servoSetpoint]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def servo_pan_move(self, offset):   #move servo to relative position vs current position
        register = 53
        pause = 0.0015
        offset = int(offset)
        self.servoPan = self.servoPan + offset
        self.servoPan = self.clamp(self.servoPan, -90, 90)
        servoSetpoint = self.servoPan + SERVO_CENTER_PAN
        data = [servoSetpoint]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def servo_grip(self, position):     #set servo position
        register = 54
        pause = 0.0015
        self.servoGrip = int(position)
        self.servoGrip = self.clamp(self.servoGrip, -10, 180)
        servoSetpoint = self.servoGrip + SERVO_CENTER_GRIP
        data = [servoSetpoint]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def servo_grip_move(self, offset):   #move servo to relative position vs current position
        register = 54
        pause = 0.0015
        offset = int(offset)
        self.servoGrip = self.servoGrip + offset
        self.servoGrip = self.clamp(self.servoGrip, -10, 180)
        servoSetpoint = self.servoGrip + SERVO_CENTER_GRIP
        data = [servoSetpoint]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def servo_trim_tilt(self, trim):   #set servo trim
        register = 55
        pause = 0.0015
        self.servoTrim_Tilt = int(trim)
        self.servoTrim_Tilt = self.clamp(self.servoTrim_Tilt, -45, 45)
        servoTrimpoint = self.servoTrim_Tilt + 127  #positive value. 127 subtr at other end
        data = [servoTrimpoint]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def servo_trim_pan(self, trim):    #set servo trim
        register = 56
        pause = 0.0015
        self.servoTrim_Pan = int(trim)
        self.servoTrim_Pan = self.clamp(self.servoTrim_Pan, -45, 45)
        servoTrimpoint = self.servoTrim_Pan + 127  #positive value. 127 subtr at other end
        data = [servoTrimpoint]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def servo_trim_grip(self, trim):   #set servo trim
        register = 57
        pause = 0.0015
        self.servoTrim_Grip = int(trim)
        self.servoTrim_Grip = self.clamp(self.servoTrim_Grip, -45, 45)
        servoTrimpoint = self.servoTrim_Grip + 127  #positive value. 127 subtr at other end
        data = [servoTrimpoint]
        resp = self.i2cWrite(register,data,pause)
        return resp

    '''
    Rangefinder Control
    '''

    ''' PIC_SetRangefinderAutoInterval, Register 65 '''
    def rangefinder_auto_interval(self, interval):
        self.rangeAutoInterval = self.clamp(interval, 0, (250*PIC_CYCLE_DURATION))
        if (self.rangeAutoInterval > 0) and (self.rangeAutoInterval < PIC_CYCLE_DURATION):
            interval_PIC = 1
        else:
            interval_PIC = int(self.rangeAutoInterval/PIC_CYCLE_DURATION)
        register = 65
        pause = 0.0015
        data = [interval_PIC]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def rangefinder(self):
        if ((time()-self._time_rangefinder) < PIC_CYCLE_DURATION):
            return self.rangefinderDistance
        resp = self.PIC_ReadRangefinder()
        return self.rangefinderDistance

    def rangefinder_good_counts(self):
        if ((time()-self._time_rangefinder) < PIC_CYCLE_DURATION):
            return self.rangefinderGoodCounts
        resp = self.PIC_ReadRangefinder()
        return self.rangefinderGoodCounts

    ''' PIC_ReadRangefinder, Register 66 '''
    def PIC_ReadRangefinder(self):
        #reply with cached data if less than one PIC cycle has passed
        if ((time()-self._time_rangefinder) < PIC_CYCLE_DURATION):
            return (self.rangefinderDistance,self.rangefinderGoodCounts)
        #else, query fresh data from PIC via i2c
        register = 66
        length = 4
        pause = 0.0017
        sleep(pause)    #make sure we're clear of any prev transaction
        i2c_reply = self.i2cRead(register,length,pause)
        if (i2c_reply < 0):
            return i2c_reply
        #mark time this read was sucessful
        self._time_rangefinder = time()
        #load variables based on i2c reply packet
        self.rangefinderDistance = i2c_reply[1]<<8 | i2c_reply[2]
        self.rangefinderGoodCounts = i2c_reply[3]
        return (self.rangefinderDistance,self.rangefinderGoodCounts)

    '''
    Other Misc Configuration Parameters
    '''

    ''' PIC_SetAverageIntervals, Register 101 '''
    def avg_interval_surface(self, avgPeriod):
        register = 101
        pause = 0.0015
        temp = (avgPeriod / (PIC_CYCLE_DURATION*8)) #avgPeriod averaged over 8 CYCLE_DURATION cycles
        self.avgIntervalSurface = int(round(temp,0))
        data = [self.avgIntervalSurface, self.avgIntervalAmbient, self.avgIntervalPower]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def avg_interval_ambient(self, avgPeriod):
        register = 101
        pause = 0.0015
        temp = (avgPeriod / (PIC_CYCLE_DURATION*8)) #avgPeriod averaged over 8 CYCLE_DURATION cycles
        self.avgIntervalAmbient = int(round(temp,0))
        data = [self.avgIntervalSurface, self.avgIntervalAmbient, self.avgIntervalPower]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def avg_interval_power(self, avgPeriod):
        register = 101
        pause = 0.0015
        temp = (avgPeriod / (PIC_CYCLE_DURATION*8)) #avgPeriod averaged over 8 CYCLE_DURATION cycles
        self.avgIntervalPower = int(round(temp,0))
        data = [self.avgIntervalSurface, self.avgIntervalAmbient, self.avgIntervalPower]
        resp = self.i2cWrite(register,data,pause)
        return resp

    def i2c_process_delay(self, speed_dps):   #set i2cProcessDelay (approx delay is delay*3uS)
                                        #normally not needed to adjust, but may be needed
                                        #to clear up I2C data errors in some cases
        register = 109
        pause = 0.0015
        speed_dps = self.clamp(speed_dps, 1, 250)
        #print speed_dps
        #self.servoSpeed = int(speed_dps)
        #self.servoSpeed = self.clamp(self.servoSpeed, 1, 3000)
        data = [speed_dps]
        resp = self.i2cWrite(register,data,pause)
        return resp


        #register = 52
        #pause = 0.0015
        #self.servoTilt = int(position)
        #self.servoTilt = self.clamp(self.servoTilt, -90, 90)
        #servoSetpoint = self.servoTilt + SERVO_CENTER_TILT
        #data = [servoSetpoint]
        #resp = self.i2cWrite(register,data,pause)
        #return resp

    def __init__(self):
        self.i2c = smbus.SMBus(1)
        self.name = "Spirit"
        self.i2c_read_extra_pause = 0
        self.spi = spidev.SpiDev()               #create SPI port object
        self.spi.open(0, 0)                      #open spi port 0, device (CS) 0
        self.spi.max_speed_hz = SPI_SPEED        #running SPI too fast will result in errors 75000 is safe

        self._time_status_reg = time() - 0.03            #last time surface sensors read
        self.statusBank0 = 0
        self.statusBank1 = 0
        self.currentWarningInt = 0
        self.voltageWarningInt = 0
        self.shutdownNowInt = 0
        self.motorStopInt = 0
        self.surfaceSenseInt = 0
        self.powerSenseInt = 0
        self.rangeSenseInt = 0
        self.ambSenseInt = 0
        self.UARTRxThreshInt = 0
        self.UARTRxNullInt = 0
        self.UARTTxInProg = 0

        self._time_inputs = time() - 0.03                #last time surface sensors read
        self.picInputs = 0
        self.button = 0
        self.buttonPower = 0
        self.accelInt1 = 0
        self.gyroInt1 = 0
        self.gyroInt2 = 0
        self.chgPresent = 0
        self.chgInProg = 0
        self.xbeeAssoc = 0

        self._time_comparators = time() - 0.03           #last time surface sensors read
        self.thresholdComparators1 = 0
        self.thresholdComparators2 = 0
        self.currentComparator = 0
        self.voltageComparator = 0
        self.leftOuterComparator = 0
        self.leftInnerComparator = 0
        self.rightOuterComparator = 0
        self.rightInnerComparator = 0
        self.rearOuterComparator = 0
        self.rearInnerComparator = 0
        self.rangefinderComparator = 0
        self.ambLeftComparator = 0
        self.ambRightComparator = 0
        self.ambRearComparator = 0
        self.wallPowerComparator = 0

        self._time_power = time() - 0.03            #last time surface sensors read
        self.powerVoltage = 0
        self.powerCurrent = 0

        self._time_power_average = time() - 0.03            #last time surface sensors read
        self.powerVoltageAverage = 0
        self.powerCurrentAverage = 0

        self._time_surface = time() - 0.03            #last time surface sensors read
        self.surfLeft0 = 0
        self.surfLeft1 = 0
        self.surfRight0 = 0
        self.surfRight1 = 0
        self.surfRear0 = 0
        self.surfRear1 = 0

        self._time_surface_average = time() - 0.03    #last time surface sensor avg read
        self.surfLeft0Average = 0
        self.surfLeft1Average = 0
        self.surfRight0Average = 0
        self.surfRight1Average = 0
        self.surfRear0Average = 0
        self.surfRear1Average = 0

        self._time_ambient = time() - 0.03            #last time surface sensors read
        self.ambLeft = 0
        self.ambRight = 0
        self.ambRear = 0

        self._time_ambient_average = time() - 0.03    #last time surface sensors read
        self.ambLeftAverage = 0
        self.ambRightAverage = 0
        self.ambRearAverage = 0

        self.servoSpeed = 3000
        self.servoTilt = 75
        self.servoPan = 90
        self.servoGrip = 10
        self.servoTrim_Tilt = 0
        self.servoTrim_Pan = 0
        self.servoTrim_Grip = 0

        self._time_rangefinder = time() - 0.03            #last time surface sensors read
        self.rangeAutoInterval = 0
        self.rangefinderDistance = 0

        self.rangefinderGoodCounts = 0
        self.avgIntervalSurface = 6
        self.avgIntervalAmbient = 6
        self.avgIntervalPower = 6

    def i2cRead(self,register,length,pause):
        sleep(pause)
        try:
            self.i2c.write_byte(PIC_I2C_ADDRESS,register)
        except IOError:
            print ("Error on Write")
            return -1
        sleep( pause + (self.i2c_read_extra_pause*.000001) )
        try:
            i2c_reply = self.i2c.read_i2c_block_data(PIC_I2C_ADDRESS,register,length)
        except IOError:
            print ("Error on Read")
            return -2
        if (i2c_reply[0] != register):
            print ("Wrong register replied")
            return -3
        else:
            return i2c_reply

    def i2cWrite(self,register,data,pause):
        sleep(pause)
        try:
            self.i2c.write_i2c_block_data(PIC_I2C_ADDRESS,register,data)
        except IOError:
            print ("Error on Write")
            return -1
        return 0

    def clamp(self, n, minn, maxn):   #constrain value to within a given range
        if n < minn:
            return minn
        elif n > maxn:
            return maxn
        else:
            return n

    def i2cTest(self):
        register = 31
        length = 12
        sleep(0.0015)
        try:
            self.i2c.write_byte(PIC_I2C_ADDRESS,register)
        except IOError:
            print ("Error on Write")
        sleep(0.0015)
        try:
            i2c_reply = self.i2c.read_i2c_block_data(PIC_I2C_ADDRESS,register,length)
        except IOError:
            print ("Error on Read")
        if (i2c_reply[0] != register):
            print ("Wrong register replied")
            return -1
        else:
            return i2c_reply

    def spi_transfer(self, dataToSend):
        if (type(dataToSend) != list):
            dataToSend = [dataToSend, 0x00]
        dataLength = len(dataToSend)
        if (dataLength > SPI_PAYLOAD_MAX_LENGTH):
            print "Error: spi_transfer: dataToSend too long (max", SPI_PAYLOAD_MAX_LENGTH, "bytes)"
            return -1
        fillerBytes = [0x00] * (SPI_PAYLOAD_MAX_LENGTH - dataLength)
        dataToSend.extend(fillerBytes)
        checksum = self.compute_checksum(dataToSend)
        dataToSend.extend([checksum, 0x00])
        resp = self.spi.xfer2(dataToSend)
        return resp

    #Code from Triangula by Tom Oinn
    #http://pythonhosted.org/triangula/_modules/triangula/arduino.html#Arduino
    def compute_checksum(self, data):   #def compute_checksum(register, data):
        """
        Calculate a checksum for the specified data and register, simply by XORing each byte in turn with the current value
        of the checksum. The value is initialised to be the register, then each byte of the data array is used in turn. This
        is intended to inter-operate with the code on the Arduino, it's not a particularly generic checksum routine and
        won't work with arbitrary I2C devices.

        :param int register:
            The register to which we're sending the data. This is used because the first part of the data transaction
            is actually the register, we want to calculate the checksum including the register part.
        :param int[] data:
            The data array to use
        :return:
            A checksum, this should be appended onto the data sent to the Arduino
        """
        xor = 0     #xor = register
        for data_byte in data:
            xor ^= data_byte
        return xor

'''
#create SPI packet to be sent ...
dataToSend = [PS3_Stick_Register,motors[0],motors[1],p,t,hiButts,loButts,0x00,0x00]
#print dataToSend
checksum = helper.compute_checksum(dataToSend) #calculate checksum based on above packet
#this code actually sends the SPI packet to the Arduino processor. The Arduino will automatically
#respond with a packet of its own at the same time. The response packet is saved in the list "resp"
resp = spi.xfer2([PS3_Stick_Register,motors[0],motors[1],p,t,hiButts,loButts,0x00,0x00,checksum,0x00]) #send it
#calculate the expected checksum of the response data to make sure it is valid
response_checksum = helper.check_checksum(resp)
spi.close()
'''





#An example of a class
class Shape:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.description = "This shape has not been described yet"
        self.author = "Nobody has claimed to make this shape yet"

    def area(self):
        return self.x * self.y

    def perimeter(self):
        return 2 * self.x + 2 * self.y

    def describe(self, text):
        self.description = text

    def authorName(self, text):
        self.author = text

    def scaleSize(self, scale):
        self.x = self.x * scale
        self.y = self.y * scale
