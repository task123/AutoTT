import time
import threading
from nanpy import ArduinoApi
from nanpy import SerialManager

class Lights:
  def __init__(self, motors):
    # these variables might need to be adjusted
    self.low_beam_value = 5
    self.high_beam_value = 400
    self.indicator_blink_time = 0.1
    self.indicator_blink_delay = 0.1
    # these variables might change
    self.headlight_pin = 9
    self.tail_light_pin = 17
    self.right_indicator_pin = 2
    self.left_indicator_pin = 16
    ##################################################
    # Values after this should not need to be changed.
    ##################################################

    self.arduino = motors.arduino

    self.arduino.pinMode(self.headlight_pin, self.arduino.OUTPUT)
    self.arduino.pinMode(self.tail_light_pin, self.arduino.OUTPUT)
    self.arduino.pinMode(self.right_indicator_pin, self.arduino.OUTPUT)
    self.arduino.pinMode(self.left_indicator_pin, self.arduino.OUTPUT)
    
    self.is_lights_on = False
    self.is_high_beam_on = False
    self.is_right_indicator_on = False
    self.is_left_indicator_on = False

  def lights_on(self):
    self.is_lights_on = True
    if (self.is_high_beam_on):
      self.arduino.analogWrite(self.headlight_pin, self.high_beam_value)
    else:
      self.arduino.analogWrite(self.headlight_pin, self.low_beam_value)
    self.arduino.digitalWrite(self.tail_light_pin, 1)
    
  def lights_off(self):
    self.is_lights_on = False
    self.is_high_beam_on = False
    self.is_right_indicator_on = False
    self.is_left_indicator_on = False
    self.arduino.analogWrite(self.headlight_pin, 0)
    self.arduino.digitalWrite(self.tail_light_pin, 0)

    
  def high_beam_on(self):
    if (self.is_lights_on):
      self.is_high_beam_on = True
      self.arduino.analogWrite(self.headlight_pin, self.high_beam_value)
    
  def high_beam_off(self):
    self.is_high_beam_on = False
    if (self.is_lights_on):
      self.arduino.analogWrite(self.headlight_pin, self.low_beam_value)
    else:
      self.arduino.analogWrite(self.headlight_pin, 0)
      
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
