#!/usr/bin/python

"""React to gyroscopic and stop/continue data sendt from AutoTTCommunication and control a class 'motors', which steers the motors.

Sends messages speed('speed') and turn('turn') to 'motors'.
 - 'speed' is a number from -100 to 100, 100 being full speed forward.
 - 'turn' is a number from -100 to 100, 100 being full turn to the right.
"""
class SteeringWithIOSGyro:
    min_roll_forward = 0.0
    min_roll_backward = -min_roll_forward
    max_roll_forward = 30.0 * 3.14 / 180.0
    max_roll_backward = -max_roll_forward
    min_pitch = 0.0
    max_pitch = 30.0 * 3.14 / 180.0
    
    def __init__(self, motors, autoTTCommunication = None, gyro_update_intervall = 1.0/60.0):
        self.motors = motors
        self.stop = True
        if (autoTTCommunication != None):
            autoTTCommunication.start_gyro_with_update_intervall(gyro_update_intervall)

    def receive_message(self, type, message):
        if (type == "Gyro" and self.stop == False):
            [roll, pitch, yaw] = message.split(';', 2)
            print roll + " " + pitch + " " + yaw
            roll = float(roll)
            pitch = float(pitch)
            yaw = float(yaw)
            if (roll < self.min_roll_forward and roll > self.min_roll_backward):
                self.motors.speed(0.0)
            elif (roll > self.max_roll_forward):
                self.motors.speed(100.0)
            elif (roll < self.max_roll_backward):
                self.motors.speed(-100.0)
            elif (roll > 0):
                self.motors.speed(100.0 * (roll - self.min_roll_forward) / (self.max_roll_forward - self.min_roll_forward))
            elif (roll < 0):
                self.motors.speed(100.0 * (roll - self.min_roll_backward) / abs(self.max_roll_backward - self.min_roll_backward))

            if (abs(pitch) < self.min_pitch):
                self.motors.turn(0.0)
            elif (abs(pitch) > self.max_pitch):
                self.motors.turn(100.0 * (pitch - self.min_pitch) / abs(pitch))
            else:
                self.motors.turn(100.0 * (pitch - self.min_pitch) / (self.max_pitch - self.min_pitch))
        elif (type == "Stop"):
            self.stop = True
            self.motors.speed(0.0)
            self.turn(0.0)
        elif (type == "Continue"):
            self.stop = False

"""React to messages from AutoTTCommunication and control a class 'motors', which steers the motors.
    
Sends messages right_speed('speed') and left_speed('speed') to 'motors'.
- 'speed' is a number from 0 to 100, 100 being full speed forward and 0 being stop.
"""
class SteeringWithIOSButtons:
    max_speed = 100.0
    def __init__(self, motors, autoTTCommunication = None, gyro_update_intervall = 1.0/60.0):
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