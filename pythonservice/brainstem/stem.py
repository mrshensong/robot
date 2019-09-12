# Copyright (c) 2018 Acroname Inc. - All Rights Reserved
#
# This file is part of the BrainStem (tm) package which is released under MIT.
# See file LICENSE or go to https://acroname.com for full license details.

"""
Provides specific module instances, and entity functionality.

The Module and Entity classes contained in this module provide the core API functionality for all of the Brainstem
modules. For more information about possible entities please see the
`Entity`_ section of the `Acroname BrainStem Reference`_

.. _Entity:
    https://acroname.com/reference/entities

.. _Acroname BrainStem Reference:
    https://acroname.com/reference
"""
import struct
import warnings
import functools

from . import _BS_C, str_or_bytes_to_byte_list, convert_int_args_to_bytes
from .module import Module, Entity
from .link import Spec
from .result import Result
from . import defs


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        # warnings.simplefilter('always', DeprecationWarning) #turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning, stacklevel=2)
        # warnings.simplefilter('default', DeprecationWarning) #reset filter
        return func(*args, **kwargs)

    return new_func


class EtherStem(Module):
    """ Concrete Module implementation for 40Pin EtherStem modules

        EtherStem modules contain the following entities:
            * system
            * analog[0-3]
            * app[0-3]
            * clock
            * digital[0-14]
            * i2c[0-1]
            * pointer[0-3]
            * servo[0-7]
            * store[0-2]
            * timer[0-7]

        Useful Constants:
            * BASE_ADDRESS (2)
            * NUMBER_OF_STORES (3)
            * NUMBER_OF_INTERNAL_SLOTS (12)
            * NUMBER_OF_RAM_SLOTS (1)
            * NUMBER_OF_SD_SLOTS (255)
            * NUMBER_OF_ANALOGS (4)
            * DAC_ANALOG_INDEX (3)
            * FIXED_DAC_ANALOG (False)
            * NUMBER_OF_DIGITALS (15)
            * NUMBER_OF_I2C (2)
            * NUMBER_OF_POINTERS (4)
            * NUMBER_OF_TIMERS (8)
            * NUMBER_OF_APPS (4)
            * NUMBER_OF_SERVOS (8)
            * NUMBER_OF_SERVO_OUTPUTS (4)
            * NUMBER_OF_SERVO_INPUTS (4)

    """

    BASE_ADDRESS = 2
    NUMBER_OF_STORES = 3
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_SD_SLOTS = 255
    NUMBER_OF_ANALOGS = 4
    DAC_ANALOG_INDEX = 3
    FIXED_DAC_ANALOG = False
    NUMBER_OF_DIGITALS = 15
    NUMBER_OF_I2C = 2
    NUMBER_OF_POINTERS = 4
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    NUMBER_OF_SERVOS = 8
    NUMBER_OF_SERVO_OUTPUTS = 4
    NUMBER_OF_SERVO_INPUTS = 4

    def __init__(self, address=2, enable_auto_networking=True, model=defs.MODEL_ETHERSTEM):
        super(EtherStem, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.analog = [Analog(self, i) for i in range(0, 4)]
        self.app = [App(self, i) for i in range(0, 4)]
        self.clock = Clock(self, 0)
        self.digital = [Digital(self, i) for i in range(0, 15)]
        self.i2c = [I2C(self, i) for i in range(0, 2)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.store = [Store(self, i) for i in range(0, 3)]
        self.timer = [Timer(self, i) for i in range(0, 8)]
        self.servo = [RCServo(self, i) for i in range(0, 8)]

    def connect(self, serial_number, **kwargs):
        return super(EtherStem, self).connect(Spec.TCPIP, serial_number)


class MTMDAQ1(Module):
    """ Concrete Module implementation for MTM-DAQ-1 module

        MTM-DAQ-1 modules contain contain the following entities:
            * system
            * app[0-3]
            * digital[0-1]
            * analog[0-19]
            * i2c[0]
            * pointer[0-3]
            * store[0-1]
            * timer[0-7]

        Useful Constants:
            * BASE_ADDRESS (10)
            * NUMBER_OF_STORES (2)
            * NUMBER_OF_INTERNAL_SLOTS (12)
            * NUMBER_OF_RAM_SLOTS (1)
            * NUMBER_OF_DIGITALS (2)
            * NUMBER_OF_ANALOGS (20)
            * NUMBER_OF_I2C (1)
            * NUMBER_OF_POINTERS (4)
            * NUMBER_OF_TIMERS (8)
            * NUMBER_OF_APPS (4)
            * ANALOG_RANGE_P0V064N0V064 (0)
            * ANALOG_RANGE_P0V64N0V64 (1)
            * ANALOG_RANGE_P0V128N0V128 (2)
            * ANALOG_RANGE_P1V28N1V28 (3)
            * ANALOG_RANGE_P1V28N0V0 (4)
            * ANALOG_RANGE_P0V256N0V256 (5)
            * ANALOG_RANGE_P2V56N2V56 (6)
            * ANALOG_RANGE_P2V56N0V0 (7)
            * ANALOG_RANGE_P0V512N0V512 (8)
            * ANALOG_RANGE_P5V12N5V12 (9)
            * ANALOG_RANGE_P5V12N0V0 (10)
            * ANALOG_RANGE_P1V024N1V024 (11)
            * ANALOG_RANGE_P10V24N10V24 (12)
            * ANALOG_RANGE_P10V24N0V0 (13)
            * ANALOG_RANGE_P2V048N0V0 (14)
            * ANALOG_RANGE_P4V096N0V0 (15)
    """

    BASE_ADDRESS = 10
    NUMBER_OF_STORES = 2
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_DIGITALS = 2
    NUMBER_OF_ANALOGS = 20
    NUMBER_OF_I2C = 1
    NUMBER_OF_POINTERS = 4
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    ANALOG_RANGE_P0V064N0V064 = 0
    ANALOG_RANGE_P0V64N0V64 = 1
    ANALOG_RANGE_P0V128N0V128 = 2
    ANALOG_RANGE_P1V28N1V28 = 3
    ANALOG_RANGE_P1V28N0V0 = 4
    ANALOG_RANGE_P0V256N0V256 = 5
    ANALOG_RANGE_P2V56N2V56 = 6
    ANALOG_RANGE_P2V56N0V0 = 7
    ANALOG_RANGE_P0V512N0V512 = 8
    ANALOG_RANGE_P5V12N5V12 = 9
    ANALOG_RANGE_P5V12N0V0 = 10
    ANALOG_RANGE_P1V024N1V024 = 11
    ANALOG_RANGE_P10V24N10V24 = 12
    ANALOG_RANGE_P10V24N0V0 = 13
    ANALOG_RANGE_P2V048N0V0 = 14
    ANALOG_RANGE_P4V096N0V0 = 15

    def __init__(self, address=10, enable_auto_networking=True, model=defs.MODEL_MTM_DAQ_1):
        super(MTMDAQ1, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.app = [App(self, i) for i in range(0, 4)]
        self.digital = [Digital(self, i) for i in range(0, 2)]
        self.analog = [Analog(self, i) for i in range(0, 20)]
        self.i2c = [I2C(self, i) for i in range(0, 1)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.store = [Store(self, i) for i in range(0, 2)]
        self.timer = [Timer(self, i) for i in range(0, 8)]

    def connect(self, serial_number, **kwargs):
        return super(MTMDAQ1, self).connect(Spec.USB, serial_number)


class MTMDAQ2(Module):
    """ Concrete Module implementation for MTM-DAQ-2 module

        MTM-DAQ-2 modules contain contain the following entities:
            * system
            * app[0-3]
            * digital[0-1]
            * analog[0-19]
            * i2c[0]
            * pointer[0-3]
            * store[0-1]
            * timer[0-7]

        Useful Constants:
            * BASE_ADDRESS (14)
            * NUMBER_OF_STORES (2)
            * NUMBER_OF_INTERNAL_SLOTS (12)
            * NUMBER_OF_RAM_SLOTS (1)
            * NUMBER_OF_DIGITALS (2)
            * NUMBER_OF_ANALOGS (20)
            * NUMBER_OF_I2C (1)
            * NUMBER_OF_POINTERS (4)
            * NUMBER_OF_TIMERS (8)
            * NUMBER_OF_APPS (4)
            * ANALOG_RANGE_P0V064N0V064 (0)
            * ANALOG_RANGE_P0V64N0V64 (1)
            * ANALOG_RANGE_P0V128N0V128 (2)
            * ANALOG_RANGE_P1V28N1V28 (3)
            * ANALOG_RANGE_P1V28N0V0 (4)
            * ANALOG_RANGE_P0V256N0V256 (5)
            * ANALOG_RANGE_P2V56N2V56 (6)
            * ANALOG_RANGE_P2V56N0V0 (7)
            * ANALOG_RANGE_P0V512N0V512 (8)
            * ANALOG_RANGE_P5V12N5V12 (9)
            * ANALOG_RANGE_P5V12N0V0 (10)
            * ANALOG_RANGE_P1V024N1V024 (11)
            * ANALOG_RANGE_P10V24N10V24 (12)
            * ANALOG_RANGE_P10V24N0V0 (13)
            * ANALOG_RANGE_P2V048N0V0 (14)
            * ANALOG_RANGE_P4V096N0V0 (15)
    """

    BASE_ADDRESS = 10
    NUMBER_OF_STORES = 2
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_DIGITALS = 2
    NUMBER_OF_ANALOGS = 20
    NUMBER_OF_I2C = 1
    NUMBER_OF_POINTERS = 4
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    ANALOG_RANGE_P0V064N0V064 = 0
    ANALOG_RANGE_P0V64N0V64 = 1
    ANALOG_RANGE_P0V128N0V128 = 2
    ANALOG_RANGE_P1V28N1V28 = 3
    ANALOG_RANGE_P1V28N0V0 = 4
    ANALOG_RANGE_P0V256N0V256 = 5
    ANALOG_RANGE_P2V56N2V56 = 6
    ANALOG_RANGE_P2V56N0V0 = 7
    ANALOG_RANGE_P0V512N0V512 = 8
    ANALOG_RANGE_P5V12N5V12 = 9
    ANALOG_RANGE_P5V12N0V0 = 10
    ANALOG_RANGE_P1V024N1V024 = 11
    ANALOG_RANGE_P10V24N10V24 = 12
    ANALOG_RANGE_P10V24N0V0 = 13
    ANALOG_RANGE_P2V048N0V0 = 14
    ANALOG_RANGE_P4V096N0V0 = 15

    def __init__(self, address=10, enable_auto_networking=True, model=defs.MODEL_MTM_DAQ_2):
        super(MTMDAQ2, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.app = [App(self, i) for i in range(0, 4)]
        self.digital = [Digital(self, i) for i in range(0, 2)]
        self.analog = [Analog(self, i) for i in range(0, 20)]
        self.i2c = [I2C(self, i) for i in range(0, 1)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.store = [Store(self, i) for i in range(0, 2)]
        self.timer = [Timer(self, i) for i in range(0, 8)]

    def connect(self, serial_number, **kwargs):
        return super(MTMDAQ2, self).connect(Spec.USB, serial_number)


class MTMEtherStem(Module):
    """ Concrete Module implementation for MTM EtherStem modules

        USBStem modules contain the following entities:
            * system
            * analog[0-3]
            * app[0-3]
            * clock
            * digital[0-14]
            * i2c[0-1]
            * pointer[0-3]
            * servo[0-7]
            * store[0-2]
            * timer[0-7]

        Useful Constants:
            * BASE_ADDRESS (4)
            * NUMBER_OF_STORES (3)
            * NUMBER_OF_INTERNAL_SLOTS (12)
            * NUMBER_OF_RAM_SLOTS (1)
            * NUMBER_OF_SD_SLOTS (255)
            * NUMBER_OF_ANALOGS (4)
            * DAC_ANALOG_INDEX (3)
            * FIXED_DAC_ANALOG (False)
            * NUMBER_OF_DIGITALS (15)
            * NUMBER_OF_I2C (2)
            * NUMBER_OF_POINTERS (4)
            * NUMBER_OF_TIMERS (8)
            * NUMBER_OF_APPS (4)
            * NUMBER_OF_SERVOS (8)
            * NUMBER_OF_SERVO_OUTPUTS (4)
            * NUMBER_OF_SERVO_INPUTS (4)

    """

    BASE_ADDRESS = 4
    NUMBER_OF_STORES = 3
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_SD_SLOTS = 255
    NUMBER_OF_ANALOGS = 4
    DAC_ANALOG_INDEX = 3
    FIXED_DAC_ANALOG = True
    NUMBER_OF_DIGITALS = 15
    NUMBER_OF_I2C = 2
    NUMBER_OF_POINTERS = 4
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    NUMBER_OF_SERVOS = 8
    NUMBER_OF_SERVO_OUTPUTS = 4
    NUMBER_OF_SERVO_INPUTS = 4

    def __init__(self, address=4, enable_auto_networking=True, model=defs.MODEL_MTM_ETHERSTEM):
        super(MTMEtherStem, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.analog = [Analog(self, i) for i in range(0, 4)]
        self.app = [App(self, i) for i in range(0, 4)]
        self.clock = Clock(self, 0)
        self.digital = [Digital(self, i) for i in range(0, 15)]
        self.i2c = [I2C(self, i) for i in range(0, 2)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.store = [Store(self, i) for i in range(0, 3)]
        self.timer = [Timer(self, i) for i in range(0, 8)]
        self.servo = [RCServo(self, i) for i in range(0, 8)]

    def connect(self, serial_number, **kwargs):
        return super(MTMEtherStem, self).connect(Spec.TCPIP, serial_number)


class MTMIOSerial(Module):
    """ Concrete Module implementation for MTM-IO-Serial module

        MTM-IO-SERIAL modules contain contain the following entities:
            * system
            * app[0-3]
            * digital[0-8]
            * i2c[0]
            * pointer[0-3]
            * servo[0-7]
            * store[0-1]
            * temperature
            * timer[0-7]
            * uart[0-3]
            * rail[0-2]

        Useful Constants:
            * BASE_ADDRESS (8)
            * NUMBER_OF_STORES (2)
            * NUMBER_OF_INTERNAL_SLOTS (12)
            * NUMBER_OF_RAM_SLOTS (1)
            * NUMBER_OF_DIGITALS (8)
            * NUMBER_OF_I2C (1)
            * NUMBER_OF_POINTERS (4)
            * NUMBER_OF_TIMERS (8)
            * NUMBER_OF_APPS (4)
            * NUMBER_OF_UART (1)
            * NUMBER_OF_RAILS (3)
            * NUMBER_OF_SERVOS (8)
            * NUMBER_OF_SERVO_OUTPUTS (4)
            * NUMBER_OF_SERVO_INPUTS (4)

            * aMTMIOSERIAL_USB_VBUS_ENABLED (0)
            * aMTMIOSERIAL_USB2_DATA_ENABLED (1)
            * aMTMIOSERIAL_USB_ERROR_FLAG (19)
            * aMTMIOSERIAL_USB2_BOOST_ENABLED (20)

            * aMTMIOSERIAL_ERROR_VBUS_OVERCURRENT (0)

    """

    BASE_ADDRESS = 8
    NUMBER_OF_STORES = 2
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_DIGITALS = 8
    NUMBER_OF_I2C = 1
    NUMBER_OF_POINTERS = 2
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    NUMBER_OF_UART = 4
    NUMBER_OF_RAILS = 3
    NUMBER_OF_SERVOS = 8
    NUMBER_OF_SIGNALS = 5
    NUMBER_OF_SERVO_OUTPUTS = 4
    NUMBER_OF_SERVO_INPUTS = 4

    # Bit defines for port state UInt32
    # use brainstem.BIT(X) from aDefs.h to get bit value.
    # i.e if (state & brainstem.BIT(aMTMIOSERIAL_USB_VBUS_ENABLED))
    aMTMIOSERIAL_USB_VBUS_ENABLED = 0
    aMTMIOSERIAL_USB2_DATA_ENABLED = 1
    aMTMIOSERIAL_USB_ERROR_FLAG = 19
    aMTMIOSERIAL_USB2_BOOST_ENABLED = 20

    # Bit defines for port error UInt32
    # use brainstem.BIT(X) from aDefs.h to get bit value.
    # i.e if (error & brainstem.BIT(aMTMIOSERIAL_ERROR_VBUS_OVERCURRENT))
    aMTMIOSERIAL_ERROR_VBUS_OVERCURRENT = 0

    def __init__(self, address=8, enable_auto_networking=True, model=defs.MODEL_MTM_IOSERIAL):
        super(MTMIOSerial, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.app = [App(self, i) for i in range(0, 4)]
        self.digital = [Digital(self, i) for i in range(0, 8)]
        self.i2c = [I2C(self, i) for i in range(0, 1)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.uart = [UART(self, i) for i in range(0, 4)]
        self.rail = [Rail(self, i) for i in range(0, 3)]
        self.store = [Store(self, i) for i in range(0, 2)]
        self.temperature = Temperature(self, 0)
        self.timer = [Timer(self, i) for i in range(0, 8)]
        self.usb = USB(self, 0)
        self.servo = [RCServo(self, i) for i in range(0, 8)]
        self.signal = [Signal(self, i) for i in range(0, 5)]

    def connect(self, serial_number, **kwargs):
        return super(MTMIOSerial, self).connect(Spec.USB, serial_number)


class MTMPM1(Module):
    """ Concrete Module implementation for MTM-PM-1 module

        MTM-PM-1 modules contain contain the following entities:
            * system
            * app[0-3]
            * digital[0-1]
            * i2c[0]
            * pointer[0-3]
            * store[0-1]
            * timer[0-7]
            * rail[0-1]
            * temperature

        Useful Constants:
            * BASE_ADDRESS (6)
            * NUMBER_OF_STORES (2)
            * NUMBER_OF_INTERNAL_SLOTS (12)
            * NUMBER_OF_RAM_SLOTS (1)
            * NUMBER_OF_DIGITALS (2)
            * NUMBER_OF_I2C (1)
            * NUMBER_OF_POINTERS (4)
            * NUMBER_OF_TIMERS (8)
            * NUMBER_OF_APPS (4)
            * NUMBER_OF_RAILS (2)
            * NUMBER_OF_TEMPERATURES (1)
    """

    BASE_ADDRESS = 6
    NUMBER_OF_STORES = 2
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_DIGITALS = 2
    NUMBER_OF_I2C = 1
    NUMBER_OF_POINTERS = 4
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    NUMBER_OF_RAILS = 2
    NUMBER_OF_TEMPERATURES = 1

    def __init__(self, address=6, enable_auto_networking=True, model=defs.MODEL_MTM_PM_1):
        super(MTMPM1, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.app = [App(self, i) for i in range(0, 4)]
        self.digital = [Digital(self, i) for i in range(0, 2)]
        self.i2c = [I2C(self, i) for i in range(0, 1)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.rail = [Rail(self, i) for i in range(0, 2)]
        self.store = [Store(self, i) for i in range(0, 2)]
        self.timer = [Timer(self, i) for i in range(0, 8)]
        self.temperature = Temperature(self, 0)

    def connect(self, serial_number, **kwargs):
        return super(MTMPM1, self).connect(Spec.USB, serial_number)


class MTMRelay(Module):
    """ Concrete Module implementation for MTM-RELAY module

        MTM-RELAY modules contain contain the following entities:
            * system
            * app[0-3]
            * digital[0-3]
            * i2c[0]
            * pointer[0-3]
            * store[0-1]
            * timer[0-7]
            * relay[0-3]
            * temperature

        Useful Constants:
            * BASE_ADDRESS (12)
            * NUMBER_OF_STORES (2)
            * NUMBER_OF_INTERNAL_SLOTS (12)
            * NUMBER_OF_RAM_SLOTS (1)
            * NUMBER_OF_DIGITALS (4)
            * NUMBER_OF_I2C (1)
            * NUMBER_OF_POINTERS (4)
            * NUMBER_OF_TIMERS (8)
            * NUMBER_OF_APPS (4)
            * NUMBER_OF_RELAYS (4)
    """

    BASE_ADDRESS = 12
    NUMBER_OF_STORES = 2
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_DIGITALS = 4
    NUMBER_OF_I2C = 1
    NUMBER_OF_POINTERS = 4
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    NUMBER_OF_RELAYS = 4

    def __init__(self, address=12, enable_auto_networking=True, model=defs.MODEL_MTM_RELAY):
        super(MTMRelay, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.app = [App(self, i) for i in range(0, 4)]
        self.digital = [Digital(self, i) for i in range(0, 4)]
        self.i2c = [I2C(self, i) for i in range(0, 1)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.relay = [Relay(self, i) for i in range(0, 4)]
        self.store = [Store(self, i) for i in range(0, 2)]
        self.timer = [Timer(self, i) for i in range(0, 8)]

    def connect(self, serial_number, **kwargs):
        return super(MTMRelay, self).connect(Spec.USB, serial_number)


class MTMUSBStem(Module):
    """ Concrete Module implementation for MTM USBStem modules

        MTMUSBStem modules contain the following entities:
            * system
            * analog[0-3]
            * app[0-3]
            * clock
            * digital[0-14]
            * i2c[0-1]
            * pointer[0-3]
            * servo[0-7]
            * store[0-2]
            * timer[0-7]

        Useful Constants:
            * BASE_ADDRESS (4)
            * NUMBER_OF_STORES (3)
            * NUMBER_OF_INTERNAL_SLOTS (12)
            * NUMBER_OF_RAM_SLOTS (1)
            * NUMBER_OF_SD_SLOTS (255)
            * NUMBER_OF_ANALOGS (4)
            * DAC_ANALOG_INDEX (3)
            * FIXED_DAC_ANALOG (True)
            * NUMBER_OF_DIGITALS (15)
            * NUMBER_OF_I2C (2)
            * NUMBER_OF_POINTERS (4)
            * NUMBER_OF_TIMERS (8)
            * NUMBER_OF_APPS (4)
            * NUMBER_OF_SERVOS (8)
            * NUMBER_OF_SERVO_OUTPUTS (4)
            * NUMBER_OF_SERVO_INPUTS (4)

    """

    BASE_ADDRESS = 4
    NUMBER_OF_STORES = 3
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_SD_SLOTS = 255
    NUMBER_OF_ANALOGS = 4
    DAC_ANALOG_INDEX = 3
    FIXED_DAC_ANALOG = True
    NUMBER_OF_DIGITALS = 15
    NUMBER_OF_I2C = 2
    NUMBER_OF_POINTERS = 4
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    NUMBER_OF_SERVOS = 8
    NUMBER_OF_SIGNALS = 5
    NUMBER_OF_SERVO_OUTPUTS = 4
    NUMBER_OF_SERVO_INPUTS = 4

    def __init__(self, address=4, enable_auto_networking=True, model=defs.MODEL_MTM_USBSTEM):
        super(MTMUSBStem, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.analog = [Analog(self, i) for i in range(0, 4)]
        self.app = [App(self, i) for i in range(0, 4)]
        self.clock = Clock(self, 0)
        self.digital = [Digital(self, i) for i in range(0, 15)]
        self.i2c = [I2C(self, i) for i in range(0, 2)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.store = [Store(self, i) for i in range(0, 3)]
        self.timer = [Timer(self, i) for i in range(0, 8)]
        self.servo = [RCServo(self, i) for i in range(0, 8)]
        self.signal = [Signal(self, i) for i in range(0, 5)]

    def connect(self, serial_number, **kwargs):
        return super(MTMUSBStem, self).connect(Spec.USB, serial_number)


class USBCSwitch(Module):
    """ Concrete Module implementation for the USBC-Switch.

        The module contains the USB entity as well as the following.

        Entities:
            * system
            * app[0-3]
            * pointer[0-3]
            * usb
            * mux
            * store[0-1]
            * timer[0-7]
            * equalizer[0-1]

        Useful Constants:
            * BASE_ADDRESS (6)
            * NUMBER_OF_STORES (3)
            * NUMBER_OF_INTERNAL_SLOTS (12)
            * NUMBER_OF_RAM_SLOTS (1)
            * NUMBER_OF_TIMERS (8)
            * NUMBER_OF_APPS (4)
            * NUMBER_OF_POINTERS (4)
            * NUMBER_OF_USB (1)
            * NUMBER_OF_MUXS  (1)
            * NUMBER_OF_EQUALIZERS (2)

            Bit defines for port state UInt32
            use brainstem.BIT(X) from aDefs.h to get bit value.
            i.e if (state & brainstem.BIT(usbPortStateVBUS))
            * usbPortStateVBUS (0)
            * usbPortStateHiSpeed (1)
            * usbPortStateSBU (2)
            * usbPortStateSS1 (3)
            * usbPortStateSS2 (4)
            * usbPortStateCC1 5)
            * usbPortStateCC2 (6)
            * usbPortStateCCFlip (13)
            * usbPortStateSSFlip (14)
            * usbPortStateSBUFlip (15)
            * usbPortStateErrorFlag (19)
            * usbPortStateUSB2Boost (20)
            * usbPortStateUSB3Boost (21)
            * usbPortStateConnectionEstablished (22)
            * usbPortStateCC1Inject (26)
            * usbPortStateCC2Inject (27)
            * usbPortStateCC1Detect (28)
            * usbPortStateCC2Detect (29)
            * usbPortStateCC1LogicState (30)
            * usbPortStateCC2LogicState 31)

            * usbPortStateOff (0)
            * usbPortStateSideA (1)
            * usbPortStateSideB (2)
            * usbPortStateSideUndefined (3)

            * TRANSMITTER_2P0_40mV (0)
            * TRANSMITTER_2P0_60mV (1)
            * TRANSMITTER_2P0_80mV (2)

            * MUX_1db_COM_0db_900mV (0)
            * MUX_0db_COM_1db_900mV (1)
            * MUX_1db_COM_1db_900mV (2)
            * MUX_0db_COM_0db_900mV (3)
            * MUX_0db_COM_0db_1100mV (4)
            * MUX_1db_COM_0db_1100mV (5)
            * MUX_0db_COM_1db_1100mV (6)
            * MUX_2db_COM_2db_1100mV (7)
            * MUX_0db_COM_0db_1300mV (8)

            * LEVEL_1_2P0 (0)
            * LEVEL_2_2P0 (1)

            * LEVEL_1_3P0 (0)
            * LEVEL_2_3P0 (1)
            * LEVEL_3_3P0 (2)
            * LEVEL_4_3P0 (3)
            * LEVEL_5_3P0 (4)
            * LEVEL_6_3P0 (5)
            * LEVEL_7_3P0 (6)
            * LEVEL_8_3P0 (7)
            * LEVEL_9_3P0 (8)
            * LEVEL_10_3P0 (9)
            * LEVEL_11_3P0 (10)
            * LEVEL_12_3P0 (11)
            * LEVEL_13_3P0 (12)
            * LEVEL_14_3P0 (13)
            * LEVEL_15_3P0 (14)
            * LEVEL_16_3P0 (15)

            * EQUALIZER_CHANNEL_BOTH (0)
            * EQUALIZER_CHANNEL_MUX (1)
            * EQUALIZER_CHANNEL_COMMON (2)
    """

    BASE_ADDRESS = 6
    NUMBER_OF_STORES = 2
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    NUMBER_OF_POINTERS = 4
    NUMBER_OF_USB = 1
    NUMBER_OF_MUXS = 1
    NUMBER_OF_EQUALIZERS = 2

    # Bit defines for port state UInt32
    # use brainstem.BIT(X) from aDefs.h to get bit value.
    # i.e if (state & brainstem.BIT(usbPortStateVBUS))
    usbPortStateVBUS = 0
    usbPortStateHiSpeed = 1
    usbPortStateSBU = 2
    usbPortStateSS1 = 3
    usbPortStateSS2 = 4
    usbPortStateCC1 = 5
    usbPortStateCC2 = 6
    usbPortStateCCFlip = 13
    usbPortStateSSFlip = 14
    usbPortStateSBUFlip = 15
    usbPortStateErrorFlag = 19
    usbPortStateUSB2Boost = 20
    usbPortStateUSB3Boost = 21
    usbPortStateConnectionEstablished = 22
    usbPortStateCC1Inject = 26
    usbPortStateCC2Inject = 27
    usbPortStateCC1Detect = 28
    usbPortStateCC2Detect = 29
    usbPortStateCC1LogicState = 30
    usbPortStateCC2LogicState = 31

    # State defines for 2 bit orientation state elements.
    usbPortStateOff = 0
    usbPortStateSideA = 1
    usbPortStateSideB = 2
    usbPortStateSideUndefined = 3

    #2.0 Equalizer Transmitter defines
    TRANSMITTER_2P0_40mV = 0
    TRANSMITTER_2P0_60mV = 1
    TRANSMITTER_2P0_80mV = 2

    #3.0 Equalizer Transmitter defines.
    MUX_1db_COM_0db_900mV = 0
    MUX_0db_COM_1db_900mV = 1
    MUX_1db_COM_1db_900mV = 2
    MUX_0db_COM_0db_900mV = 3
    MUX_0db_COM_0db_1100mV = 4
    MUX_1db_COM_0db_1100mV = 5
    MUX_0db_COM_1db_1100mV = 6
    MUX_2db_COM_2db_1100mV = 7
    MUX_0db_COM_0db_1300mV = 8

    #2.0 Equalizer Receiver defines.
    LEVEL_1_2P0 = 0
    LEVEL_2_2P0 = 1

    # 3.0 Equalizer Receiver defines.
    LEVEL_1_3P0 = 0
    LEVEL_2_3P0 = 1
    LEVEL_3_3P0 = 2
    LEVEL_4_3P0 = 3
    LEVEL_5_3P0 = 4
    LEVEL_6_3P0 = 5
    LEVEL_7_3P0 = 6
    LEVEL_8_3P0 = 7
    LEVEL_9_3P0 = 8
    LEVEL_10_3P0 = 9
    LEVEL_11_3P0 = 10
    LEVEL_12_3P0 = 11
    LEVEL_13_3P0 = 12
    LEVEL_14_3P0 = 13
    LEVEL_15_3P0 = 14
    LEVEL_16_3P0 = 15

    #Equalizer Channels
    EQUALIZER_CHANNEL_BOTH = 0
    EQUALIZER_CHANNEL_MUX = 1
    EQUALIZER_CHANNEL_COMMON = 2

    def __init__(self, address=6, enable_auto_networking=True, model=defs.MODEL_USB_C_SWITCH):
        super(USBCSwitch, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.app = [App(self, i) for i in range(0, 4)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.usb = USB(self, 0)
        self.store = [Store(self, i) for i in range(0, 2)]
        self.timer = [Timer(self, i) for i in range(0, 8)]
        self.mux = Mux(self, 0)
        self.equalizer = [Equalizer(self, i) for i in range(0, 2)]

    def connect(self, serial_number, **kwargs):
        return super(USBCSwitch, self).connect(Spec.USB, serial_number)

    @staticmethod
    def set_usbPortStateCOM_ORIENT_STATUS(var, state):
        return (var & ~(3 << 7)) | (state << 7)

    @staticmethod
    def get_usbPortStateCOM_ORIENT_STATUS(var):
        return (var & (3 << 7)) >> 7

    @staticmethod
    def set_usbPortStateMUX_ORIENT_STATUS(var, state):
        return (var & ~(3 << 9)) | (state << 9)

    @staticmethod
    def get_usbPortStateMUX_ORIENT_STATUS(var):
        return (var & (3 << 9)) >> 9

    @staticmethod
    def set_usbPortStateSPEED_STATUS(var, state):
        return (var & ~(3 << 11)) | (state << 11)

    @staticmethod
    def get_usbPortStateSPEED_STATUS(var):
        return (var & (3 << 11)) >> 11

    @staticmethod
    def set_usbPortStateDaughterCard(var, state):
        return (var & ~(7 << 16)) | (state << 16)

    @staticmethod
    def get_usbPortStateDaughterCard(var):
        return (var & (7 << 16)) >> 16


class USBHub2x4(Module):
    """ Concrete Module implementation for the USBHub2x4.

        The module contains the USB entity as well as the following.

        Entities:
            * system
            * app[0-3]
            * pointer[0-3]
            * usb
            * mux
            * store[0-1]
            * temperature
            * timer[0-7]

        Useful Constants:
            * BASE_ADDRESS (6)
            * NUMBER_OF_STORES (3)
            * NUMBER_OF_INTERNAL_SLOTS (12)
            * NUMBER_OF_RAM_SLOTS (1)
            * NUMBER_OF_TIMERS (8)
            * NUMBER_OF_APPS (4)
            * NUMBER_OF_POINTERS (4)
            * NUMBER_OF_DOWNSTREAM_USB (4)
            * NUMBER_OF_UPSTREAM_USB (2)

            Bit defines for port error UInt32
            use brainstem.BIT(X) from aDefs.h to get bit value.
            i.e if (error & brainstem.BIT(aUSBHUB2X4_USB_VBUS_ENABLED))
            * aUSBHUB2X4_USB_VBUS_ENABLED (0)
            * aUSBHUB2X4_USB2_DATA_ENABLED (1)
            * aUSBHUB2X4_USB_ERROR_FLAG (19)
            * aUSBHUB2X4_USB2_BOOST_ENABLED (20)
            * aUSBHUB2X4_DEVICE_ATTACHED (23)
            * aUSBHUB2X4_CONSTANT_CURRENT (24)

            Bit defines for port error UInt32
            use brainstem.BIT(X) from aDefs.h to get bit value.
            i.e if (error & brainstem.BIT(aUSBHUB3P_ERROR_VBUS_OVERCURRENT))
            * aUSBHUB2X4_ERROR_VBUS_OVERCURRENT (0)
            * aUSBHUB2X4_ERROR_OVER_TEMPERATURE (3)
            * aUSBHub2X4_ERROR_DISCHARGE (4)
    """

    BASE_ADDRESS = 6
    NUMBER_OF_STORES = 2
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    NUMBER_OF_POINTERS = 4
    NUMBER_OF_DOWNSTREAM_USB = 4
    NUMBER_OF_UPSTREAM_USB = 2

    # Bit defines for port state UInt32
    # use brainstem.BIT(X) from aDefs.h to get bit value.
    # i.e if (state & brainstem.BIT(aUSBHUB2X4_USB_VBUS_ENABLED))
    aUSBHUB2X4_USB_VBUS_ENABLED = 0
    aUSBHUB2X4_USB2_DATA_ENABLED = 1
    aUSBHUB2X4_USB_ERROR_FLAG = 19
    aUSBHUB2X4_USB2_BOOST_ENABLED = 20
    aUSBHUB2X4_DEVICE_ATTACHED = 23
    aUSBHUB2X4_CONSTANT_CURRENT = 24

    # Bit defines for port error UInt32
    # use brainstem.BIT(X) from aDefs.h to get bit value.
    # i.e if (error & brainstem.BIT(aUSBHUB2X4_ERROR_VBUS_OVERCURRENT))
    aUSBHUB2X4_ERROR_VBUS_OVERCURRENT = 0
    aUSBHUB2X4_ERROR_OVER_TEMPERATURE = 3
    aUSBHub2X4_ERROR_DISCHARGE = 4

    def __init__(self, address=6, enable_auto_networking=True, model=defs.MODEL_USBHUB_2X4):
        super(USBHub2x4, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.app = [App(self, i) for i in range(0, 4)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.usb = USB(self, 0)
        self.store = [Store(self, i) for i in range(0, 2)]
        self.temperature = Temperature(self, 0)
        self.timer = [Timer(self, i) for i in range(0, 8)]

    def connect(self, serial_number, **kwargs):
        return super(USBHub2x4, self).connect(Spec.USB, serial_number)


class USBHub3p(Module):
    """ Concrete Module implementation for the USBHub3p.

        The module contains the USB entity as well as the following.

        Entities:
            * system
            * app[0-3]
            * pointers[0-3]
            * usb
            * store[0-1]
            * temperature
            * timer[0-7]

        Useful Constants:
            * BASE_ADDRESS (6)
            * NUMBER_OF_STORES (3)
            * NUMBER_OF_INTERNAL_SLOTS (12)
            * NUMBER_OF_RAM_SLOTS (1)
            * NUMBER_OF_TIMERS (8)
            * NUMBER_OF_APPS (4)
            * NUMBER_OF_POINTERS (4)
            * NUMBER_OF_DOWNSTREAM_USB (8)
            * NUMBER_OF_UPSTREAM_USB (2)

            Bit defines for port state UInt32
            use brainstem.BIT(X) from aDefs.h to get bit value.
            i.e if (state & brainstem.BIT(aUSBHUB3P_USB_VBUS_ENABLED))
            * aUSBHUB3P_USB_VBUS_ENABLED (0)
            * aUSBHUB3P_USB2_DATA_ENABLED (1)
            * aUSBHUB3P_USB3_DATA_ENABLED (3)
            * aUSBHUB3P_USB_SPEED_USB2 (11)
            * aUSBHUB3P_USB_SPEED_USB3 (12)
            * aUSBHUB3P_USB_ERROR_FLAG (19)
            * aUSBHUB3P_USB2_BOOST_ENABLED (20)
            * aUSBHUB3P_DEVICE_ATTACHED (23)

            Bit defines for port error UInt32
            use brainstem.BIT(X) from aDefs.h to get bit value.
            i.e if (error & brainstem.BIT(aUSBHUB3P_ERROR_VBUS_OVERCURRENT))
            * aUSBHUB3P_ERROR_VBUS_OVERCURRENT (0)
            * aUSBHUB3P_ERROR_VBUS_BACKDRIVE (1)
            * aUSBHUB3P_ERROR_HUB_POWER (2)
            * aUSBHUB3P_ERROR_OVER_TEMPERATURE (3)

    """

    BASE_ADDRESS = 6
    NUMBER_OF_STORES = 2
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    NUMBER_OF_POINTERS = 4
    NUMBER_OF_DOWNSTREAM_USB = 8
    NUMBER_OF_UPSTREAM_USB = 2

    # Bit defines for port state UInt32
    # use brainstem.BIT(X) from aDefs.h to get bit value.
    # i.e if (state & brainstem.BIT(aUSBHUB3P_USB_VBUS_ENABLED))
    aUSBHUB3P_USB_VBUS_ENABLED = 0
    aUSBHUB3P_USB2_DATA_ENABLED = 1
    aUSBHUB3P_USB3_DATA_ENABLED = 3
    aUSBHUB3P_USB_SPEED_USB2 = 11
    aUSBHUB3P_USB_SPEED_USB3 = 12
    aUSBHUB3P_USB_ERROR_FLAG = 19
    aUSBHUB3P_USB2_BOOST_ENABLED = 20
    aUSBHUB3P_DEVICE_ATTACHED = 23

    # Bit defines for port error UInt32
    # use brainstem.BIT(X) from aDefs.h to get bit value.
    # i.e if (error & brainstem.BIT(aUSBHUB3P_ERROR_VBUS_OVERCURRENT))
    aUSBHUB3P_ERROR_VBUS_OVERCURRENT = 0
    aUSBHUB3P_ERROR_VBUS_BACKDRIVE = 1
    aUSBHUB3P_ERROR_HUB_POWER = 2
    aUSBHUB3P_ERROR_OVER_TEMPERATURE = 3

    def __init__(self, address=6, enable_auto_networking=True, model=defs.MODEL_USBHUB_3P):
        super(USBHub3p, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.app = [App(self, i) for i in range(0, 4)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.usb = USB(self, 0)
        self.store = [Store(self, i) for i in range(0, 2)]
        self.temperature = Temperature(self, 0)
        self.timer = [Timer(self, i) for i in range(0, 8)]

    def connect(self, serial_number, **kwargs):
        return super(USBHub3p, self).connect(Spec.USB, serial_number)


class USBStem(Module):
    """ Concrete Module implementation for 40Pin USBStem modules

        USBStem modules contain contain the following entities:
            * system
            * analog[0-3]
            * app[0-3]
            * clock
            * digital[0-14]
            * i2c[0-1]
            * pointer[0-3]
            * servo[0-7]
            * store[0-2]
            * timer[0-7]

    Useful Constants:
        * BASE_ADDRESS (2)
        * NUMBER_OF_STORES (3)
        * NUMBER_OF_INTERNAL_SLOTS (12)
        * NUMBER_OF_RAM_SLOTS (1)
        * NUMBER_OF_SD_SLOTS (255)
        * NUMBER_OF_ANALOGS (4)
        * DAC_ANALOG_INDEX (3)
        * FIXED_DAC_ANALOG (False)
        * NUMBER_OF_DIGITALS (15)
        * NUMBER_OF_I2C (2)
        * NUMBER_OF_POINTERS (4)
        * NUMBER_OF_TIMERS (8)
        * NUMBER_OF_APPS (4)
        * NUMBER_OF_SERVOS (8)
        * NUMBER_OF_SERVO_OUTPUTS (4)
        * NUMBER_OF_SERVO_INPUTS (4)

    """

    BASE_ADDRESS = 2
    NUMBER_OF_STORES = 3
    NUMBER_OF_INTERNAL_SLOTS = 12
    NUMBER_OF_RAM_SLOTS = 1
    NUMBER_OF_SD_SLOTS = 255
    NUMBER_OF_ANALOGS = 4
    DAC_ANALOG_INDEX = 3
    FIXED_DAC_ANALOG = False
    NUMBER_OF_DIGITALS = 15
    NUMBER_OF_I2C = 2
    NUMBER_OF_POINTERS = 4
    NUMBER_OF_TIMERS = 8
    NUMBER_OF_APPS = 4
    NUMBER_OF_SERVOS = 8
    NUMBER_OF_SERVO_OUTPUTS = 4
    NUMBER_OF_SERVO_INPUTS = 4

    def __init__(self, address=2, enable_auto_networking=True, model=defs.MODEL_USBSTEM):
        super(USBStem, self).__init__(address, enable_auto_networking, model)
        self.system = System(self, 0)
        self.analog = [Analog(self, i) for i in range(0, 4)]
        self.app = [App(self, i) for i in range(0, 4)]
        self.clock = Clock(self, 0)
        self.digital = [Digital(self, i) for i in range(0, 15)]
        self.i2c = [I2C(self, i) for i in range(0, 2)]
        self.pointer = [Pointer(self, i) for i in range(0, 4)]
        self.store = [Store(self, i) for i in range(0, 3)]
        self.timer = [Timer(self, i) for i in range(0, 8)]
        self.servo = [RCServo(self, i) for i in range(0, 8)]

    def connect(self, serial_number, **kwargs):
        return super(USBStem, self).connect(Spec.USB, serial_number)


class System(Entity):
    """ Acccess system controls configuration and information.

        The system entity is available on all BrainStem modules, and provides
        access to system information such as module, router and serial number,
        as well as control over the user LED, and information such as the system
        input voltage.

        Useful Constants:
            * BOOT_SLOT_DISABLE (255)
    """

    BOOT_SLOT_DISABLE = 255

    def __init__(self, module, index):
        """System Entity Initializer"""
        super(System, self).__init__(module, _BS_C.cmdSYSTEM, index)

    def setModuleSoftwareOffset(self, value):
        """Set the software address offset.

            The module software offset is added to the base module address, and
            potentially a hardware offset to determine the final calculated address
            the module uses on the brainstem network. You must save and reset
            the module for this change to become effective.

            Warning:
                changing the module address may cause the module to "drop off"
                the BrainStem network if the module is also the router. Please
                review the BrainStem network fundamentals before modifying the
                module address.

           args:
                value (int): The module address offset.

           Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.systemModuleSoftwareOffset, value)

    def getModule(self):
        """ Get the address the module uses on the BrainStem network.

            Return:
                Result: Result object, containing NO_ERROR and the current module address
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemModule)

    def getModuleBaseAddress(self):
        """ Get the base address the module.

            The software and hardware addresses are added to the base address
            to produce the effective module address.

            Return:
                Result: Result object, containing NO_ERROR and the current module address
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemModuleBaseAddress)

    def getModuleSoftwareOffset(self):
        """ Get the module address software offset.

            The address offset that is added to the module base address, and
            potentially the hardware offset to produce the module effective address.

            Return:
                Result: Result object, containing NO_ERROR and the current module address
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemModuleSoftwareOffset)

    def setRouter(self, value):
        """ Set the router address the module uses to communicate with the host.

            Warning:
                Changing the router address may cause the module to "drop off"
                the BrainStem network if the new router address is not in use by
                a BrainStem module. Please review the BrainStem network
                fundamentals before modifying the router address.

           args:
                value (int): The module address of the router module on the network.

           Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.systemRouter, value)

    def getRouter(self):
        """ Get the router address the module uses to communicate with the host.

            Return:
                Result: Result object, containing NO_ERROR and the current router address
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemRouter)

    def getRouterAddressSetting(self):
        """ Get the router address setting saved in the module.

            This setting may be different from the effective router if the router
            has been set and saved but no reset has been made.

            Return:
                Result: Result object, containing NO_ERROR and the current router address
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemRouterAddressSetting)

    def setHBInterval(self, value):
        """ Set the delay between heartbeat packets.

            For link modules, these heartbeat are sent to the host.
            For non-link modules, these heartbeats are sent to the router address.
            Interval values are in 25.6 millisecond increments Valid values are
            1-255; default is 10 (256 milliseconds).

            args:
                value (int): Heartbeat interval settings.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.systemHBInterval, value)

    def getHBInterval(self):
        """ Get the delay between heartbeat packets.

            For link modules, these heartbeat are sent to the host.
            For non-link modules, these heartbeats are sent to the router address.
            Interval values are in 25.6 millisecond increments.

            return:
                Result: Result object, containing NO_ERROR and the Heartbeat interval
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemHBInterval)

    def setLED(self, value):
        """ Set the system LED state.

            Most modules have a blue system LED. Refer to the module
            datasheet for details on the system LED location and color.

            args:
                value (int): LED State setting.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.systemLED, value)

    def getLED(self):
        """ Get the system LED state.

            Most modules have a blue system LED. Refer to the module
            datasheet for details on the system LED location and color.

            return:
                Result: Result object, containing NO_ERROR and the LED State
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemLED)

    def setBootSlot(self, value):
        """ Set a store slot to be mapped when the module boots.

            The boot slot will be mapped after the module boots from powers up,
            receives a reset signal on its reset input, or is issued a software
            reset command. Set the slot to 255 to disable mapping on boot.

            args:
                value (int): The slot number in aSTORE_INTERNAL to be marked
                             as a boot slot.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.systemBootSlot, value)

    def getBootSlot(self):
        """ Get the store slot which is mapped when the module boots.

            return:
                Result: Result object, containing NO_ERROR and slot number
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemBootSlot)

    def getVersion(self):
        """ Get the modules firmware version number.

            The version number is packed into the return value. Utility functions
            in the Version module can unpack the major, minor and patch numbers from
            the version number which looks like M.m.p.

            return:
                Result: Result object, containing NO_ERROR packed version number
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemVersion)

    def getModel(self):
        """ Get the module's model enumeration.

            A subset of the possible model enumerations is defined in
            aProtocolDefs.h under "BrainStem model codes". Other codes are be
            used by Acroname for proprietary module types.

            return:
                Result: Result object, containing NO_ERROR and model number
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemModel)

    def getSerialNumber(self):
        """ Get the module's serial number.

            The serial number is a unique 32bit integer which is usually
            communicated in hexadecimal format.

            return:
                Result: Result object, containing NO_ERROR and serial number
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemSerialNumber)

    def save(self):
        """ Save the system operating parameters to the persistent module flash memory.

            Operating parameters stored in the system flash will be loaded after the module
            reboots. Operating parameters include: heartbeat interval, module address,
            module router address

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.call_UEI(_BS_C.systemSave)

    def reset(self):
        """ Reset the system.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.call_UEI(_BS_C.systemReset)

    def logEvents(self):
        """ Save system log entries to slot defined by module.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.call_UEI(_BS_C.systemLogEvents)

    def getInputVoltage(self):
        """ Get the module's input voltage.

            return:
                Result: Result object, containing NO_ERROR and input voltage
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemInputVoltage)

    def getInputCurrent(self):
        """ Get the module's input current.

            return:
                Result: Result object, containing NO_ERROR and input current
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemInputCurrent)

    def getModuleHardwareOffset(self):
        """ Get the module address hardware offset.

            This is added to the base address to allow the module address to be
            configured in hardware. Not all modules support the hardware module
            address offset. Refer to the module datasheet.

            return:
                Result: Result object, containing NO_ERROR and module offset
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemModuleHardwareOffset)

    def getUptime(self):
        """ Get accumulated system uptime.

            This is the total time the system has been powered up with
            the firmware running. The returned uptime is a count of minutes
            of uptime, or may be a module dependent counter.

            return:
                Result: Result object, containing NO_ERROR and uptime in minutes
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemUptime)

    def getMaximumTemperature(self):
        """ Get the maximum temperature the system has recorded.

            This is the maximum temperature in micro-C recorded every minute.

            return:
                Result: Result object, containing NO_ERROR and max temperature in micro-C
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.systemMaxTemperature)

    def routeToMe(self, value):
        """ Enables/Disables the route to me function.

            This function allows for easy networking of BrainStem modules.
            Enabling (1) this function will send an I2C General Call to all devices
            on the network and request that they change their router address
            to the of the calling device. Disabling (0) will cause all devices
            on the BrainStem network to revert to their default address.

            args:
                value (int): Enable or disable of the route to me function 1 = enable.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.systemRouteToMe, value)


class Analog(Entity):
    """ The AnalogClass is the interface to analog entities on BrainStem modules.

        Analog entities may be configured as a input or output depending on hardware
        capabilities. Some modules are capable of providing actual voltage readings,
        while other simply return the raw analog-to-digital converter (ADC) output
        value. The resolution of the voltage or number of useful bits is also
        hardware dependent.

        Useful constants:
            * CONFIGURATION_INPUT (0)
            * CONFIGURATION_OUTPUT (1)
            * HERTZ_MINIMUM (7,000)
            * HERTZ_MAXIMUM (200,000)
            * BULK_CAPTURE_IDLE (0)
            * BULK_CAPTURE_PENDING (1)
            * BULK_CAPTURE_FINISHED (2)
            * BULK_CAPTURE_ERROR (3)

    """

    CONFIGURATION_INPUT = 0
    CONFIGURATION_OUTPUT = 1
    HERTZ_MINIMUM = 7000
    HERTZ_MAXIMUM = 200000
    BULK_CAPTURE_IDLE = 0
    BULK_CAPTURE_PENDING = 1
    BULK_CAPTURE_FINISHED = 2
    BULK_CAPTURE_ERROR = 3

    def __init__(self, module, index):
        """ Analog Entity Initializer """
        super(Analog, self).__init__(module, _BS_C.cmdANALOG, index)

    def setConfiguration(self, value):
        """ Set the analog configuration.

            Some analogs can be configured as DAC outputs. Please see your module
            datasheet to determine which analogs can be configured as DAC.

            Param:
                value (int): Set 1 for output 0 for input. Default configuration
                is input.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.analogConfiguration, value)

    def getConfiguration(self):
        """ Get the analog configuration.

            If the configuraton is 1 the analog is configured as an output, if
            the configuration is 0, the analog is set as an input.

            return:
                Result: Result object, containing NO_ERROR and analog configuration
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.analogConfiguration)

    def setRange(self, value):
        """ Set the range of an analog input.

            Set a value corresponding to a discrete range option.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.analogRange, value)

    def getRange(self):
        """ Get the range setting of an analog input

            Get a value corresponding to a discrete range option.

            return:
                Result: Result object, containing NO_ERROR and analog range
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.analogRange)

    def setValue(self, value):
        """ Set the value of an analog output (DAC) in bits.

            Set a 16 bit analog set point with 0 corresponding to the negative
            analog voltage reference and 0xFFFF corresponding to the positive
            analog voltage reference.

            Note:
                Not all modules are provide 16 useful bits; the least significant bits
                are discarded. E.g. for a 10 bit DAC, 0xFFC0 to 0x0040 is the useful
                range. Refer to the module's datasheet to determine analog bit
                depth and reference voltage.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI16(_BS_C.analogValue, value)

    def getValue(self):
        """ Get the raw ADC value in bits.

            Get a 16 bit analog set point with 0 corresponding to the negative
            analog voltage reference and 0xFFFF corresponding to the positive
            analog voltage reference.

            Note:
                Not all modules provide 16 useful bits; the least significant bits
                are discarded. E.g. for a 10 bit ADC, 0xFFC0 to 0x0040 is the useful
                range. Refer to the module's datasheet to determine analog bit
                depth and reference voltage.

            return:
                Result: Result object, containing NO_ERROR and analog value
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.analogValue)

    def setVoltage(self, value):
        """ Set the voltage level of an analog output (DAC) in microVolts with
            reference to ground.

            Set a 16 bit signed integer as voltage output (in microVolts).

            Note:
                Voltage range is dependent on the specific DAC channel range.
                See datasheet and setRange for options.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.analogVoltage, value)

    def getVoltage(self):
        """ Get the scaled micro volt value with reference to ground.

            Get a 32 bit signed integer (in microVolts) based on the boards
            ground and reference voltages.

            Note:
                Not all modules provide 32 bits of accuracy; Refer to the module's
                datasheet to determine the analog bit depth and reference voltage.

            return:
                Result: Result object, containing NO_ERROR and microVolts value
                        or a non zero Error code.

        """
        return _BS_SignCheck(self.get_UEI(_BS_C.analogVoltage))

    def setEnable(self, enable):
        """ Set the enable state of an analog output.

            Set a boolean value corresponding to on/off

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.analogEnable, enable)

    def getEnable(self):
        """ Get the enable state an analog output

            Get a boolean value corresponding to on/off

            return:
                Result: Result object, containing NO_ERROR and enable state
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.analogEnable)

    def setBulkCaptureSampleRate(self, value):
        """ Set the sample rate for this analog when bulk capturing.

            Sample rate is set in samples per second (Hertz).

            Minimum Rate: 7,000 Hertz
            Maximum Rate: 200,000 Hertz

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.analogBulkCaptureSampleRate, value)

    def getBulkCaptureSampleRate(self):
        """ Get the current sample rate setting for this analog when bulk capturing.

            Sample rate is in samples per second (Hertz).

            return:
                Result: Result object, containing NO_ERROR and sample rate
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.analogBulkCaptureSampleRate)

    def setBulkCaptureNumberOfSamples(self, value):
        """ Set the number of samples to capture for this analog when bulk capturing.

            Minimum # of Samples: 0
            Maximum # of Samples: (BRAINSTEM_RAM_SLOT_SIZE / 2) = (3FFF / 2) = 1FFF = 8191

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.analogBulkCaptureNumberOfSamples, value)

    def getBulkCaptureNumberOfSamples(self):
        """ Get the current number of samples setting for this analog when bulk capturing.

            return:
                Result: Result object, containing NO_ERROR and sample number
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.analogBulkCaptureNumberOfSamples)

    def initiateBulkCapture(self):
        """ Initiate a BulkCapture on this analog. Captured measurements are stored in the
            module's RAM store (RAM_STORE) slot 0. Data is stored in a contiguous byte array
            with each sample stored in two consecutive bytes, LSB first.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure. When the bulk capture is complete
                getBulkCaptureState() will return either finished or error.
        """
        return self.call_UEI(_BS_C.analogBulkCapture)

    def getBulkCaptureState(self):
        """ Get the current bulk capture state for this analog.

            Possible states of the bulk capture operation are;
            idle = 0
            pending = 1
            finished = 2
            error = 3

            return:
                Result: Result object, containing NO_ERROR and bulk capture state
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.analogBulkCaptureState)


class App(Entity):
    """ The AppClass calls defined app reflexes on brainstem modules.

        Calls a remote procedure defined in an active map file on a brainstem
        module. The remote procedure may return a value or not.
    """

    def __init__(self, module, index):
        """ Clock Entity Initializer """
        super(App, self).__init__(module, _BS_C.cmdAPP, index)

    def execute(self, param):
        """ Execute an App reflex on a module.

            Param:
                param (int): App routine parameter.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.appExecute, param)

    def executeAndWaitForReturn(self, param, msTimeout):
        """ Execute an App reflex on a module, and wait for it to return a
            result.

            Param:
                param (int): App routine parameter.
                msTimeout (int): millisecons to wait for routine to complete.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        self.drain_UEI(_BS_C.appReturn)
        err = self.set_UEI32(_BS_C.appExecute, param)
        if err == Result.NO_ERROR:
            return self.await_UEI_Val(_BS_C.appReturn, msTimeout)
        else:
            return Result(err, None)


class Clock(Entity):
    """ The ClockClass is the interface to the realtime clock.

        For modules that support realtime clocks, this class supports getting
        and setting clock values for year, month, day, hour, minute and second.
    """

    def __init__(self, module, index):
        """ Clock Entity Initializer """
        super(Clock, self).__init__(module, _BS_C.cmdCLOCK, index)

    def setYear(self, year):
        """ Set the current year

            Param:
                value (int): Current 4 digit year.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI16(_BS_C.clockYear, year)

    def getYear(self):
        """ Get the current year

            return:
                Result: Result object, containing NO_ERROR and current year or
                        a non zero Error code.
        """
        return self.get_UEI(_BS_C.clockYear)

    def setMonth(self, month):
        """ Set the current month

            Param:
                value (int): Current 2 digit month.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.clockMonth, month)

    def getMonth(self):
        """ Get the current month

            return:
                Result: Result object, containing NO_ERROR and current month or
                        a non zero Error code.
        """
        return self.get_UEI(_BS_C.clockMonth)

    def setDay(self, day):
        """ Set the current day of the month

            Param:
                value (int): Current 2 digit day.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.clockDay, day)

    def getDay(self):
        """ Get the current day of the month

            return:
                Result: Result object, containing NO_ERROR and current day or
                        a non zero Error code.
        """
        return self.get_UEI(_BS_C.clockDay)

    def setHour(self, hour):
        """ Set the current hour

            Param:
                value (int): Current 2 digit hour.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.clockHour, hour)

    def getHour(self):
        """ Get the current hour

            return:
                Result: Result object, containing NO_ERROR and current hour or
                        a non zero Error code.
        """
        return self.get_UEI(_BS_C.clockHour)

    def setMinute(self, minute):
        """ Set the current minute

            Param:
                value (int): Current 2 digit minute.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.clockMinute, minute)

    def getMinute(self):
        """ Get the current minute

            return:
                Result: Result object, containing NO_ERROR and current minute or
                        a non zero Error code.
        """
        return self.get_UEI(_BS_C.clockMinute)

    def setSecond(self, second):
        """ Set the current second

            Param:
                value (int): Current 2 digit second.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.clockSecond, second)

    def getSecond(self):
        """ Get the current second

            return:
                Result: Result object, containing NO_ERROR and current second or
                        a non zero Error code.
        """
        return self.get_UEI(_BS_C.clockSecond)


class Digital(Entity):
    """ The DigitalClass is the interface to digital entities on BrainStem modules.

        Digital entities have the following 5 possabilities: Digital Input,
        Digital Output, RCServo Input, RCServo Output, and HighZ.
        Other capabilities may be available and not all pins support all
        configurations. Please see the product datasheet.

        Useful Constants:
            * VALUE_LOW (0)
            * VALUE_HIGH (1)
            * CONFIGURATION_INPUT (0)
            * CONFIGURATION_OUTPUT (1)
            * CONFIGURATION_RCSERVO_INPUT (2)
            * CONFIGURATION_RCSERVO_OUTPUT (3)
            * CONFIGURATION_HIGHZ (4)
            * CONFIGURATION_INPUT_PULL_UP (0)
            * CONFIGURATION_INPUT_NO_PULL (4)
            * CONFIGURATION_INPUT_PULL_DOWN (5)
            * CONFIGURATION_SIGNAL_OUTPUT (6)
            * CONFIGURATION_SIGNAL_INPUT (7)
    """

    VALUE_LOW = 0
    VALUE_HIGH = 1
    CONFIGURATION_INPUT = 0
    CONFIGURATION_OUTPUT = 1
    CONFIGURATION_RCSERVO_INPUT = 2
    CONFIGURATION_RCSERVO_OUTPUT = 3
    CONFIGURATION_HIGHZ = 4
    CONFIGURATION_INPUT_PULL_UP = 0
    CONFIGURATION_INPUT_NO_PULL = 4
    CONFIGURATION_INPUT_PULL_DOWN = 5
    CONFIGURATION_SIGNAL_OUTPUT = 6
    CONFIGURATION_SIGNAL_INPUT = 7

    def __init__(self, module, index):
        """Digital Entity initializer"""
        super(Digital, self).__init__(module, _BS_C.cmdDIGITAL, index)

    def setConfiguration(self, configuration):
        """ Set the digital configuration.

            Param:
                configuration (int):
                    * Digital Input: CONFIGURATION_INPUT = 0
                    * Digital Output: CONFIGURATION_OUTPUT = 1
                    * RCServo Input: CONFIGURATION_RCSERVO_INPUT = 2
                    * RCServo Output: CONFIGURATION_RCSERVO_OUTPUT = 3
                    * High Z State: CONFIGURATION_HIGHZ = 4
                    * Digital Input with pull up: CONFIGURATION_INPUT_PULL_UP = 0 (Default)
                    * Digital Input with no pull up or pull down: CONFIGURATION_INPUT_NO_PULL = 4
                    * Digital Input with pull down: CONFIGURATION_INPUT_PULL_DOWN = 5
                    * Digital Signal Output: CONFIGURATION_SIGNAL_OUTPUT = 6
                    * Digital Signal Input: CONFIGURATION_SIGNAL_INPUT = 7


            Return:
                Result.error:
                    Return NO_ERROR on success, or one of the common
                    sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.digitalConfiguration, configuration)

    def getConfiguration(self):
        """ Get the digital configuration.

            If the configuration is 1 the digital is configured as an output, if
            the configuration is 0, the digital is set as an input.

            return:
                Result:
                    Result object, containing NO_ERROR and digital configuration
                    or a non zero Error code.
        """
        return self.get_UEI(_BS_C.digitalConfiguration)

    def setState(self, state):
        """ Set the digital state.

            Param:
                state (int):
                    Set 1 for logic high, set 0 for logic low. configuration
                    must be set to output.

            Return:
                Result.error:
                    Return NO_ERROR on success, or one of the common
                    sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.digitalState, state)

    def getState(self):
        """ Get the digital state.

            A return of 1 indicates the digitial is above the logic high threshold.
            A return of 0 indicates the digital is below the logic low threshold.

            return:
                Result:
                    Result object, containing NO_ERROR and digital state
                    or a non zero Error code.
        """
        return self.get_UEI(_BS_C.digitalState)

    def setStateAll(self, state):
        """ Sets the digital state of all digitals based on the bit mapping.
            Number of digitals varies across BrainStem modules. Refer to then
            datasheet for the capabilities of your module.

            Param:
                state (uint):
                    The state to be set for all digitals in a bit mapped
                    representation. 0 is logic low, 1 is logic high. Where
                    bit 0 = digital 0, bit 1 = digital 1 etc.
                    Configuration must be set to output.

            Return:
                Result.error:
                    Return NO_ERROR on success, or one of the common
                    sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.digitalStateAll, state)

    def getStateAll(self):
        """ Gets the digital state of all digitals in a bit mapped representation.
            Number of digitals varies across BrainStem modules. Refer to then
            datasheet for the capabilities of your module.

            return:
                Result:
                    Result object, containing NO_ERROR and the digital state
                    of all digitals where bit 0 = digital 0 and bit 1 = digital 1 etc.
                    0 = logic low and 1 = logic high.
                    A non zero Error code is returned on error.
        """
        return self.get_UEI(_BS_C.digitalStateAll)


