#!/usr/bin/python

import threading
from nanpy import ArduinoApi
from nanpy import SerialManager
import math
import time
import RPi.GPIO as GPIO

class TripMeter:
    #change default notches
    #sensor max value ~4.3, min value ~2.0
    def __init__(self, number_of_notches = 75.0, wheel_diameter = 0.0694, right_pin = 2, left_pin = 3):
        self.number_of_notches = number_of_notches
        self.wheel_diameter = wheel_diameter
        self.right_pin = right_pin
        self.left_pin = left_pin
        
        self.right_count = 0
        self.left_count = 0
        self.right_count_time3 = 0.0
        self.right_count_time2 = 0.0
        self.right_count_time1 = 0.0
        self.left_count_time3 = 0.0
        self.left_count_time2 = 0.0
        self.left_count_time1 = 0.0
        
        self.right_distance = 0.0
        self.left_distance = 0.0
        self.right_speed = 0.0
        self.left_speed = 0.0

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.right_pin, GPIO.IN)
        GPIO.setup(self.left_pin, GPIO.IN)
        
        GPIO.add_event_detect(self.right_pin, GPIO.RISING, self.right_new_notch)
        GPIO.add_event_detect(self.left_pin, GPIO.RISING, self.left_new_notch)

    def right_new_notch(self, channel):
        self.right_count += 1
        self.right_count_time3 = self.right_count_time2
        self.right_count_time2 = self.right_count_time1
        self.right_count_time1 = time.time()
        self.right_distance = math.pi * self.wheel_diameter * self.right_count / self.number_of_notches
        self.right_speed = 2 * math.pi * self.wheel_diameter / self.number_of_notches / (self.right_count_time1 - self.right_count_time3)
        
    def left_new_notch(self, channel):
        self.left_count += 1
        self.left_count_time3 = self.left_count_time2
        self.left_count_time2 = self.left_count_time1
        self.left_count_time1 = time.time()
        self.left_distance = math.pi * self.wheel_diameter * self.left_count / self.number_of_notches
        self.left_speed = 2 * math.pi * self.wheel_diameter / self.number_of_notches / (self.left_count_time1 - self.left_count_time3)

    def get_right_distance(self):
        return self.right_distance

    def get_left_distance(self):
        return self.left_distance

    # the absolute value
    def get_right_speed(self):
        if (time.time() - self.right_count_time1 > self.right_count_time1 - self.right_count_time3):
            self.right_speed = 0.0
        return self.right_speed

    # the absolute value
    def get_left_speed(self):
        if (time.time() - self.left_count_time1 > self.left_count_time1 - self.left_count_time3):
            self.left_speed = 0.0
        return self.left_speed

    def reset(self):
        self.left_count = 0
        self.right_count = 0

