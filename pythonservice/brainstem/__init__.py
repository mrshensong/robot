# Copyright (c) 2018 Acroname Inc. - All Rights Reserved
#
# This file is part of the BrainStem (tm) package which is released under MIT.
# See file LICENSE or go to https://acroname.com for full license details.

"""
A Package that enables communication with Acroname Brainstem Modules and
BrainStem networks.


"""
import os
import struct
from sys import platform
from ._brainstem_c import ffi
from platform import architecture


def BIT(n):
    return 1 << n


def is_base_string(data):
    try:
        basestring
    except NameError:
        basestring = str

    return isinstance(data, basestring)


def str_or_bytes_to_byte_list(data, start_index=None, end_index=None):
    if is_base_string(data):
        out_data = [ord(i) for i in data[start_index:end_index]]
    else:
        out_data = [i for i in data[start_index:end_index]]
    return out_data


def convert_int_args_to_bytes(args):
    bytes_data = b''
    for arg in args:
        if isinstance(arg, int) and 0 <= arg <= 255:
            bytes_data += struct.pack('B', arg)
        elif isinstance(arg, list) or isinstance(arg, tuple):
            for i in arg:
                if isinstance(i, int) and 0 <= i <= 255:
                    bytes_data += struct.pack('B', i)
                else:
                    raise ValueError('Invalid argument: %s must be int between 0 and 255.' % str(i))
        else:
            raise ValueError('Invalid argument: %s must be int or list/tuple of ints between 0 and 255.' % str(arg))

    return bytes_data


# Initialize the Brainstem C binding in init.
# Then you can import like so; 'from brainstem import _BS_C, ffi'
_BS_C = None
arch, plat = architecture()

try:
    if platform.startswith('darwin'):
        _BS_C = ffi.dlopen(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                        'libBrainStem2.dylib'))
    elif platform.startswith('win32'):
        if arch.startswith('32'):
            _BS_C = ffi.dlopen(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'x86', 'BrainStem2'))
        else:
            _BS_C = ffi.dlopen(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'x64', 'BrainStem2'))
    elif platform.startswith('linux'):
        _BS_C = ffi.dlopen(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libBrainStem2.so'))
    else:
        raise ImportError("Platform not supported")

# This exception is common when installing a whl that was built for a different platform.
# i.e. Installing a Windows compiled whl on a Mac.
# The platform checks above only serve to invoke the correct ffi command. If a whl was
# built for a different platform that means it won't have the correct underlying library.
except OSError:
    raise OSError("Confirm architecture. Was this whl built for another platform?")

# These imports must happen here following the initialization of the CFFI library.
from . import link
from . import discover
from . import stem
from . import defs
from . import version
from . import result
