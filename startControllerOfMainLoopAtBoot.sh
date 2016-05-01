#!/bin/bash

# check for internett connection and the start the controllerOfMainLoop.py as the mainLoop.py need 
# echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 > /dev/null 2>&1

# while [ ! $? -eq 0 ]
# do 
  # echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 > /dev/null 2>&1
# done
sleep 10
python controllerOfMainloop.py