class Equalizer(Entity):
    """ Equalizer Class provides receiver and transmitter gain/boost/emphasis
        settings for some of Acroname's products.  Please see product documentation
        for further details.
    """

    def __init__(self, module, index):
        """ Signal Entity initializer """
        super(Equalizer, self).__init__(module, _BS_C.cmdEQUALIZER, index)

    def setReceiverConfig(self, channel, config):
        """ Sets the receiver configuration for a given channel.

            :param channel: The equalizer receiver channel.
            :param config: Configuration to be applied to the receiver.
            :return: Result.error Return NO_ERROR on success, or one of the common
                    sets of return error codes on failure.
        """
        return self.set_UEI8_with_subindex(_BS_C.equalizerReceiverConfig, channel, config)

    def getReceiverConfig(self, channel):
        """ Gets the receiver configuration for a given channel.

            :param channel: The equalizer receiver channel.
            :return: Result object, containing NO_ERROR and the receiver configuration of the supplied channel
                            or a non zero Error code.
        """
        return self.get_UEI_with_param(_BS_C.equalizerReceiverConfig, channel)

    def setTransmitterConfig(self, config):
        """ Sets the transmitter configuration

            :param config: Configuration to be applied to the transmitter.
            :return: Result.error Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.equalizerTransmitterConfig, config)

    def getTransmitterConfig(self):
        """ Gets the transmitter configuration

            :return: Result object, containing NO_ERROR and the current transmitter config
                     or a non zero Error code.
        """
        return self.get_UEI(_BS_C.equalizerTransmitterConfig)


class I2C(Entity):
    """ The I2C class is the interface the I2C busses on BrainStem modules.

        The class provides a way to send read and write commands to I2C devices
        on the entitie's bus.

        Useful Constants:
            * I2C_DEFAULT_SPEED  (0)
            * I2C_SPEED_100Khz   (1)
            * I2C_SPEED_400Khz   (2)
            * I2C_SPEED_1000Khz  (3)

    """
    I2C_DEFAULT_SPEED = 0
    I2C_SPEED_100Khz = 1
    I2C_SPEED_400Khz = 2
    I2C_SPEED_1000Khz = 3

    def __init__(self, module, index):
        """ I2C entity initializer"""
        super(I2C, self).__init__(module, _BS_C.cmdI2C, index)
        self._busSpeed = self.I2C_DEFAULT_SPEED

    def getSpeed(self):
        """ Get the current speed setting of the I2C object.

            Return:
                returns a Result object containing one of the constants
                representing the I2C objects current speed setting.
        """

        return Result(Result.NO_ERROR, self._busSpeed)

    def setSpeed(self, value):
        """ Set the current speed setting of the I2C object.

            Param:
                value (int): The constant representing the bus speed setting to apply.
                             for this object.

            Return:
                returns NO_ERROR on success or PARAMETER_ERROR on failure.
        """
        if value in (0, 1, 2, 3):
            self._busSpeed = value
            return Result.NO_ERROR
        else:
            return Result.PARAMETER_ERROR

    def write(self, address, length, *args):
        """ Send I2C write command, on the I2C BUS represented by the entity.

            Param:
                address (int): The I2C address (7bit <XXXX-XXX0>) of the device to write.
                length (int): The length of the data to write in bytes.
                data (*int | list): variable number of args of either int in the range of 0 to 255 or list|tuple of ints.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        try:
            data = convert_int_args_to_bytes(args)
        except ValueError:
            return Result.PARAMETER_ERROR

        if address % 2:
            return Result.PARAMETER_ERROR

        d = struct.pack('BBBB', self.index, address, length, self._busSpeed)
        match = (self.index, address, 0)
        result = self.send_command(4 + length, d + data, match)
        if result.error == Result.NO_ERROR:
            # Look into packet...
            vals = str_or_bytes_to_byte_list(result.value)
            try:
                if (vals[4] & 0x80) > 0:
                    result._error = vals[4] ^ 0x80
            except IndexError:
                result._error = Result.IO_ERROR

        return result.error

    def read(self, address, length):
        """ Send I2C read command, on the I2C BUS represented by the entity.

            Param:
                address (int): The I2C address (7bit <XXXX-XXX0>) of the device to read.
                length (int): The length of the data to read in bytes.

            Return:
                Result: Result object, containing NO_ERROR and read data
                        or a non zero Error code.
        """
        data = struct.pack('BBBB', self.index, address | 0x01, length, self._busSpeed)
        match = (self.index, address | 0x01, length)
        result = self.send_command(4, data, match)
        if result.error == Result.NO_ERROR:
            # Look into packet...
            vals = str_or_bytes_to_byte_list(result.value)
            # If theres an error we return that in the result, and set value to None.
            try:
                if (vals[4] & 0x80) > 0:
                    result._error = vals[4] ^ 0x80
                    result._value = None
                else:
                    result._value = vals[5:5+vals[3]]
            except IndexError:
                result._error = Result.IO_ERROR
                result._value = None

        return result

    def setPullup(self, bEnable):
        """ Set software controlled I2C pullup state.

            Sets the software controlled pullup on the bus for stems with
            software controlled pullup capabilities. Check the device datasheet
            for more information.
            This setting is saved by a system.save.

            Param:
                bEnable (bool): The desired state of the pullup.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        state = 1 if bEnable else 0
        d = struct.pack('BBB', self.index, _BS_C.i2cSetPullup, state)
        match = (self.index, _BS_C.i2cSetPullup)
        result = self.send_command(3, d, match)
        if result.error == Result.NO_ERROR:
            # Look into packet...
            vals = str_or_bytes_to_byte_list(result.value)
            try:
                if (vals[4] & 0x80) > 0:
                    result._error = vals[4] ^ 0x80
            except IndexError:
                result._error = Result.IO_ERROR

        return result.error


class Mux(Entity):
    """ Access MUX specialized entities on certain BrainStem modules.

        A MUX is a multiplexer that takes one or more similar inputs
        (bus, connection, or signal) and allows switching to one or more outputs.
        An analogy would be the switchboard of a telephone operator.  Calls (inputs)
        come in and by re-connecting the input to an output, the operator
        (multiplexor) can direct that input to on or more outputs.

        One possible output is to not connect the input to anything which
        essentially disables that input's connection to anything.

        Not every MUX has multiple inputs.  Some may simply be a single input that
        can be enabled (connected to a single output) or disabled
        (not connected to anything).

        Useful Constants:
            * UPSTREAM_STATE_ONBOARD (0)
            * UPSTREAM_STATE_EDGE (1)
            * UPSTREAM_MODE_AUTO (0)
            * UPSTREAM_MODE_ONBOARD (1)
            * UPSTREAM_MODE_EDGE (2)
            * DEFAULT_MODE (UPSTREAM_MODE_AUTO)
    """

    UPSTREAM_STATE_ONBOARD = 0
    UPSTREAM_STATE_EDGE = 1
    UPSTREAM_MODE_AUTO = 0
    UPSTREAM_MODE_ONBOARD = 1
    UPSTREAM_MODE_EDGE = 2
    DEFAULT_MODE = UPSTREAM_MODE_AUTO

    def __init__(self, module, index):
        """ Mux entity initializer"""
        super(Mux, self).__init__(module, _BS_C.cmdMUX, index)

    def setEnable(self, bEnable):
        """ Enables or disables the mux based on the param.

            Param:
                bEnable (bool): True = Enable, False = Disable

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.muxEnable, bEnable)

    def getEnable(self):
        """ Gets the enable/disable status of the mux.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.get_UEI(_BS_C.muxEnable)

    def setChannel(self, channel):
        """ Enables the specified channel of the mux.

            Param:
                channel (int): The channel of the mux to enable.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.muxChannel, channel)

    def getChannel(self):
        """ Gets the current selected channel.

            Param:
                channel (int): The channel of the mux to enable.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """

        return self.get_UEI(_BS_C.muxChannel)

    def getVoltage(self, channel):
        """ Gets the voltage of the specified channel.

            On some modules this is a measured value so may not exactly match what was
            previously set via the setVoltage interface. Refer to the module datasheet to
            to determine if this is a measured or stored value.

            return:
                Result: Return result object with NO_ERROR set and the current
                mux voltage setting in the Result.value or an Error.
        """
        return _BS_SignCheck(self.get_UEI_with_param(_BS_C.muxVoltage, channel))

    def getConfiguration(self):
        """ Gets the configuration of the Mux.

            return:
                Result: Return result object with NO_ERROR set and the current
                mux voltage setting in the Result.value or an Error.
        """
        return self.get_UEI(_BS_C.muxConfig)

    def setConfiguration(self, config):
        """ Sets the configuration of the mux.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.muxConfig, config)

    def getSplitMode(self):
        """ Gets the bit packed mux split configuration.

            return:
                Result: Return result object with NO_ERROR set and the current
                mux voltage setting in the Result.value or an Error.
        """
        return self.get_UEI(_BS_C.muxSplit)

    def setSplitMode(self, splitMode):
        """ Sets the mux split configuration

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.muxSplit, splitMode)


