#!/usr/bin/env python3

import argparse
import io
import struct
import time
from copy import copy

from unicorn import *
from unicorn.arm_const import *

from init import Bmo
from openocd import OpenOcd


SOCS = {
    "MT6737M": {
        'regions': (
            {
                'base': 0x00000000,
                'size': 64*1024,
                'type': "BROM",
            },
            {
                'base': 0x00100000,
                'size': 64*1024,
                'type': "SRAM",
                'load': True,
            },
            {
                'base': 0x00200000,
                'size': 256*1024,
                'type': "L2_SRAM",
            },
            {
                'base': 0x08000000,
                'size': 0x1000,
                'type': "MMIO",
            },
            {
                'base': 0x10000000,
                'size': 0x10000000,
                'type': "MMIO",
            },
            {
                'base': 0x40000000,
                'size': 3*1024*1024*1024,
                'type': "DRAM",
            },
        ),
        'peripherals': {
            "TOPRGU": {
                'base': 0x10212000,
                'size': 0x1000,
                'type': "TOPRGU",
            },
            "UART0": {
                'base': 0x11002000,
                'size': 0x1000,
                'type': "UART",
            },
            "UART1": {
                'base': 0x11003000,
                'size': 0x1000,
                'type': "UART",
            },
            "UART2": {
                'base': 0x11004000,
                'size': 0x1000,
                'type': "UART",
            },
        },
        'masked_registers': {
            0x10211020: (1 << 13) | (1 << 12),
            0x10211A50: 1 << 15,
            0x10211A30: 1 << 15,
            0x10211370: (0x7 << 22) | (0x7 << 19),
        },
        'brom_skip': {
            # Skip mrrc/mcrr instructions.
            0x0000b9e8: 0x14,
            0x0000ba00: 0x14,
        },
    },
    "MT6771": {
        'regions': (
            {
                'base': 0x00000000,
                'size': 96*1024,
                'type': "BROM",
            },
            {
                'base': 0x00100000,
                'size': 128*1024,
                'type': "SRAM",
                'load': True,
            },
            {
                'base': 0x00200000,
                'size': 512*1024,
                'type': "L2_SRAM",
            },
            {
                'base': 0x08000000,
                'size': 0x1000,
                'type': "MMIO",
            },
            {
                'base': 0x0c530000,
                'size': 0x10000,
                'type': "MMIO",
            },
            {
                'base': 0x10000000,
                'size': 0x10000000,
                'type': "MMIO",
            },
            {
                'base': 0x40000000,
                'size': 3*1024*1024*1024,
                'type': "DRAM",
            },
        ),
        'peripherals': {
            "TOPRGU": {
                'base': 0x10007000,
                'size': 0x1000,
                'type': "TOPRGU",
            },
            "UART0": {
                'base': 0x11002000,
                'size': 0x1000,
                'type': "UART",
            },
            "UART1": {
                'base': 0x11003000,
                'size': 0x1000,
                'type': "UART",
            },
            "UART2": {
                'base': 0x11004000,
                'size': 0x1000,
                'type': "UART",
            },
        },
        'masked_registers': {
        },
        'brom_skip': {
            # Skip JTAG delay.
            0x0000009c: 4,

            # Skip mrrc/mcrr instructions.
            0x00010f54: 0x14,
            0x00010f6c: 0x14,
            0x00010f84: 0x10,
        },
    },
    "MT6797": {
        'regions': (
            {
                'base': 0x00000000,
                'size': 80*1024,
                'type': "BROM",
            },
            {
                'base': 0x00100000,
                'size': 192*1024,
                'type': "SRAM",
                'load': True,
            },
            {
                'base': 0x00200000,
                'size': 256*1024,
                'type': "L2_SRAM",
            },
            {
                # This region doesn't actually exist, but we define it
                # anyways because the preloader tries reading from it.
                'base': 0x00300000,
                'size': 0x07d00000,
                'type': "MMIO",
            },
            {
                'base': 0x08000000,
                'size': 0x1000,
                'type': "MMIO",
            },
            {
                'base': 0x10000000,
                'size': 0x10000000,
                'type': "MMIO",
            },
            {
                'base': 0x40000000,
                'size': 3*1024*1024*1024,
                'type': "DRAM",
            },
        ),
        'peripherals': {
            "TOPRGU": {
                'base': 0x10007000,
                'size': 0x1000,
                'type': "TOPRGU",
            },
            "UART0": {
                'base': 0x11002000,
                'size': 0x1000,
                'type': "UART",
            },
            "UART1": {
                'base': 0x11003000,
                'size': 0x1000,
                'type': "UART",
            },
            "UART2": {
                'base': 0x11004000,
                'size': 0x1000,
                'type': "UART",
            },
            "UART3": {
                'base': 0x11005000,
                'size': 0x1000,
                'type': "UART",
            },
        },
        'masked_registers': {
        },
        'brom_skip': {
            # Skip JTAG delay
            0x00000098: 4,

            # Skip mrrc/mcrr instructions.
            0x0000c2d4: 0x14,
            0x0000c2ec: 0x14,
        },
    },
}


