# Copyright (C) 2016. BMW Car IT GmbH. All rights reserved.
"""Common functionalities of power supply unit"""

import logging
import serial
import termios
import time
import threading
from functools import wraps

import six
from abc import abstractmethod

from power_supply_base import PowerSupplyBase, WrongPowerSupplyError

logging.basicConfig(format="%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s")
logger = logging.getLogger("mtee.testing.power_supply.power_supply_common")


LOG_TIMESTAMP_FORMAT = "%H:%M:%S,%f"
LF = serial.to_bytes([10])
CR = serial.to_bytes([13])
CRLF = serial.to_bytes([13, 10])


def log_and_raise_exception(msg, exc=ValueError):
    """Helper for logging and raising an exception"""
    logger.error(msg)
    raise exc(msg)


def assert_if_in_interval(value, lower_limit, upper_limit, error_msg):
    """Asserts the validity of value (lower_limit < value <= upper_limit)"""
    if not (isinstance(value, (float, int)) and lower_limit < value <= upper_limit):
        log_and_raise_exception(error_msg, AssertionError)


def retry_on_error(func):
    """Decorator to retry a command when invalid output is read"""

    @wraps(func)
    def inner(*args, **kwargs):
        """Wrapper"""
        retries = 3
        for _ in range(retries):
            try:
                return func(*args, **kwargs)
            except WrongPowerSupplyError:
                logger.info("Serial device connected to device other than supported by this class")
                raise
            except (ValueError, IndexError):
                logger.exception("Malformed value read")
                time.sleep(0.5)
        raise RuntimeError("Retry failed {} times".format(retries))

    return inner


# pylint: disable=arguments-differ


class PowerSupplyCommon(PowerSupplyBase, threading.Thread):
    """Common functionalities of all power supply classes"""

    __th_lock = threading.Lock()

    def __init__(
        self,
        device="/dev/ttyUSB0",
        timeout=0.5,
        logfile=None,
        loginterval=0.5,
        options=None,
        baudrate=None,
        line_ending=None,
    ):
        threading.Thread.__init__(self, name="PowerSupplyThread")
        logger.info("Opening serial port %s set to speed %s", device, baudrate)
        self.ser = serial.serial_for_url(
            device,
            baudrate,
            timeout=timeout,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        build_target = "undefined"
        if options and options.target:
            build_target = options.target

        if not logfile:
            logfile = "powersupply_{0}.log".format(build_target)

        self._logfile = logfile
        self._loginterval = loginterval
        self._output_enabled = False
        self._running = False
        self.__th_lock = threading.Lock()
        self._line_ending = line_ending
        self._baudrate = baudrate
        self.daemon = True

    def start_logging(self):
        """Start the logging thread"""
        self._running = True
        self.start()

    def stop_logging(self):
        """Stop the logging thread"""
        self._running = False
        self.join()

    @abstractmethod
    def run(self):
        """
        Thread runner method. Log power consumption in a specified interval
        """

    def _send(self, command, arg="", silent=False):
        """Send a command to the serial port"""
        self.ser.flushInput()
        self.ser.flushOutput()

        sendstr = command + arg
        if six.PY3 and isinstance(sendstr, str):
            sendstr = bytes(sendstr, "utf-8")
        if not silent:
            logger.debug("sending command '%s'", sendstr)
        self.ser.write(sendstr + self._line_ending)

    def _receive(self, expected=None, silent=False):
        """Receive a line from the serial port"""
        res = self.ser.readline().strip()
        if not silent:
            logger.debug("returned '%s'", res)
        if expected is not None:
            if res != expected:
                log_and_raise_exception(
                    "Expected '{}' from power supply, got '{}'."
                    " Do you have other (old) processes running?".format(expected, res),
                    RuntimeError,
                )
        return res

    def _send_and_receive(self, command, arg=b"", expected=None):
        """Encapsulate the send and receive procedure and resend up to three times if necessary"""
        silent = True if command in [b"GETD", b"HMGV", b"HMGC"] else False
        with self.__th_lock:
            i = 0
            while True:
                self._send(command, arg, silent)
                time.sleep(0.1)
                try:
                    return self._receive(expected, silent)
                except (RuntimeError, termios.error) as err:
                    i = i + 1
                    if i >= 3:
                        raise err
                    time.sleep(1.0)