class UART(Entity):
    """ Provides UART entity access on certain BrainStem modules.

        A UART is a "Universal Asynchronous Reciever/Transmitter".  Many times
        referred to as a COM (communication), Serial, or TTY (teletypewriter) port.

        The UART Class allows the enabling and disabling of the UART data lines
    """

    def __init__(self, module, index):
        """ UART entity initializer"""
        super(UART, self).__init__(module, _BS_C.cmdUART, index)

    def setEnable(self, bEnable):
        """ Enable the UART.

            Param:
                bEnable (bool): True = Enable, False = Disable

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.uartEnable, bEnable)

    def getEnable(self):
        """ Get the enable status of the UART.

            Return:
                Result: Result object, containing NO_ERROR and the UART state
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.uartEnable)


class Pointer(Entity):
    """ Access the reflex scratchpad from a host computer.

        The Pointers access the pad which is a shared memory area on a BrainStem module.
        The interface allows the use of the brainstem scratchpad from the host, and provides
        a mechanism for allowing the host application and brainstem relexes to communicate.

        The Pointer allows access to the pad in a similar manner as a file pointer accesses
        the underlying file. The cursor position can be set via setOffset. A read of a character
        short or int can be made from that cursor position. In addition the mode of the pointer
        can be set so that the cursor position automatically increments or set so that it does not
        this allows for multiple reads of the same pad value, or reads of multi-record values, via
        and incrementing pointer.

        Useful Constants:
          * POINTER_MODE_STATIC (0)
          * POINTER_MODE_INCREMENT (1)

    """

    POINTER_MODE_STATIC = 0
    POINTER_MODE_INCREMENT = 1

    def __init__(self, module, index):
        """ Pointer entity initializer"""
        super(Pointer, self).__init__(module, _BS_C.cmdPOINTER, index)

    def setOffset(self, offset):
        """ Set the pointer offset for this pointer.

            Param:
                offset (char): The byte offset within the pad (0 - 255).

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI16(_BS_C.pointerOffset, offset)

    def getOffset(self):
        """ Get the pointer offset for this pointer.

            Return:
                Result: Result object, containing NO_ERROR and the current offset
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.pointerOffset)

    def setMode(self, mode):
        """ Set the pointer offset for this pointer.

            Param:
                mode (char): The mode. One of POINTER_MODE_STATIC or POINTER_MODE_INCREMENT

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.pointerMode, mode)

    def getMode(self):
        """ Get the pointer offset for this pointer.

            Return:
                Result: Result object, containing NO_ERROR and the current mode
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.pointerMode)

    def setTransferStore(self, handle):
        """ Set store slot handle for the pad to store and store to pad transfer.

            Param:
                handle (char): The handle. Open slot handle id.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.pointerTransferStore, handle)

    def getTransferStore(self):
        """ Get the open slot handle for this pointer.

            Return:
                Result: Result object, containing NO_ERROR and the handle
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.pointerTransferStore)

    def setChar(self, charVal):
        """ Set a value at the current cursor position within the pad.

            If the mode is increment this write will increment the cursor by 1 byte.

            Param:
                charVal (char): The value to set into the pad at the current
                             pointer position.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.pointerChar, charVal)

    def getChar(self):
        """ Get the value of the pad at the current cursor position.

            If the mode is increment this read will increment the cursor by 1 byte.

            Return:
                Result: Result object, containing NO_ERROR and the value
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.pointerChar)

    def setShort(self, shortVal):
        """ Set a value at the current cursor position within the pad.

            If the mode is increment this write will increment the cursor by 2 bytes.

            Param:
                shortVal (short): The value to set into the pad at the current
                             pointer position.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI16(_BS_C.pointerShort, shortVal)

    def getShort(self):
        """ Get the value of the pad at the current cursor position.

            If the mode is increment this read will increment the cursor by 2 bytes.

            Return:
                Result: Result object, containing NO_ERROR and the value
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.pointerShort)

    def setInt(self, intVal):
        """ Set a value at the current cursor position within the pad.

            If the mode is increment this write will increment the cursor by 4 bytes.

            Param:
                short (short): The value to set into the pad at the current
                               pointer position.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.pointerInt, intVal)

    def getInt(self):
        """ Get the value of the pad at the current cursor position.

            If the mode is increment this read will increment the cursor by 4 bytes.

            Return:
                Result: Result object, containing NO_ERROR and the value
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.pointerInt)

    def transferToStore(self, length):
        """ Transfer length bytes from the pad cursor position into the open store handle.

            If the mode is increment the transfer will increment the cursor by length bytes.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI16(_BS_C.pointerTransferToStore, length)

    def transterFromStore(self, length):
        """ Transfer length bytes from the open store handle to the cursor position in the pad.

            If the mode is increment the transfer will increment the cursor by length bytes.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI16(_BS_C.pointerTransferFromStore, length)


