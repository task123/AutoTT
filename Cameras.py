#! /usr/bin/python
import cv2

class Cameras:
  def __init__(self):
    video_1 = cv2.VideoCapture(0)
    video_2 = cv2.VideoCapture(1)
    video_1.set(cv2.CAP_PROP_FPS,30)
    video_2.set(cv2.CAP_PROP_FPS,30)
    video_1.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    video_2.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    video_1.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    video_2.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    self.jpeg_quality = 100
    
  def start(self):
    self.is_looping = True
    if (self.stereo_vision_on = None):
      self.stereo_vision_on = False
    if (self.stream_on = None):
      self.stream_on = False
    self.camera_thread = threading.Thread(target = self.camera_loop)
    self.camera_thread.setDaemon(True)
    self.camera_thread.start()
    
  def stop(self):
    self.is_looping = False
    self.stereo_vision_on = False
    
  def camera_loop(self):
    while self.is_looping:
      _, image_1 = video1.read()
      blur_1 = cv2.GaussianBlur(image_1,(5,5),0)
      if (self.stereo_vision_on):
        _, image2 = video2.read()
        blur_1 = cv2.GaussianBlur(image_2,(5,5),0)
      if (self.stream_on):
        ret, jpeg = cv2.imencode('.jpg', image1, [cv2.IMWRITE_JPEG_QUALITY,self.jpeg_quality])
      
      
  def __del__(self):
    video1.release()
    video2.release()
