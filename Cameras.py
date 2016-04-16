#! /usr/bin/python
import cv2
from nanpy import ArduinoApi
import time

class Cameras:
    def __init__(self, motors, pin_battery_camera_1 = 13, pin_battery_camera_2 = 9):
        self.arduino = motors.arduino
        print "34"
        self.pin_battery_camera_1 = pin_battery_camera_1
        self.pin_battery_camera_2 = pin_battery_camera_2
        
        self.arduino.pinMode(self.pin_battery_camera_1, arduino.OUTPUT)
        self.arduino.pinMode(self.pin_battery_camera_2, arduino.OUTPUT)
        self.arduino.digitalWrite(self.pin_battery_camera_1, 0) # activ high
        self.arduino.digitalWrite(self.pin_battery_camera_2, 1) # activ low
        
        self.jpeg_quality = 100
        self.fps = 30
        self.frame_height = 720
        self.frame_width = 1280
        self.is_looping = True
        self.stream_on = False
        self.camera_1_on = False
        self.camera_2_on = False
        
        self.camera_thread = threading.Thread(target = self.camera_loop)
        self.camera_thread.setDaemon(True)
        self.camera_thread.start()
        
    def turn_on_relay_camera_1(self):
        self.arduino.digitalWrite(self.pin_battery_camera_1, 1) # activ high

    def conditinal_turn_off_relay_camera_1(self):
        if (not self.camera_1_on):
            self.arduino.digitalWrite(self.pin_battery_camera_1, 0)
            
    def start_camera_1(self):
        self.turn_on_relay_camera_1()
        self.video_1 = cv2.VideoCapture(0)
        self.video_1.set(cv2.CAP_PROP_FPS, self.fps)
        self.video_1.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.video_1.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.camera_1_on = True
        
    def stop_camera_1(self):
        self.camera_1_on = False
        self.conditinal_turn_off_relay_camera_1()
        self.video_1.release()

    def start_camera_2(self):
        self.arduino.digitalWrite(self.pin_battery_camera_2, 0) # activ low
        self.video_2 = cv2.VideoCapture(0)
        self.video_2.set(cv2.CAP_PROP_FPS, self.fps)
        self.video_2.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.video_2.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.camera_2_on = True
        
    def stop_camera_2(self):
        self.camera_2_on = False
        self.arduino.digitalWrite(self.pin_battery_camera_2, 1)
        self.video_2.release()
    
    def camera_loop(self):
        while True:
            if (self.camera_1_on):
                (_, image_1) = self.video_1.read()
                blur_1 = cv2.GaussianBlur(image_1,(5,5),0)
            if (self.camera_2_on):
                _, image2 = self.video2.read()
                blur_1 = cv2.GaussianBlur(image_2,(5,5),0)
            if (self.stream_on):
                ret, jpeg = cv2.imencode('.jpg', self.image_1, [cv2.IMWRITE_JPEG_QUALITY,self.jpeg_quality])
            time.sleep(3)
            print "hei"


    def turn_off(self):
        self.stop_camera_2()
        self.stop_camera_1()

        
