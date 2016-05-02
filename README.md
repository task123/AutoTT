# AutoTT
This is the code used to run the self driving car described in [this project](https://autottblog.wordpress.com). The car is controlled from an iPhone using [this app](https://github.com/task123/AutoTTApp). It include the code run on a raspberrry pi (almost all the code is run on the pi) and two Arduinos. This 'README' file will briefly explain what the different moduels that does what to give an overview of what the code does. The code should probably be cleaned up to make it more readable and elegante (especially the Cameras class), but as it works we do not feel any urgent need to do so at the time being. 

## Description of the car
The car has two electric motors, a swivel wheel in the back and two webcameras up front. It also got two light sensor to be able to follow a road marked by white and black tape. A Raspberry Pi 3 is used to steer the car with the help of one Arduino Uno and a Arduino Nano. The pi control the Arduino Uno using Nanpy described below. The Arduino Uno control the motors, the lights, the relays turning on the power from the batteries, the fan to cool the pi. It also measure the voltage on the batteries and the signal from the two lightsensors on its analog pins. The Arduino Nano measure how fast the wheels are turning using a light sensor and a wheel with slits taken from an old CD-player, and sends signals to the pi's GPIO pins.

## Overview of what the different modules does

### Connection to the app 
####(TCP.py)
The 'AutoTTCommunication' class provides a simple way of communicating with the app. The 'README' file in the apps repository describe this communication. The class also destributes the messages from the app to the appropriate receiver. 

The 'Disconnect' class turn off all the varius thing all the other classes when the app disconnects from the car.

### Steering the car
####(tripMeterArduino, Motor.py, Steering.py and Modes.py)
As already stated the Arduino Nano measure how fast the wheels are turning using a light sensor and a wheel with slits taken from an old CD-player, and sends signals to the pi's GPIO pins.

The TripMeter class initiate two interupts on the GPIO pins and calculates the speed and distance traved for each wheel when the Arduino Nano sends signals.

The Motor class controls the speed of the two wheel and uses data from the TripMeter class correct the speed of the wheels.

The Steering modules contrains several classes for steering the car. The SteeringWithIOSGyro class takes gyroscopic data from the app and sends message to the Motor class on what speed each wheel should have on this basis. It also takes data about left and right button pressed turn on and off indicators and the high beam. The SteeringWithIOSButtons class used data from this buttons to provide very basic steering. The FollowLine class takes data from the two light sensors and follows a road marked up by black and white tape.

The Modes class send data to the app about the different modes and selects among other thing what steering module is used based on the choice of mode selected in the app.

### Status and lights 
####(Status.py and Lights.py)
The Status class sends data about the battery voltage on two batteries, the CPU temperatur, CPU usage, used memory and storage to the app. 

The FanController class turn the fan on when the CPU temperatur rises above 70 C and stop when it falls below 60 C. It also sends message to the app when the temperatur rases above 80 C and when the batteri voltages fall below 6.0 V or 4.9 V.

### Cameras 
####(Cameras.py and templates)
The Cameras class takes picutes with the web cameras and stream video from a http-server using Flask in addition to using OpenCV to find stop signs, speed signs (machine learning used to read the numbers) and traffic lights. Flask is easily installed by running the command 'pip install flask' in the terminal. The templates is used for this video stream. More on our use of OpenCv is found [here](https://autottblog.wordpress.com/programming-the-car/opencv/). The Cameras class

### Running the program 
####(mainLoop.py, controllerOfMainloop.py and startControllerOfMainLoopAtBoot.sh)
mainLoop.py stickes all the moduels together to a program.

controllerOfMainloop.py is a hack to avoid the timeout of the TCP connection. By having the mainLoop write to a file when it disconnects, the controllerOfMainloop then notices than the program have disconnected and kills the process before it restarts it. This way you don't have to way several minutes to connect to the same port again, which happens very often. 

startColtrollerOfMainLoopAtBoot.sh is a shell script that is launched at boot by the pi and the wait until it got a internet connection to call controllerOfMainloop.py.

## Nanpy
Python library and Arduino program to control the Arduino from the Raspberry Pi. It is poorly documented, but work fine if you only want to control the ports. We have added 'analogReference(INTERNAL)' in the setup function of the Arduino program part of Nanpy, nanpy-firware, to get more accurate voltage readings. We have explained how to install and use it [here](https://autottblog.wordpress.com/raspberry-pi-arduino/controlling-arduino-from-raspberry-pi-with-nanpy/).

## Arduino drives
####(CH341SER_MAC and CH341SER_WIN)
Many cheap Arduino clones uses CH34x usb chips in stead of the FDTI chips used in original Arduinos as these are much cheaper. So a normal problem with these these clones is that one is missing the drives for the CH34x chip. We have included the drives for Mac and Window and it is already install on Linux (at least on the Raspbian version we tried).If you should have any problem with installing the drives on the spesific version of your operating system, just google away somebody else have almost certainly had the same issuse. 
