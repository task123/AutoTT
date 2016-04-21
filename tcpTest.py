import TCP
import time

class R:
  def receive_message(self, message):
    print message

r = R()
connection = TCP.Connection("10.22.13.211", 12345, r);

while True:
    message = raw_input("Write message: ")
    connection.send_message(message)
