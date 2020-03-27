#!/usr/bin/env python3

import argparse
import binascii
import serial
import struct
import sys
import time


def auto_int(i):
    return int(i, 0)

def hex_int(i):
    return int(i, 16)

def print_ranges(ranges):
    for base, count in sorted(ranges.items()):
        print("0x{:08X}: 0x{:08x}".format(base, count))


class ChecksumError(Exception):
    pass

class EchoBytesMismatchException(Exception):
    pass

class NotEnoughDataException(Exception):
    pass

class ProtocolError(Exception):
    pass

class UsbDl:
    commands = {
        'CMD_C8': 0xC8, # Don't know the meaning of this yet.
        'CMD_READ32': 0xD1,
        'CMD_WRITE32': 0xD4,
        'CMD_JUMP_DA': 0xD5,
        'CMD_JUMP_BL': 0xD6,
        'CMD_SEND_DA': 0xD7,
        'CMD_GET_TARGET_CONFIG': 0xD8,
        'CMD_UART1_LOG_EN': 0xDB,
        'CMD_UART1_SET_BAUD': 0xDC, # Not sure what the real name of this command is.
        'CMD_GET_BROM_LOG': 0xDD, # Not sure what the real name of this command is.
        'SCMD_GET_ME_ID': 0xE1,
        'CMD_GET_HW_SW_VER': 0xFC,
        'CMD_GET_HW_CODE': 0xFD,
    }

    socs = {
        0x0279: {
            'name': "MT6797",
            'brom': (0x00000000, 0x14000),
            'sram': (0x00100000, 0x30000),
            'l2_sram': (0x00200000, 0x100000), # Functional spec says address is 0x00400000, but that's incorrect.
            'toprgu': (0x10007000, 0x1000),
            'efusec': (0x10206000, 0x1000),
            'usbdl': 0x10001680,
            'cqdma_base': 0x10212C00,
            'tmp_addr': 0x110001A0,
            'brom_g_bounds_check': (
                (0x0010276C, 0x00000000),
                (0x00105704, 0x00000000),
            ),
            'brom_g_da_verified': 0x001030BC,
        },
        0x0321: {
            'name': "MT6735",
            'brom': (0x00000000, 0x10000),
            'sram': (0x00100000, 0x10000),
            'l2_sram': (0x00200000, 0x40000),
            'toprgu': (0x10212000, 0x1000),
            'efusec': (0x10206000, 0x1000),
            'usbdl': 0x10000818,
            'cqdma_base': 0x10217C00,
            'tmp_addr': 0x110001A0,
            'brom_g_bounds_check': (
                (0x00102760, 0x00000000),
                (0x00105704, 0x00000000),
            ),
            'brom_g_da_verified': 0x001030C0,
        },
        0x0335: {
            'name': "MT6737M",
            'brom': (0x00000000, 0x10000),
            'sram': (0x00100000, 0x10000),
            'l2_sram': (0x00200000, 0x40000),
            'toprgu': (0x10212000, 0x1000),
            'efusec': (0x10206000, 0x1000),
            'usbdl': 0x10000818,
            'cqdma_base': 0x10217C00,
            'tmp_addr': 0x110001A0,
            'brom_g_bounds_check': (
                (0x00102760, 0x00000000),
                (0x00105704, 0x00000000),
            ),
            'brom_g_da_verified': 0x001030C0,
        },
        0x0788: {
            'name': "MT8183",
            'brom': (0x00000000, 0), # TODO: Find out how large the BROM is.
            'sram': (0x00100000, 0x20000),
            'l2_sram': (0x00200000, 0x80000),
            'toprgu': (0x10007000, 0x1000),
            'efusec': (0x11F10000, 0x1000),
        },
        0x8163: {
            'name': "MT8163",
            'brom': (0x00000000, 0x14000),
            'sram': (0x00100000, 0x10000),
            'l2_sram': (0x00200000, 0x40000),
            'toprgu': (0x10007000, 0x1000),
            'efusec': (0x10206000, 0x1000),
            'usbdl': 0x10202050,
            'cqdma_base': 0x10212C00,
            'tmp_addr': 0x110001A0,
            'brom_g_bounds_check': (
                (0x00102868, 0x00000000),
                (0x001072DC, 0x00000000),
            ),
            'brom_g_da_verified': 0x001031D0,
        },
    }

    def __init__(self, port, timeout=1, write_timeout=1, debug=False):
        self.debug = debug
        self.ser = serial.Serial(port, timeout=timeout, write_timeout=write_timeout)
        hw_code = self.cmd_get_hw_code()
        self.soc = self.socs[hw_code]
        print("{} detected!".format(self.soc['name']))

    def _send_bytes(self, data, echo=True):
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

    def get_word(self):
        '''Read a big-endian 16-bit integer from the serial port.'''
        return struct.unpack('>H', self._recv_bytes(2))[0]

    def put_word(self, word):
        '''Write a big-endian 16-bit integer to the serial port.'''
        self._send_bytes(struct.pack('>H', word))

    def get_dword(self):
        '''Read a big-endian 32-bit integer from the serial port.'''
        return struct.unpack('>I', self._recv_bytes(4))[0]

    def put_dword(self, dword):
        '''Write a big-endian 32-bit integer to the serial port.'''
        self._send_bytes(struct.pack('>I', dword))

    def cmd_C8(self, subcommand):
        subcommands = {
            'B0': 0xB0,
            'B1': 0xB1,
            'B2': 0xB2,
            'B3': 0xB3,
            'B4': 0xB4,
            'B5': 0xB5,
            'B6': 0xB6,
            'B7': 0xB7,
            'B8': 0xB8,
            'B9': 0xB9,
            'BA': 0xBA,
            'C0': 0xC0,
            'C1': 0xC1,
            'C2': 0xC2,
            'C3': 0xC3,
            'C4': 0xC4,
            'C5': 0xC5,
            'C6': 0xC6,
            'C7': 0xC7,
            'C8': 0xC8,
            'C9': 0xC9,
            'CA': 0xCA,
            'CB': 0xCB,
            'CC': 0xCC,
        }
        self._send_bytes([self.commands['CMD_C8']])
        self._send_bytes([subcommands[subcommand]])
        sub_data = struct.unpack('B', self._recv_bytes(1))[0]

        status = self.get_word()
        if status != 0:
            raise ProtocolError(status)

        return sub_data

    def cmd_read32(self, addr, word_count):
        '''Read 32-bit words starting at an address.

        addr: The 32-bit starting address as an int.
        word_count: The number of words to read as an int.
        '''
        words = []

        self._send_bytes([self.commands['CMD_READ32']])
        self.put_dword(addr)
        self.put_dword(word_count)

        status = self.get_word()
        if status != 0:
            raise ProtocolError(status)

        for i in range(word_count):
            words.append(self.get_dword())

        status = self.get_word()
        if status != 0:
            raise ProtocolError(status)

        return words

    def cmd_write32(self, addr, words):
        '''Write 32 bit words starting at an address.

        addr: A 32-bit address as an int.
        words: A list of 32-bit ints to write starting at address addr.
        '''
        self._send_bytes([self.commands['CMD_WRITE32']])
        self.put_dword(addr)
        self.put_dword(len(words))

        status = self.get_word()
        if status > 0xff:
            raise ProtocolError(status)

        for word in words:
            self.put_dword(word)

        status = self.get_word()
        if status > 0xff:
            raise ProtocolError(status)

    def cmd_jump_da(self, addr):
        self._send_bytes([self.commands['CMD_JUMP_DA']])
        self.put_dword(addr)

        status = self.get_word()
        if status > 0xff:
            raise ProtocolError(status)

    def cmd_jump_bl(self):
        self._send_bytes([self.commands['CMD_JUMP_BL']])

        status = self.get_word()
        if status > 0xff:
            raise ProtocolError(status)

    def cmd_send_da(self, load_addr, data, sig_length=0, print_speed=False):
        self._send_bytes([self.commands['CMD_SEND_DA']])
        self.put_dword(load_addr)
        self.put_dword(len(data))
        self.put_dword(sig_length)

        status = self.get_word()
        if status > 0xff:
            raise ProtocolError(status)

        calc_checksum = 0
        padded_data = data
        if len(padded_data) % 2 != 0:
            padded_data += b'\0'
        for i in range(0, len(padded_data), 2):
            calc_checksum ^= struct.unpack_from('<H', padded_data, i)[0]

        start_time = time.time()
        self._send_bytes(data, echo=False)
        end_time = time.time()

        remote_checksum = self.get_word()

        if remote_checksum != calc_checksum:
            raise ChecksumError("Checksum mismatch: Expected 0x{:04x}, got 0x{:04x}.".format(calc_checksum, remote_checksum))

        status = self.get_word()
        if status > 0xff:
            raise ProtocolError(status)

        if print_speed:
            elapsed = end_time - start_time
            print("Sent {} DA bytes in {:.6f} seconds ({} bytes per second).".format(len(data), elapsed, int(len(data)/elapsed)))

    def cmd_get_target_config(self):
        self._send_bytes([self.commands['CMD_GET_TARGET_CONFIG']])

        target_config = self.get_dword()
        print("Target config: 0x{:08X}".format(target_config))
        print("\tSBC enabled: {}".format(True if (target_config & 0x1) else False))
        print("\tSLA enabled: {}".format(True if (target_config & 0x2) else False))
        print("\tDAA enabled: {}".format(True if (target_config & 0x4) else False))

        status = self.get_word()
        if status > 0xff:
            raise ProtocolError(status)

    def cmd_uart1_log_enable(self):
        self._send_bytes([self.commands['CMD_UART1_LOG_EN']])

        status = self.get_word()
        if status != 0:
            raise ProtocolError(status)

    def cmd_uart1_set_baud(self, baud):
        self._send_bytes([self.commands['CMD_UART1_SET_BAUD']])
        self.put_dword(baud)

        status = self.get_word()
        if status != 0:
            raise ProtocolError(status)

    def cmd_get_brom_log(self):
        self._send_bytes([self.commands['CMD_GET_BROM_LOG']])
        length = self.get_dword()
        log_bytes = self._recv_bytes(length)

        return log_bytes

    def scmd_get_me_id(self):
        self._send_bytes([self.commands['SCMD_GET_ME_ID']])
        length = self.get_dword()
        me_id = self._recv_bytes(length)

        status = self.get_word()
        if status != 0:
            raise ProtocolError(status)

        return me_id

    def cmd_get_hw_sw_ver(self):
        self._send_bytes([self.commands['CMD_GET_HW_SW_VER']])
        hw_subcode = self.get_word()
        hw_ver = self.get_word()
        sw_ver = self.get_word()

        status = self.get_word()
        if status != 0:
            raise ProtocolError(status)

        return (hw_subcode, hw_ver, sw_ver)

    def cmd_get_hw_code(self):
        self._send_bytes([self.commands['CMD_GET_HW_CODE']])
        hw_code = self.get_word()

        status = self.get_word()
        if status != 0:
            raise ProtocolError(status)

        return hw_code

    def memory_range_test(self, addr, byte_count, byte_granularity=4, print_speed=False):
        '''Test a range of memory to see where we have contiguous read access.

        addr: A 32-bit address as an int.
        count: The length of data to read, in bytes.
        '''
        word_count = byte_count//4
        if (byte_count % 4) > 0:
            word_count += 1

        assert byte_granularity > 0
        assert byte_granularity % 4 == 0

        ranges = {}
        previous_ranges = ranges.copy()
        base_addr = 0
        bytes_to_read = word_count * 4
        reset_base = True
        start_time = time.time()
        for offset in range(0, bytes_to_read, byte_granularity):
            current_addr = addr + offset
            if reset_base:
                base_addr = current_addr
            try:
                self.cmd_read32(current_addr, byte_granularity // 4)
                if not ranges.get(base_addr):
                    ranges[base_addr] = 0
                ranges[base_addr] += byte_granularity
                reset_base = False
            except ProtocolError:
                reset_base = True
                pass
            if offset % (0x400 * byte_granularity) == 0 and offset > 0:
                print("Reading range: {}% complete".format(int(offset / bytes_to_read * 100)))
                if ranges != previous_ranges:
                    print_ranges(ranges)
                    previous_ranges = ranges.copy()
        end_time = time.time()

        if print_speed:
            elapsed = end_time - start_time
            print("Read {} bytes in {:.6f} seconds ({} bytes per second).".format(bytes_to_read, elapsed, int(bytes_to_read/elapsed)))

        return ranges

    def cqdma_read32(self, addr, word_count):
        '''Read 32-bit words starting at an address, using the CQDMA peripheral.

        addr: The 32-bit starting address as an int.
        word_count: The number of words to read as an int.
        '''

        tmp_addr = self.soc['tmp_addr']
        cqdma_base = self.soc['cqdma_base']

        words = []
        for i in range(word_count):
            # Set DMA source address.
            self.cmd_write32(cqdma_base+0x1C, [addr+i*4])
            # Set DMA destination address.
            self.cmd_write32(cqdma_base+0x20, [tmp_addr])
            # Set DMA transfer length in bytes.
            self.cmd_write32(cqdma_base+0x24, [4])
            # Start DMA transfer.
            self.cmd_write32(cqdma_base+0x08, [0x00000001])
            # Wait for transaction to finish.
            while True:
                if (self.cmd_read32(cqdma_base+0x08, 1)[0] & 1) == 0:
                    break
            # Read word from tmp_addr.
            words.extend(self.cmd_read32(tmp_addr, 1))

        return words

    def cqdma_write32(self, addr, words):
        '''Write 32 bit words starting at an address, using the CQDMA peripheral.

        addr: A 32-bit address as an int.
        words: A list of 32-bit ints to write starting at address addr.
        '''

        tmp_addr = self.soc['tmp_addr']
        cqdma_base = self.soc['cqdma_base']

        for i in range(len(words)):
            # Write word to tmp_addr.
            self.cmd_write32(tmp_addr, [words[i]])
            # Set DMA source address.
            self.cmd_write32(cqdma_base+0x1C, [tmp_addr])
            # Set DMA destination address.
            self.cmd_write32(cqdma_base+0x20, [addr+i*4])
            # Set DMA transfer length in bytes.
            self.cmd_write32(cqdma_base+0x24, [4])
            # Start DMA transfer.
            self.cmd_write32(cqdma_base+0x08, [0x00000001])
            # Wait for transaction to finish.
            while True:
                if (self.cmd_read32(cqdma_base+0x08, 1)[0] & 1) == 0:
                    break
            # Write dummy word to tmp_addr for error detection.
            self.cmd_write32(tmp_addr, [0xc0ffeeee])

    def memory_read(self, addr, count, cqdma=False, print_speed=False):
        '''Read a range of memory to a byte array.

        addr: A 32-bit address as an int.
        count: The length of data to read, in bytes.
        '''
        word_count = count//4
        if (count % 4) > 0:
            word_count += 1

        words = []
        start_time = time.time()
        if cqdma:
            words = self.cqdma_read32(addr, word_count)
        else:
            words = self.cmd_read32(addr, word_count)
        end_time = time.time()

        data = b''
        for word in words:
            data += struct.pack('<I', word)
        data = data[:count]

        if print_speed:
            elapsed = end_time - start_time
            print("Read {} bytes in {:.6f} seconds ({} bytes per second).".format(len(data), elapsed, int(len(data)/elapsed)))

        return data

    def memory_write(self, addr, data, cqdma=False, print_speed=False):
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

        words = []
        for i in range(0, len(padded_data), 4):
            words.append(struct.unpack_from('<I', padded_data, i)[0])

        start_time = time.time()
        if cqdma:
            self.cqdma_write32(addr, words)
        else:
            self.cmd_write32(addr, words)
        end_time = time.time()

        if print_speed:
            elapsed = end_time - start_time
            print("Wrote {} bytes in {:.6f} seconds ({} bytes per second).".format(len(data), elapsed, int(len(data)/elapsed)))

    def wdt_reset(self):
        self.cmd_write32(self.soc['toprgu'][0], [0x22000000 | 0x10 | 0x4])
        time.sleep(0.001)
        self.cmd_write32(self.soc['toprgu'][0] + 0x14, [0x1209])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str, help="The serial port you want to connect to.")
    args = parser.parse_args()

    usbdl = UsbDl(args.port, debug=False)

    # Get the security configuration of the target.
    usbdl.cmd_get_target_config()

    # Disable WDT.
    print("Disabling WDT...")
    usbdl.cmd_write32(usbdl.soc['toprgu'][0], [0x22000000])

    # Dump efuses to file.
    print("Dumping efuses...")
    efuses = usbdl.memory_read(usbdl.soc['efusec'][0], usbdl.soc['efusec'][1])
    efuse_file = open("{}-efuses.bin".format(usbdl.soc['name'].lower()), 'wb')
    efuse_file.write(efuses)
    efuse_file.close()

    # Print a string to UART0.
    for byte in "Hello, there!\r\n".encode('utf-8'):
        usbdl.cmd_write32(0x11002000, [byte])

    try:
        # The C8 B1 command disables caches.
        usbdl.cmd_C8('B1')
    except:
        # The C8 command is not available in Preloader mode.
        print("Error: Not in BROM DL mode. Attempting to reboot into BROM DL mode...")
        timeout = 60 # 0x3fff is no timeout. Less than that is timeout in seconds.
        usbdl_flag = (0x444C << 16) | (timeout << 2) | 0x00000001 # USBDL_BIT_EN
        usbdl.cmd_write32(usbdl.soc['usbdl'] + 0x00, [usbdl_flag])  # USBDL_FLAG/BOOT_MISC0

        # Make sure USBDL_FLAG is not reset by the WDT.
        usbdl.cmd_write32(usbdl.soc['usbdl'] + 0x20, [0xAD98])  # MISC_LOCK_KEY
        usbdl.cmd_write32(usbdl.soc['usbdl'] + 0x28, [0x00000001])  # RST_CON
        usbdl.cmd_write32(usbdl.soc['usbdl'] + 0x20, [0])  # MISC_LOCK_KEY

        # WDT reset.
        usbdl.wdt_reset()

        # Exit because we won't be able to talk to the device any more.
        sys.exit(0)

    # Assume we have to use the CQDMA to access restricted memory.
    use_cqdma = True

    # Check if the bounds check method is available.
    if usbdl.soc.get('brom_g_bounds_check', False):
        # Disable bounds check.
        for (addr, data) in usbdl.soc['brom_g_bounds_check']:
            usbdl.cqdma_write32(addr, [data])

        # We can use normal read32/write32 commands now.
        use_cqdma = False

    # NOTE: Using the CQDMA method to dump a large (>4kB) chunk of memory,
    # like the entire BROM, will almost certainly fail and cause the CPU to
    # reset. To work around this, try dumping the memory in smaller chunks,
    # like 1kB, and saving them to disk, then reboot the SoC into BROM mode
    # again and dump the next chunk until you've dumped the memory you're
    # interested in.

    # Dump BROM.
    print("Dumping BROM...")
    brom = usbdl.memory_read(usbdl.soc['brom'][0], usbdl.soc['brom'][1], cqdma=use_cqdma, print_speed=True)
    if len(brom) != usbdl.soc['brom'][1]:
        print("Error: Failed to dump entire BROM.")
        sys.exit(1)

    brom_file = open("{}-brom.bin".format(usbdl.soc['name'].lower()), 'wb')
    brom_file.write(brom)
    brom_file.close()

    # Dump SRAM.
    print("Dumping SRAM...")
    sram = usbdl.memory_read(usbdl.soc['sram'][0], usbdl.soc['sram'][1], cqdma=use_cqdma, print_speed=True)
    sram_file = open("{}-sram.bin".format(usbdl.soc['name'].lower()), 'wb')
    sram_file.write(sram)
    sram_file.close()

    # Dump L2 SRAM.
    print("Dumping L2 SRAM...")
    l2_sram = usbdl.memory_read(usbdl.soc['l2_sram'][0], usbdl.soc['l2_sram'][1], cqdma=use_cqdma, print_speed=True)
    l2_sram_file = open("{}-l2-sram.bin".format(usbdl.soc['name'].lower()), 'wb')
    l2_sram_file.write(l2_sram)
    l2_sram_file.close()

    # Code parameters.
    binary = open("demo/mode-switch/mode-switch.bin", 'rb').read()
    load_addr = 0x00200000
    thumb_mode = False

    # Load executable.
    print("Loading executables...")
    usbdl.memory_write(load_addr, binary, cqdma=use_cqdma, print_speed=True)
    usbdl.memory_write(0x00201000, open("demo/hello-aarch64/hello-aarch64.bin", 'rb').read(), cqdma=use_cqdma, print_speed=True)

    # Mark DA as verified.
    if usbdl.soc.get('brom_g_da_verified', False):
        if use_cqdma:
            usbdl.cqdma_write32(usbdl.soc['brom_g_da_verified'], [1])
        else:
            usbdl.cmd_write32(usbdl.soc['brom_g_da_verified'], [1])
    else:
        print("Error: No DA verification address specified, exiting...")
        sys.exit(1)

    # Jump to executable.
    print("Jumping to executable...")
    if thumb_mode:
        load_addr |= 1
    usbdl.cmd_jump_da(load_addr)
