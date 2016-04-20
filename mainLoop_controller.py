import os
import time

os.system("python mainLoop.py")
file = open("pidMainLoop.txt", "w")
file.close()
while True:
  file = open("pidMainLoop.txt")
  pid = file.readline()
  file.close()
  if (pid != '\n' and pid != ''):
    os.kill(int(pid), 2)
    file = open("pidMainLoop.txt", "w")
    file.close()
    time.sleep(0.01) #make sure mainLoop.py is stopped
    os.system("python mainLoop.py")
  time.sleep(0.3)
  
