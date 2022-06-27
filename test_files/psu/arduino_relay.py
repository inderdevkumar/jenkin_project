# Copyright (C) 2014. BMW Car IT GmbH. All rights reserved.
"""Arduino Relay Reset Switch connection and communication protocol
Using https://github.com/thearn/Python-Arduino-Command-API
"""

from Arduino import Arduino
from time import sleep
import logging

logger = logging.getLogger(__name__)

# pylint: disable=arguments-differ


class ArduinoRelay():
    """Encapsulation of the Arduino Relay Reset Switch connection
    and communication protocol
    """

    MODEL = "Arduino Micro + 8 relay board"

    BAUDRATE = 9600

    boards = {}

    @classmethod
    def _get_arduino_board(cls, port="/dev/ttyACM0"):
        """Get arduino board by port, if not exists, create one

        :param str port: arduino device
        :return: Arduino board object
        :rtype: Arduino
        """
        if port not in cls.boards:
            logger.info("Opening serial port '%s' with speed %s", port, cls.BAUDRATE)
            cls.boards[port] = Arduino(cls.BAUDRATE, port=port, timeout=2)
        else:
            logger.info("Using serial port '%s' with speed %s", port, cls.BAUDRATE)
        return cls.boards[port]

    def __init__(self, port="/dev/ttyACM0", pin=8):
        # use the autodiscover feature
        self.pin = pin
        self.board = self._get_arduino_board(port=port)
        logger.info("Using pin '%d' on Arduino", pin)
        self.board.pinMode(self.pin, "OUTPUT")
        self.board.digitalWrite(self.pin, "HIGH")

    def trigger(self, duration=0.2):
        """Turn the Relay ON and OFF again after time specified by duration parameter"""
        logger.info("Triggering pin #%d for %gs.", self.pin, duration)
        duration = float(duration)
        if duration <= 0:
            msg = "Positive time required (%gs)" % duration
            logger.error(msg)
            raise ValueError(msg)
        # make sure that the relay is in OFF state
        self.switch(active=False)
        # trigger the cycle
        self.switch()
        sleep(duration)
        self.switch(active=False)

    def switch(self, active=True):
        """Switch relay on or off"""
        state = "LOW" if active else "HIGH"
        logger.info("Setting pin #%d state to %s.", self.pin, state)
        self.board.digitalWrite(self.pin, state)

