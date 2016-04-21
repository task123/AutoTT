#!/usr/bin/python

import math
import time
import os
from nanpy import ArduinoApi

"""React to gyroscopic and stop/continue data sendt from AutoTTCommunication and control a class 'motors', which steers the motors.
Remember to start the gyro with autoTTCommunication.start_gyro_with_update_intervall(gyro_update_intervall)

Sends messages set_right_speed('speed') and set_left_speed('speed') to 'motors'.
 - 'speed' is a number from -100 to 100, 100 being full speed forward, -100 being full speed in reverse.
"""
class SteeringWithIOSGyro:
    def __init__(self, motors, autoTTCommunication = None):
        # this values might need to be adjusted
        self.min_roll = 3.5 * 3.14 / 180.0
        self.max_roll = 45.0 * 3.14 / 180.0
        self.max_pitch = 80.0 * 3.14 / 180.0
        gyro_update_intervall = 1.0/60.0
        ##################################################
        # Values after this should not need to be changed.
        ##################################################
        
        self.motors = motors
        
        self.stop = True
        if (autoTTCommunication != None):
            autoTTCommunication.start_gyro_with_update_intervall(gyro_update_intervall)

    def receive_message(self, type, message):
        if (type == "Gyro" and self.stop == False):
            [roll, pitch, yaw] = message.split(';', 2)
            roll = float(roll)
            pitch = float(pitch)
            yaw = float(yaw)

            direction_angle = math.atan2(pitch, roll)
            direction_angle *= 180.0 / math.pi
            
            speed = math.sqrt((roll / self.max_roll)**2 + (pitch / self.max_pitch)**2)
            if (speed > 1.0):
                speed = 1.0
            elif (speed < (self.min_roll / self.max_roll)):
                speed = 0.0
            
            right_speed = 0.0
            left_speed = 0.0
            if (direction_angle >= 0.0 and direction_angle <= 90.0):
                left_speed = 100.0 * speed
                right_speed = left_speed * (1 - direction_angle / 45.0)
            elif (direction_angle < 0.0 and direction_angle >= -90.0):
                right_speed = 100.0 * speed
                left_speed = right_speed * (1 + direction_angle / 45.0)
            elif (direction_angle > 90.0 and direction_angle <= 180.0):
                right_speed = -100.0 * speed
                left_speed = -right_speed * (1 - (direction_angle - 90.0) / 45.0)
            elif (direction_angle < -90.0 and direction_angle >= -180.0):
                left_speed = -100.0 * speed
                right_speed = -left_speed * (1 + (direction_angle - 90.0) / 45.0)

            self.motors.set_right_speed(right_speed)
            self.motors.set_left_speed(left_speed)
        elif (type == "Stop"):
            self.stop = True
            self.motors.stop()
        elif (type == "Continue"):
            self.stop = False

"""React to messages from AutoTTCommunication and control a class 'motors', which steers the motors.
    
Sends messages set_right_speed('speed') and set_left_speed('speed') to 'motors'.
- 'speed' is a number from 0 to 100, 100 being full speed forward and 0 being stop.
"""
class SteeringWithIOSButtons:
    max_speed = 100.0
    def __init__(self, motors, autoTTCommunication = None):
        # this values might need to be adjusted
        gyro_update_intervall = 1.0/60.0
        ##################################################
        # Values after this should not need to be changed.
        ##################################################
        
        self.motors = motors
        
        self.stop = True
        if (autoTTCommunication != None):
            autoTTCommunication.start_gyro_with_update_intervall(gyro_update_intervall)
            autoTTCommunication.button_on()
    
    def receive_message(self, type, message):
        if (type == "LeftButtonTouchDown" and self.stop == False):
            self.motors.left_speed(max_speed)
        elif (type == "RightButtonTouchDown" and self.stop == False):
            self.motors.right_speed(max_speed)
        elif (type == "LeftButtonTouchUp"):
            self.motors.right_speed(0.0)
        elif (type == "RightButtonTouchUp"):
            self.motors.left_speed(0.0)
        elif (type == "Stop"):
            self.stop = True
            self.motors.left_speed(0.0)
            self.motors.right_speed(0.0)
        elif (type == "Continue"):
            self.stop = False

