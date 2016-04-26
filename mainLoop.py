import TCP
import Motor
import Steering
import Status
import time
import Cameras
import Lights
import Modes
import os

port = 12345 

motors = None
cameras = None
fan_controller = None
disconnect = None
try:
    trip_meter = Motor.TripMeter()
    motors = Motor.Motor(trip_meter)
    print "Ready to login"
    autoTTCommunication = TCP.AutoTTCommunication(port)
    lights = Lights.Lights(motors)
    steering = Steering.SteeringWithIOSGyro(motors, autoTTCommunication = autoTTCommunication)
    modes = Modes.Modes(autoTTCommunication, steering, lights)
    cameras = Cameras.Cameras(motors, autoTTCommunication, streaming_port = port + 1)
    status = Status.Status(autoTTCommunication, motors)
    fan_controller = Status.FanController(motors, status, autoTTCommunication)
    disconnect = TCP.Disconnect(autoTTCommunication, motors, cameras, fan_controller)
    autoTTCommunication.set_receivers(gyro_recv = steering, mode_recv = modes, status_recv = status, stop_cont_recv = steering, 
            disconnect_recv = disconnect, shut_down_recv = disconnect, 
            video_recv = cameras)
    time.sleep(0.5) # wait for AutoTT iOS app to start the gyro class
    autoTTCommunication.start_gyro_with_update_intervall(1.0/60.0)
    modes.send_modes_and_info_modes()
    
    line = "LLL"
    while True:
        time.sleep(0.3)
        if (not disconnect.good_connection):
            print "hei"
            pid = os.getpid()
            print "1"
            file = open("pidMainLoop.txt", "w")
            print "2"
            file.write(str(pid))
            print "3"
            file.close()
            print "4"
            file = open("pidMainLoop.txt")
            print "5"
            line = file.readline()
            print "6"
            if (line != ''):
                print "file"
            print line
            file.close()


except:
    if (motors != None):
        motors.turn_off()
    if (cameras != None):
        cameras.turn_off()
    if (fan_controller != None):
        fan_controller.turn_off()
    if (disconnect != None):
        disconnect.disconnect()
