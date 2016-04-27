#!/usr/bin/python

import time
import threading
import socket
import os

class Connection:
    #the class 'receiver_of_message' must implement receive_message(message)
    def __init__(self, ip_address, port, receiver_of_messages):
        self.ip_address = ip_address
        self.port = port
        self.receiver_of_messages = receiver_of_messages
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip_address,port))
        self.sock.listen(1)
        (self.client, (self.ip_client,self.port_client)) = self.sock.accept()
        self.run_receive_message_thread = True
        self.receive_message_thread = threading.Thread(target = self.receive_messages)
        self.receive_message_thread.setDaemon(True)
        self.receive_message_thread.start()

    def receive_messages(self):
        while self.run_receive_message_thread:
            message = self.client.recv(1024)
            self.receiver_of_messages.receive_message(message)

    def send_message(self, message):
        self.client.sendall(message)
        
    def close(self):
        self.run_receive_message_thread = False
        self.sock.close()

class AutoTTCommunication:
    #all recv classes must implement receive_message(self, message_type, message)
    def __init__(self, port, ip_address = None, gyro_recv = None, main_view_recv = None, mode_recv = None, status_recv = None, stop_cont_recv = None, disconnect_recv = None, shut_down_recv = None, connection_test_recv = None,  video_recv = None, button_recv = None):
        self.gyro_recv = gyro_recv
        self.mode_recv = mode_recv
        self.status_recv = status_recv
        self.stop_cont_recv = stop_cont_recv
        self.disconnect_recv = disconnect_recv
        self.shut_down_recv = shut_down_recv
        self.connection_test_recv = connection_test_recv
        self.video_recv = video_recv
        self.button_recv = button_recv
        if (ip_address == None):
            gw = os.popen("ip -4 route show default").read().split() # commando works on raspberry pi, but not mac
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((gw[2], 0))
            ip_address = sock.getsockname()[0]
        self.tcp = Connection(ip_address, port, self)
    
    def set_receivers(self, gyro_recv = None, main_view_recv = None, mode_recv = None, status_recv = None, stop_cont_recv = None, disconnect_recv = None, shut_down_recv = None, connection_test_recv = None, video_recv = None, button_recv = None):
        self.gyro_recv = gyro_recv
        self.mode_recv = mode_recv
        self.status_recv = status_recv
        self.stop_cont_recv = stop_cont_recv
        self.disconnect_recv = disconnect_recv
        self.shut_down_recv = shut_down_recv
        self.connection_test_recv = connection_test_recv
        self.video_recv = video_recv
        self.button_recv = button_recv

    def receive_message(self, message):
        while (len(message) > 0):
            try:
                [type, message] = message.split('#$#', 1)
                [message, next_message] = message.split('%^%\r\n', 1)
                if (type != "Gyro"):
                    print message
                if (type == "Gyro" and self.gyro_recv is not None):
                    self.gyro_recv.receive_message(type, message)
                elif (type == "MainView" and self.main_view_recv is not None):
                    self.main_view_recv.receive_message(type, message)
                elif (type == "Modes" and self.mode_recv is not None):
                    self.mode_recv.receive_message(type, message)
                elif (type == "InfoModes" and self.mode_recv is not None):
                    self.mode_recv.receive_message(type, message)
                elif (type == "ChosenMode" and self.mode_recv is not None):
                    print "chosen"
                    print message
                    print self.mode_recv
                    self.mode_recv.receive_message(type, message)
                elif (type == "Status" and self.status_recv is not None):
                    self.status_recv.receive_message(type, message)
                elif (type == "Stop" and self.stop_cont_recv is not None):
                    self.stop_cont_recv.receive_message(type, message)
                elif (type == "Continue" and self.stop_cont_recv is not None):
                    self.stop_cont_recv.receive_message(type, message)
                elif (type == "Disconnect" and self.disconnect_recv is not None):
                    self.disconnect_recv.receive_message(type, message)
                elif (type == "ShutDown" and self.shut_down_recv is not None):
                    self.shut_down_recv.receive_message(type, message)
                elif (type == "ConnectionTest" and self.connection_test_recv is not None):
                    self.connection_test_recv.receive_message(type, message)
                elif (type == "VideoStream" and self.video_recv is not None):
                    self.video_recv.receive_message(type, message)
                elif (type == "VideoQuality" and self.video_recv is not None):
                    self.video_recv.receive_message(type, message)
                elif (type == "LeftButtonTouchDown" and self.button_recv is not None):
                    print "ld"
                    self.button_recv.receive_message(type, message)
                elif (type == "RightButtonTouchDown" and self.button_recv is not None):
                    print "rd"
                    self.button_recv.receive_message(type, message)
                elif (type == "LeftButtonTouchUp" and self.button_recv is not None):
                    print "lu"
                    self.button_recv.receive_message(type, message)
                elif (type == "RightButtonTouchUp" and self.button_recv is not None):
                    print "ru"
                    self.button_recv.receive_message(type, message)
                message = next_message
            except:
                message = ""
                
    def close(self):
        self.tcp.close()

    def send_message(self, type, message):
        self.tcp.send_message(type + "#$#" + message + "%^%\r\n")

    def start_gyro_with_update_intervall(self, seconds):
        self.send_message("Gyro", str(seconds))

    def start_gyro(self):
        self.send_message("Gyro", str(1.0/60.0))

    def buttons_on(self):
        print "button"
        self.send_message("ButtonsOn", "")

    def buttons_off(self):
        self.send_message("ButtonsOff", "")

    def modes(self, list_of_modes):
        message = ""
        for mode in list_of_modes:
            message = message + mode + ";"
        if (len(message) > 0):
            message = message[:-1]
        self.send_message("Modes", message)

    def info_modes(self, list_of_info_modes, chosen_info_number):
        self.send_message("InfoModes", list_of_info_modes[chosen_info_number])

    def status(self, list_of_status):
        message = ""
        for status in list_of_status:
            message = message + status + ";"
        if (len(message) > 0):
            message = message[:-1]
        self.send_message("Status", message)

    def message(self, message):
        self.send_message("Message",message)

class Disconnect:
    def __init__(self, autoTTCommunication, motors, cameras, fan_controller):
        self.autoTTCommunication = autoTTCommunication
        self.motors = motors
        self.cameras = cameras
        self.fan_controller = fan_controller
        self.good_connection = True
        self.time_of_last_connection = time.time()
                                         
    def receive_message(self, type, message):
        if (type == "Disconnect"):
            self.disconnect()
        elif (type == "Shutdown"):
            self.disconnect()
            os.system("sudo shutdown now")

    def disconnect(self):
        self.motors.turn_off()
        self.cameras.turn_off()
        self.fan_controller.turn_off()
        self.good_connection = False
        self.autoTTCommunication.close()