class Rail(Entity):
    """ Provides power rail functionality on certain modules.

        This entity is only available on certain modules. The RailClass can
        be used to control power to downstream devices, I has the ability to
        take current and voltage measurements, and depending on hardware, may
        have additional modes and capabilities.

        Useful Constants:
            * KELVIN_SENSING_OFF (0)
            * KELVIN_SENSING_ON (1)
            * OPERATIONAL_MODE_AUTO (0)
            * OPERATIONAL_MODE_LINEAR (1)
            * OPERATIONAL_MODE_SWITCHER (2)
            * OPERATIONAL_MODE_SWITCHER_LINEAR (3)
            * DEFAULT_OPERATIONAL_MODE (OPERATIONAL_MODE_AUTO)
            * OPERATIONAL_STATE_INITIALIZING (0)
            * OPERATIONAL_STATE_POWER_GOOD (1)
            * OPERATIONAL_STATE_POWER_FAULT (2)
            * OPERATIONAL_STATE_LDO_OVERTEMP (3)
            * OPERATIONAL_STATE_LINEAR (4)
            * OPERATIONAL_STATE_SWITCHER (5)
    """
    KELVIN_SENSING_OFF = 0
    KELVIN_SENSING_ON = 1
    OPERATIONAL_MODE_AUTO = 0
    OPERATIONAL_MODE_LINEAR = 1
    OPERATIONAL_MODE_SWITCHER = 2
    OPERATIONAL_MODE_SWITCHER_LINEAR = 3
    DEFAULT_OPERATIONAL_MODE = OPERATIONAL_MODE_AUTO
    OPERATIONAL_STATE_INITIALIZING = 0
    OPERATIONAL_STATE_POWER_GOOD = 1
    OPERATIONAL_STATE_POWER_FAULT = 2
    OPERATIONAL_STATE_LDO_OVERTEMP = 3
    OPERATIONAL_STATE_LINEAR = 4
    OPERATIONAL_STATE_SWITCHER = 5

    def __init__(self, module, index):
        """Rail initializer"""
        super(Rail, self).__init__(module, _BS_C.cmdRAIL, index)

    def getCurrent(self):
        """Get the rail current.

            Return:
                Result: Result object, containing NO_ERROR and the current in microamps
                        or a non zero Error code.
        """
        return _BS_SignCheck(self.get_UEI(_BS_C.railCurrent))

    def setCurrentLimit(self, microamps):
        """Set the rail current limit setting.

           Check product datasheet to see if this feature is available.

           args:
                microamps (int): The current in micro-amps (1 == 1e-6A).

           Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.railCurrentLimit, microamps)

    def getCurrentLimit(self):
        """ Get the rail current limit setting.

            Check product datasheet to see if this feature is available.

            args:
                microamps (int): The current in micro-amps (1 == 1e-6A).

            return:
                Result: Return result object with NO_ERROR set and the current
                        limit setting in the Result.value or an Error condition.
        """
        return self.get_UEI(_BS_C.railCurrentLimit)

    def getTemperature(self):
        """ Get the rail temperature.

            return:
                Result: Return result object with NO_ERROR set and the rail temperature
                in the Result.value or an Error condition.
        """
        return self.get_UEI(_BS_C.railTemperature)

    def getEnable(self):
        """ Get the state of the rail switch.

            Not all rails can be switched on and off. Refer to the
            module datasheet for capability specification of the rails.

            return:
                Result: Return result object with NO_ERROR set and the current
                rail enable state in the Result.value or an Error condition.
        """
        return self.get_UEI(_BS_C.railEnable)

    def setEnable(self, bEnable):
        """ Set the state of the rail switch.

            Not all rails can be switched on and off. Refer to the
            module datasheet for capability specification of the rails.

            args:
                bEnable (bool): true: enable and connect to the supply rail voltage;
                                false: disable and disconnect from the supply rail voltage

            return:
                Result.error: Return NO_ERROR on success, or one of the common
                              sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.railEnable, bEnable)

    def setVoltage(self, microvolts):
        """ Set the rail supply voltage.

            Rail voltage control capabilities vary between modules. Refer to the
            module datasheet for definition of the rail voltage capabilities.

            args:
                microvolts (int): The voltage in micro-volts (1 == 1e-6V) to be supply by the rail.

            return:
                Result.error: Return NO_ERROR on success, or one of the common
                              sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.railVoltage, microvolts)

    def getVoltage(self):
        """ Get the rail supply voltage.

            Rail voltage control capabilities vary between modules. Refer to the
            module datasheet for definition of the rail voltage capabilities.

            On some modules this is a measured value so may not exactly match what was
            previously set via the setVoltage interface. Refer to the module datasheet to
            to determine if this is a measured or stored value.

            return:
                Result: Return result object with NO_ERROR set and the current
                rail voltage setting in the Result.value or an Error.
        """
        return _BS_SignCheck(self.get_UEI(_BS_C.railVoltage))

    def getVoltageSetpoint(self):
        """ Get the rail setpoint voltage.

            Rail voltage control capabilities vary between modules. Refer to the
            module datasheet for definition of the rail voltage capabilities.

            return:
                Result: Return result object with NO_ERROR set and the current
                rail voltage setting in the Result.value or an Error.
        """
        return _BS_SignCheck(self.get_UEI(_BS_C.railVoltageSetpoint))

    def setKelvinSensingEnable(self, bEnable):
        """ Enable or Disable kelvin sensing on the module.

            Refer to the module datasheet for definition of the rail kelvin sensing capabilities.

            args:
                bEnable (bool): enable or disable kelvin sensing.

            return:
                Result.error: Return NO_ERROR on success, or one of the common
                              sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.railKelvinSensingEnable, bEnable)

    def getKelvinSensingEnable(self):
        """ Determine whether kelvin sensing is enabled or disabled.

            Refer to the module datasheet for definition of the rail kelvin
            sensing capabilities.

            args:
                bEnable (bool): Kelvin sensing is enabled or disabled.

            return:
                Result: Return result object with NO_ERROR set and the current
                rail kelvin sensing mode setting in the Result.value or an Error.
        """
        return self.get_UEI(_BS_C.railKelvinSensingMode)

    def getKelvinSensingState(self):
        """ Determine whether kelvin sensing has been disabled by the system.

            Refer to the module datasheet for definition of the rail kelvin
            sensing capabilities.

            return:
                Result: Return result object with NO_ERROR set and the current
                rail kelvin sensing state setting in the Result.value or an Error.
        """
        return self.get_UEI(_BS_C.railKelvinSensingState)

    def setOperationalMode(self, mode):
        """ Set the operational mode of the rail.

            Refer to the module datasheet for definition of the rail operational capabilities.

            args:
                mode (int): The operational mode to employ.

            return:
                Result.error: Return NO_ERROR on success, or one of the common
                          sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.railOperationalMode, mode)

    def getOperationalMode(self):
        """ Determine the current operational mode of the system.

            Refer to the module datasheet for definition of the rail operational
            mode capabilities.

            return:
                Result: Return result object with NO_ERROR set and the current
                rail operational mode setting in the Result.value or an Error.
        """
        return self.get_UEI(_BS_C.railOperationalMode)

    def getOperationalState(self):
        """ Determine the current operational state of the system.

        Refer to the module datasheet for definition of the rail operational states.

        return:
            Result: Return result object with NO_ERROR set and the current
            rail operational state in the Result.value or an Error.
        """
        return self.get_UEI(_BS_C.railOperationalState)


class RCServo(Entity):
    """ Provides RCServo functionality on certain modules.

        This entity is only available on certain modules. The RCServoClass can
        be used to interpret and control RC Servo signals and motors via the digital
        pins.

        Useful Constants:
            * SERVO_DEFAULT_POSITION (128)
            * SERVO_DEFAULT_MIN (64)
            * SERVO_DEFAULT_MAX (192)
    """

    SERVO_DEFAULT_POSITION = 128
    SERVO_DEFAULT_MIN = 64
    SERVO_DEFAULT_MAX = 192

    def __init__(self, module, index):
        super(RCServo, self).__init__(module, _BS_C.cmdSERVO, index)

    def setEnable(self, enable):
        """ Enable the servo channel.

            Param:
                enable (bool): The state to be set. 0 is disabled, 1 is enabled

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.servoEnable, enable)

    def getEnable(self):
        """ Get the enable status of the servo channel.

            If the enable status is 0 the servo channel is disabled, if the status
            is 1 the channel is enabled.

            Return:
                Result: Result object, containing NO_ERROR and servo enable status
                        or a non zero Error code.
        """

        return self.get_UEI(_BS_C.servoEnable)

    def setPosition(self, position):
        """ Set the position of the servo channel.

            Param:
                position (int): The position to be set. With the default configuration
                64 = a 1ms pulse and 192 = a 2ms pulse.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.servoPosition, position)

    def getPosition(self):
        """ Get the position of the servo channel.

            Default configuration: 1ms = 64 and 2ms = 192

            Return:
                Result: Result object, containing NO_ERROR and the servo position
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.servoPosition)

    def setReverse(self, reverse):
        """ Se the output to be reverse on the servo channel.

            Param:
                reverse (bool): Reverse mode: 0 = not reversed, 1 = reversed.
                ie: setPosition of 64 would actually apply 192 tot he servo output;
                however, getPosition will return 64.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.servoReverse, reverse)

    def getReverse(self):
        """ Get the reverse status of the channel.

            0 = not reversed, 1 = reversed

            Return:
                Result: Result object, containing NO_ERROR and the reverse status
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.servoReverse)


