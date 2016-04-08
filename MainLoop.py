import TCP
import Motor
import Steering
import Status

port = 12345
ip_address = "10.22.9.52"

autoTTCommunication = TCP.AutoTTCommunication(port, ip_address = ip_address)
trip_meter = Motor.TripMeter()
motors = Motor.Motor(trip_meter)
steering = Steering.SteeringWithIOSGyro(motors, autoTTCommunication = autoTTCommunication)
mode = Steering.Mode(autoTTCommunication, steering)
status = Status.Status(autoTTCommunication, motors)
autoTTCommunication.set_receivers(gyro_recv = steering, mode_recv = mode, status_recv = status, stop_cont_recv = steering)

while True:
    sleep(10)



