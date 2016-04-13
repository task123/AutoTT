#!/usr/bin/python

import time
import threading
import socket

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
            
        print "after while"

    def send_message(self, message):
        self.client.sendall(message)
        
    def close(self):
        self.run_receive_message_thread = False
        self.sock.close()

class AutoTTCommunication:
    #all recv classes must implement receive_message(message_type, message)
    def __init__(self, port, ip_address = None, gyro_recv = None, main_view_recv = None, mode_recv = None, status_recv = None, stop_cont_recv = None, disconnect_recv = None, shut_down_recv = None,  video_recv = None, button_recv = None):
        self.gyro_recv = gyro_recv
        self.mode_recv = mode_recv
        self.status_recv = status_recv
        self.stop_cont_recv = stop_cont_recv
        self.disconnect_recv = disconnect_recv
        self.shut_down_recv = shut_down_recv
        self.video_recv = video_recv
        self.button_recv = button_recv
        if (ip_address == None):
            ip_address = socket.gethostbyname(socket.gethostname())
        self.tcp = Connection(ip_address, port, self)
    
    def set_receivers(self, gyro_recv = None, main_view_recv = None, mode_recv = None, status_recv = None, stop_cont_recv = None, disconnect_recv = None, shut_down_recv = None,  video_recv = None, button_recv = None):
        self.gyro_recv = gyro_recv
        self.mode_recv = mode_recv
        self.status_recv = status_recv
        self.stop_cont_recv = stop_cont_recv
        self.disconnect_recv = disconnect_recv
        self.shut_down_recv = shut_down_recv
        self.video_recv = video_recv
        self.button_recv = button_recv

    def receive_message(self, message):
        while (len(message) > 0):
            try:
                [type, message] = message.split('#$#', 1)
                [message, next_message] = message.split('%^%\r\n', 1)
                if (type == "Gyro" and self.gyro_recv is not None):
                    self.gyro_recv.receive_message(type, message)
                elif (type == "MainView" and self.main_view_recv is not None):
                    self.main_view_recv.receive_message(type, message)
                elif (type == "Modes" and self.mode_recv is not None):
                    self.mode_recv.receive_message(type, message)
                elif (type == "InfoModes" and self.mode_recv is not None):
                    self.mode_recv.receive_message(type, message)
                elif (type == "Status" and self.status_recv is not None):
                    self.status_recv.receive_message(type, message)
                elif (type == "Stop" and self.stop_cont_recv is not None):
                    self.stop_cont_recv.receive_message(type, message)
                elif (type == "Continue" and self.stop_cont_recv is not None):
                    self.stop_cont_recv.receive_message(type, message)
                elif (type == "Disconnect" and self.disconnect_recv is not None):
                    print "her"
                    self.disconnect_recv.receive_message(type, message)
                elif (type == "ShutDown" and self.shut_down_recv is not None):
                    self.shut_down_recv.receive_message(type, message)
                elif (type == "VideoStream" and self.video_recv is not None):
                    self.video_recv.receive_message(type, message)
                elif (type == "VideoQuality" and self.video_recv is not None):
                    self.video_recv.receive_message(type, message)
                elif (type == "LeftButtonTouchDown" and self.button_recv is not None):
                    self.button_recv.receive_message(type, message)
                elif (type == "RightButtonTouchDown" and self.button_recv is not None):
                    self.button_recv.receive_message(type, message)
                elif (type == "LeftButtonTouchUp" and self.button_recv is not None):
                    self.button_recv.receive_message(type, message)
                elif (type == "RightButtonTouchUp" and self.button_recv is not None):
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

    def info_modes(self, list_of_info_modes):
        message = ""
        for info_mode in list_of_info_modes:
            message = message + info_mode + ";"
        if (len(message) > 0):
            message = message[:-1]
        self.send_message("InfoModes", message)

    def status(self, list_of_status):
        message = ""
        for status in list_of_info_status:
            message = message + status + ";"
        if (len(message) > 0):
            message = message[:-1]
        self.send_message("Status", message)

    def message(self, message):
        self.send_message("Message",message)