class Relay(Entity):
    """ The RelayClass is the interface to relay entities on BrainStem modules.

        Relay entities may be enabled (set) or disabled (cleared low).
        Other capabilities may be available, please see the product
        datasheet.

        Useful Constants:
            * VALUE_LOW (0)
            * VALUE_HIGH (1)
    """

    VALUE_LOW = 0
    VALUE_HIGH = 1

    def __init__(self, module, index):
        """Relay Entity initializer"""
        super(Relay, self).__init__(module, _BS_C.cmdRELAY, index)

    def setEnable(self, bEnable):
        """ Enables or disables the relay based on bEnable.

            Param:
                bEnable (int): Set 1 for enable, set 0 for disable.

            Return:
                Result.error: Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.relayEnable, bEnable)

    def getEnable(self):
        """ Get the relay enable state.

            A return of 1 indicates the relay is enabled.
            A return of 0 indicates the relay is disabled.

            return:
                Result: Result object, containing NO_ERROR and digital state
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.relayEnable)

    def getVoltage(self):
        """ Get the scaled micro volt value with refrence to ground.

            Get a 32 bit signed integer (in micro Volts) based on the boards
            ground and refrence voltages.

            Note:
                Not all modules provide 32 bits of accuracy; Refer to the module's
                datasheet to determine the analog bit depth and reference voltage.

            return:
                Result: Result object, containing NO_ERROR and microVolts value
                        or a non zero Error code.

        """
        return _BS_SignCheck(self.get_UEI(_BS_C.relayVoltage))


