import TCP
import Steering
import Motor
import time

"""
add
print "right speed: " + str(right_speed)
print "left speed: " + str(left_speed)
under     
def receive_message(self, type, message):
    if (type == "Gyro" and self.stop == False):
and comment out
self.motors.set_right_speed(right_speed)
self.motors.set_left_speed(left_speed)
too test with driving the Motor class
"""

autoTTCommunication = TCP.AutoTTCommunication(12345)

trip_meter = Motor.TripMeter()
motors = Motor.Motor(trip_meter)
steering = Steering.SteeringWithIOSGyro(motors)
autoTTCommunication.gyro_recv = steering
autoTTCommunication.stop_cont_recv = steering
print "hei"
autoTTCommunication.send_message("Gyro", "0.2")
time.sleep(2)
autoTTCommunication.send_message("Gyro", "0.2")
autoTTCommunication.send_message("Gyro", "0.2")
print "printa Gyro"


while True:
    time.sleep(5)