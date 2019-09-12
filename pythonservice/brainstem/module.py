# Copyright (c) 2018 Acroname Inc. - All Rights Reserved
#
# This file is part of the BrainStem (tm) package which is released under MIT.
# See file LICENSE or go to https://acroname.com for full license details.

"""
A module that provides base classes for BrainStem Modules and Entities.

The Module and Entity classes are designed to be extended for specific types
of BraiStem Modules and Entities. For more information about Brainstem Modules
and Entities, please see the `Terminology`_ section of the `Acroname BrainStem Reference`_

.. _Terminology:
    https://acroname.com/reference/terms.html

.. _Acroname BrainStem Reference:
    https://acroname.com/reference
"""
import gc
import struct
from time import sleep

from . import _BS_C
from ._link import Link, UEI
from .link import Spec, Status
from .result import Result
from . import discover


class Module(object):
    """
    Base class for BrainStem Modules.

    Provides default implementations for connecting and disconnecting from
    BrainStem modules via the module's serial number, a `Spec`_ object or through another
    module.

    .. _Spec:
        brainstem.spec
    """

    def __init__(self, address, enable_auto_networking=True, model=0):
        """
         Initialize a Module object.

         Args:
            address (int): The BrainStem module addresses should be even integers.
        """
        self.__address = address
        self.__link = None
        self.__spec = None
        self.__bAutoNetworking = enable_auto_networking
        self.__model = model

    @property
    def address(self):
        """ int: Return the Brainstem module address. """
        return self.__address

    @property
    def bAutoNetworking(self):
        """ bool: Return the current networking mode. """
        return self.__bAutoNetworking

    @property
    def spec(self):
        """ Spec: Return the current spec object. """
        return self.__spec

    @property
    def link(self):
        """ Link: return the current link or None. """
        return self.__link

    @property
    def model(self):
        """ Model: returns the model number of the object. """
        return self.__model

    # Connect from spec should be fast. The spec fully qualifies connection
    # parameters for the link.
    def connectFromSpec(self, spec):
        """ Result.error: Connect to a BrainStem module with a Spec.

            args:
                spec (Spec): The specifier for the connection.

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result
        """

        if spec is None:
            return Result.PARAMETER_ERROR
        err = Result.NO_ERROR

        self.__link = Link.create_link(spec)
        if self.__link is not None:
            status = self.__link.get_status()
            count = 0

            # Wait for two seconds trying to confirm we are connected...
            while status != _BS_C.RUNNING and count <= 1000:
                if status in (_BS_C.INVALID_LINK_STREAM, _BS_C.IO_ERROR, _BS_C.UNKNOWN_ERROR):
                    err = Result.IO_ERROR
                    break
                sleep(0.01)
                count += 1
                status = self.__link.get_status()

            if status != _BS_C.RUNNING:
                err = Result.NOT_READY
            else:
                self.autoNetwork()

            if err != Result.NO_ERROR and err != Result.NOT_READY:
                self.__link = None
            else:
                self.__spec = spec
        else:
            err = Result.RESOURCE_ERROR
        return err

    def autoNetwork(self):
        if self.bAutoNetworking:
            magic_address = self.__link.getModuleAddress()
            if magic_address.error == Result.NO_ERROR \
                    and magic_address.value != 0 \
                    and self.__address != magic_address.value:
                self.__address = magic_address.value

    def connectThroughLinkModule(self, module):
        """ Result.error: Connect to network module.

            Connects to a Brainstem module on a BrainStem network, through
            the module given as an argument. The module passed in must have
            an active valid connection.

            args:
                module (Module): The brainstem module to connec through.

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result

        """
        if module.isConnected():
            self.__link = module.link
            return Result.NO_ERROR
        else:
            return Result.CONNECTION_ERROR

    def connect(self, transport, serial_number):
        """ Result.error: Connect to a Module with a transport type and serial number.

            args:
                transport (Spec.transport): The transport to connect over.
                serial_number (int): Serial number of the module.

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result
        """
        if transport == Spec.TCPIP:
            spec = discover.findModule(transport, serial_number)
        else:
            spec = Spec(transport, serial_number, self.__address, 1)
        return self.connectFromSpec(spec)

    def isConnected(self):
        """ Returns true if the Module has an active connection or false otherwise"""
        # if we don't have a linkref we can't be connected.
        if self.__link is None:
            return False

        stat = self.__link.get_status()
        # We should ask our linkref, what the status is and return that.
        if stat == _BS_C.RUNNING:    # or stat == _BS_C.INITIALIZING:
            return True
        else:
            return False

    def getStatus(self):
        """ Returns the status of the BrainStem connection

            See brainstem.link.Status for the possiable states.

        """
        if self.__link is None:
            return Status.INVALID_LINK_STREAM
        else:
            return self.__link.get_status()

    def disconnect(self):
        """ Disconnect from the Brainstem module."""
        self.__link = None
        # We need to make sure the link is collected immediately... or it can
        # lead to driver wedging.
        gc.collect()

    def reconnect(self):
        """ Reconnect a lost connection to a Brainstem module."""
        if self.isConnected():
            return Result.NO_ERROR

        if self.__spec is not None:
            return self.connectFromSpec(self.__spec)
        else:
            return Result.CONFIGURATION_ERROR

    def setModuleAddress(self, address):
        """ Set the address of the module object.

            This method changes the local address of the module, not of the
            device. It is possible to set the module address of the device via
            system.setModuleSoftwareOffset().

            args:
                address (int): The module address to switch to for this module instance.

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result

        """
        if (address % 2) or (address > 254):
            return Result.PARAMETER_ERROR

        self.__address = address

        return Result.NO_ERROR

    def setNetworkingMode(self, mode):
        """ Set the networking mode of the module object.

            By default the module object is configured to automatically adjust
            its address based on the devices current module address.  So that,
            if the device has a software or hardware offset it will still be
            able to communicate with the device. If advanced networking is required
            the auto networking mode can be turned off.

            args:
                mode (bool):
                    True or 1 = Auto networking
                    False or 0 = Manual networking

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result

        """
        self.__bAutoNetworking = mode

        return Result.NO_ERROR

    def discoverAndConnect(self, transport, serial_number=None):
        """ Discover and connect from the Module level.

            A disover-based connect. This member function will connect to the first
            available BrainStem found on the given transport.  If the serial number is
            passed, it will only connect to the module with that serial number.
            Passing 0 or None as the serial number will create a link to the first
            link module found on the specified transport.

            args:
                transport (int): The module address to switch to for this module instance.
                serial_number (int): The module serial_number to look for.

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result
        """
        spec = None
        if serial_number is None or serial_number == 0:
            specs = discover.findAllModules(transport)
            for s in specs:
                if self.model == 0 or self.model == s.model:
                    spec = s
                    break
        else:
            spec = discover.findModule(transport, serial_number)

        if spec is not None:
            result = self.connectFromSpec(spec)
        else:
            return Result.NOT_FOUND

        return result