class Signal(Entity):
    """ The Signal Class is the interface to digital pins configured to produce square wave signals.

        This class is designed to allow for square waves at various frequencies and duty cycles. Control
        is defined by specifying the wave period as (T3Time) and the active portion of the cycle as (T2Time).
        See the entity overview section of the reference for more detail regarding the timiing.

    """

    def __init__(self, module, index):
        """ Signal Entity initializer """
        super(Signal, self).__init__(module, _BS_C.cmdSIGNAL, index)

    def setEnable(self, enable):
        """
        Enable/Disable the signal output.

        :param enable: True to enable, false to disable
        :return: Result.error Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.signalEnable, enable)

    def getEnable(self):
        """ Get the Enable/Disable of the signal.

        :return: Result object, containing NO_ERROR and boolean value True for enabled False for disabled
                        or a non zero Error code.
        """
        return self.get_UEI(_BS_C.signalEnable)

    def setInvert(self, invert):
        """ Invert the signal output.

            Normal mode is High on t0 then low at t2.
            Inverted mode is Low at t0 on period start and high at t2.

            :param invert: True to invert, false for normal mode.
            :return: Result.error Return NO_ERROR on success, or one of the common
                sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.signalInvert, invert)

    def getInvert(self):
        """ Get the invert status of the signal.

            :return: Result object, containing NO_ERROR and boolean value True for inverted False for normal
                     or a non zero Error code.
        """
        return self.get_UEI(_BS_C.signalInvert)

    def setT3Time(self, t3_nsec):
        """ Set the signal period or T3 in nanoseconds.

            :param t3_nsec: Tnteger not larger than unsigned 32 bit max value representing the wave period in nanoseconds.
            :return: Result.error Return NO_ERROR on success, or one of the common
                     sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.signalT3Time, t3_nsec)

    def getT3Time(self):
        """ Get the current wave period (T3) in nanoseconds.

            :return: Result object, containing NO_ERROR and an integer value not larger than the max unsigned 32bit value.
                     or a non zero Error code.
        """
        return self.get_UEI(_BS_C.signalT3Time)

    def setT2Time(self, t2_nsec):
        """ Set the signal active period or T2 in nanoseconds.

            :param t2_nsec: Tnteger not larger than unsigned 32 bit max value representing the wave active period in nanoseconds.
            :return: Result.error Return NO_ERROR on success, or one of the common
                     sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.signalT2Time, t2_nsec)

    def getT2Time(self):
        """ Get the current wave active period (T2) in nanoseconds.

            :return: Result object, containing NO_ERROR and an integer value not larger than the max unsigned 32bit value.
                     or a non zero Error code.
        """
        return self.get_UEI(_BS_C.signalT2Time)


