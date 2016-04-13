import Motor

trip_meter = Motor.TripMeter()
motor = Motor.Motor(trip_meter)

while True:
    right_speed = input("Set right speed (-100 to 100):")
    left_speed = input("Set left speed (-100 to 100):")
    motor.set_right_speed(right_speed)
    motor.set_left_speed(left_speed)
    
