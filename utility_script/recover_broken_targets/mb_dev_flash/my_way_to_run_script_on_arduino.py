#!/usr/bin/env python
"""
 Blinks an LED on digital pin 13
 in 1 second intervals
"""

from Arduino import Arduino
import time

board = Arduino('9600') #plugged in via USB, serial com at rate 9600
board.pinMode(5, "OUTPUT")
board.digitalWrite(5, "LOW")
#board.digitalWrite(5, "HIGH")

#while True:
   # board.digitalWrite(5, "LOW")
   # time.sleep(1)
   # board.digitalWrite(5, "HIGH")
   # time.sleep(1)
