import time
import serial

arduino = serial.Serial('/dev/cu.usbmodem1421', 115200, timeout = 10)


while True:
    arduino.write("hei")
    time.sleep(2)
