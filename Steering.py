#!/usr/bin/python

import math
import time
import os
from nanpy import ArduinoApi
import threading
import numpy as np

"""React to gyroscopic and stop/continue data sendt from AutoTTCommunication and control a class 'motors', which steers the motors.
Remember to start the gyro with autoTTCommunication.start_gyro_with_update_intervall(gyro_update_intervall)

Sends messages set_right_speed('speed') and set_left_speed('speed') to 'motors'.
 - 'speed' is a number from -100 to 100, 100 being full speed forward, -100 being full speed in reverse.
"""
class SteeringWithIOSGyro:
    def __init__(self, motors):
        # these values might need to be adjusted
        self.min_roll = 3.5 * 3.14 / 180.0
        self.max_roll = 45.0 * 3.14 / 180.0
        self.max_pitch = 80.0 * 3.14 / 180.0
        self.distance_to_travel_before_stopping_for_stop_sign = 0.05
        self.distance_to_travel_before_stopping_for_traffic_light = 0.05
        self.distance_to_travel_before_changing_speed_limit = 0.05
        self.time_waiting_at_stop_sign = 3.0
        ##################################################
        # Values after this should not need to be changed.
        ##################################################
        
        self.motors = motors
        self.trip_meter = motors.trip_meter
        
        self.stop = True
        self.traffic_stop = True
        self.speed_limit = 100.0
        self.is_speed_limit_on = False
        
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
            if (self.is_speed_limit_on):
                highest_speed = left_speed
                if (right_speed > left_speed):
                    highest_speed = right_speed
                if (highest_speed > self.speed_limit):
                    right_speed = right_speed / highest_speed * self.speed_limit
                    left_speed = left_speed / highest_speed * self.speed_limit
            self.motors.set_right_speed(right_speed)
            self.motors.set_left_speed(left_speed)
        elif (type == "Stop"):
            self.traffic_stop = False
            self.stop = True
            self.motors.stop()
        elif (type == "Continue"):
            self.traffic_stop = True
            self.stop = False
        elif (self.is_button_indicators_on and type == "RightButtonTouchDown"):
            if (self.is_left_indicator_on):
                self.is_left_indicator_on = False
                if (self.is_high_beam_on):
                    self.lights.high_beam_off()
                else:
                    self.lights.high_beam_on()
                self.is_high_beam_on = not self.is_high_beam_on
                self.lights.left_indicator_off()
            else:
                if (self.is_right_indicator_on):
                    self.lights.right_indicator_off()
                else:
                    self.lights.right_indicator_on()
                self.is_right_indicator_on = not self.is_right_indicator_on
        elif (self.is_button_indicators_on and type == "LeftButtonTouchDown"):
            if (self.is_right_indicator_on):
                self.is_right_indicator_on = False
                if (self.is_high_beam_on):
                    self.lights.high_beam_off()
                else:
                    self.lights.high_beam_on()
                self.is_high_beam_on = not self.is_high_beam_on
                self.lights.right_indicator_off()
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
            
    def stop_sign(self):
       print "inside stop"
       self.traffic_stop = True
       self.trip_meter.reset()
       while (self.trip_meter.get_right_distance() < self.distance_to_travel_before_stopping_for_stop_sign and self.trip_meter.get_left_distance() < self.distance_to_travel_before_stopping_for_stop_sign):
           time.sleep(0.01)
       if (not self.stop):
           self.stop = True
           time.sleep(self.time_waiting_at_stop_sign)
           if (self.traffic_stop):
               self.stop = False
              
    def traffic_light(light_color):
       if (light_color == "red"):
           self.traffic_stop = True
           self.trip_meter.reset()
           while (self.trip_meter.get_right_distance() < self.distance_to_travel_before_stopping_for_traffic_light and self.trip_meter.get_left_distance() < self.distance_to_travel_before_stopping_for_traffic_light):
               time.sleep(0.01)
           self.stop = True
       elif (light_color == "green"):
           if (self.traffic_stop):
               self.stop = False
               
    def speed_limit(speed_limit):
        self.trip_meter.reset()
        while (self.trip_meter.get_right_distance() < self.distance_to_travel_before_changing_speed_limit and self.trip_meter.get_left_distance() < self.distance_to_travel_before_changing_speed_limit):
            time.sleep(0.01)
        self.speed_limit = speed_limit

    def start_following_speed_limit(self):
        self.is_speed_limit_on = True
        
    def stop_following_speed_limit(self):
        self.is_speed_limit_on = False
        
