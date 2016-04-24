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
        self.arduino.digitalWrite(self.pin_battery_camera_1, 0) # active high
        self.arduino.digitalWrite(self.pin_battery_camera_2, 0) # active low
        
        self.image_1 = None
        self.image_2 = None
        self.blur_1 = None
        self.blur_2 = None
        
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
    
        self.look_for_stop_sign = False
        self.look_for_speed_sign = False
        self.look_for_traffic_light = False
        
        self.draw_rectangles = False
        self.write_distances = False
        self.write_type_of_objects = False
    
        self.ok_to_send_messages = True

    def is_camera_1_on(self):
        return self.camera_1_on
            
    def start_camera_1(self):
        self.arduino.digitalWrite(self.pin_battery_camera_1, 1) # active high
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
                (_, self.image_1) = self.video_1.read()
                self.blur_1 = cv2.GaussianBlur(self.image_1,(5,5),0)
            if (self.camera_2_on):
                _, self.image2 = self.video2.read()
                self.blur_2 = cv2.GaussianBlur(self.image_2,(5,5),0)
            if (self.look_for_stop_sign or self.look_for_speed_sign or self.look_for_traffic_light or self.draw_rectangles or self.write_distances or self.write_type_of_objects):
                self.detect_signs_and_lights()
            if (self.stream_on):
                if (self.image_1 != None):
                    ret, self.stream_image_jpeg = cv2.imencode('.jpg', self.image_1, [cv2.IMWRITE_JPEG_QUALITY,self.jpeg_quality])
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
                self.frame_width = 760
                self.jpeg_quality = 95
                self.reduse_stream_fps_by_a_factor = 1
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
                self.frame_height = 240
                self.frame_width = 360
                self.jpeg_quality = 35
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


    def set_look_for_stop_sign(self,look_for_stop_sign):
        self.look_for_stop_sign = look_for_stop_sign

    def get_look_for_stop_sign(self):
        return self.look_for_stop_sign

    def set_look_for_speed_sign(self,look_for_speed_sign):
        self.look_for_speed_sign = look_for_speed_sign
    
    def get_look_for_speed_sign(self):
        return self.look_for_speed_sign

    def set_look_for_traffic_light(self,look_for_traffic_light):
        self.look_for_traffic_light = look_for_traffic_light

    def get_look_for_traffic_light(self):
        return look_for_traffic_light

    def set_draw_rectangles(self,draw_rectangles):
        self.draw_rectangles = draw_rectangles
        
    def get_draw_rectangles(self):
        return self.draw_rectangles

    def set_write_distances(self,write_distances):
        self.write_distances = write_distances
    
    def get_write_distances(self):
        return self.write_distances

    def set_write_type_of_objects(self, write_type_of_objects):
        self.write_type_of_objects = write_type_of_objects
    
    def get_write_type_of_objects(self):
        return self.write_type_of_objects
    
    def set_ok_to_send_messages(self, ok_to_send_messages)
        self.ok_to_send_messages = ok_to_send_messages

    def get_ok_to_send_messages(self)
        return self.ok_to_send_messages

    def detect_signs_and_lights(self):
            hsv_image_1 = cv2.cvtColor(self.image_1, cv2.COLOR_BGR2HSV)
            font = cv2.FONT_HERSHEY_PLAIN
            font_size = 1.5
            font_thickness
            
            # Looking for stop signs and speed signs
            if (self.look_for_speed_sign or self.look_for_stop_sign):
                red_mask_low = cv2.inRange(hsv_image_1,np.array((0,100,100), dtype = "uint8"),np.array((7, 255, 255), dtype = "uint8"))
                red_mask_high = cv2.inRange(hsv_image_1,np.array((160,100,100), dtype = "uint8"),np.array((179, 255, 255), dtype = "uint8"))
                red_mask = cv2.addWeighted(red_mask_low,1.0, red_mask_high,1.0, 0.0)
                red_mask = cv2.GaussianBlur(red_mask,(5,5),0)

                #Looking for stop signs
                if (self.look_for_stop_sign):
                    red_edges = cv2.Canny(red_mask,100,50)
                    _, red_contours, hierarchy = cv2.findContours(red_edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                    if contours is not None:
                        for i in range(0,len(contours)):
                            peripheral = cv2.arcLength(red_contours[i], True)
                            approximate_polygon = cv2.approxPolyDP(red_contours[i], 0.03 * peripheral, True)
                            if (len(approximate_polygon) == 8 and cv2.isContourConvex(approximate_polygon) and cv2.contourArea(approximate_polygon) > 300):
                                x,y,w,h = cv2.boundingRect(approximate_polygon)
                                stop_sign = redMaskCopy[y:(y+h),x:(x+w)]
                                sign_rows,sign_cols = stop_sign.shape
                                average_intensity=0
                                for row in range(0,sign_rows):
                                    for col in range(0,sign_cols):
                                        average_intensity = average_intensity + stop_sign[row,col]
                                average_intensity = average_intensity/stop_sign.size
                                if (average_intensity > 90):
                                    # We have now found a stop sign
                                    if (self.draw_rectangles):
                                        cv2.rectangle(self.image_1, (x,y), (x+w,y+h), (0,0,155),3)
                                    if (write_type_of_objects):
                                        cv2.putText(self.image_1, "Stop", (x,y-7), font, font_size, (0,0,200),font_thickness)
                                    if (cv2.contourArea(approximate_polygon) > 3000 and cv2.contourArea(approximate_polygon) > 2000 and self.ok_to_send_messages):
                                        # Here we send a message to stop the car. We have to ajust the parameter so that we enter this if at the correct distance.

                                        self.ok_to_send_messages = False

                #Looking for speed signs
                if(self.look_for_speed_sign):
                    red_circles = cv2.HoughCircles(red_mask,cv2.HOUGH_GRADIENT,1,100000,param1=50,param2=40,minRadius=3,maxRadius=70)
                    if circles is not None:
                        red_circles = np.uint16(np.around(red_circles))










