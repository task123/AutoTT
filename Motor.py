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

        GPIO.setup(self.right_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.left_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        GPIO.add_event_detect(self.right_pin, GPIO.RISING, callback=self.right_count)
        GPIO.add_event_detect(self.left_pin, GPIO.RISING, callback=self.left_count)

    def right_count(channel):
        self.right_count += 1
        self.right_count_time3 = self.right_count_time2
        self.right_count_time2 = self.right_count_time1
        self.right_count_time1 = time.time()
        self.right_distance = math.pi * self.wheel_diameter * self.right_count / self.number_of_notches
        self.right_speed = math.pi * self.wheel_diameter / (2 * self.number_of_notches) / (self.right_count_time1 - self.right_count_time3)
        
    def left_count(channel):
        self.left_count += 1
        self.left_count_time3 = self.left_count_time2
        self.left_count_time2 = self.left_count_time1
        self.left_count_time1 = time.time()
        self.left_distance = math.pi * self.wheel_diameter * self.left_count / self.number_of_notches
        self.left_speed = math.pi * self.wheel_diameter / (2 * self.number_of_notches) / (self.left_count_time1 - self.left_count_time3)

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
    def __init__(trip_meter,  pin_right_forward = 5, pin_right_backward = 10, pin_left_forward = 6, pin_left_backward = 11, pin_motor_LED = 8, max_speed = 0.6, min_voltage = 1.0, correction_interval = 0.05, proportional_term_in_PID = 1.0, derivative_term_in_PID = 0.05):
        self.trip_meter = trip_meter
        self.connection = SerialManager(device='/dev/ttyACM0')
        self.arduino=ArduinoApi(connection=self.connection)
    
        self.pin_right_forward = pin_right_forward
        self.pin_right_backward = pin_right_backward
        self.pin_left_forward = pin_left_forward
        self.pin_left_backward = pin_left_backward
        self.pin_motor_LED = pin_motor_LED
        
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

        self.arduino.digitalWrite(pin_motor_LED, 0)
        
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
            true_right_speed = self.trip_meter.get_right_speed() * 100.0 / max_speed
            true_left_speed = self.trip_meter.get_left_speed() * 100.0 / max_speed
            
            if (right_speed > 0.0):
                self.right_backward_value = 0
                next_previous_right_forward_value = self.right_forward_value
                self.right_forward_value += self.proportional_term_in_PID * (right_speed - true_right_speed) - self.derivative_term_in_PID * (self.right_forward_value - self.previous_right_forward_value) / self.correction_interval
                self.previous_right_forward_value = next_previous_right_forward_value
            elif (right_speed < 0.0):
                self.right_forward_value = 0
                next_previous_right_backward_value = self.right_backward_value
                self.right_backward_value += self.proportional_term_in_PID * (right_speed - true_right_speed) - self.derivative_term_in_PID * (self.right_backward_value - self.previous_right_backward_value) / self.correction_interval
                self.previous_right_backward_value = next_previous_right_backward_value
            else:
                self.right_forward_value = 0
                self.right_backward_value = 0
                self.previous_right_forward_value = 0
                self.previous_right_backward_value = 0
            
            if (left_speed > 0.0):
                self.left_backward_value = 0
                next_previous_left_forward_value = self.left_forward_value
                self.left_forward_value += self.proportional_term_in_PID * (left_speed - true_left_speed) - self.derivative_term_in_PID * (self.left_forward_value - self.previous_left_forward_value) / self.correction_interval
                self.previous_left_forward_value = next_previous_left_forward_value
            elif (left_speed < 0.0):
                self.left_forward_value = 0
                next_previous_left_backward_value = self.left_backward_value
                self.left_backward_value += self.proportional_term_in_PID * (left_speed - true_left_speed) - self.derivative_term_in_PID * (self.left_backward_value - self.previous_left_backward_value) / self.correction_interval
                self.previous_left_backward_value = next_previous_left_backward_value
            else:
                self.left_forward_value = 0
                self.left_backward_value = 0
                self.previous_left_forward_value = 0
                self.previous_left_backward_value = 0
            
            if (not self.stop):
                self.arduino.analogWrite(pin_right_forward, self.right_forward_value)
                self.arduino.analogWrite(pin_right_backward, self.right_backward_value)
                self.arduino.analogWrite(pin_left_forward, self.left_forward_value)
                self.arduino.analogWrite(pin_left_backward, self.left_backward_value)


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
        self.arduino.digitalWrite(pin_motor_LED, 1)
        self.stop()
        time.sleep(30)

    # 'right_speed' is a number between -100 and 100, where 100 is full speed forward on the right wheel
    def set_right_speed(self, right_speed):
        self.right_speed = right_speed
        self.stop = False
        if (right_speed == 0):
            self.right_forward_value = 0
            self.right_backward_value = 0
        elif (right_speed > 0):
            self.right_forward_value = self.right_speed / 100.0 * (255 - self.min_value) + self.min_value
            self.right_backward_value = 0
        elif (right_speed < 0):
            self.right_forward_value = 0
            self.right_backward_value = -self.right_speed / 100.0 * (255 - self.min_value) + self.min_value
    
    # 'left_speed' is a number between -100 and 100, where 100 is full speed forward on the left wheel
    def set_left_speed(self, left_speed):
        self.left_speed = left_speed
        self.stop = False
        if (left_speed == 0):
            self.left_forward_value = 0
            self.left_backward_value = 0
        elif (left_speed > 0):
            self.left_forward_value = self.left_speed / 100.0 * (255 - self.min_value) + self.min_value
            self.left_backward_value = 0
        elif (left_speed < 0):
            self.left_forward_value = 0
            self.left_backward_value = -self.left_speed / 100.0 * (255 - self.min_value) + self.min_value



