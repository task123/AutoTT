import TCP
import time

class R:
  def receive_of_messages(self, message):
    print message

r = R()
connection = TCP.Connection("10.22.8.239", 12345, r);

print "hei"

while True:
  time.sleep(10)
