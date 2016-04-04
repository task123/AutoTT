#!/usr/bin/python

"""React to gyroscopic and stop/continue data sendt from AutoTTCommunication and control a class 'motors', which steers the motors.

Sends messages set_right_speed('speed') and set_left_speed('speed') to 'motors'.
 - 'speed' is a number from -100 to 100, 100 being full speed forward, -100 being full speed in reverse.
"""
class SteeringWithIOSGyro:
    min_roll = 2.0 * 3.14 / 180.0
    max_roll = 30.0 * 3.14 / 180.0
    max_pitch = 30.0 * 3.14 / 180.0
    
    def __init__(self, motors, autoTTCommunication = None, gyro_update_intervall = 1.0/60.0):
        self.motors = motors
        self.stop = True
        if (autoTTCommunication != None):
            autoTTCommunication.start_gyro_with_update_intervall(gyro_update_intervall)

    def receive_message(self, type, message):
        if (type == "Gyro" and self.stop == False):
            [roll, pitch, yaw] = message.split(';', 2)
            roll = float(roll)
            pitch = float(pitch)
            yaw = float(yaw)
            
            direction_angle = math.atan(pitch / roll)
            if (roll > 0 and pitch > 0):
                direction_angle = math.pi / 2.0 - direction_angle
            elif (roll < 0 and pitch > 0):
                direction_angle = direction_angle - math.pi / 2.0
            elif (roll < 0 and pitch < 0):
                direction_angle = direction_angle + math.pi / 2.0
            elif (roll > 0 and pitch < 0):
                direction_angle = math.pi / 2.0 + direction_angle
            direction_angle *= 180.0 / math.pi
            speed = math.sqrt((roll / max_roll)**2 + (pitch / max_pitch)**2)
            if (speed > 1.0):
                speed = 1.0
            elif (speed < (min_roll / max_roll)):
                speed = 0.0

            if (direction_angle >= 0.0 and direction_angle <= 90.0):
                right_speed = 100.0 * speed
                left_speed = right_speed * (1 - direction_angle / 45.0)
            elif (direction_angle < 0.0 and direction_angle >= -90.0):
                left_speed = 100.0 * speed
                right_speed = left_speed * (1 + direction_angle / 45.0)
            elif (direction_angle > 90.0 and direction_angle <= 180.0):
                left_speed = -100.0 * speed
                right_speed = -left_speed * (1 - (direction_angle - 90.0) / 45.0)
            elif (direction_angle < -90.0 and direction_angle >= -180.0):
                right_speed = -100.0 * speed
                left_speed = -right_speed * (1 + (direction_angle - 90.0) / 45.0)
        
        elif (type == "Stop"):
            self.stop = True
            self.motors.speed(0.0)
            self.turn(0.0)
        elif (type == "Continue"):
            self.stop = False

"""React to messages from AutoTTCommunication and control a class 'motors', which steers the motors.
    
Sends messages set_right_speed('speed') and set_left_speed('speed') to 'motors'.
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