# Copyright (c) 2018 Acroname Inc. - All Rights Reserved
#
# This file is part of the BrainStem (tm) package which is released under MIT.
# See file LICENSE or go to https://acroname.com for full license details.

"""
A module that provides methods for discovering brainstem modules over USB and TPCIP.

The discovery module provides an interface for locating BrainStem modules accross
multiple transports. It provides a way to find all modules for a give transport
as well as specific modules by serial number, or first found. The result of a call
to one of the discovery functions is either a list of brainstem.link.Spec objects,
or a single brainstem.link.Spec.

The Discovery module allows users to find specific brainstem devices via their
serial number, or a list of all devices connected to the host via usb or on the
same subnet via TCP/IP. In all cases a :doc:`Spec <link>` object is returned with
connection details for the device. In addition do connection details, the BrainStem
model is returned. This model is one of a list of BrainStem device model numbers
which are accessible via the :doc:`defs <defs>` module.

A typical interactive python session finding all connected USB modules might look
like the following.

    >> import brainstem
    >> module_list = brainstem.discover.findAllModules(brainstem.link.Spec.USB)
    >> print [str(s) for s in module_list]
    ['Model: 4 LinkType: USB(serial: 0xCB4A3B25, module: 0)', 'Model: 13 LinkType: USB(serial: 0x40F5849A, module: 0)']

For an overview of links, discovery and the Brainstem network
see the `Acroname BrainStem Reference`_

.. _Acroname BrainStem Reference:
    https://acroname.com/reference
"""

from . import _BS_C, ffi
from .link import Spec


def findModule(transports, serial_number):
    """ Return the Spec for the module with the given serial number.

        Transports can be presented as a list. TCPIP modules
        take a little longer to find due to the Multicast and gather
        necessary for finding modules on the local network segment.

        args:
            transports (list(int)): A list of transports or a single transport.
            serial_number (int): The module serial_number to look for.

        Return:
            Spec: The connection spec for the module whose serial number is
                  given in the args.
    """
    _result = None

    if not hasattr(transports, '__iter__'):
        transports = [transports]

    for trans in transports:
        # translate python Spec to C enum type.
        _trans = _get_c_transport(trans)
        if _trans is None:
            return _result

        # Now get a linkSpec* variable if there is a module.
        _cspec = _BS_C.aDiscovery_FindModule(_trans, serial_number)

        if _cspec != ffi.NULL:
            _result = _get_python_find_result(_cspec)
            # Free the memory allocated by the C Lib call. CFFI didn't allocate,
            # so the _cspec doesn't "own" the memory and it won't be GC'd
            linkref = ffi.new('linkSpec**')
            linkref[0] = _cspec
            _BS_C.aLinkSpec_Destroy(linkref)

    # return translated result or None if not found.
    return _result


def findFirstModule(transport):
    """ Return the Spec for the first module found on the given transport.

       TCPIP modules take a little longer to find due to the Multicast and
       gather necessary for finding modules on the local network segment.

        args:
            transport (int): One of USB or TCPIP.

        return:
            Spec: The connection spec of the first module found on the
                  given transport.
    """
    _result = None

    if not hasattr(transport, '__iter__'):
        transport = [transport]

    for trans in transport:
        # translate python Spec to C enum type.
        _trans = _get_c_transport(trans)
        if _trans is None:
            return _result

        # Now get a linkSpec* variable if there is a module.
        _cspec = _BS_C.aDiscovery_FindFirstModule(_trans)

        if _cspec != ffi.NULL:
            _result = _get_python_find_result(_cspec)
            # Free the memory allocated by the C Lib call. CFFI didn't allocate,
            # so the _cspec doesn't "own" the memory and it won't be GC'd
            linkref = ffi.new('linkSpec**')
            linkref[0] = _cspec
            _BS_C.aLinkSpec_Destroy(linkref)

    # return translated result or None if not found.
    return _result


def findAllModules(transports):
    """ Return a list of Specs for all modules found on the transports given.

        Transports can be presented as a list, and the results would be
        a list of all modules found for those transports. TCPIP modules
        take a little longer to find due to the Multicast and gather
        necessary for finding modules on the local network segment.

        args:
            transports (list(int)): A list of transports or a single transport.

        Return:
            list(Spec): A list of the Specs for all modules found.
    """
    _results = list()
    _cresults = ffi.new_handle(_results)

    @ffi.callback("_Bool(linkSpec*, _Bool*, void*)")
    def findAll(spec, success, context):
        results = ffi.from_handle(context)
        device = _get_python_find_result(spec)
        results.append(device)
        success[0] = True
        return True

    if not hasattr(transports, '__iter__'):
        transports = [transports]

    for trans in transports:
        # translate python Spec to C enum type.
        _trans = _get_c_transport(trans)
        if _trans is None:
            return _results

        _BS_C.aDiscovery_EnumerateModules(_trans, findAll, _cresults)

    return _results


def _get_c_transport(transport):
    """ Internal: Translate Spec transport to cffi transport"""
    _trans = None
    if transport == Spec.USB:
        _trans = _BS_C.USB
    if transport == Spec.TCPIP:
        _trans = _BS_C.TCPIP
    return _trans


def _get_python_find_result(cspec):
    """ Internal: Translate cffi spec into python Spec"""
    if cspec.type == _BS_C.USB:
        result = Spec(Spec.USB, cspec.serial_num, cspec.module, cspec.model)
    else:
        result = Spec(Spec.TCPIP, cspec.serial_num, cspec.module, cspec.model,
                      ip_address=cspec.t.ip.ip_address, tcp_port=cspec.t.ip.ip_port)
    return result