class Motor:
    # correct max speed, min voltage
    def __init__(self, trip_meter,  pin_right_forward = 5, pin_right_backward = 10, pin_left_forward = 6, pin_left_backward = 11, 
            pin_motor_battery = 8, max_speed = 0.55, min_voltage = 1.0, correction_interval = 0.01, 
            proportional_term_in_PID = 0.12, derivative_term_in_PID = 0.001):
        self.trip_meter = trip_meter
        self.connection = SerialManager(device='/dev/ttyACM0')
        self.arduino=ArduinoApi(connection=self.connection)
    
        self.pin_right_forward = pin_right_forward
        self.pin_right_backward = pin_right_backward
        self.pin_left_forward = pin_left_forward
        self.pin_left_backward = pin_left_backward
        self.pin_motor_battery = pin_motor_battery
        
        self.max_speed  = max_speed
        self.min_value = math.floor(min_voltage / 5.0 * 255)
        self.correction_interval = correction_interval
        self.proportional_term_in_PID = proportional_term_in_PID
        self.derivative_term_in_PID = derivative_term_in_PID
                            
        self.arduino.pinMode(pin_right_forward, self.arduino.OUTPUT)
        self.arduino.pinMode(pin_right_backward, self.arduino.OUTPUT)
        self.arduino.pinMode(pin_left_forward, self.arduino.OUTPUT)
        self.arduino.pinMode(pin_left_backward, self.arduino.OUTPUT)
        self.arduino.pinMode(pin_motor_LED, self.arduino.OUTPUT)

        self.arduino.digitalWrite(pin_motor_battery, 1)
        
        self.power = 0.0
        self.turn = 0.0
        self.right_forward_value = 0
        self.right_backward_value = 0
        self.left_forward_value = 0
        self.left_backward_value = 0
        self.previous_right_forward_value = 0
        self.previous_right_backward_value = 0
        self.previous_left_forward_value = 0
        self.previous_left_backward_value = 0
        self.right_speed = 0.0
        self.left_speed = 0.0
        self.stop = True
    
        self.motor_control_thread = threading.Thread(target = self.motor_control)
        self.motor_control_thread.setDaemon(True)
        self.motor_control_thread.start()
        
    def motor_control(self):
        while True:
            self.true_right_speed = self.trip_meter.get_right_speed() * 100.0 / self.max_speed
            self.true_left_speed = self.trip_meter.get_left_speed() * 100.0 / self.max_speed
            
            if (self.right_speed > 0.0):
                self.right_backward_value = 0
                next_previous_right_forward_value = self.right_forward_value
                self.right_forward_value += self.proportional_term_in_PID * (self.right_speed - self.true_right_speed) - self.derivative_term_in_PID * (self.right_forward_value - self.previous_right_forward_value) / self.correction_interval
                self.previous_right_forward_value = next_previous_right_forward_value
            elif (self.right_speed < 0.0):
                self.right_forward_value = 0
                next_previous_right_backward_value = self.right_backward_value
                self.right_backward_value += self.proportional_term_in_PID * (self.right_speed - self.true_right_speed) - self.derivative_term_in_PID * (self.right_backward_value - self.previous_right_backward_value) / self.correction_interval
                self.previous_right_backward_value = next_previous_right_backward_value
            else:
                self.right_forward_value = 0
                self.right_backward_value = 0
                self.previous_right_forward_value = 0
                self.previous_right_backward_value = 0
            
            if (self.left_speed > 0.0):
                self.left_backward_value = 0
                next_previous_left_forward_value = self.left_forward_value
                self.left_forward_value += self.proportional_term_in_PID * (self.left_speed - self.true_left_speed) - self.derivative_term_in_PID * (self.left_forward_value - self.previous_left_forward_value) / self.correction_interval
                self.previous_left_forward_value = next_previous_left_forward_value
            elif (self.left_speed < 0.0):
                self.left_forward_value = 0
                next_previous_left_backward_value = self.left_backward_value
                self.left_backward_value += self.proportional_term_in_PID * (self.left_speed - self.true_left_speed) - self.derivative_term_in_PID * (self.left_backward_value - self.previous_left_backward_value) / self.correction_interval
                self.previous_left_backward_value = next_previous_left_backward_value
            else:
                self.left_forward_value = 0
                self.left_backward_value = 0
                self.previous_left_forward_value = 0
                self.previous_left_backward_value = 0
            
            if (not self.stop):
                print self.right_forward_value
                if (self.right_forward_value < 0):
                    self.right_forward_value = 0.0
                elif (self.right_forward_value > 255):
                    self.right_forward_value = 255
                if (self.right_backward_value < 0.0):
                    self.right_backward_value = 0.0
                elif (self.right_backward_value > 255):
                    self.right_backward_value = 255
                if (self.left_forward_value < 0.0):
                    self.left_forward_value = 0.0
                elif (self.left_forward_value > 255):
                    self.left_forward_value = 255
                if (self.left_backward_value < 0.0):
                    self.left_backward_value = 0.0 
                elif (self.left_backward_value > 255):
                    self.left_backward_value = 255
                self.arduino.analogWrite(self.pin_right_forward, self.right_forward_value)
                self.arduino.analogWrite(self.pin_right_backward, self.right_backward_value)
                self.arduino.analogWrite(self.pin_left_forward, self.left_forward_value)
                self.arduino.analogWrite(self.pin_left_backward, self.left_backward_value)
                
            time.sleep(self.correction_interval)


    def stop(self):
        self.stop = True
        self.right_speed = 0.0
        self.left_speed = 0.0
        self.right_forward_value = 0
        self.right_backward_value = 0
        self.left_forward_value = 0
        self.left_backward_value = 0
        self.arduino.analogWrite(pin_right_forward, 0)
        self.arduino.analogWrite(pin_right_backward, 0)
        self.arduino.analogWrite(pin_left_forward, 0)
        self.arduino.analogWrite(pin_left_backward, 0)

    def turn_off(self):
        self.arduino.digitalWrite(pin_motor_battery, 0)
        self.stop()
        time.sleep(30)

    # 'right_speed' is a number between -100 and 100, where 100 is full speed forward on the right wheel
    def set_right_speed(self, right_speed):
        self.right_speed = right_speed
        self.stop = False
        if (self.right_speed == 0):
            self.right_forward_value = 0
            self.right_backward_value = 0
        elif (self.right_speed > 0):
            self.right_forward_value = self.right_speed / 100.0 * (255 - self.min_value) + self.min_value
            self.right_backward_value = 0
        elif (self.right_speed < 0):
            self.right_forward_value = 0
            self.right_backward_value = -self.right_speed / 100.0 * (255 - self.min_value) + self.min_value
    
    # 'left_speed' is a number between -100 and 100, where 100 is full speed forward on the left wheel
    def set_left_speed(self, left_speed):
        self.left_speed = left_speed
        self.stop = False
        if (self.left_speed == 0):
            self.left_forward_value = 0
            self.left_backward_value = 0
        elif (self.left_speed > 0):
            self.left_forward_value = self.left_speed / 100.0 * (255 - self.min_value) + self.min_value
            self.left_backward_value = 0
        elif (self.left_speed < 0):
            self.left_forward_value = 0
            self.left_backward_value = -self.left_speed / 100.0 * (255 - self.min_value) + self.min_value