class BmOcd:
    def __init__(self, address, port, debug=False, verbose=False):
        self.debug = debug
        self.verbose = verbose or debug
        self.ocd = OpenOcd(tclRpcIp=address, tclRpcPort=port, verbose=self.verbose)
        self.ocd.__enter__()

    def close(self):
        self.ocd.__exit__()

    def readw(self, addr):
        result = self.ocd.send("mdw 0x{:08x}".format(addr))
        word = int(result.split(": ")[1].strip(), 16)
        return word

    def writew(self, addr, word):
        self.ocd.send("mww 0x{:08x} 0x{:08x}".format(addr, word))
        time.sleep(0.0001)

    def setbaud(self, *args, **kwargs):
        print("Warning: setbaud not supported for BmOcd.")

    def memory_read(self, addr, count, fast=False, print_speed=False):
        '''Read a range of memory to a byte array.

        addr: A 32-bit address as an int.
        count: The length of data to read, in bytes.
        '''
        word_count = count//4
        if (count % 4) > 0:
            word_count += 1

        data = b''
        start_ns = time.perf_counter_ns()
        for i in range(word_count):
            data += struct.pack('<I', self.readw(addr + i * 4))
        end_ns = time.perf_counter_ns()

        data = data[:count]

        if print_speed:
            elapsed = end_ns - start_ns
            print("Read {} bytes in {:.6f} seconds ({} bytes per second).".format(len(data), elapsed/1000000000, len(data)*1000000000//elapsed))

        return data


def memory_region(address, size):
    return range(address, address+size)

def hook_code(mu, addr, size, user_data):
    print('>>> Tracing instruction at 0x{:08x}, instruction size = {}'.format(addr, size))

    soc = user_data

    if addr in soc.get('brom_skip', {}).keys():
        skip_len = soc['brom_skip'][addr]
        mu.reg_write(UC_ARM_REG_PC, addr + skip_len)
        return

    # Skip mrrc/mcrr instructions.
    if addr == 0x00201080:
        mu.reg_write(UC_ARM_REG_PC, addr + 0x10)

    # Patch all timeouts to be at least 1 second.
    if addr in (0x00212a6a, 0x0021a7e2):
        r5 = mu.reg_read(UC_ARM_REG_R5)
        if (r5 / 13000000) < 1:
            r5 = 1 * 13000000
        mu.reg_write(UC_ARM_REG_R5, r5)

def hook_mmio(mu, access, addr, size, value, user_data):
    (soc, bmo) = user_data

    rtype = "MMIO"
    for region in soc['regions']:
        if addr in memory_region(region['base'], region['size']):
            rtype = region['type']
            break

    # Peripheral handler
    for peripheral in soc['peripherals'].items():
        (pname, pinfo) = peripheral
        base = pinfo['base']

        if addr not in memory_region(base, pinfo['size']):
            continue

        if pinfo['type'] == "UART":
            if addr == (base + 0x14) and access == UC_MEM_READ:
                mu.mem_write(addr, struct.pack('<I', (1 << 6) | (1 << 5)))
                return

            if addr == base and access == UC_MEM_WRITE:
                uart_buf = pinfo.get('buffer')
                if uart_buf is None:
                    return

                char = value & 0xff
                uart_buf.write(bytes([char]))
                uart_buf.flush()
                if char in b'\n\r':
                    buf = uart_buf.getvalue().replace(b'\r', b'\n')
                    if buf[-2] != ord('\n'):
                        print("{} log line: {}".format(pname, buf.rstrip(b'\n').split(b'\n')[-1].decode('utf-8')))

                return

            print("Skipping {} config write: *0x{:08x} = 0x{:08x}".format(pname, addr, value))
            return

        if pinfo['type'] == "TOPRGU":
            if addr in (base, base+0x14) and access == UC_MEM_WRITE:
                print("Skipping WDT write: *0x{:08x} = 0x{:08x}".format(addr, value))
                return

    # Masked register accesses.
    masks = soc.get('masked_registers', {})
    if addr in masks.keys() and access == UC_MEM_WRITE and bmo:
        mask = masks[addr]
        orig = copy(value)
        new = copy(value)
        new &= (~mask) & 0xffffffff
        new |= bmo.readw(addr) & mask
        diff = orig ^ new
        if diff != 0:
            value = new
            print("Masking register write. Before: *0x{:08x} = 0x{:08x}, after: *0x{:08x} = 0x{:08x}, diff: 0x{:08x}".format(
                addr, orig, addr, value, diff))

    assert size <= 4

    dtype = {
        1: "uint8_t",
        2: "uint16_t",
        4: "uint32_t",
        8: "uint64_t",
    }.get(size)
    dfmt = {
        1: 'B',
        2: '<H',
        4: '<I',
    }.get(size)
    dstr = {
        1: '0x{:02x}',
        2: '0x{:04x}',
        4: '0x{:08x}',
    }.get(size)


    aligned_addr = (addr // 4) * 4
    addr_offset = addr % 4
    assert (addr_offset + size) <= 4

    rw_through = (
        "MMIO",
        "DRAM",
    )
    if access == UC_MEM_READ:
        if bmo and rtype in rw_through:
            aligned_data = struct.pack('<I', bmo.readw(aligned_addr))
            data = aligned_data[addr_offset:addr_offset+size]
            mu.mem_write(addr, data)
        data_bytes = mu.mem_read(addr, size)
        data_int = struct.unpack(dfmt, data_bytes)[0]
        data_str = dstr.format(data_int)
        print("{} read: *({} *)(0x{:08x}) = {}".format(rtype, dtype, addr, data_str))
    elif access == UC_MEM_WRITE:
        data_str = dstr.format(value)
        print("{} write: *({} *)(0x{:08x}) = {}".format(rtype, dtype, addr, data_str))
        if bmo and rtype in rw_through:
            aligned_data = bytearray(struct.pack('<I', bmo.readw(aligned_addr)))
            aligned_data[addr_offset:addr_offset+size] = struct.pack('<I', value)[:size]
            bmo.writew(aligned_addr, struct.unpack('<I', aligned_data)[0])

def hook_unmapped(mu, access, addr, size, value, user_data):
    access_string = {
        UC_MEM_READ_UNMAPPED: "read",
        UC_MEM_WRITE_UNMAPPED: "write",
        UC_MEM_FETCH_UNMAPPED: "fetch",
    }.get(access)
    print("Error: Failed to {} {} bytes of unmapped memory at 0x{:016x}.".format(access_string, size, addr))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('binary', type=str, help="The binary you want to load.")
    parser.add_argument('-S', '--soc', type=str, choices=SOCS.keys(), default="MT6737M", help="The SoC you want to emulate. Default: MT6737M")
    parser.add_argument('-l', '--load-address', type=str, default="0", help="The address you want to load the binary at. Default: 0")
    parser.add_argument('-e', '--entrypoint', type=str, default="0", help="The address you want to start executing from (add 1 for Thumb mode). Default: 0")
    parser.add_argument('-p', '--port', type=str, help="The BMO serial port you want to connect to.")
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help="The baud rate you want to connect at. Default: 115200")
    parser.add_argument('-s', '--baudrate-next', type=int, default=115200, help="The baud rate you want to switch to. Default: 115200")
    parser.add_argument('-O', '--openocd', type=str, help="The OpenOCD address and port you want to connect to.")
    args = parser.parse_args()

    assert not (args.port and args.openocd)

    soc = SOCS[args.soc]

    bmo = None
    if args.port:
        print("Initializing BMO...")
        bmo = Bmo(args.port, baudrate=args.baudrate, debug=False)
        if args.baudrate_next != args.baudrate:
            print("Switching to baudrate to {}...".format(args.baudrate_next))
            bmo.setbaud(args.baudrate_next)

            bmo = Bmo(args.port, baudrate=args.baudrate_next, debug=False)
    elif args.openocd:
        address, port = args.openocd.split(":")
        bmo = BmOcd(address, int(port), debug=False)

    # Create the machine.
    print("Initializing virtual CPU...")
    mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)

    # Map memory.
    for region in soc['regions']:
        base = region['base']
        size = region['size']
        rtype = region['type']
        print("Mapping {} region from 0x{:08x} to 0x{:08x}.".format(rtype, base, base+size-1))
        mu.mem_map(base, size)

        # Optionally load region from SoC.
        if bmo and region.get('load', False):
            print("Loading {} from SoC...".format(rtype))
            data = bmo.memory_read(base, size, fast=True, print_speed=True)
            mu.mem_write(base, data)

    # Initialize peripherals.
    for (pname, pinfo) in soc['peripherals'].items():
        if pinfo['type'] == "UART":
            # Virtual UART
            pinfo['buffer'] = io.BytesIO()

    # Load and execute the binary.
    binary = open(args.binary, 'rb').read()
    mu.mem_write(int(args.load_address, 0), binary)
    mu.hook_add(UC_HOOK_CODE, hook_code, soc)
    mu.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, hook_mmio, (soc, bmo))
    mu.hook_add(UC_HOOK_MEM_UNMAPPED, hook_unmapped)
    print("Starting emulator!")
    mu.emu_start(int(args.entrypoint, 0), len(binary))

if __name__ == "__main__":
    main()
