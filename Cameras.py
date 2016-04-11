#! /usr/bin/python
import cv2

class Cameras:
  def __init__(self):
    video1 = cv2.VideoCapture(0)
    video2 = cv2.VideoCapture(1)
    video1.set(cv2.cv.CV_CAP_PROP_FPS,30)
    video2.set(cv2.cv.CV_CAP_PROP_FPS,30)
    video1.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,720)
    video2.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,720)
    video1.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,1280)
    video2.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,1280)
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
      _, image1 = video1.read()
      if (self.stereo_vision_on):
        _, image2 = video2.read()
      if (self.stream_on):
        ret, jpeg = cv2.imencode('.jpg', image1, [cv2.cv.CV_IMWRITE_JPEG_QUALITY,self.jpeg_quality])
      
      
  def __del__(self):
    video1.release()
    video2.release()
