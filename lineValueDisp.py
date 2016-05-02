import threading
from nanpy import ArduinoApi
from nanpy import SerialManager
import math
import time
import Motor

print "1"
trip_meter = Motor.TripMeter()
print "2"
motors = Motor.Motor(trip_meter)

print "3"
pin_photo_diode_power = 12
pin_left_photo_diode = 18
pin_right_photo_diode = 19

print "4"
arduino = motors.arduino

print "5"
arduino.pinMode(pin_photo_diode_power, arduino.OUTPUT)
arduino.pinMode(pin_left_photo_diode, arduino.INPUT)
arduino.pinMode(pin_right_photo_diode, arduino.INPUT)
print "6"
arduino.digitalWrite(pin_photo_diode_power, 1)
print "7"
try:
  while (True):
    print str(arduino.analogRead(pin_right_photo_diode)) + "    " + str(arduino.analogRead(pin_left_photo_diode))
    time.sleep(0.1)
except:
  print "8"
  motors.turn_off
  arduino.digitalWrite(pin_photo_diode_power, 0)
  print "9"
