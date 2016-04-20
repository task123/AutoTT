import os
import time

while True:
  file = open("pidMainLoop.txt")
  pid = file.readline()
  file.close()
  print pid
  if (pid != ''):
    os.kill(int(pid), 2)
  time.sleep(0.3)
  
