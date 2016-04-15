import TCP
import Motor
import Steering
import Status
import time
import os

port = 12345 # will change between 12345 and 12346
ip_address = "10.22.6.65"

motors = None
connection_test = None
try:
    trip_meter = Motor.TripMeter()
    motors = Motor.Motor(trip_meter)
    autoTTCommunication = TCP.AutoTTCommunication(port, ip_address = ip_address)
    steering = Steering.SteeringWithIOSGyro(motors, autoTTCommunication = autoTTCommunication)
    mode = Steering.Mode(autoTTCommunication, steering)
    status = Status.Status(autoTTCommunication, motors)
    connection_test = Steering.ConnectionTest(autoTTCommunication, motors)
    autoTTCommunication.set_receivers(gyro_recv = steering, mode_recv = mode, status_recv = status, 
            stop_cont_recv = steering, disconnect_recv = connection_test, shut_down_recv = connection_test)
    time.sleep(0.1)
    autoTTCommunication.start_gyro_with_update_intervall(1.0/60.0)
    #connection_test.set_intervall(0.05)
    #modes.send_modes_and_info_modes()
        
    while True: #connection_test.get_good_connection():
        time.sleep(0.3)
            
except:
    if (motors):
        motors.turn_off()
    if (connection_test):
        connection_test.disconnect()
    
# os.system("sudo reboot")
