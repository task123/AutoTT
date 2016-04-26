# hack to avoid the waiting time after the connection with the app is closed 
# (before it can connect again on the same port)

import os
import time
import subprocess
import sys

file = open("pidMainLoop.txt", "w")
file.close()
subprocess.Popen([sys.executable, "mainLoop.py"])
while True:
  file = open("pidMainLoop.txt")
  pid = file.readline()
  file.close()
  if (pid != '\n' and pid != ''):
    print "kill"
    os.kill(int(pid), 2)
    file = open("pidMainLoop.txt", "w")
    file.close()
    time.sleep(1) #make sure mainLoop.py is stopped
    subprocess.Popen([sys.executable, "mainLoop.py"])
    print "sub"
  time.sleep(0.3)
  
