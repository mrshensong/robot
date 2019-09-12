# Copyright (c) 2018 Acroname Inc. - All Rights Reserved
#
# This file is part of the BrainStem (tm) package which is released under MIT.
# See file LICENSE or go to https://acroname.com for full license details.

import signal
import threading
import struct

from . import _BS_C, ffi, str_or_bytes_to_byte_list
from .link import Spec
from .result import Result


class UEI(object):

    VOID = 0
    BYTE = 1
    SHORT = 2
    INT = 4

    def __init__(self):
        self.module = 0
        self.command = 0
        self.option = 0
        self.specifier = 0
        self._subindex = None
        self.value = 0
        self._type = UEI.VOID
        self.length = 3

    def __str__(self):
        ret = 'UEI:\n'
        ret = ret + '  Module: 0x%x\n' % self.module
        ret = ret + '  Command: 0x%x\n' % self.command
        ret = ret + '  Option: 0x%x\n' % self.option
        ret = ret + '  specifier: 0x%x\n' % self.specifier
        ret = ret + '  type: %d\n' % self.type
        if self.subindex is not None:
            ret = ret + '  subindex: %d\n' % self.subindex
        ret = ret + '  value: %d\n' % self.value
        return ret

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value
        self.length = self.length + value

    @property
    def subindex(self):
        return self._subindex

    @subindex.setter
    def subindex(self, value):
        self._subindex = value
        self.length = self.length + 1

    def init_with_bytearray(self, module, byte_array):
        self.module = module
        self.command, self.option, self.specifier = struct.unpack('BBB', byte_array[0:3])
        try:
            self.value, = struct.unpack('>I', byte_array[3:])
            self.type = UEI.INT
        except struct.error:
            try:
                self.value, = struct.unpack('>H', byte_array[3:])
                self.type = UEI.SHORT
            except struct.error:
                try:
                    self.value, = struct.unpack('B', byte_array[3:])
                    self.type = UEI.BYTE
                except struct.error:
                    self.type = UEI.VOID

    def as_bytearray(self):
        result = struct.pack('BBB', self.command, self.option, self.specifier)
        if self.subindex is not None:
            result = result + struct.pack('B', self.subindex)
        if self.type == UEI.BYTE:
            result = result + struct.pack('B', self.value)
        elif self.type == UEI.SHORT:
            result = result + struct.pack('>H', self.value)
        elif self.type == UEI.INT:
            result = result + struct.pack('BBBB',
                                          (self.value >> 24) & 0xFF,
                                          (self.value >> 16) & 0xFF,
                                          (self.value >> 8) & 0xFF,
                                          self.value & 0xFF
                                          )
        return result


class _Packet(object):

    def __init__(self):
        self.address = 0
        self.length = 0
        self.data = None

    def init_with_cpacket(self, cpacket):
        # grab the length and data from the cpacket.
        self.address = cpacket.address
        self.length = cpacket.dataSize
        buff = ffi.buffer(cpacket.data, self.length)
        self.data = buff[:]
        packetref = ffi.new('aPacket*')
        packetref[0] = cpacket
        _BS_C.aPacket_Destroy(packetref)

    def init_with_data(self, address, length, byte_array):
        if length <= (_BS_C.MAX_PACKET_BYTES - 0):
            self.address = address
            self.length = length
            self.data = byte_array
            return Result.NO_ERROR
        else:
            return Result.OVERRUN_ERROR

    def cpacket(self):
        # strange syntax here, we don't want to allocate space for the NULL
        # terminator.
        if self.length <= (_BS_C.MAX_PACKET_BYTES - 0):
            try:
                data = ffi.new("uint8_t[]", self.data[:self.length])
                return _BS_C.aPacket_CreateWithData(self.address, self.length, data)
            except TypeError:
                return ffi.NULL
        else:
            return ffi.NULL


