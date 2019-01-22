#!/usr/bin/env python3

import argparse
import binascii
import serial
import struct


def auto_int(i):
    return int(i, 0)

def hex_int(i):
    return int(i, 16)


class UsbDl:
    commands = {
        'CMD_READ32': 0xD1,
        'CMD_WRITE32': 0xD4,
        'CMD_JUMP_DA': 0xD5,
        'CMD_GET_TARGET_CONFIG': 0xD8,
        'CMD_UART1_LOG_EN': 0xDB,
        'CMD_GET_HW_SW_VER': 0xFC,
        'CMD_GET_HW_CODE': 0xFD,
    }

    hw_code_map = {
        0x0279: "MT6797",
        0x0321: "MT6735",
        0x0335: "MT6737M",
        0x8163: "MT8163",
    }

    cqdma_addrs = {
        "MT6797": {
            'cqdma_base': 0x10212C00,
            'tmp_addr': 0x110001A0,
        },
        "MT6735": {
            'cqdma_base': 0x10217C00,
            'tmp_addr': 0x110001A0,
        },
        "MT6737M": {
            'cqdma_base': 0x10217C00,
            'tmp_addr': 0x110001A0,
        },
        "MT8163": {
            'cqdma_base': 0x10212C00,
            'tmp_addr': 0x110001A0,
        },
    }

    def __init__(self, port, timeout=1, write_timeout=1, debug=False):
        self.debug = debug
        self.ser = serial.Serial(port, timeout=timeout, write_timeout=write_timeout)
        hw_code = self.cmd_get_hw_code()
        self.soc = self.hw_code_map[hw_code]
        print("{} detected!".format(self.soc))
        self.cqdma_base = self.cqdma_addrs[self.soc]['cqdma_base']
        self.tmp_addr = self.cqdma_addrs[self.soc]['tmp_addr']

    def _send_bytes(self, data):
        data = bytes(data)
        if self.debug:
            print("-> {}".format(binascii.b2a_hex(data)))
        self.ser.write(data)
        echo = self.ser.read(len(data))
        if self.debug:
            print("<- {}".format(binascii.b2a_hex(echo)))
        if echo != data:
            raise Exception

    def _recv_bytes(self, count):
        data = self.ser.read(count)
        if self.debug:
            print("<- {}".format(binascii.b2a_hex(data)))
        if len(data) != count:
            raise Exception
        return bytes(data)

    def cmd_read32(self, addr, word_count):
        '''Read 32-bit words starting at an address.

        addr: The 32-bit starting address as an int.
        word_count: The number of words to read as an int.
        '''
        words = []

        self._send_bytes([self.commands['CMD_READ32']])
        self._send_bytes(struct.pack('>I', addr))
        self._send_bytes(struct.pack('>I', word_count))

        status = struct.unpack('>H', self._recv_bytes(2))[0]
        if status != 0:
            print(status)
            raise Exception

        for i in range(word_count):
            word = self._recv_bytes(4)
            words.append(struct.unpack('>I', word)[0])

        status = struct.unpack('>H', self._recv_bytes(2))[0]
        if status != 0:
            print(status)
            raise Exception

        return words

    def cmd_write32(self, addr, words):
        '''Write 32 bit words starting at an address.

        addr: A 32-bit address as an int.
        words: A list of 32-bit ints to write starting at address addr.
        '''
        self._send_bytes([self.commands['CMD_WRITE32']])
        self._send_bytes(struct.pack('>I', addr))
        self._send_bytes(struct.pack('>I', len(words)))

        status = struct.unpack('>H', self._recv_bytes(2))[0]
        if status > 0xff:
            print(status)
            raise Exception

        for word in words:
            self._send_bytes(struct.pack('>I', word))

        status = struct.unpack('>H', self._recv_bytes(2))[0]
        if status > 0xff:
            print(status)
            raise Exception

    def cmd_get_hw_sw_ver(self):
        self._send_bytes([self.commands['CMD_GET_HW_SW_VER']])
        hw_subcode = struct.unpack('>H', self._recv_bytes(2))[0]
        hw_ver = struct.unpack('>H', self._recv_bytes(2))[0]
        sw_ver = struct.unpack('>H', self._recv_bytes(2))[0]

        status = struct.unpack('>H', self._recv_bytes(2))[0]
        if status != 0:
            print(status)
            raise Exception

        return (hw_subcode, hw_ver, sw_ver)

    def cmd_get_hw_code(self):
        self._send_bytes([self.commands['CMD_GET_HW_CODE']])
        hw_code = struct.unpack('>H', self._recv_bytes(2))[0]

        status = struct.unpack('>H', self._recv_bytes(2))[0]
        if status != 0:
            print(status)
            raise Exception

        return hw_code

    def cqdma_read32(self, addr, word_count):
        '''Read 32-bit words starting at an address, using the CQDMA peripheral.

        addr: The 32-bit starting address as an int.
        word_count: The number of words to read as an int.
        '''

        words = []
        for i in range(word_count):
            # Set DMA source address.
            self.cmd_write32(self.cqdma_base+0x1C, [addr+i*4])
            # Set DMA destination address.
            self.cmd_write32(self.cqdma_base+0x20, [self.tmp_addr])
            # Set DMA transfer length in bytes.
            self.cmd_write32(self.cqdma_base+0x24, [4])
            # Start DMA transfer.
            self.cmd_write32(self.cqdma_base+0x08, [0x00000001])
            # Stop and reset DMA transfer.
            self.cmd_write32(self.cqdma_base+0x0C, [0x00000001])
            # Read word from tmp_addr.
            words.extend(self.cmd_read32(self.tmp_addr, 1))

        return words

    def cqdma_write32(self, addr, words):
        '''Write 32 bit words starting at an address, using the CQDMA peripheral.

        addr: A 32-bit address as an int.
        words: A list of 32-bit ints to write starting at address addr.
        '''

        for i in range(len(words)):
            # Write word to tmp_addr.
            self.cmd_write32(self.tmp_addr, [words[i]])
            # Set DMA source address.
            self.cmd_write32(self.cqdma_base+0x1C, [self.tmp_addr])
            # Set DMA destination address.
            self.cmd_write32(self.cqdma_base+0x20, [addr+i*4])
            # Set DMA transfer length in bytes.
            self.cmd_write32(self.cqdma_base+0x24, [4])
            # Start DMA transfer.
            self.cmd_write32(self.cqdma_base+0x08, [0x00000001])
            # Stop and reset DMA transfer.
            self.cmd_write32(self.cqdma_base+0x0C, [0x00000001])
            # Write dummy word to tmp_addr for error detection.
            self.cmd_write32(self.tmp_addr, [0xc0ffeeee])

    def memory_read(self, addr, count, cqdma=False):
        '''Read a range of memory to a byte array.

        addr: A 32-bit address as an int.
        count: The length of data to read, in bytes.
        '''
        word_count = count//4
        if (count % 4) > 0:
            word_count += 1

        words = []
        if cqdma:
            words = self.cqdma_read32(addr, word_count)
        else:
            words = self.cmd_read32(addr, word_count)

        data = b''
        for word in words:
            data += struct.pack('<I', word)

        return data[:count]

    def memory_write(self, addr, data, cqdma=False):
        '''Write a byte array to a range of memory.

        addr: A 32-bit address as an int.
        data: The data to write.
        '''
        data = bytes(data)

        # Pad the byte array.
        remaining_bytes = (len(data) % 4)
        if remaining_bytes > 0:
            data += b'\0' * (4 - remaining_bytes)

        words = []
        for i in range(0, len(data), 4):
            words.append(struct.unpack_from('<I', data, i)[0])

        if cqdma:
            self.cqdma_write32(addr, words)
        else:
            self.cmd_write32(addr, words)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str, help="The serial port you want to connect to.")
    args = parser.parse_args()

    usbdl = UsbDl(args.port, debug=False)

    # Disable WDT.
    print("Disabling WDT...")
    usbdl.cmd_write32(0x10007000, [0x22000000])

    # Dump efuses to file.
    print("Dumping efuses...")
    foo = usbdl.memory_read(0x10206000, 0x1000, cqdma=False)
    e = open("{}-efuses.bin".format(usbdl.soc.lower()), 'wb')
    e.write(foo)
    e.close()

    # Print a string to UART0.
    for byte in "Hello, there!\r\n".encode('utf-8'):
        usbdl.cmd_write32(0x11002000, [byte])
