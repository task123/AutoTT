#!/usr/bin/python

import math
import time
import os
from nanpy import ArduinoApi
import Steering
import TCP
import Lights
import Motor

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
    
    def __init__(self, autoTTCommunication, motors,  lights, steering, cameras, status, disconnect):
        self.autoTTCommunication = autoTTCommunication
        self.motors = motors
        self.lights = lights
        self.steering = steering
        self.cameras = cameras
        self.status = status
        self.disconnect = disconnect
        
    
    def receive_message(self, type, message):
        print "mode " + message
        if (type == "Modes"):
            self.autoTTCommunication.modes(self.list_of_modes)
        elif (type == "InfoModes"):
            self.autoTTCommunication.info_modes(self.list_of_info_modes, int(message))
        elif (type == "ChosenMode"):
            if (message == " 0"): # Tilt Steering
                self.steering = Steering.SteeringWithIOSGyro(self.motors, self.autoTTCommunication)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras)
                steering.button_indicators_off()
                autoTTCommunication.buttons_off()
            elif (message == "1"): # Tilt, Lights
                print "yess"
                self.steering = Steering.SteeringWithIOSGyro(self.motors, self.autoTTCommunication)
                print "1"
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras, button_recv = self.steering)
                print "2"
                self.steering.button_indicators_on(self.lights)
                print "3"
                self.autoTTCommunication.buttons_on()
                print "4"
            elif (message == "2"): # Tilt with AOA
                self.steering = Steering.SteeringWithIOSGyro(self.motors, self.autoTTCommunication)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras)
            elif (message == "3"): # Button Steering
                self.steering = Steering.SteeringWithIOSButtons(self.motors, self.autoTTCommunication)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras, button_recv = self.steering)
            elif (message == "4"): # Button with AOA
                self.steering = Steering.SteeringWithIOSButtons(self.motors, self.autoTTCommunication)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras, button_recv = self.steering)
            elif (message == "5"): # Follow line
                steering
            elif (message == "6"): # Stop sign
                steering
            elif (message == "7"): # Traffic light
                steering
            elif (message == "8"): # Self steering
                steering

    def send_modes(self):
        time.sleep(0.01)
        self.autoTTCommunication.modes(self.list_of_modes)