"""React to messages from AutoTTCommunication and control a class 'motors', which steers the motors.
    
Sends messages set_right_speed('speed') and set_left_speed('speed') to 'motors'.
- 'speed' is a number from 0 to 100, 100 being full speed forward and 0 being stop.
"""
class SteeringWithIOSButtons:
    max_speed = 100.0
    def __init__(self, motors):
        self.motors = motors
        
        self.stop = True
    
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
    def __init__(self, motors, speed = 17, lights = None):
        # these values might need to be adjusted
        self.proportional_term_in_PID = 0.004
        self.derivative_term_in_PID = 0.00
        self.part_off_new_error_used_in_smoothing = 0.5 #0.18
        self.left_photo_diode_found_black_line_value = 100
        self.right_photo_diode_found_black_line_value = 100
        self.left_photo_diode_found_white_line_value = 420
        self.right_photo_diode_found_white_line_value = 430
        self.junction_found_value = 420
        self.correction_interval = 0.01
        self.distance_to_travel_before_stopping_for_stop_sign = 0.05
        self.distance_to_travel_before_stopping_for_traffic_light = 0.05
        self.distance_to_travel_before_changing_speed_limit = 0.05
        self.turn_after_distance = 0.07
        self.time_waiting_at_stop_sign = 2.0
        # these values might change
        self.pin_photo_diode_power = 12
        self.pin_left_photo_diode = 18
        self.pin_right_photo_diode = 19
        ##################################################
        # Values after this should not need to be changed.
        ##################################################
        
        self.motors = motors
        self.speed = speed
        self.lights = lights
        
        self.arduino = self.motors.arduino
        self.trip_meter = self.motor.trip_meter
        
        self.left_speed = self.speed
        self.right_speed = self.speed
        self.error = 0
        self.previous_error = 0

        self.stopped = True #Need this to have an absolute stop, implement a if/else in PID loop
        self.traffic_stop = True
        self.is_speed_limit_on = False
        self.speed_limit = 100.0
        self.quit = False
        self.junction_left_check = [0, 0, 0, 0, 0]
        self.junction_right_check = [0, 0, 0, 0, 0]
        self.is_turning_left = False
        self.is_turning_right = False
        self.have_detected_junction = False
    
        self.arduino.pinMode(self.pin_photo_diode_power,self.arduino.OUTPUT)
        self.arduino.pinMode(self.pin_left_photo_diode, self.arduino.INPUT)
        self.arduino.pinMode(self.pin_right_photo_diode, self.arduino.INPUT)
       
        self.arduino.digitalWrite(self.pin_photo_diode_power, 1)
        self.find_line(self.speed)
        
                        if (self.is_at_junction() and (self.is_turning_left or self.is_turning_right)):
                    self.trip_meter.reset()
                    self.have_detected_junction = True
                    
                if self.is_turning_left and self.have_detected_junction and self.trip_meter.get_right_distance() > self.turn_after_distance):
                    self.turn_left()
                if self.is_turning_right and self.have_detected_junction and self.trip_meter.get_right_distance() > self.turn_after_distance):
                    self.turn_right()
                    

    def set_speed(speed):
       self.speed = speed
        
    def start_following_line(self):
        self.quit = True
        time.sleep(0.1)
        self.quit = False
        self.follow_line_thread = threading.Thread(target = self.follow_line_loop)
        self.follow_line_thread.setDaemon(True)
        self.follow_line_thread.start()
 
    def follow_line_loop(self):
        print "following line"
        while not self.quit:
            if (self.stopped):
                self.motors.stop()
            else:
                self.new_error = self.arduino.analogRead(self.pin_right_photo_diode) - self.arduino.analogRead(self.pin_left_photo_diode)
                
                self.error = self.part_off_new_error_used_in_smoothing * self.new_error + (1.0 - self.part_off_new_error_used_in_smoothing) * self.error
                
                self.left_speed = self.speed * (1.0 - self.error*self.proportional_term_in_PID + (self.error - self.previous_error)*self.derivative_term_in_PID/self.correction_interval)
                self.right_speed = self.speed * (1.0 + self.error*self.proportional_term_in_PID - (self.error - self.previous_error)*self.derivative_term_in_PID/self.correction_interval)
                
                if (self.left_speed > 100 or self.right_speed > 100):
                    if (self.left_speed > self.right_speed):
                        self.right_speed -= self.left_speed - 100
                        self.left_speed = 100
                    else:
                        self.left_speed -= self.right_speed - 100
                        self.right_speed = 100

                self.motors.set_left_speed(self.left_speed)
                self.motors.set_right_speed(self.right_speed)
                
                self.previous_error = self.error
                print self.error
                
                if (self.is_at_junction() and (self.is_turning_left or self.is_turning_right) and not self.have_detected_junction):
                    self.trip_meter.reset()
                    self.have_detected_junction = True
                    
                if self.is_turning_left and self.have_detected_junction and self.trip_meter.get_left_distance() > self.turn_after_distance):
                    self.have_detected_junction = False
                    self.is_turning_left = False
                    self.turn_left()
                if self.is_turning_right and self.have_detected_junction and self.trip_meter.get_right_distance() > self.turn_after_distance):
                    self.have_detected_junction = False
                    self.is_turning_right = False
                    self.turn_right()
                    
            time.sleep(self.correction_interval)
            
    def is_at_juncition(self):
        self.junction_left_check[4] = self.junction_left_check[3]
        self.junction_left_check[3] = self.junction_left_check[2]
        self.junction_left_check[2] = self.junction_left_check[1]
        self.junction_left_check[1] = self.junction_left_check[0]
        self.junction_left_check[0] = self.arduino.analogRead(self.pin_left_photo_diode)
        self.junction_right_check[4] = self.junction_right_check[3]
        self.junction_right_check[3] = self.junction_right_check[2]
        self.junction_right_check[2] = self.junction_right_check[1]
        self.junction_right_check[1] = self.junction_right_check[0]
        self.junction_right_check[0] = self.arduino.analogRead(self.pin_right_photo_diode)
        if (np.median(self.junction_left_check) > self.junction_found_value and np.median(self.junction_right_check) > self.junction_found_value):
            return True
        else:
            return False
            
    def turn_left():
        self.motors.set_right_speed(0)
        self.motors.set_left_speed(self.speed)
        self.trip_meter.reset()
        while (self.trip_meter.get_left_distance() < self.distance_turned_before_looking_for_line):
            time.sleep(0.05)
        

    def stop(self):
        self.stopped = True
        self.arduino.digitalWrite(self.pin_photo_diode_power, 0)
        self.motors.turn_off()

    def find_line(self, speed, turning = False):
        self.quit = False
        self.find_line_thread = threading.Thread(target = self.find_line_loop, args=(speed, turning,))
        self.find_line_thread.setDaemon(True)
        self.find_line_thread.start()
     
    def find_line_loop(self,speed, turning):
        white_line_found_left = False
        white_line_found_right = False
        line_found_left = False
        line_found_right = False
        while (self.stopped and not self.quit):
            time.sleep(0.01)
        if (not turning):
            self.motors.set_left_speed(speed)
            self.motors.set_right_speed(speed)
        left_value_list = []
        left_value_list.append((self.left_photo_diode_found_white_line_value - self.left_photo_diode_found_black_line_value) / 2.0 + self.left_photo_diode_found_black_line_value)
        left_value_list.append(left_value_list[0])
        left_value_list.append(left_value_list[0])
        left_value_list.append(left_value_list[0])
        left_value_list.append(left_value_list[0])
        right_value_list = []
        right_value_list.append((self.right_photo_diode_found_white_line_value - self.right_photo_diode_found_black_line_value) / 2.0 + self.right_photo_diode_found_black_line_value)
        right_value_list.append(right_value_list[0])
        right_value_list.append(right_value_list[0])
        right_value_list.append(right_value_list[0])
        right_value_list.append(right_value_list[0])
        while not line_found_left and not line_found_right and not self.quit:
            left_value_list[4] = left_value_list[3]
            left_value_list[3] = left_value_list[2]
            left_value_list[2] = left_value_list[1]
            left_value_list[1] = left_value_list[0]
            left_value_list[0] = self.arduino.analogRead(self.pin_left_photo_diode)
            left_value = np.median(left_value_list)
            right_value_list[4] = right_value_list[3]
            right_value_list[3] = right_value_list[2]
            right_value_list[2] = right_value_list[1]
            right_value_list[1] = right_value_list[0]
            right_value_list[0] = self.arduino.analogRead(self.pin_right_photo_diode)
            right_value = np.median(right_value_list)
            print str(right_value_list[0]) + "   " + str(left_value_list[0])
            if (left_value > self.left_photo_diode_found_white_line_value):
                white_line_found_left = True
                print "white line left found"
            if (right_value > self.right_photo_diode_found_white_line_value):
                white_line_found_right = True
                print "white line right found"
            if (left_value < self.left_photo_diode_found_black_line_value and white_line_found_left):
                line_found_left = True
                print "left diode triggered low"
            elif (right_value < self.right_photo_diode_found_black_line_value and white_line_found_right):
                line_found_right = True
                print "right diode triggered low"
            while (self.stopped and not self.quit):
                time.sleep(0.01)
            time.sleep(self.correction_interval)
        print "Line found!"
        while not self.quit:
            if (line_found_left and self.arduino.analogRead(self.pin_left_photo_diode) > self.left_photo_diode_found_black_line_value):
                self.motors.set_right_speed(0.0)
                self.motors.set_left_speed(0.0)
                if (not turning):
                    self.start_following_line()
                print "break"
                break
            elif (line_found_right and self.arduino.analogRead(self.pin_right_photo_diode) > self.right_photo_diode_found_black_line_value):
                self.motors.set_right_speed(0.0)
                self.motors.set_left_speed(0.0)
                if (not turning):
                    self.start_following_line()
                print "break"
                break
            time.sleep(self.correction_interval)
        
    def receive_message(self, type, message):
        print type
        if (type == "Stop"):
            self.stopped = True
            self.traffic_stop = False
            self.motors.set_left_speed(0.0)
            self.motors.set_right_speed(0.0)
        elif (type == "Continue"):
            self.stopped = False
            self.traffic_stop = True
            self.motors.set_right_speed(self.new_right_speed)
            self.motors.set_left_speed(self.new_left_speed)
        elif (type = "SpeechRecognition"):
            if (message == "DRIVE"):
                self.stopped = False
                self.traffic_stop = True
                if (self.is_turning_left):
                    self.motors.set_right_speed(0.0)
                    self.motors.set_left_speed(self.speed)
                elif (self.is_turning_right):
                    self.motors.set_right_speed(self.speed)
                    self.motors.set_left_speed(0.0)
                else:
                    self.motors.set_right_speed(self.speed)
                    self.motors.set_left_speed(self.speed)
            elif (message == "STOP"):
                self.stopped = True
                self.traffic_stop = False
                self.motors.set_left_speed(0.0)
                self.motors.set_right_speed(0.0)
            elif (message == "RIGHT"):
                self.is_turning_right = True
                self.is_turning_left = False
            elif (message == "LEFT"):
                self.is_turning_left = True
                self.is_turning_right = False
            elif (message == "HIGH"):
                if (self.lights != None):
                    if (self.lights.is_high_beam_on):
                        self.lights.high_beam_off()
                    else:
                        self.lights.high_beam_on()
            
    def stop_sign(self):
       self.traffic_stop = True
       self.trip_meter.reset()
       while (self.trip_meter.get_right_distance() < self.distance_to_travel_before_stopping_for_stop_sign and self.trip_meter.get_left_distance() < self.distance_to_travel_before_stopping_for_stop_sign):
           time.sleep(0.01)
       if (not self.stopped):
           self.stopped = True
           time.sleep(self.time_waiting_at_stop_sign)
           if (self.traffic_stop):
               self.stopped = False
              
    def traffic_light(light_color):
       if (light_color == "red"):
           self.traffic_stop = True
           self.trip_meter.reset()
           while (self.trip_meter.get_right_distance() < self.distance_to_travel_before_stopping_for_traffic_light and self.trip_meter.get_left_distance() < self.distance_to_travel_before_stopping_for_traffic_light):
               time.sleep(0.01)
           self.stopped = True
       elif (light_color == "green"):
           if (self.traffic_stop):
               self.stopped = False
               
    def speed_limit(speed_limit):
        self.trip_meter.reset()
        while (self.trip_meter.get_right_distance() < self.distance_to_travel_before_changing_speed_limit and self.trip_meter.get_left_distance() < self.distance_to_travel_before_changing_speed_limit):
            time.sleep(0.01)
        self.speed_limit = speed_limit
        
    def start_following_speed_limit(self):
        self.is_speed_limit_on = True
        
    def stop_following_speed_limit(self):
        self.is_speed_limit_on = False

    def stop_following_line(self):
        print "stop_following_line"
        self.quit = True
        self.stopped
        time.sleep(0.5)
        self.arduino.digitalWrite(self.pin_photo_diode_power, 0)
        self.motors.set_left_speed(0.0)
        self.motors.set_right_speed(0.0)
        print "end stop_following_line"
