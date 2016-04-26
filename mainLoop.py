import TCP
import Motor
import Steering
import Status
import time
import os
import sys
import Cameras
import subprocess

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
    steering = Steering.SteeringWithIOSGyro(motors, autoTTCommunication = autoTTCommunication)
    modes = Steering.Modes(autoTTCommunication, steering)
    cameras = Cameras.Cameras(motors, autoTTCommunication, streaming_port = port + 1)
    status = Status.Status(autoTTCommunication, motors)
    """
    fan_controller = Status.FanController(motors, status, autoTTCommunication)
    disconnect = TCP.Disconnect(autoTTCommunication, motors, cameras, fan_controller)
    autoTTCommunication.set_receivers(gyro_recv = steering, mode_recv = modes, status_recv = status, stop_cont_recv = steering, 
            disconnect_recv = disconnect, shut_down_recv = disconnect, 
            video_recv = cameras)
    time.sleep(0.5) # wait for AutoTT iOS app to start the gyro class
    autoTTCommunication.start_gyro_with_update_intervall(1.0/60.0)
    modes.send_modes_and_info_modes()
    """
    
    while True:
        time.sleep(0.3)
        """
        if (not disconnect.good_connection):
            pid = os.getpid()
            file = open("pidMainLoop.txt", "w")
            file.write(str(pid))
            file.close()
        """


except:
    if (motors != None):
        motors.turn_off()
    if (cameras != None):
        cameras.turn_off()
    if (fan_controller != None):
        fan_controller.turn_off()
    if (disconnect != None):
        disconnect.disconnect()
