import TCP
import Motor
import Steering
import Status
import time
import Cameras
import Lights
import Modes
import os

try:
  trip_meter = Motor.TripMeter()
  motors = Motor.Motor(trip_meter)
  follow_line = Steering.FollowLine(motors, start_speed = 20)

  while True:
    time.sleep(10)
except:
  print "except"
  motors.turn_off()
  follow_line.stop()
