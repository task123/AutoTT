#!/usr/bin/python

import math
import time
import os
from nanpy import ArduinoApi

class Modes:
    list_of_modes = ["Tilt Steering", "Tilt, Lights", "Tilt with AOA", "Button Steering", "Button with AOA", "Follow line", "Stop sign", "Traffic light", "Self steering"] # AOA - Automated Object Avoidence
    
    list_of_info_modes = ["Tilt Steering", "Tilt, Lights", "Tilt with AOA", "Button Steering", "Button with AOA", "Follow line", "Stop sign", "Traffic light", "Self steering"]
    """
    ["Control the car by tilting your iOS device.", 
    "As 'Tilt Stering', but with lights on. The indicators are controlled by pushing the right/left side of the screen and the high beam by pushing both sides of the screen.", 
    "Control the car by tilting your iOS device while AOA (Automated Object Avoidence) stops you from crashing into objects.", 
    "Control the car by pushing the right and lift side of the screen.", 
    "Control the car by pushing the right and left side of the screen while AOA (Automated Object Avoidence) stops you from crashing into objects.", 
    "The car tries to follow a line on the ground and stops when objects blocks its way.", 
    "The car tries to follow a line on the ground and stops for stop signs and objects blocking its way.", 
    "The car tries to follow a line on the ground and stops for red traffic lights and objects blocking its way.", 
    "The car tries to follow a line on the ground and stops for stop signs, red traffic lights and objects blocking its way."]
    """
    
    def __init__(self, autoTTCommunication, steering, lights):
        self.autoTTCommunication = autoTTCommunication
        self.steering = steering
        self.lights = lights
    
    def receive_message(self, type, message):
        print "mode " + message
        if (type == "Modes"):
            self.autoTTCommunication.modes(self.list_of_modes)
        elif (type == "InfoModes"):
            self.autoTTCommunication.info_modes(self.list_of_info_modes)
        elif (type == "ChosenMode"):
            print "chosenMode"
            b = ( message == " 1" )
            print b
            print len(message)
            if (message == " 0"): # Tilt Steering
                steering = SteeringWithIOSGyro(self.motors, self.autoTTCommunication)
                autoTTCommunication.set_receivers(gyro_recv = steering, stop_cont_recv = steering, button_recv = None)
                steering.lights_off()
                autoTTCommunication.buttons_off()
            elif (message == "1"): # Tilt, Lights
                print "yess"
                steering = SteeringWithIOSGyro(self.motors, self.autoTTCommunication)
                autoTTCommunication.set_receivers(gyro_recv = steering, stop_cont_recv = steering, button_recv = steering)
                steering.lights_on(lights)
                autoTTCommunication.buttons_on()
            elif (message == "2"): # Tilt with AOA
                steering = SteeringWithIOSGyro(self.motors, self.autoTTCommunication)
                autoTTCommunication.set_receivers(gyro_recv = steering, stop_cont_recv = steering)
            elif (message == "3"): # Button Steering
                steering = SteeringWithIOSButtons(self.motors, self.autoTTCommunication)
                autoTTCommunication.set_receivers(gyro_recv = steering, stop_cont_recv = steering)
            elif (message == "4"): # Button with AOA
                steering = SteeringWithIOSButtons(self.motors, self.autoTTCommunication)
                autoTTCommunication.set_receivers(gyro_recv = steering, stop_cont_recv = steering)
            elif (message == "5"): # Follow line
                steering
            elif (message == "6"): # Stop sign
                steering
            elif (message == "7"): # Traffic light
                steering
            elif (message == "8"): # Self steering
                steering

    def send_modes_and_info_modes(self):
        print "sendt"
        time.sleep(0.01)
        self.autoTTCommunication.modes(self.list_of_modes)
        time.sleep(0.01) # wait to make sure AutoTT iOS app receive these as two seperate messages
        self.autoTTCommunication.info_modes(self.list_of_info_modes)
