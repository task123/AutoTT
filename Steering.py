#!/usr/bin/python

import math
import time
import os

"""React to gyroscopic and stop/continue data sendt from AutoTTCommunication and control a class 'motors', which steers the motors.
Remember to start the gyro with autoTTCommunication.start_gyro_with_update_intervall(gyro_update_intervall)

Sends messages set_right_speed('speed') and set_left_speed('speed') to 'motors'.
 - 'speed' is a number from -100 to 100, 100 being full speed forward, -100 being full speed in reverse.
"""
class SteeringWithIOSGyro:
    def __init__(self, motors, gyro_update_intervall = 1.0/60.0, min_roll = 2.0 * 3.14 / 180.0, max_roll = 30.0 * 3.14 / 180.0, max_pitch = 30.0 * 3.14 / 180.0):
        self.motors = motors
        self.stop = True
        self.min_roll = min_roll
        self.max_roll = max_roll
        self.max_pitch = max_pitch

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
    def __init__(self, motors, gyro_update_intervall = 1.0/60.0):
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

class Mode:
    list_of_modes = ["Tilt Steering", "Tilt with AOA", "Button Steering", "Button with AOA", "Follow line", "Stop sign", "Traffic light", "Self steering"] # AOA - Automated Object Avoidence
    
    list_of_info_modes = ["Control the car by tilting your iOS device.", "Control the car by tilting your iOS device while AOA (Automated Object Avoidence) stops you from crashing into objects.", "Control the car by pushing the right and lift side of the screen.", "Control the car by pushing the right and left side of the screen while AOA (Automated Object Avoidence) stops you from crashing into objects.", "The car tries to follow a line on the ground and stops when objects blocks its way.", "The car tries to follow a line on the ground and stops for stop signs and objects blocking its way.", "The car tries to follow a line on the ground and stops for red traffic lights and objects blocking its way.", "The car tries to follow a line on the ground and stops for stop signs, red traffic lights and objects blocking its way."]
    
    def __init__(self, autoTTCommunication, steering):
        self.autoTTCommunication = autoTTCommunication
        self.steering = steering
    
    def recieve_message(self, type, message):
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
        self.autoTTCommunication.modes(self.list_of_modes)
        self.autoTTCommunication.info_modes(self.list_of_info_modes)

class ConnectionTest:
    def __init__(self, autoTTCommunication, motors):
        self.autoTTCommunication = autoTTCommunication
        self.motors = motors
        self.good_connection = True
        self.time_of_last_connection = time.time()
    
    def set_intervall(self, intervall):
        self.intervall = intervall
        self.autoTTCommunication.send_message("ConnectionTest", str(self.intervall))
                                         
    def receive_message(self, type, message):
        if (type == "ConnectionTest"):
            self.time_of_last_connection = time.time()
        elif (type == "Disconnect"):
            self.disconnect()
            print "Disconnected"
        elif (type == "Shutdown"):
            self.disconnect()
            os.system("sudo shutdown now")

    def get_good_connection(self):
        if (self.good_connection):
            self.good_connection = True
            print time.time() - self.time_of_last_connection
            print (time.time() - self.time_of_last_connection < 10 * self.intervall)
            if (self.good_connection):
                return True
            else:
                self.disconnect()
                return False
        else:
            return False

    def disconnect(self):
        self.motors.turn_off()
        self.good_connection = False
        self.autoTTCommunication.close()

