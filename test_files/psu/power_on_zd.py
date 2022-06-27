from arduino_relay import ArduinoRelay
import time
device = "/dev/ttyUSB_Arduino"
"""for i in range(2,10):
    a = ArduinoRelay(device, pin=i)
    a.switch(True)
    time.sleep(1)
    a.switch(False)
    time.sleep(3)"""

#time.sleep(3)
a = ArduinoRelay(device, pin=2)
#a.switch(True)
b = ArduinoRelay(device, pin=3)


c = ArduinoRelay(device, pin=6)


d = ArduinoRelay(device, pin=7)
#a.switch(False)
#time.sleep(1)
#b.switch(False)
#c.switch(True)
d.switch(False)
time.sleep(1)

d.switch(True)
