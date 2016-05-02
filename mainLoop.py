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
lights = None
cameras = None
fan_controller = None
disconnect = None
modes = None
steering = None
try:
    trip_meter = Motor.TripMeter()
    motors = Motor.Motor(trip_meter)
    lights = Lights.Lights(motors) 
    lights.blink_high_beam()
    lights.off()
    print "Ready to login"
    autoTTCommunication = TCP.AutoTTCommunication(port)
    steering = Steering.SteeringWithIOSGyro(motors)
    cameras = Cameras.Cameras(motors, autoTTCommunication, streaming_port = port + 1)
    status = Status.Status(autoTTCommunication, motors)
    fan_controller = Status.FanController(motors, status, autoTTCommunication)
    disconnect = TCP.Disconnect(autoTTCommunication, motors, lights, cameras, fan_controller)
    modes = Modes.Modes(autoTTCommunication, motors,  lights, steering, cameras, status, disconnect)
    autoTTCommunication.set_receivers(gyro_recv = steering, mode_recv = modes, status_recv = status, stop_cont_recv = steering, 
            disconnect_recv = disconnect, shut_down_recv = disconnect, 
            video_recv = cameras)
    time.sleep(0.5) # wait for AutoTT iOS app to start the gyro class
    autoTTCommunication.start_gyro_with_update_intervall(1.0/60.0)
    modes.send_modes()
    time.sleep(0.2)
    modes.send_modes()
    
    while True:
        time.sleep(0.3)
        if (not disconnect.good_connection):
            pid = os.getpid()
            file = open("pidMainLoop.txt", "w")
            file.write(str(pid))
            file.close()


except:
    print "except"
    if (isinstance(steering, Steering.FollowLine)):
        print "steering 1"
        steering.stop_following_line()
        print "steering 2"
        time.sleep(0.5)
    if (motors != None):
        motors.arduino.digitalWrite(12, 0) #turn off the light for the photo diodes under the car
        motors.turn_off()
    if (lights != None):
        lights.off()
    if (cameras != None):
        cameras.turn_off()
    if (fan_controller != None):
        fan_controller.turn_off()
    if (disconnect != None):
        disconnect.disconnect()
