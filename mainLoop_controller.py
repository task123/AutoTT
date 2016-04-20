import os
import time

os.system("python mainLoop.py")
file = open("pidMainLoop.txt", "w")
file.close()
while True:
  file = open("pidMainLoop.txt")
  pid = file.readline()
  file.close()
  print pid != ''
  print pid != '\n'
  print "mellomrom"
  if (pid != '\n' and pid != ''):
    print "kill"
    os.kill(int(pid), 2)
    file = open("pidMainLoop.txt", "w")
    print "1"
    file.write("")
    print "2"
    file.close()
    time.sleep(1) #make sure mainLoop.py is stopped
    print "restart mainLoop"
    os.system("python mainLoop.py")
  time.sleep(0.3)
  