class Entity(object):
    """
    Base class for BrainStem Entity.

    Provides the default implementation for a functional entity within
    the BrainStem. This can include IO like GPIOs, Analogs etc. For a
    more detailed description of Entities see the `Terminology`_ section
    of the brainstem reference for more information.

    .. _Terminology:
        https://acroname.com/reference/terms.html

    """
    def __init__(self, module, command, index):
        """
         Initialize an Entity object.

         Args:
            module (Module): The Module this entity belongs to.
            command (int): The BrainStem command for the entity.
            index (int): The entity index for this entity instance.
        """
        self.__module = module
        self.__command = command
        self.__index = index

    @property
    def module(self):
        """Module: Return this entities module."""
        return self.__module

    @property
    def command(self):
        """int: Return the entitiy command."""
        return self.__command

    @property
    def index(self):
        """int: Return the entity index"""
        return self.__index

    def call_UEI(self, option):
        """ Result.error: Call a set UEI on this entity.

            args:
                option (int): The command option.

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result
        """
        uei = UEI()
        uei.type = UEI.VOID

        try:
            return self._set_UEI(option, uei)
        except struct.error:
            return Result.RANGE_ERROR

    def set_UEI8(self, option, value):
        """ Result.error: Call a set UEI with byte param on this entity.

            args:
                option (int): The command option.
                value (byte): The byte parameter to send.

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result
        """
        uei = UEI()
        uei.type = UEI.BYTE
        uei.value = value

        try:
            return self._set_UEI(option, uei)
        except struct.error:
            return Result.RANGE_ERROR

    def set_UEI8_with_subindex(self, option, subindex, value):
        """ Result.error: Call a set UEI with a subindex.

            args:
                option (int): The command option.
                subindex (byte): The subindex of the entity.
                param (byte): The byte parameter to send.

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result
        """
        uei = UEI()
        uei.type = UEI.BYTE
        uei.value = value
        uei.subindex = subindex

        try:
            return self._set_UEI(option, uei)
        except struct.error:
            return Result.RANGE_ERROR

    def set_UEI16(self, option, value):
        """ Result.error: Call a set UEI with short param on this entity.

            args:
                option (int): The command option.
                value (short): The short parameter to send.

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result
        """
        uei = UEI()
        uei.type = UEI.SHORT
        uei.value = value

        try:
            return self._set_UEI(option, uei)
        except struct.error:
            return Result.RANGE_ERROR

    def set_UEI32(self, option, value):
        """ Result.error: Call a set UEI with int param on this entity.

            args:
                option (int): The command option.
                value (int): The int parameter to send.

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result
        """
        uei = UEI()
        uei.type = UEI.INT
        uei.value = value

        try:
            return self._set_UEI(option, uei)
        except struct.error:
            return Result.RANGE_ERROR

    def set_UEI32_with_subindex(self, option, subindex, value):
        """ Result.error: Call a set UEI with a subindex.

            args:
                option (int): The command option.
                subindex (byte): The subindex of the entity.
                param (byte): The byte parameter to send.

            returns:
                Result.error: Returns an error result from the list of defined
                error codes in brainstem.result
        """
        uei = UEI()
        uei.type = UEI.INT
        uei.value = value
        uei.subindex = subindex

        try:
            return self._set_UEI(option, uei)
        except struct.error:
            return Result.RANGE_ERROR

    def get_UEI(self, option):
        """ Result.error: Get a UEI value.

            args:
                option (int): The command option.

            returns:
                Result: Returns a result object, whose value is set,
                        on with the requested value when the results error is
                        set to NO_ERROR
        """
        uei = UEI()
        uei.type = UEI.VOID
        return self._get_UEI(option, uei)

    def drain_UEI(self, option):
        """ drain UEI packets matchin option.

            args:
                option (int): The command option.

            returns:
                Result: Returns a result object, whose value is the number of
                        packets drained, and the error value set to NO_ERROR
        """
        return self.module.link.drain_UEI_packets(self.module.address,
                                                  self.command,
                                                  option | _BS_C.ueiOPTION_VAL,
                                                  self.index)

    def await_UEI_Val(self, option, timeout):
        return self.module.link.receive_UEI(self.module.address,
                                            self.command,
                                            option | _BS_C.ueiOPTION_VAL,
                                            self.index,
                                            timeout)

    def get_UEI_with_param(self, option, param):
        """ Result.error: Get a UEI value based on a parameter.

            args:
                option (int): The command option.
                param(byte): The command parameter

            returns:
                Result: Returns a result object, whose value is set,
                        on with the requested value when the results error is
                        set to NO_ERROR
        """
        uei = UEI()
        uei.type = UEI.BYTE
        uei.value = param
        return self._get_UEI(option, uei)

    def send_command(self, length, data, match_tuple):
        if self.module.link is None:
            return Result(_BS_C.aErrConnection, None)
        else:
            result = self.module.link.send_command_packet(self.module.address, self.command, length, data)
            if result == Result.NO_ERROR:
                result = self.module.link.receive_command_packet(self.module.address,
                                                                 self.command,
                                                                 match_tuple)

                return result
            else:
                return Result(result, None)

    def _fill_UEI(self, option, req_type, uei):
        """ Internal: fill a UEI object"""
        uei.module = self.module.address
        uei.command = self.command
        uei.option = req_type | option
        uei.specifier = _BS_C.ueiSPECIFIER_RETURN_HOST | self.index
        return uei

    def _get_UEI(self, option, uei):
        """ Internal: send get UEI"""
        if self.module.link is None:
            return Result(_BS_C.aErrConnection, None)
        else:
            self._fill_UEI(option, _BS_C.ueiOPTION_GET, uei)
            self.module.link.send_UEI(uei)
            result = self.module.link.receive_UEI(self.module.address,
                                                  self.command,
                                                  option | _BS_C.ueiOPTION_VAL,
                                                  self.index)
            return result

    def _set_UEI(self, option, uei):
        """ Internal: send set UEI"""
        if self.module.link is None:
            return _BS_C.aErrConnection
        else:
            self._fill_UEI(option, _BS_C.ueiOPTION_SET, uei)
            self.module.link.send_UEI(uei)
            result = self.module.link.receive_UEI(self.module.address,
                                                  self.command,
                                                  option | _BS_C.ueiOPTION_ACK,
                                                  self.index)
            return result.error
