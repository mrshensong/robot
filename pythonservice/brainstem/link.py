# Copyright (c) 2018 Acroname Inc. - All Rights Reserved
#
# This file is part of the BrainStem (tm) package which is released under MIT.
# See file LICENSE or go to https://acroname.com for full license details.

"""
A module that provides a Spec class for specifying a connection to a BrainStem module.

A Spec instance fully describes a connection to a brainstem module. In the case of
USB based stems this is simply the serial number of the module. For TCPIP based stems
this is an IP address and TCP port.

For more information about links and the Brainstem network
see the `Acroname BrainStem Reference`_

.. _Acroname BrainStem Reference:
    https://acroname.com/reference
"""
import socket
import struct


class Status(object):
    """ Status variables represent the link status possibilities for Brainstem Links.

        Status States:
            * STOPPED (0)
            * INITIALIZING (1)
            * RUNNING (2)
            * STOPPING (3)
            * SYNCING (4)
            * INVALID_LINK_STREAM (5)
            * IO_ERROR (6)
            * UNKNOWN_ERROR (7)

    """

    STOPPED = 0
    INITIALIZING = 1
    RUNNING = 2
    STOPPING = 3
    SYNCING = 4
    INVALID_LINK_STREAM = 5
    IO_ERROR = 6
    UNKNOWN_ERROR = 7


class Spec(object):
    """ Spec class for specifying connection details

        Instances of Spec represent the connection details for a brainstem link.
        The Spec class also contains constants representing the possible transport
        types for BrainStem modules.

        args:
            transport (int): One of USB or TCPIP.
            serial_number (int): The module serial number.
            module: The module address on the Brainstem network.
            model: The device model number of the Brainstem module.
            **keywords: For TCPIP modules the possibilities are,

                        * ip_address: (int) The IP address of the module.
                        * tcp_port: (int) The TCP port of the module.

        Attributes:
            transport (USB/TCPIP): instance attribute holding transport type.
            serial_number (int): Module serial number.
            module (int): Module address.
            model (int): Brainstem device type: See Defs module for listing.
            ip_address (Optional[int]): IP address for TCP/IP based modules.
            tcp_port (Optional[int]): TCP port for TCP/IP based modules.

    """
    USB = 1                             #: USB transport type.
    TCPIP = 2                           #: TCPIP transport type.

    def __init__(self, transport, serial_number, module, model, **keywords):

        self.transport = transport
        self.serial_number = serial_number
        self.module = module

        # Model was added in 2.2.0  This adds legacy support
        if model == 1:
            self.model = 'BrainStem'
        elif model == 2:
            self.model = 'MTM-IO-Serial'
        else:
            self.model = model

        for key in keywords.keys():
            if key == 'ip_address':
                if isinstance(keywords[key], int):
                    self.ip_address = keywords[key]
                else:
                    try:
                        self.ip_address = socket.inet_aton(keywords[key])
                    except socket.error:
                        pass

            if key == 'tcp_port':
                if isinstance(keywords[key], int):
                    self.tcp_port = keywords[key]
                else:
                    try:
                        self.tcp_port = int(keywords[key])
                    except ValueError:
                        pass

    def __str__(self):
        type_string = "USB"
        if self.transport == Spec.TCPIP:
            type_string = "TCPIP"

        addr, port = ('', '')
        if hasattr(self, 'ip_address'):
            addr = ", IP Address: %s" % socket.inet_ntoa(struct.pack('!I', socket.htonl(self.ip_address)))
        if hasattr(self, 'tcp_port'):
            port = ", TCP Port: %d" % self.tcp_port
        return 'Model: %s LinkType: %s(serial: %08X%s%s)' % (self.model, type_string, self.serial_number, addr, port)
