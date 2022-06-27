# Copyright (C) 2014. BMW Car IT GmbH. All rights reserved.
"""Power Supply connection and communication protocol"""

from abc import ABCMeta, abstractproperty

from six import with_metaclass


class WrongPowerSupplyError(RuntimeError):
    """Device connected is not supported by the handling class"""

    pass


class PowerSupplyBase(with_metaclass(ABCMeta, object)):  # pylint: disable=no-init
    """Interface definition for the Power Supply HW"""

    @abstractproperty
    def voltage(self):
        """Get output Voltage [V]

        :returns: float
        :raises RuntimeError: if the device responses different than expected
        """

    @abstractproperty
    def voltage_preset(self):
        """Get preset output Voltage [V]

        :return: the preset output Voltage [V]
        :rtype: float
        :raises RuntimeError: if the device responses different than expected
        """

    @abstractproperty
    @voltage_preset.setter
    def voltage_preset(self, voltage):
        """Preset output Voltage

        :param float voltage: preset Voltage [V]
        :raises ValueError: if the requested Voltage is higher then device's physical maximum
        :raises RuntimeError: if the device responses different than expected
        """

    @abstractproperty
    def voltage_max(self):
        """Get maximum output Voltage [V]

        :return: the maximum output Voltage [V]
        :rtype: float
        :raises RuntimeError: if the device responses different than expected
        """

    @abstractproperty
    @voltage_max.setter
    def voltage_max(self, voltage):
        """Set maximum output Voltage

        :param float voltage: maximum Voltage [V]
        :raises ValueError: if the requested Voltage is higher then device's physical maximum
        :raises RuntimeError: if the device responses different than expected
        """

    @abstractproperty
    def current(self):
        """Get output Current [A]

        :return: the output Current [A]
        :rtype: float
        :raises RuntimeError: if the device responses different than expected
        """

    @abstractproperty
    def current_preset(self):
        """Get preset output Current [A]

        :return: the preset output Current [A]
        :rtype: float
        :raises RuntimeError: if the device responses different than expected
        """

    @abstractproperty
    @current_preset.setter
    def current_preset(self, current):
        """Preset output Current

        :param float current: preset Current [A]
        :raises ValueError: if the requested Current is higher then device's physical maximum
        :raises RuntimeError: if the device responses different than expected
        """

    @abstractproperty
    def current_max(self):
        """Get maximum output Current [A]

        :return: the maximum output Current [A]
        :rtype: float
        :raises RuntimeError: if the device responses different than expected
        """

    @abstractproperty
    @current_max.setter
    def current_max(self, current):
        """Set maximum output Current

        :param float current: preset maximum Current [A]
        :raises ValueError: if the requested Current is higher then device's physical maximum
        :raises RuntimeError: if the device responses different than expected
        """

    @abstractproperty
    def enabled(self):
        """Enable or disable the power output

        :return: output power status
        :rtype: bool
        :raises RuntimeError: if the device responses different than expected
        """

    @abstractproperty
    @enabled.setter
    def enabled(self, status):
        """Enable or disable the power output

        :param bool status: output power status
        :raises RuntimeError: if the device responses different than expected
        """

