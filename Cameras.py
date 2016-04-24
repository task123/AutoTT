#! /usr/bin/python
import cv2
from nanpy import ArduinoApi
import time
import threading
from flask import Flask, render_template, Response

class Cameras:
    # streaming_port on AutoTT iOS app is by default port + 1
    def __init__(self, motors, autoTTCommunication, streaming_port):
        # these values might change
        self.pin_battery_camera_1 = 13
        self.pin_battery_camera_2 = 9
        ##################################################
        # Values after this should not need to be changed.
        ##################################################
        
        self.arduino = motors.arduino
        self.autoTTCommunication = autoTTCommunication
        self.streaming_port = streaming_port
        
        self.arduino.pinMode(self.pin_battery_camera_1, self.arduino.OUTPUT)
        self.arduino.pinMode(self.pin_battery_camera_2, self.arduino.OUTPUT)
        self.arduino.digitalWrite(self.pin_battery_camera_1, 0) # activ high
        self.arduino.digitalWrite(self.pin_battery_camera_2, 0) # activ low
        
        self.jpeg_quality = 95
        self.stream_on = False
        self.reduse_stream_fps_by_a_factor = 1
        self.new_stream_image = False
        self.camera_1_on = False
        self.camera_2_on = False
        self.video_1 = None
        self.video_2 = None

        self.camera_thread = threading.Thread(target = self.camera_loop)
        self.camera_thread.setDaemon(True)
        self.camera_thread.start()
        
        self.video_stream_thread = threading.Thread(target = self.video_stream_loop)
        self.video_stream_thread.setDaemon(True)
        self.video_stream_thread.start()

    def is_camera_1_on(self):
        return self.camera_1_on
            
    def start_camera_1(self):
        self.arduino.digitalWrite(self.pin_battery_camera_1, 1) # activ high
        time.sleep(5)
        self.video_1 = cv2.VideoCapture(0)
        self.video_1.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.video_1.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.camera_1_on = True
        
    def stop_camera_1(self):
        self.camera_1_on = False
        self.arduino.digitalWrite(self.pin_battery_camera_1, 0)
        if (self.video_1 != None):
            self.video_1.release()

    def start_camera_2(self):
        self.arduino.digitalWrite(self.pin_battery_camera_2, 0) # activ low
        time.sleep(5)
        self.video_2 = cv2.VideoCapture(1)
        self.video_2.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.video_2.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.camera_2_on = True
        
    def stop_camera_2(self):
        self.camera_2_on = False
        self.arduino.digitalWrite(self.pin_battery_camera_2, 1)
        if (self.video_2 != None):
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
                if (image_1 != None):
                    ret, self.stream_image_jpeg = cv2.imencode('.jpg', image_1, [cv2.IMWRITE_JPEG_QUALITY,self.jpeg_quality])
                    self.new_stream_image = True
            time.sleep(0.01)

    def turn_off(self):
        self.stop_camera_2()
        self.stop_camera_1()
        
    def receive_message(self, type, message):
        if (type == "VideoStream"):
            if (message == "On"):
                self.start_video_stream()
            elif (message == "Off"):
                self.stop_video_stream()
        if (type == "VideoQuality"):
            if (message == "High"):
                self.frame_height = 460
                self.frame_width = 790
                self.jpeg_quality = 10
                self.reduse_stream_fps_by_a_factor = 2
                if (self.video_1 != None):
                    self.video_1.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                    self.video_1.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                if (self.video_2 != None):
                    self.video_2.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                    self.video_2.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                self.autoTTCommunication.send_message("VideoStreamRefresh", "")
            elif (message == "Medium"):
                self.frame_height = 300
                self.frame_width = 568
                self.jpeg_quality = 95
                self.reduse_stream_fps_by_a_factor = 1
                if (self.video_1 != None):
                    self.video_1.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                    self.video_1.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                if (self.video_2 != None):
                    self.video_2.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                    self.video_2.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                self.autoTTCommunication.send_message("VideoStreamRefresh", "")
            elif (message == "Low"):
                self.frame_height = 300
                self.frame_width = 568
                self.jpeg_quality = 20
                self.reduse_stream_fps_by_a_factor = 1
                if (self.video_1 != None):
                    self.video_1.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                    self.video_1.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                if (self.video_2 != None):
                    self.video_2.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                    self.video_2.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                self.autoTTCommunication.send_message("VideoStreamRefresh", "")
                
    def start_video_stream(self):
        if (not self.camera_1_on):
            self.start_camera_1()
        self.have_yield = False
        self.stream_on = True
        self.autoTTCommunication.send_message("VideoStreamRefresh", "")
        time.sleep(0.1)
        self.autoTTCommunication.send_message("VideoStreamRefresh", "")
        while (not self.have_yield):
            time.sleep(0.1)
        self.autoTTCommunication.send_message("VideoStreamStarted", "")

    def stop_video_stream(self):
        self.stream_on = False
        time.sleep(0.05)
        self.conditionally_stop_camera_1()

    
    def conditionally_stop_camera_1(self):
        if (not self.stream_on):
            self.stop_camera_1()
            
    def video_stream_loop(self):
        flaskApp = Flask(__name__)
        running = False
        
        @flaskApp.route('/')
        def index():
            return render_template('index.html')
    
        def gen():
            self.frame_count = 0
            while (self.stream_on):
                while (not self.new_stream_image):
                    time.sleep(0.001)
                self.new_stream_image = False
                if (self.frame_count % self.reduse_stream_fps_by_a_factor == 0):
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + self.stream_image_jpeg.tostring() + b'\r\n\r\n')
                    self.have_yield = True
                self.frame_count += 1
                

        @flaskApp.route('/video_feed')
        def video_feed():
            return Response(gen(),
                mimetype='multipart/x-mixed-replace; boundary=frame')
        
        flaskApp.run(host='0.0.0.0', port=self.streaming_port, debug=False, use_reloader=False)
