import os
import time

while True:
  file = open("pidMainLoop.txt")
  pid = file.readline()
  file.close()
  print pid
  if (pid != '\n'):
    os.kill(int(pid), 2)
  time.sleep(0.3)
  
