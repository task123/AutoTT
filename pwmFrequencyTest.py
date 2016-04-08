#!/usr/bin/python

import sys, tty, termios, time, select
import thread
from nanpy import ArduinoApi
from nanpy import SerialManager
connection = SerialManager(device='/dev/ttyACM0')

#from nanpy import serial_manager
#serial_manager.connect('/dev/ttyACM0')
# serial  connection to Arduino
# kan hende vi maa endre adresse her

Arduino=ArduinoApi(connection=connection)

pin_right = 6
pin_left = 5
Arduino.pinMode(pin_right, Arduino.OUTPUT)
Arduino.pinMode(pin_left, Arduino.OUTPUT)

Arduino.analogWrite(pin_right, 130)

while True:
  Arudino.digitalWrite(pin_left, 1)
  time.sleep(0.01)
  Ardino.digitalWrite(pin_left, 0)
  time.sleep(0.01)
