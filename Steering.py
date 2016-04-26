#!/usr/bin/python

import math
import time
import os
from nanpy import ArduinoApi
import threading

"""React to gyroscopic and stop/continue data sendt from AutoTTCommunication and control a class 'motors', which steers the motors.
Remember to start the gyro with autoTTCommunication.start_gyro_with_update_intervall(gyro_update_intervall)

Sends messages set_right_speed('speed') and set_left_speed('speed') to 'motors'.
 - 'speed' is a number from -100 to 100, 100 being full speed forward, -100 being full speed in reverse.
"""
class SteeringWithIOSGyro:
    def __init__(self, motors, autoTTCommunication = None):
        # these values might need to be adjusted
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
        
        self.light = None
        self.is_button_indicator_on = False
        self.is_left_indicator_on = False
        self.is_right_indicator_on = False
        self.is_high_beam_on = False


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
        elif (self.is_button_indicators_on and type == "RightButtonTouchDown"):
            print "right"
            if (self.is_left_indicator_on):
                self.is_left_indicator_on = False
                if (self.is_high_beam_on):
                    self.lights.high_beam_off()
                else:
                    self.lights.high_beam_on()
                self.is_high_beam_on = not self.is_high_beam_on
            else:
                if (self.is_right_indicator_on):
                    self.lights.right_indicator_off()
                else:
                    self.lights.right_indicator_on()
                self.is_right_indicator_on = not self.is_right_indicator_on
        elif (self.is_button_indicators_on and type == "LeftButtonTouchDown"):
            print "left"
            if (self.is_right_indicator_on):
                self.is_right_indicator_on = False
                if (self.is_high_beam_on):
                    self.lights.high_beam_off()
                else:
                    self.lights.high_beam_on()
                self.is_high_beam_on = not self.is_high_beam_on
            else:
                if (self.is_left_indicator_on):
                    self.lights.left_indicator_off()
                else:
                    self.lights.left_indicator_on()
                self.is_left_indicator_on = not self.is_left_indicator_on
        elif (self.is_button_indicators_on and type == "RightButtonTouchUp"):
            if (self.is_right_indicator_on):
                self.is_right_indicator_on = False
                self.lights.right_indicator_off()
        elif (self.is_button_indicators_on and type == "LeftButtonTouchUp"):
            if (self.is_left_indicator_on):
                self.is_left_indicator_on = False
                self.lights.left_indicator_off()
            
    def button_indicators_on(self, lights):
        self.lights = lights
        self.is_button_indicators_on = True
        self.lights.on()
        
    def button_indicators_off(self):
        self.is_button_indicators_on = False
        if (self.lights != None):
            self.light.off()

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

"""
Follows a line on the ground and can make turns at junctions.

The car must start off the line, such that it will cross it when driving straight ahead.
"""
# It is adjusted to work for a line of black electrical tape on a grey speckled floor.
class FollowLine:
    def __init__(self, motors, start_speed = 30):
        # these values might need to be adjusted
        self.proportional_term_in_PID = 1
        self.derivative_term_in_PID = 0
        self.left_photo_diode_found_line_value = 130
        self.right_photo_diode_found_line_value = 250
        self.target_value_left_photo_diode = 150
        self.target_value_right_photo_diode = 270
        self.correction_interval = 0.01
        # these values might change
        self.pin_photo_diode_power = 12
        self.pin_left_photo_diode = 18
        self.pin_right_photo_diode = 19
        ##################################################
        # Values after this should not need to be changed.
        ##################################################
        
        self.motors = motors
        self.arduino = motors.arduino
        
        self.set_speed(start_speed)
        
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
        
        self.arduino.digitalWrite(12,1)
        self.find_line(start_speed)
        
    def start_following_line(self):
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
        self.previous_right_error = self.arduino.analogRead(self.pin_right_photo_diode) - self.target_value_right_photo_diode
 
    def follow_line_loop(self):
        print "following line"
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

    def find_line(self, speed):
        self.find_line_thread = threading.Thread(target = self.find_line_loop, args=(speed,))
        self.find_line_thread.setDaemon(True)
        self.find_line_thread.start()
     
    def find_line_loop(self,speed):
        print speed
        self.stopped = False
        self.motors.set_left_speed(speed)
        self.motors.set_right_speed(speed)
        print "speed set"
        line_found_left = False
        line_found_right = False
        while not line_found_left and not line_found_right:
            if (self.arduino.analogRead(self.pin_left_photo_diode) < self.left_photo_diode_found_line_value):
                line_found_left = True
            elif (self.arduino.analogRead(self.pin_right_photo_diode) < self.right_photo_diode_found_line_value):
                line_found_right = True
            time.sleep(self.correction_interval)
        print "Line found!"
        while True:
            if (line_found_left and self.arduino.analogRead(self.pin_left_photo_diode) > self.left_photo_diode_found_line_value):
                self.motors.set_left_speed(speed)
                self.motors.set_right_speed(0)
                self.start_following_line()
                print "break"
                break
            elif (line_found_right and self.arduino.analogRead(self.pin_right_photo_diode) > self.right_photo_diode_found_line_value):
                self.motors.set_right_speed(speed)
                self.motors.set_left_speed(0)
                self.start_following_line()
                print "break"
                break
            time.sleep(self.correction_interval)
        
            


