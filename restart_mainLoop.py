import os
import time

file = open("pidMainLoop.txt", "w")
file.close()
while True:
  file = open("pidMainLoop.txt")
  pid = file.readline()
  file.close()
  print pid
  if (pid != '\n'):
    os.kill(int(pid), 2)
    file = open("pidMainLoop.txt", "w")
    file.close()
  time.sleep(0.3)
  