# The link class manages the link to the stem. We REALLY only want one
# link to be created. Users should never directly instanciate a Link object.
# instead they should call the static method create_link.
class Link(object):

    def __init__(self, spec, clinkref):
        self.__spec = spec
        self.__clinkref = clinkref
        # Keep this around... We rely on the library being open
        # when the link object is destroyed... and we can't rely
        # on the teardown order in the interpreter, so we store a
        # reference here.
        self.__libref = _BS_C

    # When we're destroyed... clean up memory.
    def __del__(self):
        if self.__clinkref is None:
            return

        linkref = ffi.new("aLinkRef*")
        linkref[0] = self.__clinkref
        _BS_C.aLink_Destroy(linkref)

    @staticmethod
    def create_link(spec):
        link = None
        # new link interfacee
        clink = None

        if spec.transport == Spec.USB:
            clink = _BS_C.aLink_CreateUSB(spec.serial_number)
        elif spec.transport == Spec.TCPIP:
            clink = _BS_C.aLink_CreateTCPIP(spec.ip_address, spec.tcp_port)

        if clink != ffi.NULL:  # Then we need to add it to our instances list.
            link = Link(spec, clink)

        # Either returns valid link or None.
        return link

    # Need to reset the link because some error occured. Deletes old clink,
    # and starts a new one. Returning an error if this does not succeed.
    # This can raise and exception if we have problems deleting the stream,
    # or creating a new one. This is usually fatal, ane will require resetting
    # hardware or other User intervention.
    def reset_link(self):

        if self.__clinkref is not None and self.__clinkref != ffi.NULL:
            linkref = ffi.new("aLinkRef*")
            linkref[0] = self.__clinkref
            err = _BS_C.aLink_Destroy(linkref)
            # Possible Fatal error here.
            self.__clinkref = ffi.NULL
            if err != _BS_C.aErrNone and err != _BS_C.aErrParam:
                raise IOError("Error %d Destroying stream in reset." % err)

        clink = ffi.NULL
        # Create the stream based on transport and serial number
        if self.__spec.transport == Spec.USB:
            clink = _BS_C.aLink_CreateUSB(self.__spec.serial_number)
        elif self.__spec.transport == Spec.TCPIP:
            clink = _BS_C.aLink_CreateSocket(self.__spec.ip_address, self.__spec.tcp_port)
        self.__clinkref = clink

    def get_status(self):

        if self.__clinkref is not None:
            ret = _BS_C.aLink_GetStatus(self.__clinkref)
        else:
            ret = _BS_C.INVALID_LINK_STREAM

        return ret

    def send_packet(self, module, length, data):
        if self.__clinkref is not None:
            packet = _Packet()
            err = packet.init_with_data(module, length, data)
            if err == Result.NO_ERROR:
                cpacket = packet.cpacket()
                if cpacket != ffi.NULL:
                    # print (cpacket.address, cpacket.dataSize) + tuple([ord(i) for i in ffi.buffer(cpacket.data)[:]])
                    err = _BS_C.aLink_PutPacket(self.__clinkref, cpacket)
                    pr = ffi.new("aPacket**")
                    pr[0] = cpacket
                    _BS_C.aPacket_Destroy(pr)
                else:
                    err = Result.RESOURCE_ERROR
        else:
            err = Result.CONNECTION_ERROR
        return err

    def send_UEI(self, uei):
        return self.send_packet(uei.module, uei.length, uei.as_bytearray())

    def send_command_packet(self, module, command, length, data):
        return self.send_packet(module, length + 1, struct.pack('B', command) + data)

    def drain_UEI_packets(self, module, command, option, index):
        if self.__clinkref is not None:

            uei = UEI()
            uei.module = module
            uei.command = command
            uei.option = option
            uei.specifier = index
            count = _BS_C.aLink_DrainPackets(self.__clinkref, self._UEIFilter, ffi.new_handle(uei))
            return Result(Result.NO_ERROR, count)
        else:
            return Result(Result.CONNECTION_ERROR, 0)

    def receive_UEI(self, module, command, option, index, timeout=1000):
        if self.__clinkref is not None:

            uei = UEI()
            uei.module = module
            uei.command = command
            uei.option = option
            uei.specifier = index
            cpacket = _BS_C.aLink_AwaitFirst(self.__clinkref, self._UEIFilter, ffi.new_handle(uei), timeout)
            if cpacket != ffi.NULL:
                pr = ffi.new("aPacket**")
                pr[0] = cpacket
                _BS_C.aPacket_Destroy(pr)
                if (uei.specifier & _BS_C.ueiREPLY_ERROR) != 0:
                    return Result(uei.value, 0)
                else:
                    return Result(Result.NO_ERROR, uei.value)
            else:
                return Result(Result.TIMEOUT, 0)
        else:
            return Result(Result.CONNECTION_ERROR, 0)

    def receive_command_packet(self, module, command, match_tuple=(), timeout=1000):
        if self.__clinkref is not None:

            @ffi.callback("uint8_t(aPacket*, void*)")
            def command_filter(cfpacket, ref):
                try:
                    if isinstance(threading.current_thread(), threading._MainThread):
                        signal.signal(signal.SIGINT, signal.SIG_IGN)
                        if hasattr(signal, 'SIGQUIT'):
                            signal.signal(signal.SIGQUIT, signal.SIG_IGN)

                    match_params = ffi.from_handle(ref)
                    packet = ffi.buffer(cfpacket.data)
                    # copy ffi.buffer object into regular byte string.
                    packet = packet[:]
                    packet = tuple(str_or_bytes_to_byte_list(packet))
                    packet = (cfpacket.address,) + packet

                    def teq(tvalues):
                        for val in tvalues:
                            if not val:
                                return False
                        return True

                    def chkeq(frec, fmatch):
                        if type(fmatch) is list:
                            return frec in fmatch
                        else:
                            return frec == fmatch

                    return teq([chkeq(lrec, lmatch) for lrec, lmatch in zip(packet, match_params)])
                finally:
                    if isinstance(threading.current_thread(), threading._MainThread):
                        signal.signal(signal.SIGINT, signal.SIG_DFL)
                        if hasattr(signal, 'SIGQUIT'):
                            signal.signal(signal.SIGQUIT, signal.SIG_DFL)

            match = (module, command) + match_tuple
            cpacket = _BS_C.aLink_AwaitFirst(self.__clinkref, command_filter, ffi.new_handle(match), timeout)
            if cpacket != ffi.NULL:
                buff = ffi.buffer(cpacket.data)
                result = Result(Result.NO_ERROR, buff[:])
                result._length = cpacket.dataSize
                pr = ffi.new("aPacket**")
                pr[0] = cpacket
                _BS_C.aPacket_Destroy(pr)
                return result
            else:
                return Result(Result.TIMEOUT, None)
        else:
            return Result(Result.CONNECTION_ERROR, None)

    def getModuleAddress(self):
        return self.send_magic_command()

    def recieve_magic_command(self):
        if self.__clinkref is not None:

            # Special case callback for cmdMAGIC
            # ref is unused, however it needs to exist to match filterproc.
            @ffi.callback("uint8_t(aPacket*, void*)")
            def command_MAGIC(cfpacket, ref):
                try:
                    if isinstance(threading.current_thread(), threading._MainThread):
                        signal.signal(signal.SIGINT, signal.SIG_IGN)
                        if hasattr(signal, 'SIGQUIT'):
                            signal.signal(signal.SIGQUIT, signal.SIG_IGN)

                    if cfpacket.address > 0 and cfpacket.dataSize == 0:
                        return True
                    else:
                        return False
                finally:
                    if isinstance(threading.current_thread(), threading._MainThread):
                        signal.signal(signal.SIGINT, signal.SIG_DFL)
                        if hasattr(signal, 'SIGQUIT'):
                            signal.signal(signal.SIGQUIT, signal.SIG_DFL)

            match = (0, 0)
            cpacket = _BS_C.aLink_AwaitFirst(self.__clinkref, command_MAGIC, ffi.new_handle(match), 1000)
            if cpacket != ffi.NULL:
                result = Result(Result.NO_ERROR, cpacket.address)
                pr = ffi.new("aPacket**")
                pr[0] = cpacket
                _BS_C.aPacket_Destroy(pr)
                return result
            else:
                return Result(Result.TIMEOUT, None)

        else:
            return Result(Result.CONNECTION_ERROR, None)

    def send_magic_command(self):
        data = struct.pack('B', 0)
        err = self.send_packet(_BS_C.cmdMAGIC, 0, data)
        if err == Result.NO_ERROR:
            return self.recieve_magic_command()
        else:
            return Result(err, None)

    @staticmethod
    @ffi.callback("uint8_t(aPacket*, void*)")
    def _UEIFilter(cpacket, ref):
        try:
            if isinstance(threading.current_thread(), threading._MainThread):
                signal.signal(signal.SIGINT, signal.SIG_IGN)
                if hasattr(signal, 'SIGQUIT'):
                    signal.signal(signal.SIGQUIT, signal.SIG_IGN)

            uei = ffi.from_handle(ref)
            if uei.module == cpacket.address and \
               cpacket.dataSize >= 3 and \
               uei.command == cpacket.data[0] and \
               uei.option == cpacket.data[1] and \
               uei.specifier == (cpacket.data[2] & _BS_C.ueiSPECIFIER_INDEX_MASK):

                # Set the response specifier... could be an error.
                uei.specifier = cpacket.data[2]

                if (uei.specifier & _BS_C.ueiREPLY_ERROR) != 0:
                    buff = ffi.buffer(cpacket.data, cpacket.dataSize)
                    uei.value, = struct.unpack('B', buff[3])
                    uei.type = UEI.BYTE
                    return 1

                if cpacket.dataSize == 3:
                    uei.type = UEI.VOID
                    uei.value = 0
                    return 1
                elif cpacket.dataSize == 4:
                    uei.type = UEI.BYTE
                    buff = ffi.buffer(cpacket.data, cpacket.dataSize)
                    uei.value, = struct.unpack('B', buff[3])
                    return 1
                elif cpacket.dataSize == 5:
                    uei.type = UEI.SHORT
                    buff = ffi.buffer(cpacket.data, cpacket.dataSize)
                    uei.value, = struct.unpack('>H', buff[3:])
                    return 1
                elif cpacket.dataSize == 7:
                    uei.type = UEI.INT
                    buff = ffi.buffer(cpacket.data, cpacket.dataSize)
                    uei.value, = struct.unpack('>I', buff[3:])
                    return 1
                else:
                    return 0
            else:
                return 0
        finally:
            if isinstance(threading.current_thread(), threading._MainThread):
                signal.signal(signal.SIGINT, signal.SIG_DFL)
                if hasattr(signal, 'SIGQUIT'):
                    signal.signal(signal.SIGQUIT, signal.SIG_DFL)
