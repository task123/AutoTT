import Motor
import time

tripMeter = Motor.TripMeter()

while True:
    print "right speed: " + str(tripMeter.get_right_speed())
    print "left speed: " + str(tripMeter.get_left_speed())
    print "right distance: " + str(tripMeter.get_right_distance())
    print "left distance: " + str(tripMeter.get_left_distance())
    print "right count: " + str(tripMeter.right_count)
    print "left count: " + str(tripMeter.left_count)
    time.sleep(2)