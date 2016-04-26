import time
import threading
from nanpy import ArduinoApi
from nanpy import SerialManager

class Lights:
  def __init__(self, motors):
    # these variables might need to be adjusted
    low_beam_value = 5
    high_beam_value = 400
    indicator_blink_time = 0.1
    indicator_blink_delay = 0.1
    # these variables might change
    headlight_pin = 9
    tail_light_pin = 17
    right_indicator_pin = 2
    left_indicator_pin = 16
    ##################################################
    # Values after this should not need to be changed.
    ##################################################

    self.arduino = motors.arduino

    self.arduino.pinMode(headlight_pin, self.arduino.OUTPUT)
    self.arduino.pinMode(tail_light_pin, self.arduino.OUTPUT)
    self.arduino.pinMode(right_indicator_pin, self.arduino.OUTPUT)
    self.arduino.pinMode(left_indicator_pin, self.arduino.OUTPUT)
    
    self.is_lights_on = False
    self.is_high_beam_on = False
    self.is_right_indicator_on = False
    self.is_left_indicator_on = False

  def lights_on(self):
    self.is_lights_on = True
    if (self.is_high_beam_on):
      self.arduino.analogWrite(headlight_pin, high_beam_value)
    else:
      self.arduino.analogWrite(headlight_pin, low_beam_value)
    self.arduino.digitalWrite(tail_light_pin, 1)
    
  def lights_off(self):
    self.is_lights_on = False
    self.is_high_beam_on = False
    self.is_right_indicator_on = False
    self.is_left_indicator_on = False
    self.arduino.analogWrite(headlight_pin, 0)
    self.arduino.digitalWrite(tail_light_pin, 0)

    
  def high_beam_on(self):
    if (self.is_lights_on):
      self.is_high_beam_on = True
      self.arduino.analogWrite(headlight_pin, high_beam_value)
    
  def high_beam_off(self):
    self.is_high_beam_on = False
    if (self.is_lights_on):
      self.arduino.analogWrite(headlight_pin, low_beam_value)
    else:
      self.arduino.analogWrite(headlight_pin, 0)
      
  def right_indicator_loop(self):
    while (self.is_right_indicator_on):
      self.arduino.digitalWrite(self.right_indicator_pin, 1)
      time.sleep(self.indicator_blink_time)
      self.arduino.digitalWrite(self.right_indicator_pin, 0)
      time.sleep(self.indicator_blink_delay)
      
  def left_indicator_loop(self):
    while (self.is_left_indicator_on):
      self.arduino.digitalWrite(self.left_indicator_pin, 1)
      time.sleep(self.indicator_blink_time)
      self.arduino.digitalWrite(self.left_indicator_pin, 0)
      time.sleep(self.indicator_blink_delay)
      
  def right_indicator_on(self):
    self.is_right_indicator_on = True
    self.right_indicator_thread = threading.Thread(target = self.right_indicator_loop)
    self.right_indicator_thread.setDaemon(True)
    self.right_indicator_thread.start()
    
  def left_indicator_on(self):
    self.is_left_indicator_on = True
    self.left_indicator_thread = threading.Thread(target = self.left_indicator_loop)
    self.left_indicator_thread.setDaemon(True)
    self.left_indicator_thread.start()
    
  def right_indicator_off(self):
    self.is_right_indicator_on = False

  def left_indicator_off(self):
    self.is_left_indicator_on = False
