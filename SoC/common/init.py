#!/usr/bin/env python3

import argparse
import binascii
import serial
import struct
import sys
import time


class EchoBytesMismatchException(Exception):
    pass

class NotEnoughDataException(Exception):
    pass

class Bmo:
    commands = {
        'EXIT': ord(b'\r'),
        'READ': ord(b'R'),
        'WRITE': ord(b'W'),
        'SETBAUD': ord(b'S'),
        'MEM_READ': ord(b'r'),
        'MEM_WRITE': ord(b'w'),
    }

    def __init__(self, port, baudrate=115200, timeout=1, write_timeout=1, debug=False, verbose=False):
        self.debug = debug
        self.verbose = verbose or debug
        self.ser = serial.Serial(port, baudrate, timeout=timeout, write_timeout=write_timeout)
        self._send_bytes(b'\r' * 10)
        try:
            self._recv_bytes(1000)
        except:
            pass
        self._send_bytes(b'bmo\r', echo=True)
        ack = self._recv_bytes(5)
        print(ack)
        assert ack == b'\nOK\r\n'

    def close(self):
        self.ser.close()

    def _send_bytes(self, data, echo=False):
        data = bytes(data)
        if self.debug:
            print("-> {}".format(binascii.b2a_hex(data)))
        self.ser.write(data)
        if echo:
            echo_data = self.ser.read(len(data))
            if self.debug:
                print("<- {}".format(binascii.b2a_hex(echo_data)))
            if echo_data != data:
                raise EchoBytesMismatchException

    def _recv_bytes(self, count):
        data = self.ser.read(count)
        if self.debug:
            print("<- {}".format(binascii.b2a_hex(data)))
        if len(data) != count:
            raise NotEnoughDataException
        return bytes(data)

    def get_dword(self):
        '''Read a little-endian 32-bit integer from the serial port.'''
        return struct.unpack('<I', self._recv_bytes(4))[0]

    def put_dword(self, dword):
        '''Write a little-endian 32-bit integer to the serial port.'''
        self._send_bytes(struct.pack('<I', dword))

    def exit(self):
        '''Exits binary mode.'''

        self._send_bytes([self.commands['EXIT']])

    def readw(self, addr):
        '''Read a 32-bit word.

        addr: The 32-bit starting address as an int.
        '''
        self._send_bytes([self.commands['READ']])
        self.put_dword(addr)

        word = self.get_dword()

        if self.verbose:
            print("0x{:08x} => 0x{:08x}".format(addr, word))

        return word

    def writew(self, addr, word):
        '''Write a 32 bit word.

        addr: A 32-bit address as an int.
        word: The 32-bit word to write.
        '''
        if self.verbose:
            print("0x{:08x} <= 0x{:08x}".format(addr, word))

        self._send_bytes([self.commands['WRITE']])
        self.put_dword(addr)
        self.put_dword(word)

    def setbaud(self, baudrate):
        '''Sets the baudrate.'''

        self._send_bytes([self.commands['SETBAUD']])
        self.put_dword(baudrate)
        self.close()

    def memory_read(self, addr, count, fast=False, print_speed=False):
        '''Read a range of memory to a byte array.

        addr: A 32-bit address as an int.
        count: The length of data to read, in bytes.
        '''
        word_count = count//4
        if (count % 4) > 0:
            word_count += 1

        data = b''
        if fast:
            aligned_count = word_count * 4

            self._send_bytes([self.commands['MEM_READ']])
            self.put_dword(addr)
            self.put_dword(aligned_count)

            block_size = 0x1000
            cbs = block_size
            start_ns = time.perf_counter_ns()
            for i in range(0, aligned_count, block_size):
                if aligned_count - i < cbs:
                    cbs = aligned_count - i
                data += self._recv_bytes(cbs)
                time.sleep(0.0001)
            end_ns = time.perf_counter_ns()
        else:
            start_ns = time.perf_counter_ns()
            for i in range(word_count):
                data += struct.pack('<I', self.readw(addr + i * 4))
            end_ns = time.perf_counter_ns()
        data = data[:count]

        if print_speed:
            elapsed = end_ns - start_ns
            print("Read {} bytes in {:.6f} seconds ({} bytes per second).".format(len(data), elapsed/1000000000, len(data)*1000000000//elapsed))

        return data

    def memory_write(self, addr, data, fast=False, print_speed=False):
        '''Write a byte array to a range of memory.

        addr: A 32-bit address as an int.
        data: The data to write.
        '''
        data = bytes(data)

        # Pad the byte array.
        padded_data = data
        remaining_bytes = (len(padded_data) % 4)
        if remaining_bytes > 0:
            padded_data += b'\0' * (4 - remaining_bytes)

        if fast:
            self._send_bytes([self.commands['MEM_WRITE']])
            self.put_dword(addr)
            self.put_dword(len(padded_data))

            block_size = 0x1000
            start_ns = time.perf_counter_ns()
            for i in range(0, len(padded_data), block_size):
                self._send_bytes(padded_data[i:i+block_size])
                time.sleep(0.0001)
            end_ns = time.perf_counter_ns()
        else:
            start_ns = time.perf_counter_ns()
            for i in range(0, len(padded_data), 4):
                self.writew(addr + i, struct.unpack_from('<I', padded_data, i)[0])
            end_ns = time.perf_counter_ns()

        if print_speed:
            elapsed = end_ns - start_ns
            print("Wrote {} bytes in {:.6f} seconds ({} bytes per second).".format(len(data), elapsed/1000000000, len(data)*1000000000//elapsed))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str, help="The serial port you want to connect to.")
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help="The baud rate you want to connect at. Default: 115200")
    parser.add_argument('-s', '--baudrate-next', type=int, default=115200, help="The baud rate you want to switch to. Default: 115200")
    args = parser.parse_args()

    bmo = Bmo(args.port, baudrate=args.baudrate, debug=False)
    if args.baudrate_next != args.baudrate:
        print("Switching to baudrate to {}...".format(args.baudrate_next))
        bmo.setbaud(args.baudrate_next)

        bmo = Bmo(args.port, baudrate=args.baudrate_next, debug=False)

    #bmo.debug = True
    #bmo.debug = False

    print(bmo.memory_read(0, 0x10000, print_speed=True).hex())
