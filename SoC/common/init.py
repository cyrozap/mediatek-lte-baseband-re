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
    }

    def __init__(self, port, baudrate=115200, timeout=1, write_timeout=1, debug=False):
        self.debug = debug
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
        words = []

        self._send_bytes([self.commands['READ']])
        self.put_dword(addr)

        return self.get_dword()

    def writew(self, addr, word):
        '''Write a 32 bit word.

        addr: A 32-bit address as an int.
        word: The 32-bit word to write.
        '''
        self._send_bytes([self.commands['WRITE']])
        self.put_dword(addr)
        self.put_dword(word)

    def memory_read(self, addr, count, print_speed=False):
        '''Read a range of memory to a byte array.

        addr: A 32-bit address as an int.
        count: The length of data to read, in bytes.
        '''
        word_count = count//4
        if (count % 4) > 0:
            word_count += 1

        data = b''
        start_time = time.time()
        for i in range(word_count):
            data += struct.pack('<I', self.readw(addr + i * 4))
        end_time = time.time()
        data = data[:count]

        if print_speed:
            elapsed = end_time - start_time
            print("Read {} bytes in {:.6f} seconds ({} bytes per second).".format(len(data), elapsed, int(len(data)/elapsed)))

        return data

    def memory_write(self, addr, data, print_speed=False):
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

        start_time = time.time()
        for i in range(0, len(padded_data), 4):
            self.writew(addr + i, struct.unpack_from('<I', padded_data, i)[0])
        end_time = time.time()

        if print_speed:
            elapsed = end_time - start_time
            print("Wrote {} bytes in {:.6f} seconds ({} bytes per second).".format(len(data), elapsed, int(len(data)/elapsed)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str, help="The serial port you want to connect to.")
    args = parser.parse_args()

    bmo = Bmo(args.port, debug=False)

    #bmo.debug = True
    #bmo.debug = False

    print(bmo.memory_read(0, 0x10000, print_speed=True).hex())
