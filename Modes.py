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
    list_of_modes = ["Tilt Steering", "Tilt, Lights", "Tilt with AOA", "Button Steering", "Button with AOA", "Follow line", "Stop sign", "Traffic light", "Speed limit", "Tilt, Traffic rules, Light", "Self steering"] # AOA - Automated Object Avoidence
    
    list_of_info_modes = ["Control the car by tilting your iOS device.", 
    "As 'Tilt Stering', but with lights on. The indicators are controlled by pushing the right/left side of the screen and the high beam by pushing both sides of the screen.", 
    "Control the car by tilting your iOS device while AOA (Automated Object Avoidence) stops you from crashing into objects.", 
    "Control the car by pushing the right and lift side of the screen.", 
    "Control the car by pushing the right and left side of the screen while AOA (Automated Object Avoidence) stops you from crashing into objects.", 
    "The car tries to follow a line on the ground and stops when objects blocks its way.", 
    "The car tries to follow a line on the ground and stops for stop signs and objects blocking its way.", 
    "The car tries to follow a line on the ground and stops for red traffic lights and objects blocking its way.", 
    "As 'Tilt, Lights', but with speedlimits.",
    "As 'Tilt, Lights', but with speedlimits and the car stops for stop signs, red traffic lights and object blocking its way.",
    "The car tries to follow a line on the ground and stops for stop signs, red traffic lights and objects blocking its way."]
    
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
                self.steering = Steering.SteeringWithIOSGyro(self.motors)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras)
                self.lights.off()
                self.autoTTCommunication.buttons_off()
                self.cameras.stop_following_traffic_rules()
            elif (message == "1"): # Tilt, Lights
                self.steering = Steering.SteeringWithIOSGyro(self.motors)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras, button_recv = self.steering)
                self.steering.button_indicators_on(self.lights)
                self.autoTTCommunication.buttons_on()
                self.cameras.stop_following_traffic_rules()
            elif (message == "2"): # Tilt with AOA
                self.steering = Steering.SteeringWithIOSGyro(self.motors)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras)
                self.lights.off()
                self.autoTTCommunication.buttons_off()
                self.cameras.stop_following_traffic_rules()
            elif (message == "3"): # Button Steering
                self.steering = Steering.SteeringWithIOSButtons(self.motors)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras, button_recv = self.steering)
                self.lights.off()
                self.autoTTCommunication.buttons_on()
                self.cameras.stop_following_traffic_rules()
            elif (message == "4"): # Button with AOA
                self.steering = Steering.SteeringWithIOSButtons(self.motors)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras, button_recv = self.steering)
                self.lights.off()
                self.autoTTCommunication.buttons_on()
                self.cameras.stop_following_traffic_rules()
            elif (message == "5"): # Follow line
                self.steering = Steering.FollowLine(self.motors)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras)
                self.lights.off()
                self.autoTTCommunication.buttons_off()
                self.cameras.stop_following_traffic_rules()
            elif (message == "6"): # Stop sign
                self.steering = Steering.SteeringWithIOSGyro(self.motors)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras)
                self.lights.off()
                self.autoTTCommunication.buttons_off()
                self.cameras.stop_following_traffic_rules()
                self.cameras.start_looking_for_stop_signs()
            elif (message == "7"): # Traffic light
                self.steering = Steering.SteeringWithIOSGyro(self.motors)
                self.autoTTCommunication.set_receivers(gyro_recv = self.steering, mode_recv = self, status_recv = self.status, 
                    stop_cont_recv = self.steering, disconnect_recv = self.disconnect, shut_down_recv = self.disconnect, 
                    video_recv = self.cameras)
                self.lights.off()
                self.autoTTCommunication.buttons_off()
                self.cameras.stop_following_traffic_rules()
                self.cameras.start_looking_for_traffic_lights()
            elif (message == "8"): # Tilt, Traffic rules, Lights
                steering
            elif (message == "9"): # Self steering
                steering

    def send_modes(self):
        time.sleep(0.01)
        self.autoTTCommunication.modes(self.list_of_modes)
