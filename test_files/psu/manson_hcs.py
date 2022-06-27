# Copyright (C) 2014. BMW Car IT GmbH. All rights reserved.
"""Manson Switching Mode Power Supply connection and communication protocol"""

import logging
import six
import time
from datetime import datetime

from power_supply_common import (
    PowerSupplyCommon,
    LOG_TIMESTAMP_FORMAT,
    retry_on_error,
    WrongPowerSupplyError,
    CR,
    assert_if_in_interval,
)


logger = logging.getLogger(__name__)

# pylint: disable=arguments-differ


def build_command(command):
    """Wrapper to build a python version independent command

    :param str command: Command string to be decoded (py3)
    :return: A byte object if py3, a string if py2
    """
    if six.PY3:
        return bytes(command, "utf-8")
    return command


class MansonHCS(PowerSupplyCommon):
    """Encapsulation of the Manson Switching Mode Power Supply connection
    and communication protocol

    USB driver : Kernel built-in cp210x driver
    Model: Manson HCS-3300/3302/3304 USB
    """

    MODEL = "Manson HCS-3300/3302/3304 USB"

    VOLTAGE_MIN = 1.0

    def __init__(self, device="/dev/ttyUSB0", timeout=0.5, logfile=None, loginterval=1.0, options=None, baudrate=9600):
        super(MansonHCS, self).__init__(
            device=device,
            baudrate=baudrate,
            timeout=timeout,
            logfile=logfile,
            loginterval=loginterval,
            options=options,
            line_ending=CR,
        )
        try:
            self.max_supported_voltage, self.max_supported_current = self._bare_get_max_voltage_and_current()
        except ValueError:
            raise WrongPowerSupplyError
        self._preset_constant_voltage_mode()

    def run(self):
        """Thread runner method. Log power consumption in a specified interval"""
        with open(self._logfile, "w") as logfile:
            while self._running:
                res = self._send_and_receive(b"GETD")  # request the current value
                logfile.write(datetime.now().strftime(LOG_TIMESTAMP_FORMAT))
                logfile.write(" ")
                try:
                    logfile.write("{:.1f}V {:.1f}A".format(float(res[:4]) / 100, float(res[4:8]) / 100))
                except ValueError:
                    logger.error("Can not convert string to float: %s", res)
                logfile.write("\n")

                time.sleep(self._loginterval)

    @retry_on_error
    def _is_constant_voltage_mode(self):
        """Get the power output status

        Return true if power supply operates in constant voltage mode"""
        res = self._send_and_receive(b"GETD")  # Get PS Display values of Voltage, Current and Status of CC/CV
        # <voltage>=????
        # <current>=????
        # <status>=0/1 (0=CV, 1=CC)
        # 150016001[CR] = 15V, 16A, CC mode
        return True if not int(res[8:9]) else False

    @retry_on_error
    def _get_max_voltage_and_current(self):
        """Get maximum Voltage and output Current from PSU"""
        self._bare_get_max_voltage_and_current()

    def _bare_get_max_voltage_and_current(self):  # pylint: disable=invalid-name
        """Get maximum Voltage and output Current from PSU without retries"""
        res = self._send_and_receive(b"GMAX")
        # <voltage>=???
        # <current>=???
        # 180200[CR] = 18.0V, 20.0A
        return float(res[:2]), float(res[3:5])

    def _preset_constant_voltage_mode(self):
        """Sets PSU into constant voltage mode if:
        current_preset_value or and over_current_protection_value == 0,
        current_preset_value > over_current_protection_value and
        they both ! = self.max_supported_current
        """
        over_current_protection_value = self.current_max
        current_preset_value = self.current_preset

        if all(
            [
                current_preset_value and over_current_protection_value,
                over_current_protection_value >= current_preset_value,
                over_current_protection_value == self.max_supported_current,
                current_preset_value == self.max_supported_current,
            ]
        ):
            return

        logger.info("PSU in unpredictable state. Trying to recover")
        self.enabled = False
        self.current_max = self.max_supported_current
        self.current_preset = self.max_supported_current

    @property
    @retry_on_error
    def voltage(self):
        """Get output Voltage"""
        res = self._send_and_receive(b"GETD")  # Get PS Display values of Voltage, Current and Status of CC/CV
        # <voltage>=????
        # <current>=????
        # <status>=0/1 (0=CV, 1=CC)
        # 150016001[CR] = 15V, 16A, CC mode
        return float(res[:4]) / 100

    @property
    @retry_on_error
    def voltage_preset(self):
        """Preset output Voltage"""
        res = self._send_and_receive(b"GETS")  # Get PS preset Voltage & Current value
        # <voltage>=???
        # <current>=???
        # 150180[CR] = 15.0V, 18.0A
        return float(res[:3]) / 10

    @voltage_preset.setter
    @retry_on_error
    def voltage_preset(self, voltage):
        """Set preset output Voltage"""
        assert_if_in_interval(
            voltage,
            self.VOLTAGE_MIN,
            self.max_supported_voltage,
            "Voltage for {} must be in range {}-{}V".format(self.MODEL, self.VOLTAGE_MIN, self.max_supported_voltage),
        )
        # Preset Voltage value
        # <voltage>=???
        # VOLT127[CR] = 12.7V
        command = "{:03}".format(int(voltage * 10))
        process_command = build_command(command)
        self._send_and_receive(b"VOLT", process_command, b"OK")

    @property
    @retry_on_error
    def voltage_max(self):
        """Get maximum output Voltage"""
        res = self._send_and_receive(b"GOVP")  # Get preset upper limit of output Voltage
        # <voltage>=???
        # 111[CR] = 11.1V
        return float(res[:3]) / 10

    @voltage_max.setter
    @retry_on_error
    def voltage_max(self, voltage):
        """Set maximum output Voltage"""
        assert_if_in_interval(
            voltage,
            self.VOLTAGE_MIN,
            self.max_supported_voltage,
            "Voltage for {} must be in range {}-{}V".format(self.MODEL, self.VOLTAGE_MIN, self.max_supported_voltage),
        )
        # Preset upper limit of output Voltage
        # <voltage>=???
        # SOVP151[CR] = 15.1V
        command = "{:03}".format(int(voltage * 10))
        process_command = build_command(command)
        self._send_and_receive(b"SOVP", process_command, b"OK")

    @property
    @retry_on_error
    def current(self):
        """Get output Current"""
        res = self._send_and_receive(b"GETD")  # Get PS Display values of Voltage, Current and Status of CC/CV
        # <voltage>=????
        # <current>=????
        # <status>=0/1 (0=CV, 1=CC)
        # 150016001[CR] = 15V, 16A, CC mode
        return float(res[4:8]) / 100

    @property
    @retry_on_error
    def current_preset(self):
        """Preset output Current"""
        res = self._send_and_receive(b"GETS")  # Get PS preset Voltage & Current value
        # <voltage>=???
        # <current>=???
        # 150180[CR] = 15.0V, 18.0A
        return float(res[3:6]) / 10

    @current_preset.setter
    @retry_on_error
    def current_preset(self, current):
        """Set preset output Current"""
        assert_if_in_interval(
            current,
            0,
            self.max_supported_current,
            "Maximum Current for {} must be in range 0>value<={}A".format(self.MODEL, self.max_supported_current),
        )
        # Preset Current value
        # <current>=???
        # CURR120[CR] = 12.0A
        command = "{:03}".format(int(current * 10))
        process_command = build_command(command)
        self._send_and_receive(b"CURR", process_command, b"OK")

    @property
    @retry_on_error
    def current_max(self):
        """Get maximum output Current"""
        res = self._send_and_receive(b"GOCP")  # Get preset upper limit of output Current
        # <current>=???
        # 111[CR] = 11.1A
        return float(res[:3]) / 10

    @current_max.setter
    @retry_on_error
    def current_max(self, current):
        """Set maximum output Current"""
        assert_if_in_interval(
            current,
            0,
            self.max_supported_current,
            "Maximum Current for {} must be in range 0>value<={}A".format(self.MODEL, self.max_supported_current),
        )
        # Preset upper limit of output Current
        # <current>=???
        # SOCP151[CR] = 15.1A
        command = "{:03}".format(int(current * 10))
        process_command = build_command(command)
        self._send_and_receive(b"SOCP", process_command, b"OK")

    @property
    def enabled(self):
        """Get the power output status"""
        # return the stored value since there is not protocol support to read
        # the value from the power supply
        return self._output_enabled

    @enabled.setter
    @retry_on_error
    def enabled(self, status):
        """Enable or disable the power output

        Output on/off control
        <ON/OFF>=0 ON, 1 OFF
        SOUT[CR]
        """
        command = "SOUT{}".format("0" if status else "1")
        process_command = build_command(command)
        try:
            self._send_and_receive(process_command)
            self._output_enabled = bool(status)
        except RuntimeError as err:
            self._output_enabled = not bool(status)
            raise err

