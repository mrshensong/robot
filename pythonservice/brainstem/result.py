# Copyright (c) 2018 Acroname Inc. - All Rights Reserved
#
# This file is part of the BrainStem (tm) package which is released under MIT.
# See file LICENSE or go to https://acroname.com for full license details.

"""
A module that provides a result class for returning results of UEI commands.

Results consist of an error attribute and a value attribute. If the error
attribute is set to NO_ERROR, then the result value is the response to the
UEI command that was sent.

For more information about return values for commands and UEI's
see the `Acroname BrainStem Reference`_

.. _Acroname BrainStem Reference:
    https://acroname.com/reference
"""
from . import _BS_C


class Result(object):
    """ Result class for returning results of commands

        Instances of Result represent the response to a command. The Result class
        also contains constants representing the possible errors that may be encountered
        during interaction with a BrainStem module.
    """

    NO_ERROR = _BS_C.aErrNone                               # 0: No Error occurred.
    MEMORY_ERROR = _BS_C.aErrMemory                         # 1: Memory allocation/de-allocation error.
    PARAMETER_ERROR = _BS_C.aErrParam                       # 2: Invalid parameters given.
    NOT_FOUND = _BS_C.aErrNotFound                          # 3: Entity, module or information not found.
    FILE_NAME_LENGTH_ERROR = _BS_C.aErrFileNameLength       # 4: File name is to long.
    BUSY = _BS_C.aErrBusy                                   # 5: Module or resource is currently busy.
    IO_ERROR = _BS_C.aErrIO                                 # 6: An Input/Output error occurred.
    MODE_ERROR = _BS_C.aErrMode                             # 7: Invalid Mode or mode not accessible for current state.
    WRITE_ERROR = _BS_C.aErrWrite                           # 8: Write error occurred.
    READ_ERROR = _BS_C.aErrRead                             # 9: Read error occurred.
    EOF_ERROR = _BS_C.aErrEOF                               # 10: Unexpected end of file encountered.
    NOT_READY = _BS_C.aErrNotReady                          # 11: Resource not ready.
    PERMISSION_ERROR = _BS_C.aErrPermission                 # 12: Insufficient permissions.
    RANGE_ERROR = _BS_C.aErrRange                           # 13: Request is outside of valid range.
    SIZE_ERROR = _BS_C.aErrSize                             # 14: Size is incorrect for resource.
    OVERRUN_ERROR = _BS_C.aErrOverrun                       # 15: Buffer was overrun or will be.
    PARSE_ERROR = _BS_C.aErrParse                           # 16: Unable to parse command.
    CONFIGURATION_ERROR = _BS_C.aErrConfiguration           # 17: Configuration is invalid.
    TIMEOUT = _BS_C.aErrTimeout                             # 18: Timeout occurred.
    INITIALIZATION_ERROR = _BS_C.aErrInitialization         # 19: Could not initialize resource.
    VERSION_ERROR = _BS_C.aErrVersion                       # 20: Version mismatch
    UNIMPLEMENTED_ERROR = _BS_C.aErrUnimplemented           # 21: Functionality unavailable or unimplemented.
    DUPLICATE = _BS_C.aErrDuplicate                         # 22: Duplicate request received.
    CANCELED = _BS_C.aErrCancel                             # 23: Request was canceled
    PACKET_ERROR = _BS_C.aErrPacket                         # 24: packet was invalid or had invalid contents.
    CONNECTION_ERROR = _BS_C.aErrConnection                 # 25: connection is no longer valid, or was closed.
    INDEX_RANGE_ERROR = _BS_C.aErrIndexRange                # 26: Requested entity does not exist.
    SHORT_COMMAND_ERROR = _BS_C.aErrShortCommand            # 27: Command to short, not enough data to parse.
    INVALID_ENTITY_ERROR = _BS_C.aErrInvalidEntity          # 28: Entity is not available, or does not exist.
    INVALID_OPTION_ERROR = _BS_C.aErrInvalidOption          # 29: Option for given entity is invalid.
    RESOURCE_ERROR = _BS_C.aErrResource                     # 30: Error allocating or acquiring a resource.
    MEDIA_ERROR = _BS_C.aErrMedia                           # 31: Media not found or not available.
    UNKNOWN_ERROR = _BS_C.aErrUnknown                       # 32: Unknown error encountered.

    def __init__(self, error, value):
        """ Initialize a Result object

            args:
                error (int): The error value.
                value (int): the result value.
        """
        self._error = error
        self._value = value

    @property
    def error(self):
        """ Return the error attribute"""
        return self._error

    @property
    def value(self):
        """ Return the value attribute"""
        return self._value

    def __repr__(self):
        """ Return a representation of the Result object"""
        return "<id(%x) %s>" % (id(self), str(self))

    def __str__(self):
        """ Pretty print the Result object"""
        return "<Result(%s): %s>" % (self.error, str(self.value))
