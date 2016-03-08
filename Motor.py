import threading
from nanpy import ArduinoApi
from nanpy import SerialManager
import math
import time

class TripMeter:
    #change default notches
    #sensor max value ~4.3, min value ~2.0
    def __init__(self, pin_right_trip_sensor = 15, pin_left_trip_sensor = 14, lower_limit_sensor = 2.85, higher_limit_sensor = 3.35, number_of_notches = 100.0, wheel_diameter = 0.0694):
        self.pin_left_trip_sensor = pin_left_trip_sensor
        self.pin_right_trip_sensor = pin_right_trip_sensor
        self.lower_limit_sensor = lower_limit_sensor
        self.higher_limit_sensor = higher_limit_sensor
        self.number_of_notches = number_of_notches
        self.wheel_diameter = wheel_diameter
        
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
        
        self.trip_meter_thread = threading.Thread(target = self.tripMeter)
        self.trip_meter_thread.setDaemon(True)
        self.trip_meter_thread.start()

    
    
    def tripMeter(self):
        while True:
            right_read = self.arduino.analogRead(self.pin_right_trip_sensor)
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
            
            left_read = self.arduino.analogRead(self.pin_left_trip_sensor)
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
            
            self.right_distance = math.pi * self.wheel_diameter * self.right_count / (2 * number_of_notches)
            self.left_distance = math.pi * self.wheel_diameter * self.left_count / (2 * number_of_notches)
            self.right_speed = math.pi * self.wheel_diameter / number_of_notches / (self.right_count_time1 - self.right_count_time3)
            self.left_speed = math.pi * self.wheel_diameter / number_of_notches / (self.left_count_time1 - self.left_count_time3)

    def get_right_distance(self):
        return self.right_distance

    def get_left_distance(self):
        return self.left_distance

    def get_right_speed(self):
        return self.right_speed

    def get_left_speed(self):
        return self.left_speed

    def reset(self):
        self.left_count = 0
        self.right_count = 0

class Motor:
    # correct max speed
    def __init__(tripMeter, pin_right_forward = 5, pin_right_backward = 10, pin_left_forward = 6, pin_left_backward = 11, pin_motor_LED = 8, max_speed = 0.6, correction_interval = 0.01):
        self.trip_meter = trip_meter
        self.arduino = trip_meter.arduino
                            
        self.pin_right_forward = pin_right_forward
        self.pin_right_backward = pin_right_backward
        self.pin_left_forward = pin_left_forward
        self.pin_left_backward = pin_left_backward
        self.pin_motor_LED = pin_motor_LED
                            
        self.arduino.pinMode(pin_right_forward, self.arduino.OUTPUT)
        self.arduino.pinMode(pin_right_backward, self.arduino.OUTPUT)
        self.arduino.pinMode(pin_left_forward, self.arduino.OUTPUT)
        self.arduino.pinMode(pin_left_backward, self.arduino.OUTPUT)
        self.arduino.pinMode(pin_motor_LED, self.arduino.OUTPUT)

        self.arduino.digitalWrite(pin_motor_LED, 0)
        
        self.speed = 0.0
        self.turn = 0.0
        self.right_forward_value = 0
        self.right_backward_value = 0
        self.left_forward_value = 0
        self.left_backward_value = 0
    
        self.motor_control_thread = threading.Thread(target = self.motor_control)
        self.motor_control_thread.setDaemon(True)
        self.motor_control_thread.start()
    
    def motor_control(self):
        while True:
            true_speed = self.trip_meter.get_right_speed + self.trip_meter.get_left_speed / 2.0 / max_speed
            if (true_speed != 0):
                true_turn = (self.trip_meter.get_right_speed - self.trip_meter.get_left_speed) / (self.trip_meter.get_right_speed + self.trip_meter.get_left_speed)
            else:
                true_speed = 0

    
    def stop(self):
        self.arduino.analogWrite(pin_right_forward, 0)
        self.arduino.analogWrite(pin_right_backward, 0)
        self.arduino.analogWrite(pin_left_forward, 0)
        self.arduino.analogWrite(pin_left_backward, 0)

    def turn_off(self):
        self.arduino.digitalWrite(pin_motor_LED, 1)
        self.stop()
        time.sleep(30)

    def speed(self, speed):


    def turn(self, turn):


    def right_speed(self, speed):


    def left_speed(self, speed):


