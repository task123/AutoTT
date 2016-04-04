import Motor
import time

tripMeter = Motor.TripMeter()

while True:
    print "right speed: " + tripMeter.get_right_speed()
    print "left speed: " + tripMeter.get_left_speed()
    print "right distance: " + tripMeter.get_right_distance()
    print "left distance: " + tripMeter.get_left_distance()
    time.sleep(2)