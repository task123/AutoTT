import threading
from nanpy import ArduinoApi
from nanpy import SerialManager
import math
import time
import Motor

trip_meter = Motor.TripMeter()
motors = Motor.Motor(trip_meter)

pin_photo_diode_power = 12
pin_left_photo_diode = 18
pin_right_photo_diode = 19

arduino = motors.arduino
            
arduino.pinMode(pin_photo_diode_power, arduino.OUTPUT)
arduino.pinMode(pin_left_photo_diode, arduino.INPUT)
arduino.pinMode(pin_right_photo_diode, arduino.INPUT)

arduino.digitalWrite(pin_photo_diode_power, 1)

try:
  while (True):
    print str(analogRead(pin_right_photo_diode)) + "    " + str(analogRead(pin_right_photo_diode))
    time.sleep(0.1)
except:
  motors.turn_off
  arduino.digitalWrite(pin_photo_diode_power, 0)
