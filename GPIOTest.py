import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

pin = 3

GPIO.setup(pin, GPIO.OUT)

try:
while True:
        GPIO.output(pin, 1)
        time.sleep(2)
        GPIO.output(pin, 0)
        time.sleep(2)
except KeyboardInterrupt:
    GPIO.cleanup()
#GPIO.cleanup()
