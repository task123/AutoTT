#! /usr/bin/python

class Cameras:
  def __init__(self):
    video = cv2.VideoCapture(0)
    video.set(cv2.cv.CV_CAP_PROP_FPS,30)
    video.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,720)
    video.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,1280)
    
  def start(self):
    self.is_looping = True
    self.camera_thread = threading.Thread(target = self.camera_loop)
    self.camera_thread.setDaemon(True)
    self.camera_thread.start()
    
  def stop(self):
    self.is_looping = False
    
  def camera_loop(self):
    while self.is_looping:
      _, image = video.read()
      
  def __del__(self):
    camera.release()