class Store(Entity):
    """ Access the store on a BrainStem Module.

        The store provides a flat file system on modules that have storage capacity.
        Files are referred to as slots and they have simple zero-based numbers
        for access. Store slots can be used for generalized storage and commonly
        contain compiled reflex code (files ending in .map) or templates used by the
        system. Slots simply contain bytes with no expected organization but
        the code or use of the slot may impose a structure.

        Stores have fixed indices based on type. Not every module contains a
        store of each type. Consult the module datasheet for details on which
        specific stores are implemented, if any, and the capacities of
        implemented stores.

        Useful Constants:
            * INTERNAL_STORE (0)
            * RAM_STORE (1)
            * SD_STORE (2)
    """

    INTERNAL_STORE = 0
    RAM_STORE = 1
    SD_STORE = 2

    def __init__(self, module, index):
        """Store initializer"""
        super(Store, self).__init__(module, _BS_C.cmdSTORE, index)

    def getSlotState(self, slot):
        """ Get slot state.

            Slots which contain reflexes may be "enabled," i.e. the reflexes
            contained in the slot are active.

            args:
                slot (int): The slot number.

            return:
                Result: Return result object with NO_ERROR set and the current
                        state of the slot in the Result.value or an Error.
        """
        return self.get_UEI_with_param(_BS_C.storeSlotState, slot)

    def loadSlot(self, slot, data, length):
        """ Load the slot.

            args:
                slot (int): The slot number.
                data (str, bytes): The data.
                length (int): The data length in bytes.

            return:
                Result.error: Return NO_ERROR on success, or one of the common
                              sets of return error codes on failure.
        """

        result = self._openSlot(slot, _BS_C.slotOpenWrite)
        handle = result.value if result.error == Result.NO_ERROR else 0xFF
        if handle != 0xFF:
            count = 0
            match = ([_BS_C.slotWrite, _BS_C.slotWrite | _BS_C.bitSlotError], handle)
            while result.error == Result.NO_ERROR and count < length:
                packet = struct.pack('BB', _BS_C.slotWrite, handle)
                block = length - count

                if block > (_BS_C.MAX_PACKET_BYTES - 3):  # 3 = (cmdSLOT, slotWrite, handle)
                    block = (_BS_C.MAX_PACKET_BYTES - 3)

                # blocksum on the stem relies on an overflow of a uint8_t... simulate this.
                blocksum = 0
                try:
                    for i in data[count:count + block]:
                        try:
                            blocksum += ord(i)
                        except TypeError:
                            blocksum += i
                        blocksum %= 256
                except TypeError:
                    result = Result(_BS_C.aErrParam, None)
                    break

                packet = packet + data[count:(count + block)]
                if self.module.link is None:
                    result = Result(_BS_C.aErrConnection, None)
                    break
                else:
                    result._error = self.module.link.send_command_packet(self.module.address,
                                                                         _BS_C.cmdSLOT,
                                                                         len(packet), packet)
                    if result.error == Result.NO_ERROR:
                        result = self.module.link.receive_command_packet(self.module.address,
                                                                         _BS_C.cmdSLOT,
                                                                         match, 1000)

                    if result.error == Result.NO_ERROR:
                        vals = str_or_bytes_to_byte_list(result.value, 0, 4)
                        if (vals[1] & _BS_C.bitSlotError) > 0:
                            result._error = vals[3]
                            result._value = None
                        elif blocksum != vals[3]:
                            # print "blocksum: %d, val: %d" % (blocksum, vals[3])
                            result._error = Result.IO_ERROR
                            result._value = None
                        else:
                            count = count + block
                    else:
                        result._error = result.error

            self._closeSlot(handle)

        return result.error

    def unloadSlot(self, slot):
        """ Unload the slot data.

            args:
                slot (int): The slot number.

            return:
                Result: Either Returns result object with NO_ERROR set
                        and Result.value containing a tuple of (str|bytes, int)
                        containing the unloaded data and length, or an Error.
        """
        result = self.getSlotSize(slot)
        size = result.value if result.error == Result.NO_ERROR else 0
        handle = 0xFF
        if result.error == Result.NO_ERROR:
            result = self._openSlot(slot, _BS_C.slotOpenRead)
            handle = result.value if result.error == Result.NO_ERROR else 0xFF

        if handle != 0xFF and size != 0:
            count = 0
            data = struct.pack('BB', _BS_C.slotRead, handle)
            match = ([_BS_C.slotRead, _BS_C.slotRead | _BS_C.bitSlotError], handle)
            result_data = b''
            while result.error == Result.NO_ERROR and count < size:
                if self.module.link is None:
                    result = Result(_BS_C.aErrConnection, None)
                    break
                else:
                    error = self.module.link.send_command_packet(self.module.address, _BS_C.cmdSLOT, 2, data)
                    if error == Result.NO_ERROR:
                        result = self.module.link.receive_command_packet(self.module.address,
                                                                         _BS_C.cmdSLOT,
                                                                         match, 1000)

                    if result.error == Result.NO_ERROR:
                        vals = str_or_bytes_to_byte_list(result.value, 0, 4)
                        length = result._length
                        if (vals[1] & _BS_C.bitSlotError) > 0:
                            result._error = vals[3]
                            result._value = None
                        else:
                            count = count + (length - 3)
                            result_data = result_data + result.value[3:length]

            self._closeSlot(handle)
            result = Result(result.error, result_data)

        return result

    def slotEnable(self, slot):
        """ Enable the slot """
        return self.set_UEI8(_BS_C.storeSlotEnable, slot)

    def slotDisable(self, slot):
        """ Disable the slot"""
        return self.set_UEI8(_BS_C.storeSlotDisable, slot)

    def getSlotCapacity(self, slot):
        """ Get the slot capacity.

            Returns the Capacity of the slot, i.e. The number of bytes it can hold.

            return:
                Result: Either the capacity of the slot in Result.value or an error.
        """
        result = Result(_BS_C.aErrNone, None)
        # [slotCapacity, store, slot]
        data = struct.pack('BBB', _BS_C.slotCapacity, self.index, slot)
        match = ([_BS_C.slotCapacity, _BS_C.slotCapacity | _BS_C.bitSlotError], self.index, slot)
        if self.module.link is None:
            return Result(_BS_C.aErrConnection, None)
        else:
            result._error = self.module.link.send_command_packet(self.module.address, _BS_C.cmdSLOT, 3, data)
            if result.error == Result.NO_ERROR:
                result = self.module.link.receive_command_packet(self.module.address, _BS_C.cmdSLOT, match)
        if result.error == Result.NO_ERROR:
            # Look into packet...
            vals = str_or_bytes_to_byte_list(result.value)
            # If theres an error we return that in the result, and set value to None.
            try:
                if (vals[1] & _BS_C.bitSlotError) > 0:
                    result._error = vals[4]
                    result._value = None
                else:
                    result._value = (vals[4] << 8) + vals[5]

            except IndexError:
                result._error = Result.IO_ERROR
                result._value = None

        return result

    def getSlotSize(self, slot):
        """ Get the slot size.

            Returns the size of the data currently filling the slot in bytes.

            return:
                Result: Either the size of the slot in Result.value or an error.
        """
        result = Result(_BS_C.aErrNone, None)
        # [slotSize, store, slot]
        data = struct.pack('BBB', _BS_C.slotSize, self.index, slot)
        match = ([_BS_C.slotSize, _BS_C.slotSize | _BS_C.bitSlotError], self.index, slot)
        if self.module.link is None:
            return Result(_BS_C.aErrConnection, None)
        else:
            result._error = self.module.link.send_command_packet(self.module.address, _BS_C.cmdSLOT, 3, data)
            if result.error == Result.NO_ERROR:
                result = self.module.link.receive_command_packet(self.module.address, _BS_C.cmdSLOT, match)
        if result.error == Result.NO_ERROR:
            # Look into packet...
            vals = str_or_bytes_to_byte_list(result.value)
            # If theres an error we return that in the result, and set value to None.
            try:
                if (vals[1] & _BS_C.bitSlotError) > 0:
                    result._error = vals[4]
                    result._value = None
                else:
                    result._value = (vals[4] << 8) + vals[5]

            except IndexError:
                result._error = Result.IO_ERROR
                result._value = None

        return result

    def _openSlot(self, slot, rw_access):
        result = Result(_BS_C.aErrNone, None)
        # [slotOpenRead| slotOpenWrite, store, slot]
        data = struct.pack('BBB', rw_access, self.index, slot)
        match = ([rw_access, rw_access | _BS_C.bitSlotError], self.index, slot)
        if self.module.link is None:
            return Result(_BS_C.aErrConnection, None)
        else:
            result._error = self.module.link.send_command_packet(self.module.address, _BS_C.cmdSLOT, 3, data)
            if result.error == Result.NO_ERROR:
                result = self.module.link.receive_command_packet(self.module.address, _BS_C.cmdSLOT, match)
        if result.error == Result.NO_ERROR:
            # Look into packet...
            vals = str_or_bytes_to_byte_list(result.value)
            # If theres an error we return that in the result, and set value to None.
            try:
                if (vals[1] & _BS_C.bitSlotError) > 0:
                    result._error = vals[4]
                    result._value = None
                else:
                    result._value = vals[4]

            except IndexError:
                result._error = Result.IO_ERROR
                result._value = None

        return result

    def _closeSlot(self, handle):
        result = Result(_BS_C.aErrNone, None)
        # [slotClose, handle]
        data = struct.pack('BB', _BS_C.slotClose, handle)
        match = ([_BS_C.slotClose, _BS_C.slotClose | _BS_C.bitSlotError], handle)
        if self.module.link is None:
            return Result(_BS_C.aErrConnection, None)
        else:
            result._error = self.module.link.send_command_packet(self.module.address, _BS_C.cmdSLOT, 2, data)
            if result.error == Result.NO_ERROR:
                result = self.module.link.receive_command_packet(self.module.address, _BS_C.cmdSLOT, match)
        if result.error == Result.NO_ERROR:
            # Look into packet...
            vals = str_or_bytes_to_byte_list(result.value)
            # If theres an error we return that in the result, and set value to None.
            try:
                if (vals[1] & _BS_C.bitSlotError) > 0:
                    result._error = vals[3]
                    result._value = None
                else:
                    result._value = True

            except IndexError:
                result._error = Result.IO_ERROR
                result._value = None

        return result


class Temperature(Entity):
    """ Provide interface to temperature sensor.

        This entitiy is only available on certain modules, and provides a
        temperature reading in microcelsius.
    """

    def __init__(self, module, index):
        """Temperature object initializer"""
        super(Temperature, self).__init__(module, _BS_C.cmdTEMPERATURE, index)

    def getTemperature(self):
        """ Get the temperature.

            return:
                Result: Return result object with NO_ERROR set and the current
                temperature measurement in the Result.value or an Error.
        """
        return self.get_UEI(_BS_C.temperatureMicroCelsius)


class Timer(Entity):
    """ Schedules events to occur at future times.

        Reflex routines can be written which will be executed upon expiration
        of the timer entity. The timer can be set to fire only once, or to
        repeat at a certain interval.

        Useful Constants:
            * SINGLE_SHOT_MODE (0)
            * REPEAT_MODE (1)
            * DEFAULT_MODE (SINGLE_SHOT_MODE)

    """

    SINGLE_SHOT_MODE = 0
    REPEAT_MODE = 1
    DEFAULT_MODE = SINGLE_SHOT_MODE

    def __init__(self, module, index):
        """Timer object initializer"""
        super(Timer, self).__init__(module, _BS_C.cmdTIMER, index)

    def getExpiration(self):
        """ Get the currently set expiration time in microseconds.

            This is not a "live" timer. That is, it shows the expiration time
            originally set with setExpiration; it does not "tick down" to show
            the time remaining before expiration.

            return:
                Result: Return result object with NO_ERROR set and the timer
                expiration in uSeconds in the Result.value or an Error.
        """
        return self.get_UEI(_BS_C.timerExpiration)

    def setExpiration(self, usecDuration):
        """ Set the expiration time for the timer entity.

            When the timer expires, it will fire the associated timer[index]() reflex.

            args:
                usecDuration (int): The duration before timer expiration in microseconds.

            return:
                Result.error: Return NO_ERROR on success, or one of the common
                          sets of return error codes on failure.
        """
        return self.set_UEI32(_BS_C.timerExpiration, usecDuration)

    def getMode(self):
        """ Get the mode of the timer.

            Valid timer modes are single mode and repeat mode.

            return:
                Result: Return result object with NO_ERROR set and the timer mode
                either single (0) or repeat (1) in the Result.value or an Error.
        """
        return self.get_UEI(_BS_C.timerMode)

    def setMode(self, mode):
        """ Set the mode of the timer.

            args:
                mode (int): The mode of the timer. aTIMER_MODE_REPEAT or aTIMER_MODE_SINGLE.

            return:
                Result.error: Return NO_ERROR on success, or one of the common
                          sets of return error codes on failure.
        """
        return self.set_UEI8(_BS_C.timerMode, mode)


