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
    def __init__(self, motors, start_speed = 30):
        # these values might need to be adjusted
        self.proportional_term_in_PID = 1
        self.derivative_term_in_PID = 0
        self.left_photo_diode_found_line_value = 180
        self.right_photo_diode_found_line_value = 140
        self.target_value_left_photo_diode = 210
        self.target_value_right_photo_diode = 170
        self.correction_interval = 0.01
        self.distance_to_travel_before_stopping_for_stop_sign = 0.05
        self.distance_to_travel_before_stopping_for_traffic_light = 0.05
        self.distance_to_travel_before_changing_speed_limit = 0.05
        self.time_waiting_at_stop_sign = 2.0
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
        
        self.new_left_speed = start_speed
        self.new_right_speed = start_speed
        self.left_error = 0
        self.right_error = 0
        self.previous_left_error = 0
        self.previous_right_error = 0
        
        self.stopped = True #Need this to have an absolute stop, implement a if/else in PID loop
        self.traffic_stop = True
        self.is_speed_limit_on = False
        self.speed_limit = 100.0
        self.quit = False
    
        self.arduino.pinMode(self.pin_photo_diode_power,self.arduino.OUTPUT)
        self.arduino.pinMode(self.pin_left_photo_diode, self.arduino.INPUT)
        self.arduino.pinMode(self.pin_right_photo_diode, self.arduino.INPUT)
       
        self.arduino.digitalWrite(self.pin_photo_diode_power, 1)
        self.find_line(start_speed)
        
    def start_following_line(self):
        print "start_following_line"
        self.quit = True
        time.sleep(1)
        self.quit = False
        print "1"
        self.follow_line_thread = threading.Thread(target = self.follow_line_loop)
        print "2"
        self.follow_line_thread.setDaemon(True)
        self.follow_line_thread.start()

    def set_speed(self, target_speed):
        self.target_speed = int(target_speed)
        if (self.target_speed > 100):
            self.target_speed = 100
        if (self.target_speed < -100):
            self.target_speed = -100
        
        self.previous_left_error = self.arduino.analogRead(self.pin_left_photo_diode) - self.target_value_left_photo_diode
        self.previous_right_error = self.arduino.analogRead(self.pin_right_photo_diode) - self.target_value_right_photo_diode
 
    def follow_line_loop(self):
        print "following line"
        while not self.quit:
            print "run loop"
            if (self.stopped):
                self.motors.stop()
            else:
                self.left_error = self.arduino.analogRead(self.pin_left_photo_diode) - self.target_value_left_photo_diode
                self.right_error = self.arduino.analogRead(self.pin_right_photo_diode) - self.target_value_right_photo_diode
                
                self.new_left_speed = self.target_speed + self.left_error*self.proportional_term_in_PID + (self.left_error - self.previous_left_error)*self.derivative_term_in_PID/self.correction_interval
                self.new_right_speed = self.target_speed + self.right_error*self.proportional_term_in_PID + (self.right_error - self.previous_right_error)*self.derivative_term_in_PID/self.correction_interval
                
                print self.new_right_speed 
                if (self.is_speed_limit_on):
                    highest_speed = new_left_speed
                    if (new_right_speed > new_left_speed):
                        highest_speed = new_right_speed
                    if (highest_speed > self.speed_limit):
                        new_right_speed = new_right_speed / highest_speed * self.speed_limit
                        new_left_speed = new_left_speed / highest_speed * self.speed_limit
                    
                self.motors.set_left_speed(self.new_left_speed)
                self.motors.set_right_speed(self.new_right_speed)

                self.previous_left_error = self.left_error
                self.previous_right_error = self.right_error

            time.sleep(self.correction_interval)

    def stop(self):
        self.stopped = True
        self.arduino.digitalWrite(self.pin_photo_diode_power, 0)
        self.motors.turn_off()

    def find_line(self, speed):
        self.quit = False
        self.find_line_thread = threading.Thread(target = self.find_line_loop, args=(speed,))
        self.find_line_thread.setDaemon(True)
        self.find_line_thread.start()
     
    def find_line_loop(self,speed):
        line_found_left = False
        line_found_right = False
        while (self.stopped and not self.quit):
            time.sleep(0.01)
        self.motors.set_left_speed(speed)
        self.motors.set_right_speed(speed)
        while not line_found_left and not line_found_right and not self.quit:
            if (self.arduino.analogRead(self.pin_left_photo_diode) < self.left_photo_diode_found_line_value):
                line_found_left = True
                print "left diode triggered low"
            elif (self.arduino.analogRead(self.pin_right_photo_diode) < self.right_photo_diode_found_line_value):
                line_found_right = True
                print "right diode triggered low"
            while (self.stopped and not self.quit):
                time.sleep(0.01)
            time.sleep(self.correction_interval)
        print "Line found!"
        print self.quit
        while not self.quit:
            if (line_found_left and self.arduino.analogRead(self.pin_left_photo_diode) > self.left_photo_diode_found_line_value):
                self.motors.set_right_speed(0.0)
                self.motors.set_left_speed(0.0)
                self.new_right_speed = 0.0
                self.new_left_speed = 0.0
                print "ssss"
                time.sleep(5)
                self.start_following_line()
                print "break"
                break
            elif (line_found_right and self.arduino.analogRead(self.pin_right_photo_diode) > self.right_photo_diode_found_line_value):
                self.motors.set_right_speed(0.0)
                self.motors.set_left_speed(0.0)
                self.new_right_speed = 0.0
                self.new_left_speed = 0.0
                print "ssss"
                time.sleep(5)
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
        self.arduino.digitalWrite(self.pin_photo_diode_power, 0)
        self.quit = True
