import Motor
import threading
import time

def print_speed_loop(trip_meter):
    while True: 
        print "%f   %f" % (trip_meter.get_right_speed(), trip_meter.get_left_speed())
        time.sleep(0.1)
        

trip_meter = Motor.TripMeter()
motor = Motor.Motor(trip_meter)

print_speed_thread = threading.Thread(target = print_speed_loop, args=(trip_meter,))
print_speed_thread.setDaemon(True)
print_speed_thread.start()

try: 
    while True:
        right_speed = input("Set right speed (-100 to 100):")
        left_speed = input("Set left speed (-100 to 100):")
        motor.set_right_speed(right_speed)
        motor.set_left_speed(left_speed)
except:
    motor.set_right_speed(0)
    motor.set_left_speed(0)
    motor.turn_off()