class USB(Entity):
    """ USBClass provides methods to interact with a USB hub and USB switches.

        Different USB hub products have varying support; check the
        datasheet to understand the capabilities of each product.

        Useful Constants:
            * UPSTREAM_MODE_AUTO (2)
            * UPSTREAM_MODE_PORT_0 (0)
            * UPSTREAM_MODE_PORT_1 (1)
            * UPSTREAM_MODE_NONE (255)
            * DEFAULT_UPSTREAM_MODE (UPSTREAM_MODE_AUTO)

            * UPSTREAM_STATE_PORT_0 (0)
            * UPSTREAM_STATE_PORT_1 (1)

            * BOOST_0_PERCENT (0)
            * BOOST_4_PERCENT (1)
            * BOOST_8_PERCENT (2)
            * BOOST_12_PERCENT (3)

            * PORT_MODE_SDP (0)
            * PORT_MODE_CDP (1)
            * PORT_MODE_CHARGING (2)
            * PORT_MODE_PASSIVE (3)
            * PORT_MODE_USB2_A_ENABLE (4)
            * PORT_MODE_USB2_B_ENABLE (5)
            * PORT_MODE_VBUS_ENABLE (6)
            * PORT_MODE_SUPER_SPEED_1_ENABLE (7)
            * PORT_MODE_SUPER_SPEED_2_ENABLE (8)
            * PORT_MODE_USB2_BOOST_ENABLE (9)
            * PORT_MODE_USB3_BOOST_ENABLE (10)
            * PORT_MODE_AUTO_CONNECTION_ENABLE (11)
            * PORT_MODE_CC1_ENABLE (12)
            * PORT_MODE_CC2_ENABLE (13)
            * PORT_MODE_SBU_ENABLE (14)
            * PORT_MODE_CC_FLIP_ENABLE (15)
            * PORT_MODE_SS_FLIP_ENABLE (16)
            * PORT_MODE_SBU_FLIP_ENABLE (17)
            * PORT_MODE_USB2_FLIP_ENABLE (18)
            * PORT_MODE_CC1_INJECT_ENABLE (19)
            * PORT_MODE_CC2_INJECT_ENABLE (20)

            * PORT_SPEED_NA (0)
            * PORT_SPEED_HISPEED (1)
            * PORT_SPEED_SUPERSPEED (2)
    """

    UPSTREAM_MODE_AUTO = 2
    UPSTREAM_MODE_PORT_0 = 0
    UPSTREAM_MODE_PORT_1 = 1
    UPSTREAM_MODE_NONE = 255
    DEFAULT_UPSTREAM_MODE = UPSTREAM_MODE_AUTO

    UPSTREAM_STATE_PORT_0 = 0
    UPSTREAM_STATE_PORT_1 = 1

    BOOST_0_PERCENT = 0
    BOOST_4_PERCENT = 1
    BOOST_8_PERCENT = 2
    BOOST_12_PERCENT = 3

    PORT_MODE_SDP = 0
    PORT_MODE_CDP = 1
    PORT_MODE_CHARGING = 2
    PORT_MODE_PASSIVE = 3
    PORT_MODE_USB2_A_ENABLE = 4
    PORT_MODE_USB2_B_ENABLE = 5
    PORT_MODE_VBUS_ENABLE = 6
    PORT_MODE_SUPER_SPEED_1_ENABLE = 7
    PORT_MODE_SUPER_SPEED_2_ENABLE = 8
    PORT_MODE_USB2_BOOST_ENABLE = 9
    PORT_MODE_USB3_BOOST_ENABLE = 10
    PORT_MODE_AUTO_CONNECTION_ENABLE = 11
    PORT_MODE_CC1_ENABLE = 12
    PORT_MODE_CC2_ENABLE = 13
    PORT_MODE_SBU_ENABLE = 14
    PORT_MODE_CC_FLIP_ENABLE = 15
    PORT_MODE_SS_FLIP_ENABLE = 16
    PORT_MODE_SBU_FLIP_ENABLE = 17
    PORT_MODE_USB2_FLIP_ENABLE = 18
    PORT_MODE_CC1_INJECT_ENABLE = 19
    PORT_MODE_CC2_INJECT_ENABLE = 20

    PORT_SPEED_NA = 0
    PORT_SPEED_HISPEED = 1
    PORT_SPEED_SUPERSPEED = 2

    def __init__(self, module, index):
        """USBClass initializer"""
        super(USB, self).__init__(module, _BS_C.cmdUSB, index)

    def setPortEnable(self, channel):
        """Enable both power and data lines for a USB port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbPortEnable, channel)

    def setPortDisable(self, channel):
        """Disable both power and data lines for a USB port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbPortDisable, channel)

    def setDataEnable(self, channel):
        """Enable just the data lines for a USB port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbDataEnable, channel)

    def setDataDisable(self, channel):
        """Disable just the data lines for a USB port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbDataDisable, channel)

    def setHiSpeedDataEnable(self, channel):
        """Enable Hi-Speed (USB2.0) data transfer for a USB port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbHiSpeedDataEnable, channel)

    def setHiSpeedDataDisable(self, channel):
        """Disable Hi-Speed (USB2.0) data transfer for a USB port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbHiSpeedDataDisable, channel)

    def setSuperSpeedDataEnable(self, channel):
        """Enable SuperSpeed (USB3.0) data transfer for a USB port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbSuperSpeedDataEnable, channel)

    def setSuperSpeedDataDisable(self, channel):
        """Disable SuperSpeed (USB3.0) data transfer for a USB port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbSuperSpeedDataDisable, channel)

    def setPowerEnable(self, channel):
        """Enable just the power line for a USB port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbPowerEnable, channel)

    def setPowerDisable(self, channel):
        """Disable just the power line for a USB port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """

        return self.set_UEI8(_BS_C.usbPowerDisable, channel)

    def getPortCurrent(self, channel):
        """Get the current through the power line for a port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return _BS_SignCheck(self.get_UEI_with_param(_BS_C.usbPortCurrent, channel))

    def getPortVoltage(self, channel):
        """Get the voltage on the power line for a port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return _BS_SignCheck(self.get_UEI_with_param(_BS_C.usbPortVoltage, channel))

    def getHubMode(self):
        """Get a bit mapped representation of the hub mode.
            Usually represents the port data and power lines enable/disable
            state in one bit packed result.
            See the product datasheet for state mapping.

        Returns: Result object
        """
        return self.get_UEI(_BS_C.usbHubMode)

    def setHubMode(self, mode):
        """Set a bit mapped representation of the hub mode.
            Usually represents the port data and power lines enable/disable.
            See the product datasheet for state mapping.

        Args:
            mode (int): The hub state

        Returns: Result object
        """
        return self.set_UEI32(_BS_C.usbHubMode, mode)

    def clearPortErrorStatus(self, channel):
        """Clear the error status for the given channel.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbPortClearErrorStatus, channel)

    def getUpstreamMode(self):
        """Get the upstream switch mode for the USB upstream ports.

        Returns: Result object
        """
        return self.get_UEI(_BS_C.usbUpstreamMode)

    def setUpstreamMode(self, mode):
        """Set the upstream switch mode for the USB upstream ports

        Args:
            mode (int):
                * Auto: UPSTREAM_MODE_AUTO = 2
                * Port 0: UPSTREAM_STATE_PORT_0 = 0
                * Port 1: UPSTREAM_STATE_PORT_1 = 1

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbUpstreamMode, mode)

    def getUpstreamState(self):
        """Get the upstream switch state for the USB upstream ports.

        Returns: Result object
            Result value 2 if no ports plugged in; 0 if port0 is active,
            1 if port1 is active.
        """
        return self.get_UEI(_BS_C.usbUpstreamState)

    def setEnumerationDelay(self, ms_delay):
        """Set the interport enumeration delay in milliseconds.
            This setting must be saved with a stem.system.save() call for it to be active.
            This setting is persistent across hub power down. Resetting the hub will
            return this setting to the default value of 0ms.

        Args:
            ms_delay (int): Interport delay in milliseconds

        Returns: Result object
        """
        return self.set_UEI32(_BS_C.usbHubEnumerationDelay, ms_delay)

    def getEnumerationDelay(self):
        """Get the interport enumeration delay in milliseconds.

        Returns: Result object
        """
        return self.get_UEI(_BS_C.usbHubEnumerationDelay)

    def setPortCurrentLimit(self, channel, microAmps):
        """Set the current limit for the port. If the set limit is not achievable,
            devices will round down to the nearest available current limit setting.
            This setting can be saved with a stem.system.save() call to make it persistent.

        Args:
            channel (int): Port index.
            microAmps (int): The current limit setting in microAmps (1A=10e6)

        Returns: Result object
        """
        return self.set_UEI32_with_subindex(_BS_C.usbPortCurrentLimit, channel, microAmps)

    def getPortCurrentLimit(self, channel):
        """Get the current limit for the port.

        Returns: Result object
        """
        return self.get_UEI_with_param(_BS_C.usbPortCurrentLimit, channel)

    def setPortMode(self, channel, mode):
        """Set the mode for the Port.
           The mode setting defaults to SDP or Standard Downstream port, and
           can be set to CDP (charging downstream port) for devices that require
           high port charge current above 500 milliamps.

        Args:
            channel (int): Port Index.
            mode (int): Mode The port mode setting (0 - SDP, 1 - CDP).

        Returns: Result.error value.
        """
        return self.set_UEI32_with_subindex(_BS_C.usbPortMode, channel, mode)

    def getPortMode(self, channel):
        """Get the mode for the Port.
           The mode setting defaults to SDP or Standard Downstream port, and
           can be set to CDP (charging downstream port) for devices that require
           high port charge current above 500 milliamps.

           Returns: Result object
        """
        return self.get_UEI_with_param(_BS_C.usbPortMode, channel)

    def getPortState(self, channel):
        """Get the state for the Port.

           Returns: Result object
        """
        return self.get_UEI_with_param(_BS_C.usbPortState, channel)

    def getPortError(self, channel):
        """Get the error for the Port.

           Returns: Result object
        """
        return self.get_UEI_with_param(_BS_C.usbPortError, channel)

    def setUpstreamBoostMode(self, setting):
        """Set the upstream boost mode.
            Boost mode increases the drive strength of the USB data signals (power signals
            are not changed). Boosting the data signal strength may help to overcome
            connectivity issues when using long cables or connecting through "pogo" pins.
            Possible modes are 0 - no boost, 1 - 4%% boost, 2 - 8%% boost,
            3 - 12%% boost. This setting is not applied until a stem.system.save() call
            and power cycle of the hub. Setting is then persistent until changed or the hub
            is reset. After reset, default value of 0%% boost is restored.

        Args:
            setting (int): Upstream boost setting 0, 1, 2, or 3.

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbUpstreamBoostMode, setting)

    def getUpstreamBoostMode(self):
        """Get the upstream boost mode.

        Returns: Result object
            Result value 0 - no boost, 1 - 4%% boost, 2 - 8%% boost, 3 - 12%% boost.
        """
        return self.get_UEI(_BS_C.usbUpstreamBoostMode)

    def setDownstreamBoostMode(self, setting):
        """Set the downstream boost mode.
            Boost mode increases the drive strength of the USB data signals (power signals
            are not changed). Boosting the data signal strength may help to overcome
            connectivity issues when using long cables or connecting through "pogo" pins.
            Possible modes are 0 - no boost, 1 - 4%% boost, 2 - 8%% boost,
            3 - 12%% boost. This setting is not applied until a stem.system.save() call
            and power cycle of the hub. Setting is then persistent until changed or the hub
            is reset. After reset, default value of 0%% boost is restored.

        Args:
            setting (int): Downstream boost setting 0, 1, 2, or 3.

        Returns: Result object
        """
        return self.set_UEI8(_BS_C.usbDownstreamBoostMode, setting)

    def getDownstreamBoostMode(self):
        """Get the downstream boost mode.

        Returns: Result object
            Result value 0 - no boost, 1 - 4%% boost, 2 - 8%% boost, 3 - 12%% boost.
        """
        return self.get_UEI(_BS_C.usbDownstreamBoostMode)

    def getDownstreamDataSpeed(self, channel):
        """Get the downstream port data speed.

        Returns: Result object
            Result value:
                * N/A: PORT_SPEED_NA = 0
                * Hi Speed: PORT_SPEED_HISPEED = 1
                * SuperSpeed: PORT_SPEED_SUPERSPEED = 2
        """
        return self.get_UEI_with_param(_BS_C.usbDownstreamDataSpeed, channel)

    def setConnectMode(self, channel, mode):
        """Set The connection mode for the Switch.
        :param channel: USB sub channel.
        :param mode: 0 = Manual mode, 1 = Auto mode.
        :return: NO_ERROR on success and error code on failure.
        """

        return self.set_UEI8_with_subindex(_BS_C.usbConnectMode, channel, mode)

    def getConnectMode(self, channel):
        """Get The connection mode for the Switch.
        :param channel: USB sub channel.
        :return: NO_ERROR on success and error code on failure.
        """
        return self.get_UEI_with_param(_BS_C.usbConnectMode, channel)

    def setCC1Enable(self, channel, enable):
        """Enable CC1 lines for a Type C USB port

        Args:
            channel (int): The USB port number
            enable (int): enable (0 = disable, 1 = enable)

        Returns: Result object
        """
        return self.set_UEI8_with_subindex(_BS_C.usbCC1Enable, channel, enable)

    def setCC2Enable(self, channel, enable):
        """Enable CC2 lines for a Type C USB port

        Args:
            channel (int): The USB port number
            enable (int): enable [0 = disable, 1 = enable]

        Returns: Result object
        """
        return self.set_UEI8_with_subindex(_BS_C.usbCC2Enable, channel, enable)

    def setSBUEnable(self, channel, enable):
        """Enable SBU1/SBU2 lines for a Type C USB port based on usbPortMode settings.

        Args:
            channel (int): The USB port number
            enable (int): enables SBU1/SBU2 [0 = disable, 1 = enable]

        Returns: Result object
        """
        return self.set_UEI8_with_subindex(_BS_C.usbSBUEnable, channel, enable)

    def getCC1Current(self, channel):
        """Get the current through the CC1 line for a port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return _BS_SignCheck(self.get_UEI_with_param(_BS_C.usbCC1Current, channel))

    def getCC2Current(self, channel):
        """Get the current through the CC2 line for a port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return _BS_SignCheck(self.get_UEI_with_param(_BS_C.usbCC2Current, channel))

    def getCC1Voltage(self, channel):
        """Get the voltage on the CC1 line for a port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return _BS_SignCheck(self.get_UEI_with_param(_BS_C.usbCC1Voltage, channel))

    def getCC2Voltage(self, channel):
        """Get the voltage on the CC2 line for a port.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return _BS_SignCheck(self.get_UEI_with_param(_BS_C.usbCC2Voltage, channel))

    def setCableFlip(self, channel, enable):
        """Enables a cable orientation flip within the S85 switch.

        Args:
            channel (int): The USB port number
            enable (int): enables cable flip. [0 = disable, 1 = enable]

        Returns: Error
        """
        return self.set_UEI8_with_subindex(_BS_C.usbCableFlip, channel, enable)

    def getCableFlip(self, channel):
        """Get the status of cable orientation flip within the S85 switch.

        Args:
            channel (int): The USB port number

        Returns: Result object
        """
        return _BS_SignCheck(self.get_UEI_with_param(_BS_C.usbCableFlip, channel))

    def setAltModeConfig(self, channel, configuration):
        """Sets alt mode configuration for defined USB channel.
            See the product datasheet for device specific details

        Args:
            channel (int): The USB channel
            configuration (uint): The configuration to set

        Returns: Result object
        """
        return self.set_UEI32_with_subindex(_BS_C.usbAltMode, channel, configuration)

    def getAltModeConfig(self, channel):
        """Gets alt mode configuration for defined USB channel.
            See the product datasheet for device specific details.

        Args:
            channel (int): The USB channel

        Returns: Result object
        """
        return self.get_UEI_with_param(_BS_C.usbAltMode, channel)

# For Handling negative values.
def _BS_SignCheck(result):
        if result.error == Result.NO_ERROR:
            result._value = -0x100000000 + result.value if result.value & 0x80000000 else result.value
        return result
