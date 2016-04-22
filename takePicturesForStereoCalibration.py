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

webCamHndlr_r = cv2.VideoCapture(1)
webCamHndlr_l = cv2.VideoCapture(0)

i = 0
while (True):
     print "press key to take picture number" + str(i+1)
     i += 1
     cv2.waitKey()
     ret,imgr  = webCamHndlr_r.read()
     ret,imgl  = webCamHndlr_l.read()
     if (imgl == None or imgr == None):
          print "imgl or imgr is equal to None"
     cv2.imwrite("chess_images/chessboard_r_" + str(i) + ".png", imgr)
     cv2.imwrite("chess_images/chessboard_l_" + str(i) + ".png", imgl)
