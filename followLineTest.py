import TCP
import Motor
import Steering
import Status
import time
import Cameras
import Lights
import Modes
import os

trip_meter = Motor.TripMeter()
motors = Motor.Motor(trip_meter)
follow_line = Steering.FollowLine(motors, start_speed = 10)

while True:
  time.sleep(10)
