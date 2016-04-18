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
import time

class Status:
    # need the 'trip_meter' to get the arduino connection
    # change pin_motor_battery and pin_raspberry_pi
    def  __init__(self, autoTTCommunication, motors, pin_motor_battery = 15, pin_raspberry_pi_battery = 14, arduino_max_voltage_analog_read = 5.01):
        self.autoTTCommunication = autoTTCommunication
        self.arduino = motors.arduino
        self.pin_motor_battery = pin_motor_battery
        self.pin_raspberry_pi_battery = pin_raspberry_pi_battery
        self.arduino_max_voltage_analog_read = arduino_max_voltage_analog_read
    
        self.arduino.pinMode(pin_motor_battery, self.arduino.INPUT)
        self.arduino.pinMode(pin_raspberry_pi_battery, self.arduino.INPUT)

    def receive_message(self, type, message):
        if (type == "Status"):
            list_of_status = []
            list_of_status.insert(0, "Motor battery voltage: %.2f V" % (self.getMotorBatteryVolt()))
            list_of_status.insert(1, "Raspberry Pis battery voltage: %.2f V" % (self.getRaspberryPiBatteryVolt()))
            list_of_status.insert(2, "Temperature: %s C" % (self.getCPUtemperature()))
            list_of_status.insert(3, "CPU usage: %s %%" % (self.getCPUuse()))
            list_of_status.insert(4, "Memory used: %d MB" % (self.getRAMinfo()[1]))
            list_of_status.insert(5, "Free memory: %d MB" % (self.getRAMinfo()[2]))
            list_of_status.insert(6, "Disk space used: %s GB" % (self.getDiskSpace()[1][:-1]))
            list_of_status.insert(7, "Free disk space: %s GB" % (self.getDiskSpace()[2][:-1]))
            self.autoTTCommunication.status(list_of_status)

    def getMotorBatteryVolt(self):
        return (99.2 + 99.7) / 99.7 * self.arduino.analogRead(self.pin_motor_battery) / 1023.0 * self.arduino_max_voltage_analog_read
    
    def getRaspberryPiBatteryVolt(self):
        return (223.1 + 99.7) / 223.1 * self.arduino.analogRead(self.pin_raspberry_pi_battery) / 1023.0 * self.arduino_max_voltage_analog_read

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
                ramInfo = line.split()[1:4]
                ramInfo[0] = int(ramInfo[0]) / 1000
                ramInfo[1] = int(ramInfo[1]) / 1000
                ramInfo[2] = int(ramInfo[2]) / 1000
                return ramInfo

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

class FanController:
    def __init__(self, motors, status, autoTTCommunication):
        self.start_temp = 70.0
        self.stop_temp = 65.0
        self.warning_message_temp = 80.0
        self.start_value = 100
        self.max_value = 400
        self.fan_pin = 3
        self.warning_message_motor_battery_volt = 6.0
        self.warning_message_motor_battery_volt_sendt = False
        self.warning_message_raspberry_pi_battery_volt = 4.9
        self.warning_message_motor_battery_volt_sendt = False

        
        self.arduino = motors.arduino
        self.status = status
        self.autoTTCommunication = autoTTCommunication
        
        self.warning_message_sendt = False
        
        arduino.pinMode(self.fan_pin, arduino.OUTPUT)
        
        self.fan_control_thread = threading.Thread(target = self.fan_controller_loop)
        self.fan_control_thread.setDaemon(True)
        self.fan_control_thread.start()
        
    def fan_controller_loop(self):
        self.arduino.analogWrite(self.fan_pin, 0)
        while True:
            # temp = float(self.status.getCPUtemperature())
            """
            if (temp > self.start_temp):
                fan_value = (temp - self.start_temp) / (85.0 - self.start_temp) * (self.max_value - self.start_value) + self.start_value
                if (temp > warning_message_temp and not self.warning_message_sendt):
                    self.autoTTCommunication.message("The CPU temperatur is over %f C." % (self.warning_message_temp))
                    self.warning_message_sendt = True
                self.arduino.analogWrite(self.fan_pin, fan_value)
            elif (temp < self.stop_temp):
                self.warning_message_sendt = False
                self.arduino.analogWrite(self.fan_pin, 0)
            motor_battery_volt = self.status.getMotorBatteryVolt()
            if (motor_battery_volt < self.warning_message_motor_battery_volt):
                self.autoTTCommunication.message("The voltage on the battery driving the motors is under %.2f V" % (motor_battery_volt))
            raspberry_pi_battery_volt = self.status.getRaspberryPiBatteryVolt()
            if (raspberry_pi_battery_volt < self.warning_message_raspberry_pi_volt):
                self.autoTTCommunication.message("The voltage on the battery driving the raspberry pi is under %.2f V" % (raspberry_pi_battery_volt))
            """
            time.sleep(3)
            
