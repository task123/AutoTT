#!/usr/bin/env python2.7
# script by Alex Eames http://RasPi.tv
"""
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

time_stamp = 0.0
right_count = 0
left_count = 0
right_pin = 2
left_pin = 3



# GPIO 23 & 24 set up as inputs. One pulled up, the other down.
# 23 will go to GND when button pressed and 24 will go to 3V3 (3.3V)
# this enables us to demonstrate both rising and falling edge detection
GPIO.setup(right_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(left_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# now we'll define the threaded callback function
# this will run in another thread when our event is detected
def my_callback_right(channel):
    print "Rising edge detected on port 24 - even though, in the main thread,"
    print "we are still waiting for a falling edge - how cool?\n"
    time_now = time.time()
    if (time_now - time_stamp) >= 0.005:
        print "Rising edge detected on port 24 - even though, in the main thread,"
        print "we are still waiting for a falling edge - how cool?\n"
        time_stamp = time_now
        right_count += 1
        print right_count

def my_callback_left(channel):
    print "Rising edge detected on port 24 - even though, in the main thread,"
    print "we are still waiting for a falling edge - how cool?\n"
    time_now = time.time()
    if (time_now - time_stamp) >= 0.005:
        print "Rising edge detected on port 24 - even though, in the main thread,"
        print "we are still waiting for a falling edge - how cool?\n"
        time_stamp = time_now
        left_count += 1
        print left_count

print "Make sure you have a button connected so that when pressed"
print "it will connect GPIO port 23 (pin 16) to GND (pin 6)\n"
print "You will also need a second button connected so that when pressed"
print "it will connect GPIO port 24 (pin 18) to 3V3 (pin 1)"
raw_input("Press Enter when ready\n>")

# The GPIO.add_event_detect() line below set things up so that
# when a rising edge is detected on port 24, regardless of whatever
# else is happening in the program, the function "my_callback" will be run
# It will happen even while the program is waiting for
# a falling edge on the other button.
GPIO.add_event_detect(right_pin, GPIO.RISING, callback=my_callback_right)
GPIO.add_event_detect(left_pin, GPIO.RISING, callback=my_callback_left)


try:
    print "Waiting for falling edge on port 23"
    print "Falling edge detected. Here endeth the second lesson."
    raw_input("Press key to exit?")

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # clean up GPIO on normal exit

"""
#!/usr/bin/env python2.7
# script by Alex Eames http://RasPi.tv

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# GPIO 23 & 24 set up as inputs. One pulled up, the other down.
# 23 will go to GND when button pressed and 24 will go to 3V3 (3.3V)
# this enables us to demonstrate both rising and falling edge detection
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# now we'll define the threaded callback function
# this will run in another thread when our event is detected
def my_callback(channel):
    print "Rising edge detected on port 24 - even though, in the main thread,"
    print "we are still waiting for a falling edge - how cool?\n"

print "Make sure you have a button connected so that when pressed"
print "it will connect GPIO port 23 (pin 16) to GND (pin 6)\n"
print "You will also need a second button connected so that when pressed"
print "it will connect GPIO port 24 (pin 18) to 3V3 (pin 1)"
raw_input("Press Enter when ready\n>")

# The GPIO.add_event_detect() line below set things up so that
# when a rising edge is detected on port 24, regardless of whatever
# else is happening in the program, the function "my_callback" will be run
# It will happen even while the program is waiting for
# a falling edge on the other button.
GPIO.add_event_detect(2, GPIO.RISING, callback=my_callback)

try:
    print "Waiting for falling edge on port 23"
    GPIO.wait_for_edge(3, GPIO.FALLING)
    print "Falling edge detected. Here endeth the second lesson."

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # clean up GPIO on normal exit
