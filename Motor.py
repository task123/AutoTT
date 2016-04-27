#!/usr/bin/python

import threading
from nanpy import ArduinoApi
from nanpy import SerialManager
import math
import time
import RPi.GPIO as GPIO

class TripMeter:
    def __init__(self):
        # these values might change
        self.right_pin = 2
        self.left_pin = 3
        # these values might change in a different application
        self.number_of_notches = 75.0
        self.wheel_diameter = 0.0694
        ##################################################
        # Values after this should not need to be changed.
        ##################################################
        
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
    def __init__(self, trip_meter):
        # these values might need to be adjusted
        self.max_speed  = 0.55
        min_voltage = 1.0
        self.correction_interval = 0.01
        self.proportional_term_in_PID = 50 #0.12
        self.derivative_term_in_PID = 0.01
        # these values might change
        self.pin_right_forward = 6
        self.pin_right_backward = 11
        self.pin_left_forward = 5
        self.pin_left_backward = 10
        self.pin_motor_battery = 7
        ##################################################
        # Values after this should not need to be changed.
        ##################################################
        
        self.trip_meter = trip_meter
        
        self.min_value = math.floor(min_voltage / 5.0 * 255)
        
        try:
            self.connection = SerialManager(device='/dev/ttyACM2')
            self.arduino = ArduinoApi(connection=self.connection)
        except:
            try:
                self.connection = SerialManager(device='/dev/ttyACM0')
                self.arduino = ArduinoApi(connection=self.connection)
            except:
                try:
                    self.connection = SerialManager(device='/dev/ttyACM1')
                    self.arduino = ArduinoApi(connection=self.connection)
                except:
                    try:
                        self.connection = SerialManager(device='/dev/ttyACM3')
                        self.arduino = ArduinoApi(connection=self.connection)
                    except:
                        print "Could not connect to the arduino using /dev/ttyACM0, /dev/ttyACM1, /dev/ttyACM2 or /dev/ttyACM3"
            
        self.arduino.pinMode(self.pin_right_forward, self.arduino.OUTPUT)
        self.arduino.pinMode(self.pin_right_backward, self.arduino.OUTPUT)
        self.arduino.pinMode(self.pin_left_forward, self.arduino.OUTPUT)
        self.arduino.pinMode(self.pin_left_backward, self.arduino.OUTPUT)
        self.arduino.pinMode(self.pin_motor_battery, self.arduino.OUTPUT)
        
        self.arduino.pinMode(13, self.arduino.OUTPUT)
        self.arduino.digitalWrite(13, 1)

        self.arduino.digitalWrite(self.pin_motor_battery, 0)
        
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
        self.stopped = True
    
        self.motor_control_thread = threading.Thread(target = self.motor_control_loop)
        self.motor_control_thread.setDaemon(True)
        self.motor_control_thread.start()

    def motor_control_loop(self):
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
                self.right_backward_value += self.proportional_term_in_PID * (-self.right_speed - self.true_right_speed) - self.derivative_term_in_PID * (self.right_backward_value - self.previous_right_backward_value) / self.correction_interval
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
                self.left_backward_value += self.proportional_term_in_PID * (-self.left_speed - self.true_left_speed) - self.derivative_term_in_PID * (self.left_backward_value - self.previous_left_backward_value) / self.correction_interval
                self.previous_left_backward_value = next_previous_left_backward_value
            else:
                self.left_forward_value = 0
                self.left_backward_value = 0
                self.previous_left_forward_value = 0
                self.previous_left_backward_value = 0
            
            if (not self.stopped):
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
        self.stopped = True
        self.right_speed = 0.0
        self.left_speed = 0.0
        self.right_forward_value = 0
        self.right_backward_value = 0
        self.left_forward_value = 0
        self.left_backward_value = 0
        self.arduino.analogWrite(self.pin_right_forward, 0)
        self.arduino.analogWrite(self.pin_right_backward, 0)
        self.arduino.analogWrite(self.pin_left_forward, 0)
        self.arduino.analogWrite(self.pin_left_backward, 0)

    def turn_off(self):
        self.arduino.digitalWrite(self.pin_motor_battery, 1)
        self.stop()

    # 'right_speed' is a number between -100 and 100, where 100 is full speed forward on the right wheel
    def set_right_speed(self, right_speed):
        self.right_speed = right_speed
        self.stopped = False
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
        self.stopped = False
        if (self.left_speed == 0):
            self.left_forward_value = 0
            self.left_backward_value = 0
        elif (self.left_speed > 0):
            self.left_forward_value = self.left_speed / 100.0 * (255 - self.min_value) + self.min_value
            self.left_backward_value = 0
        elif (self.left_speed < 0):
            self.left_forward_value = 0
            self.left_backward_value = -self.left_speed / 100.0 * (255 - self.min_value) + self.min_value



