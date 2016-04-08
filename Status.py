#!/usr/bin/python
"""
This module uses the code provided by PhJulien at https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=22180 extensively.
Thanks to PhJulien for making his code avalible.
"""
import os
from nanpy import ArduinoApi
from nanpy import SerialManager
import TCP
import Motor

class Status:
    # need the 'trip_meter' to get the arduino connection
    # change pin_motor_battery and pin_raspberry_pi
    def  __init__(self, autoTTCommunication, motors, pin_motor_battery = 1, pin_raspberry_pi_battery = 2):
        self.autoTTCommunication = autoTTCommunication
        self.arduino = motors.arduino
        self.pin_motor_battery = pin_motor_battery
        self.pin_raspberry_pi_battery = pin_raspberry_pi_battery
    
        self.arduino.pinMode(pin_motor_battery, self.arduino.INPUT)
        self.arduino.pinMode(pin_raspberry_pi_battery, self.arduino.INPUT)

    def recieve_message(self, type, message):
        if (type == "Status"):
            list_of_status.insert(0, "Motor battery voltage: %.3f V" % (self.getMotorBatteryVolt()))
            list_of_status.insert(1, "Raspberry Pis battery volgate: %.3f" % (self.getRaspberryPiBatteryVolt()))
            list_of_status.insert(2, "Temperature: %s C" % (self.getCPUTemperature()))
            list_of_status.insert(3, "CPU usage: %s %%" % (self.getCPUUse()))
            list_of_status.insert(4, "Memory used: %s kb" % (self.getRAMinfo()[1]))
            list_of_status.insert(5, "Free memory: %s kb" % (self.getRAMinfo()[2]))
            list_of_status.insert(6, "Disk space used: %s kb" % (getDiskSpace()[1]))
            list_of_status.insert(7, "Free disk space: %s kb" % (getDiskSpace()[2]))
            self.autoTTCommunication.status(list_of_status)
            
    def getMotorBatteryVolt(self):
        return self.arduino.analogRead(self.pin_motor_battery) / 1023.0 * 5.0
    
    def getRaspberryPiBatteryVolt(self):
        return self.arduino.analogRead(self.pin_raspberry_pi_battery) / 1023.0 * 5.0

    # Return CPU temperature as a character string
    def getCPUtemperature(self):
        res = os.popen('vcgencmd measure_temp').readline()
        return(res.replace("temp=","").replace("'C\n",""))

    # Return RAM information (unit=kb) in a list
    # Index 0: total RAM
    # Index 1: used RAM
    # Index 2: free RAM
    def getRAMinfo(self):
        p = os.popen('free')
        i = 0
        while 1:
            i = i + 1
            line = p.readline()
            if i==2:
                return(line.split()[1:4])

    # Return % of CPU used by user as a character string
    def getCPUuse(self):
        return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
               )))

    # Return information about disk space as a list (unit included)
    # Index 0: total disk space
    # Index 1: used disk space
    # Index 2: remaining disk space
    # Index 3: percentage of disk used
    def getDiskSpace(self):
        p = os.popen("df -h /")
        i = 0
        while 1:
            i = i +1
            line = p.readline()
            if i==2:
                return(line.split()[1:5])