class FollowLine:
    def __init__(self, motors, autoTTCommunication = None):
        # this values might need to be adjusted
        self.proportional_term_in_PID = 1
        self.derivative_term_in_PID = 1
        self.target_value_left_photo_diode = 300
        self.target_value_right_photo_diode = 500
        self.correction_interval = 0.01
        # this values might change
        self.pin_photo_diode_power = 7
        self.pin_left_photo_diode = 18
        self.pin_right_photo_diode = 19
        ##################################################
        # Values after this should not need to be changed.
        ##################################################

        self.motors = motors
        self.autoTTCommunication = autoTTCommunication
        self.arduino = motors.arduino

        self.target_speed = 0
        self.new_left_speed = 0
        self.new_right_speed = 0
        self.left_error = 0
        self.right_error = 0
        self.previous_left_error = 0
        self.previous_right_error = 0
        
        self.stopped = True #Need this to have an absolute stop, implement a if/else in PID loop
    
        self.arduino.pinMode(self.pin_photo_diode_power,self.arduino.OUTPUT)
        self.arduino.pinMode(self.pin_left_photo_diode, self.arduino.INPUT)
        self.arduino.pinMode(self.pin_right_photo_diode, self.arduino.INPUT)
    
        self.arduino.digitalWrite(self.pin_photo_diode_power, 0)
     
        self.follow_line_thread = threading.Thread(target = self.follow_line_loop)
        self.follow_line_thread.setDaemon(True)
        self.follow_line_thread.start()

    def set_speed(self, target_speed):
        self.target_speed = int(target_speed)
        if (self.target_speed > 100):
            self.target_speed = 100
        if (self.target_speed < -100):
            self.target_speed = -100
        
        self.stopped = False
        self.previous_left_error = self.arduino.analogRead(self.pin_left_photo_diode) - self.target_value_left_photo_diode
        self.previous_right_error = self.arduino.alalogRead(self.pin_right_photo_diode) - self.target_value_right_photo_diode
 
     def follow_line_loop(self):
        while True:
            if (self.stopped):
                self.motors.stop()
            else:
                self.left_error = self.arduino.analogRead(self.pin_left_photo_diode) - self.target_value_left_photo_diode
                self.right_error = self.arduino.analogRead(self.pin_right_photo_diode) - self.target_value_right_photo_diode
                
                self.new_left_speed = self.target_speed + self.left_error*self.proportional_term_in_PID + (self.left_error - self.previous_left_error)*self.derivative_term_in_PID/self.correction_interval
                self.new_right_speed = self.target_speed + self.right_error*self.proportional_term_in_PID + (self.right_error - self.previous_right_error)*self.derivative_term_in_PID/self.correction_interval

                self.motors.set_left_speed(self.new_left_speed)
                self.motors.set_right_speed(self.new_right_speed)

                self.previous_left_error = self.left_error
                self.previous_right_error = self.right_error

            time.sleep(self.correction_interval)

    def stop(self):
        self.stopped = True

    def find_line(self):
        # add function
        a = 2


class Modes:
    list_of_modes = ["Tilt Steering", "Tilt with AOA", "Button Steering", "Button with AOA", "Follow line", "Stop sign", "Traffic light", "Self steering"] # AOA - Automated Object Avoidence
    
    list_of_info_modes = ["Control the car by tilting your iOS device.", "Control the car by tilting your iOS device while AOA (Automated Object Avoidence) stops you from crashing into objects.", "Control the car by pushing the right and lift side of the screen.", "Control the car by pushing the right and left side of the screen while AOA (Automated Object Avoidence) stops you from crashing into objects.", "The car tries to follow a line on the ground and stops when objects blocks its way.", "The car tries to follow a line on the ground and stops for stop signs and objects blocking its way.", "The car tries to follow a line on the ground and stops for red traffic lights and objects blocking its way.", "The car tries to follow a line on the ground and stops for stop signs, red traffic lights and objects blocking its way."]
    
    def __init__(self, autoTTCommunication, steering):
        self.autoTTCommunication = autoTTCommunication
        self.steering = steering
    
    def receive_message(self, type, message):
        if (type == "Modes"):
            self.autoTTCommunication.modes(self.list_of_modes)
        elif (type == "InfoModes"):
            self.autoTTCommunication.info_modes(self.list_of_info_modes)
        elif (type == "ChosenMode"):
            if (message == "0"): # Tilt Steering
                steering = SteeringWithIOSGyro(self.motors, self.autoTTCommunication)
                autoTTCommunication.set_receivers(gyro_recv = steering, stop_cont_recv = steering)
            elif (message == "1"): # Tilt with AOA
                steering = SteeringWithIOSGyro(self.motors, self.autoTTCommunication)
                autoTTCommunication.set_receivers(gyro_recv = steering, stop_cont_recv = steering)
            elif (message == "2"): # Button Steering
                steering = SteeringWithIOSButtons(self.motors, self.autoTTCommunication)
                autoTTCommunication.set_receivers(gyro_recv = steering, stop_cont_recv = steering)
            elif (message == "3"): # Button with AOA
                steering = SteeringWithIOSButtons(self.motors, self.autoTTCommunication)
                autoTTCommunication.set_receivers(gyro_recv = steering, stop_cont_recv = steering)
            elif (message == "4"): # Follow line
                steering
            elif (message == "5"): # Stop sign
                steering
            elif (message == "6"): # Traffic light
                steering
            elif (message == "7"): # Self steering
                steering

    def send_modes_and_info_modes(self):
        time.sleep(0.01)
        self.autoTTCommunication.modes(self.list_of_modes)
        time.sleep(0.01) # wait to make sure AutoTT iOS app receive these as two seperate messages
        self.autoTTCommunication.info_modes(self.list_of_info_modes)
