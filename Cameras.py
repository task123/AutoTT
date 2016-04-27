#! /usr/bin/python
import cv2
from nanpy import ArduinoApi
import time
import threading
from flask import Flask, render_template, Response
import numpy as np

# sends messages stop_sign(), traffic_light(), speed_limit(speed_limit) to 'steering' set by set_steering(steering)
class Cameras:
    # streaming_port on AutoTT iOS app is by default port + 1
    def __init__(self, motors, autoTTCommunication, streaming_port):
        # these values might change
        self.pin_battery_camera_1 = 13
        self.pin_battery_camera_2 = 8
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
        
        self.frame_height = 300
        self.frame_width = 568
        self.jpeg_quality = 95
        self.stream_on = False
        self.reduse_stream_fps_by_a_factor = 1
        self.new_stream_image = False
        self.camera_1_on = False
        self.camera_2_on = False
        self.video_1 = None
        self.video_2 = None
        
        self.look_for_stop_sign = False
        self.look_for_speed_sign = False
        self.look_for_traffic_light = False
        
        self.draw_rectangles = False
        self.write_distances = False
        self.write_type_of_objects = False
        
        self.knn = cv2.ml.KNearest_create()
        self.knn_initialized = False
    
        self.ok_to_send_messages = True
        
        self.steering = None

        self.camera_thread = threading.Thread(target = self.camera_loop)
        self.camera_thread.setDaemon(True)
        self.camera_thread.start()
        
        self.video_stream_thread = threading.Thread(target = self.video_stream_loop)
        self.video_stream_thread.setDaemon(True)
        self.video_stream_thread.start()
        
    def set_steering(self, steering):
        self.steering = steering

    def is_camera_1_on(self):
        return self.camera_1_on
            
    def start_camera_1(self):
        self.arduino.digitalWrite(self.pin_battery_camera_1, 1) # active high
        time.sleep(2)
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
        time.sleep(2)
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


    def start_looking_for_stop_signs(self):
        if (not self.camera_1_on):
            self.start_camera_1()
        self.look_for_stop_sign = True

    def stop_looking_for_stop_signs(self):
        self.conditionally_stop_camera_1()
        self.look_for_stop_sign = False

    def start_looking_for_speed_signs(self):
        if (not self.camera_1_on):
            self.start_camera_1()
        self.look_for_speed_sign = True
    
    def stop_looking_for_speed_signs(self):
        self.conditionally_stop_camera_1()
        self.look_for_speed_sign = False

    def start_looking_for_traffic_lights(self):
        if (not self.camera_1_on):
            self.start_camera_1()
        self.look_for_traffic_light = True

    def stop_looking_for_traffic_lights(self):
        self.conditionally_stop_camera_1()
        self.look_for_traffic_light = False

    def start_drawing_rectangles(self):
        if (not self.camera_1_on):
            self.start_camera_1()
        self.draw_rectangles = True
        
    def stop_drawing_rectangles(self):
        self.draw_rectangles = False

    def start_writing_distances(self):
        if (not self.camera_1_on):
            self.start_camera_1()
        self.write_distances = True
    
    def stop_writing_distances(self):
        self.conditionally_stop_camera_1()
        self.write_distances = False

    def start_writing_type_of_objects(self):
        if (not self.is_camera_1_on()):
            self.start_camera_1()
        self.write_type_of_objects = True
    
    def stop_writing_type_of_objects(self):
        self.write_type_of_objects = False
        
    def stop_following_traffic_rules(self):
        self.stop_looking_for_stop_signs()
        self.stop_looking_for_speed_signs()
        self.stop_looking_for_traffic_lights()
        self.stop_drawing_rectangles()
        self.stop_writing_type_of_objects()
    
    def set_ok_to_send_messages(self, ok_to_send_messages):
        self.ok_to_send_messages = ok_to_send_messages

    def get_ok_to_send_messages(self):
        return self.ok_to_send_messages

    def detect_signs_and_lights(self):
        if (self.image_1 == None):
            print "cameras attribute image_1 is None"
        hsv_image_1 = cv2.cvtColor(self.image_1, cv2.COLOR_BGR2HSV)
        font = cv2.FONT_HERSHEY_PLAIN
        font_size = 1.5
        font_thickness = 2
    
        red_mask_low = cv2.inRange(hsv_image_1,np.array((0,100,100), dtype = "uint8"),np.array((7, 255, 255), dtype = "uint8"))
        red_mask_high = cv2.inRange(hsv_image_1,np.array((160,100,100), dtype = "uint8"),np.array((179, 255, 255), dtype = "uint8"))
        red_mask = cv2.addWeighted(red_mask_low,1.0, red_mask_high,1.0, 0.0)
        red_mask = cv2.GaussianBlur(red_mask,(5,5),0)

        #Looking for stop signs
        if (self.look_for_stop_sign):
            red_edges = cv2.Canny(red_mask,100,50)
            _, red_contours, hierarchy = cv2.findContours(red_edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            if red_contours is not None:
                for i in range(0,len(red_contours)):
                    peripheral = cv2.arcLength(red_contours[i], True)
                    approximate_polygon = cv2.approxPolyDP(red_contours[i], 0.03 * peripheral, True)
                    if (len(approximate_polygon) == 8 and cv2.isContourConvex(approximate_polygon) and cv2.contourArea(approximate_polygon) > 300):
                        x,y,w,h = cv2.boundingRect(approximate_polygon)
                        stop_sign = red_mask[y:(y+h),x:(x+w)]
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
                            if (self.write_type_of_objects):
                                cv2.putText(self.image_1, "Stop", (x,y-7), font, font_size, (0,0,200),font_thickness)
                            if (cv2.contourArea(approximate_polygon) > 3000 and cv2.contourArea(approximate_polygon) > 2000 and self.ok_to_send_messages):
                                # Here we send a message to stop the car. We have to ajust the parameter so that we enter this if at the correct distance.
                                if (self.steering != None):
                                    self.steering.stop_sign()
                                self.ok_to_send_messages = False

        #Looking for speed signs
        take_median_of_speed_signs = 15
        result_list_speed_signs = []
        is_only_inner_circle = False
        if(self.look_for_speed_sign):
            if (not self.knn_initialized):
                with np.load('knn_data.npz') as data:
                    train = data['train']
                    train_labels = data['train_labels']
                knn.train(train,cv2.ml.ROW_SAMPLE,train_labels)
                self.knn_initialized = True
            
            red_circles = cv2.HoughCircles(red_mask,cv2.HOUGH_GRADIENT,1,100000,param1=50,param2=40,minRadius=3,maxRadius=70)
            if red_circles is not None:
                red_circles = np.uint16(np.around(red_circles))
                (rows,columns,channels) = self.image_1.shape
                sign_area = np.zeros((rows,columns), dtype=np.uint8)
                cv2.ellipse(sign_area,(red_circles[0,:][0][0],red_circles[0,:][0][1]),(red_circles[0,:][0][2],red_circles[0,:][0][2]), 90,0,180,(255,255,255),-1,8,0)
                hsv_half_sign_image = cv2.bitwise_and(self.image_1, self.image_1, mask=sign_area )
                _,sign_mask = cv2.threshold(hsv_half_sign_image[:,:,2], 150, 255, cv2.THRESH_BINARY_INV)
                
                temp_sum = 0
                for sat_values in hsv_half_sign_image[:,:,1].flat:
                    temp_sum = temp_sum + sat_values
                average_sat_value = temp_sum.astype(np.float32)/(red_circles[0,:][0][2]**2)
                if average_sat_value < 80:
                    is_only_inner_circle = True

                sign_center_x = red_circles[0,:][0][0]
                sign_center_y = red_circles[0,:][0][1]
                sign_radius = red_circles[0,:][0][2]
                x_start =int(sign_center_x-sign_radius*0.8)
                x_end = sign_center_x
                y_start =int(sign_center_y-sign_radius*0.5)
                y_end =int(sign_center_y+sign_radius*0.5)

                temporary_ROI = sign_mask[y_start:y_end,x_start:x_end]
                cv2.imshow("number",temporary_ROI)
                resized_ROI = [cv2.resize(temporary_ROI,(20,20),interpolation=cv2.INTER_LINEAR)]

                resized_ROI_array = np.array(resized_ROI[0])
                temporary_array = resized_ROI_array.astype(np.uint8)  # No idea whatsoever why you have to do this
                prepeared_array = temporary_array.reshape(-1,400).astype(np.float32)
                _,result,neighbours,dist = knn.findNearest(prepeared_array,k=10)
                result_list_speed_signs.append(result)
                if (len(result_list_speed_signs) > take_median_of_speed_signs):
                    result_list_speed_signs.pop(0)
                copy_result_list = list(result_list_speed_signs)
                copy_result_list.sort()
                speed_sign_value = copy_result_list.pop(int(len(copy_result_list)/2))[0][0]*10

                if(self.draw_rectangles):
                    #draw rectangles
                    cv2.rectangle(self.image_1, (sign_center_x-sign_radius,sign_center_y-sign_radius), (sign_center_x+sign_radius,sign_center_y+sign_radius), (0,0,155),3)
                if(self.write_type_of_objects):
                    #write objects
                    cv2.putText(self.image_1, "Speed limit: %d" % speed_sign_value, (sign_center_x-sign_radius,sign_center_y-sign_radius-7), font, font_size, (0,0,200),font_thickness)
                if(self.ok_to_send_messages and is_only_inner_circle and sign_radius > 27):
                    #Send message
                    #must calibrate the distance given by sign_radius. Also, must reset ok_to_send_messages somewhere else, probably in steering...
                    if (self.steering != None):
                        self.steering.speed_limit(speed_sign_value)
                    self.ok_to_send_messages = False

        #Looking for traffic lights
        if(self.look_for_traffic_light):
            green_mask = cv2.inRange(hsv_image_1,np.array((80,100,50), dtype = "uint8"),np.array((90, 255, 255), dtype = "uint8"))
            yellow_mask = cv2.inRange(hsv_image_1,np.array((20,50,100), dtype = "uint8"),np.array((30, 255, 255), dtype = "uint8"))

            green_circles = cv2.HoughCircles(green_mask,cv2.HOUGH_GRADIENT,1,15, param1=100,param2=10,minRadius=1,maxRadius=30)
            yellow_circles = cv2.HoughCircles(yellow_mask,cv2.HOUGH_GRADIENT,1,15, param1=100,param2=7,minRadius=1,maxRadius=20)
            red_circles = cv2.HoughCircles(red_mask,cv2.HOUGH_GRADIENT,1,15,param1=100,param2=10,minRadius=1,maxRadius=20)

            red_light_mask = cv2.inRange(hsv_image_1,np.array((0,0,240), dtype = "uint8"),np.array((255, 255, 255), dtype = "uint8"))
            green_light_mask = cv2.inRange(hsv_image_1,np.array((0,0,50), dtype = "uint8"),np.array((70, 200, 255), dtype = "uint8"))



            if (red_circles is not None and green_circles is not None):
                for g_circ in range(0,len(green_circles[0,:])):
                    for r_circ in range(0,len(red_circles[0,:])):
                        if ( abs(red_circles[0,:][r_circ][0]-green_circles[0,:][g_circ][0]) < 10 and  abs(red_circles[0,:][r_circ][1]-green_circles[0,:][g_circ][1]) < 70):
                            x_min = int(red_circles[0,:][r_circ][0] - red_circles[0,:][r_circ][2]*3)
                            x_max = int(red_circles[0,:][r_circ][0] + red_circles[0,:][r_circ][2]*3)
                            green_minus_red = abs(green_circles[0,:][g_circ][1]-red_circles[0,:][r_circ][1])
                            y_min = int(red_circles[0,:][r_circ][1] + green_minus_red/2*(1-2))
                            y_max = int(red_circles[0,:][r_circ][1] + green_minus_red/2*(1+2))
                            
                            #Checking if it is the correct proportionality and if green is on top, might have to ajust the proportionality interval
                            if(green_circles[0,:][g_circ][1]>red_circles[0,:][r_circ][1] and (y_max-y_min)/(x_max-x_min) > 1.8 and (y_max-y_min)/(x_max-x_min) < 2.2):
                                
                                #Finding which color is on
                                if (yellow_circles is not None):
                                    for y_circ in range(0,len(yellow_circles[0,:])):
                                        if (abs(yellow_circles[0,:][y_circ][0]-green_circles[0,:][g_circ][0]) < 10  and abs(yellow_circles[0,:][y_circ][1]-green_circles[0,:][g_circ][1]) < 40):
                                            red_x = red_circles[0,:][r_circ][0]
                                            red_y = red_circles[0,:][r_circ][1]
                                            red_r = red_circles[0,:][r_circ][2] *0.50
                                            
                                            green_x = green_circles[0,:][g_circ][0]
                                            green_y = green_circles[0,:][g_circ][1]
                                            green_r = green_circles[0,:][g_circ][2] *0.50
                                            
                                            
                                            
                                            red_ROI = red_light_mask[int(red_y-red_r):int(red_y+red_r),int(red_x-red_r):int(red_x+red_r)]
                                            green_ROI = green_light_mask[int(green_y-green_r):int(green_y+green_r),int(green_x-green_r):int(green_x+green_r)]
                                            
                                            red_rows,red_cols = red_ROI.shape
                                            red_avg=0
                                            for row in range(0,red_rows):
                                                for col in range(0,red_cols):
                                                    red_avg = red_avg + red_ROI[row,col]
                                            red_avg = red_avg/red_ROI.size
                                            
                                            green_rows,green_cols = green_ROI.shape
                                            green_avg=0
                                            for row in range(0,green_rows):
                                                for col in range(0,green_cols):
                                                    green_avg = green_avg + green_ROI[row,col]
                                            green_avg = green_avg/green_ROI.size

                                            if(red_avg > 150):
                                                traffic_light_value = 0 # 0 red, 1 yellow, 2 green
                                                green_light_value = 255
                                                red_light_value = 0
                                            elif(green_avg > 100):
                                                traffic_light_value = 2 # 0 red, 1 yellow, 2 green
                                                green_light_value = 0
                                                red_light_value = 255

                                            if (self.draw_rectangles):
                                                cv2.rectangle(self.image_1, (x_min,y_min), (x_max,y_max), (0,green_light_value,red_light_value),3)
                                            if (write_type_of_objects):
                                                cv2.putText(self.image_1, "Traffic light", (x_min,y_min-7), font, font_size, (0,green_light_value,red_light_value),font_thickness)
                                            if (self.ok_to_send_messages and green_y - red_y > 55):
                                                # Here we send a message to stop the car. We have to ajust the parameter so that we enter this if at the correct distance.
                                                if (self.steering != None):
                                                    self.steering.traffic_light()
                                                self.ok_to_send_messages = False










