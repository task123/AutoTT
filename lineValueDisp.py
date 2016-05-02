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
    right_value = (arduino.analogRead(pin_right_photo_diode) - 129.0) / 334.0
    left_value = (arduino.analogRead(pin_left_photo_diode) - 87.0) / 280.0
    error = 0
    print str(right_value) + "    " + str(left_value) # + "    " + str(right_value + left_value) + "    " + str(right_value - left_value)
    if (right_value > 1):
      error = 2 * right_value
    elif (left_value > 1):
      error = - 2 * left_value
    else:
      error = right_value - left_value
    #print error
    time.sleep(0.1)
except:
  motors.turn_off
  arduino.digitalWrite(pin_photo_diode_power, 0)
