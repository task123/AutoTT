import cv2
import numpy as np
from nanpy import ArduinoApi
from nanpy import SerialManager
import time

try:
     connection = SerialManager(device='/dev/ttyACM2')
     arduino = ArduinoApi(connection=connection)
except:
     try:
          connection = SerialManager(device='/dev/ttyACM0')
          arduino = ArduinoApi(connection=connection)
     except:
          try:
               connection = SerialManager(device='/dev/ttyACM1')
               arduino = ArduinoApi(connection=connection)
          except:
               try:
                    connection = SerialManager(device='/dev/ttyACM3')
                    arduino = ArduinoApi(connection=connection)
               except:
                    print "Could not connect to the arduino using /dev/ttyACM0, /dev/ttyACM1, /dev/ttyACM2 or /dev/ttyACM3"
            
arduino.pinMode(13, arduino.OUTPUT)
arduino.digitalWrite(13, 1)
arduino.pinMode(9, arduino.OUTPUT)
arduino.digitalWrite(9, 0)

right_camera = cv2.VideoCapture(1)
left_camera = cv2.VideoCapture(0)

i = 0
while (True):
     print "press key to take picture number" + str(i+1)
     i += 1
     cv2.waitKey()
     ret, right_image  = right_camera.read()
     ret, left_image  = left_camera.read()
     if (right_image == None or left_image == None):
          print "right_image or left_image is equal to None"
     cv2.imwrite("chess_images/chessboard_r_" + str(i) + ".png", right_image)
     cv2.imwrite("chess_images/chessboard_l_" + str(i) + ".png", left_image)
