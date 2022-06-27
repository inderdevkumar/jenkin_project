
#!/usr/bin/env python
from Arduino import Arduino
import time


def Blink(led_pin, baud, port="/dev/ttyACM2"):
    """
    Blinks an LED in 1 sec intervals
    """
    print baud, port
    board = Arduino(baud, port)
    print baud, port
    board.pinMode(led_pin, "OUTPUT")
    while True:
        board.digitalWrite(led_pin, "LOW")
        print board.digitalRead(led_pin)  # confirm LOW (0)
        time.sleep(1)
        board.digitalWrite(led_pin, "HIGH")
        print board.digitalRead(led_pin)  # confirm HIGH (1)
        time.sleep(1)

if __name__ == "__main__":
    Blink(4, '9600')
