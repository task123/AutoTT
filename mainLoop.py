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
    autoTTCommunication = TCP.AutoTTCommunication(port, ip_address = ip_address)
    print "1"
    trip_meter = Motor.TripMeter()
    print "2"
    motors = Motor.Motor(trip_meter)
    print "3"
    steering = Steering.SteeringWithIOSGyro(motors, autoTTCommunication = autoTTCommunication)
    print "4"
    mode = Steering.Mode(autoTTCommunication, steering)
    print "5"
    status = Status.Status(autoTTCommunication, motors)
    print "6"
    connection_test = Steering.ConnectionTest(autoTTCommunication, motors)
    print "7"
    autoTTCommunication.set_receivers(gyro_recv = steering, mode_recv = mode, status_recv = status, 
            stop_cont_recv = steering, disconnect_recv = connection_test, shut_down_recv = connection_test)
    #connection_test.set_intervall(0.05)
    #modes.send_modes_and_info_modes()
        
    print "hei"
    while True: #connection_test.get_good_connection():
        time.sleep(0.3)
            
except:
    if (motors):
        motors.turn_off()
    if (connection_test):
        connection_test.disconnect()
    
# os.system("sudo reboot")
