import os
import time
import signal

def killstuff():
  file = open("pidMainLoop.txt")
  pid = file.readline()
  file.close()
  os.kill(pid, 2)
  
signal.signal(2, killstuff)

while True:
  time.sleep(10)
  
