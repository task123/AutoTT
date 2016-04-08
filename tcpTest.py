import TCP
import time

class R:
  def receive_message(self, message):
    print message

r = R()
connection = TCP.Connection("10.22.9.52", 12345, r);

print "hei"

while True:
  time.sleep(10)
