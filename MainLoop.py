import TCP
import Motor
import Steering
import Status
import time

port = 12346
ip_address = "10.22.8.34"

while True:
    autoTTCommunication = TCP.AutoTTCommunication(port, ip_address = ip_address)
    trip_meter = Motor.TripMeter()
    motors = Motor.Motor(trip_meter)
    steering = Steering.SteeringWithIOSGyro(motors, autoTTCommunication = autoTTCommunication)
    mode = Steering.Mode(autoTTCommunication, steering)
    status = Status.Status(autoTTCommunication, motors)
    connection_test = Steering.ConnectionTest(autoTTCommunication, motors)
    autoTTCommunication.set_receivers(gyro_recv = steering, mode_recv = mode, status_recv = status, stop_cont_recv = steering, disconnect_recv = connection_test, shut_down_recv = connection_test)
    connection_test.set_connection_test_intervall(0.05)
    
    while connection_test.get_good_connection:
        time.sleep(0.3)


