#!/usr/bin/python

import threading
from nanpy import ArduinoApi
from nanpy import SerialManager
import math
import time

class TripMeter:
    #change default notches
    #sensor max value ~4.3, min value ~2.0
    def __init__(self, pin_right_trip_sensor = 15, pin_left_trip_sensor = 14, lower_limit_sensor = 2.85, higher_limit_sensor = 3.35, number_of_notches = 100.0, wheel_diameter = 0.0694, measurement_interval = 0.001):
        self.pin_left_trip_sensor = pin_left_trip_sensor
        self.pin_right_trip_sensor = pin_right_trip_sensor
        self.lower_limit_sensor = lower_limit_sensor
        self.higher_limit_sensor = higher_limit_sensor
        self.number_of_notches = number_of_notches
        self.wheel_diameter = wheel_diameter
        self.measurement_interval = measurement_interval
        
        self.connection = SerialManager(device='/dev/ttyACM0')
        self.arduino=ArduinoApi(connection=self.connection)
        self.arduino.pinMode(pin_right_trip_sensor, self.arduino.INPUT)
        self.arduino.pinMode(pin_left_trip_sensor, self.arduino.INPUT)
        
        self.right_previously_high = False
        self.left_previously_high = False
        self.right_count = 0
        self.left_count = 0
        self.right_count_time1 = time.time()
        self.right_count_time2 = time.time()
        self.right_count_time3 = time.time()
        self.left_count_time1 = time.time()
        self.left_count_time2 = time.time()
        self.left_count_time3 = time.time()
        self.right_speed = 0.0
        self.left_speed = 0.0
        self.right_distance = 0.0
        self.left_distance = 0.0
        
        self.trip_meter_thread = threading.Thread(target = self.trip_meter)
        self.trip_meter_thread.setDaemon(True)
        self.trip_meter_thread.start()

    
    # no reason to call this explicitly as __init__ calls it in its own thread
    def trip_meter(self):
        self.i = 0
        while True:
            right_read = self.arduino.analogRead(self.pin_right_trip_sensor) / 1023.0 * 5.0
            if (right_read > self.higher_limit_sensor and not self.right_previously_high):
                self.right_count = self.right_count + 1
                self.right_count_time3 = self.right_count_time2
                self.right_count_time2 = self.right_count_time1
                self.right_count_time1 = time.time()
                self.right_previously_high = True
            elif (right_read < self.lower_limit_sensor and self.right_previously_high):
                self.right_count = self.right_count + 1
                self.right_count_time3 = self.right_count_time2
                self.right_count_time2 = self.right_count_time1
                self.right_count_time1 = time.time()
                self.right_previously_high = False
            
            left_read = self.arduino.analogRead(self.pin_left_trip_sensor) / 1023.0 * 5.0
            if (left_read > self.higher_limit_sensor and not self.left_previously_high):
                self.left_count = self.left_count + 1
                self.left_count_time3 = self.left_count_time2
                self.left_count_time2 = self.left_count_time1
                self.left_count_time1 = time.time()
                self.left_previously_high = True
            elif (left_read < self.lower_limit_sensor and self.left_previously_high):
                self.left_count = self.left_count + 1
                self.left_count_time3 = self.left_count_time2
                self.left_count_time2 = self.left_count_time1
                self.left_count_time1 = time.time()
                self.left_previously_high = False
            
            self.right_distance = math.pi * self.wheel_diameter * self.right_count / (2 * self.number_of_notches)
            self.left_distance = math.pi * self.wheel_diameter * self.left_count / (2 * self.number_of_notches)
            if ((time.time() - self.right_count_time1) < 2 * (self.right_count_time1 - self.right_count_time3)):
                self.right_speed = math.pi * self.wheel_diameter / self.number_of_notches / (self.right_count_time1 - self.right_count_time3)
            else:
                self.right_speed = 0.0
            if ((time.time() - self.left_count_time1) < 2 * (self.left_count_time1 - self.left_count_time3)):
                self.left_speed = math.pi * self.wheel_diameter / self.number_of_notches / (self.left_count_time1 - self.left_count_time3)
            else:
                self.left_speed = 0.0
            self.t = time.time()
            right_read = self.arduino.analogRead(self.pin_right_trip_sensor)
            left_read = self.arduino.analogRead(self.pin_left_trip_sensor)
            if(self.i < 5):
                print time.time() - self.t
                self.i += 1
            time.sleep(self.measurement_interval)

    def get_right_distance(self):
        return self.right_distance

    def get_left_distance(self):
        return self.left_distance

    # the absolute value
    def get_right_speed(self):
        return self.right_speed

    # the absolute value
    def get_left_speed(self):
        return self.left_speed

    def reset(self):
        self.left_count = 0
        self.right_count = 0

class Motor:
    # correct max speed, min voltage
    def __init__(trip_meter,  pin_right_forward = 5, pin_right_backward = 10, pin_left_forward = 6, pin_left_backward = 11, pin_motor_LED = 8, max_speed = 0.6, min_voltage = 1.0, correction_interval = 0.05, proportional_term_in_PID = 1.0, derivative_term_in_PID = 0.05):
        self.trip_meter = trip_meter
        self.arduino = trip_meter.arduino
    
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



