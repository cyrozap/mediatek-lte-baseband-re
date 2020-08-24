#!/usr/bin/env python3

import argparse
import io
import struct
from copy import copy

from unicorn import *
from unicorn.arm_const import *

from init import Bmo


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
    },
}

def memory_region(address, size):
    return range(address, address+size)

def hook_code(mu, addr, size, user_data):
    print('>>> Tracing instruction at 0x{:08x}, instruction size = {}'.format(addr, size))

    # Skip mrrc/mcrr instructions.
    if addr == 0x00201080:
        mu.reg_write(UC_ARM_REG_PC, addr + 0x10)
    if addr in (0x0000b9e8, 0x0000ba00):
        mu.reg_write(UC_ARM_REG_PC, addr + 0x14)

    if addr == 0x00210e92:
        print("Skipping RTC thing for now.")
        mu.reg_write(UC_ARM_REG_PC, addr + size + 1)

def hook_mmio(mu, access, addr, size, value, user_data):
    (soc, bmo) = user_data

    rtype = "MMIO"
    for region in soc['regions']:
        if addr in memory_region(region['base'], region['size']):
            rtype = region['type']
            break

    # WDT
    wdt_base = 0x10212000
    if addr in (wdt_base, wdt_base+0x14) and access == UC_MEM_WRITE:
        print("Skipping WDT write: *0x{:08x} = 0x{:08x}".format(addr, value))
        return

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

    # UART1 GPIO config registers
    masks = {
        0x10211020: (1 << 13) | (1 << 12),
        0x10211A50: 1 << 15,
        0x10211A30: 1 << 15,
        0x10211370: ((0x7 << 22) | (0x7 << 19)) | (0x1 << 22) | (0x1 << 19),
    }
    if addr in masks.keys() and access == UC_MEM_WRITE and bmo:
        mask = masks[addr]
        orig = copy(value)
        value &= (~mask) & 0xffffffff
        value |= bmo.readw(addr) & mask
        print("Masking UART1 GPIO config write. Before: *0x{:08x} = 0x{:08x}, after: *0x{:08x} = 0x{:08x}, diff: 0x{:08x}".format(
            addr, orig, addr, value, orig ^ value))

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
        #"DRAM",
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('binary', type=str, help="The binary you want to load.")
    parser.add_argument('-S', '--soc', type=str, choices=SOCS.keys(), default="MT6737M", help="The SoC you want to emulate. Default: MT6737M")
    parser.add_argument('-l', '--load-address', type=str, default="0", help="The address you want to load the binary at. Default: 0")
    parser.add_argument('-e', '--entrypoint', type=str, default="0", help="The address you want to start executing from (add 1 for Thumb mode). Default: 0")
    parser.add_argument('-p', '--port', type=str, help="The BMO serial port you want to connect to.")
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help="The baud rate you want to connect at. Default: 115200")
    parser.add_argument('-s', '--baudrate-next', type=int, default=115200, help="The baud rate you want to switch to. Default: 115200")
    args = parser.parse_args()

    soc = SOCS[args.soc]

    bmo = None
    if args.port:
        print("Initializing BMO...")
        bmo = Bmo(args.port, baudrate=args.baudrate, debug=False)
        if args.baudrate_next != args.baudrate:
            print("Switching to baudrate to {}...".format(args.baudrate_next))
            bmo.setbaud(args.baudrate_next)

            bmo = Bmo(args.port, baudrate=args.baudrate_next, debug=False)

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
            print("Loading {} from SoC...")
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
    mu.hook_add(UC_HOOK_CODE, hook_code)
    mu.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, hook_mmio, (soc, bmo))
    print("Starting emulator!")
    mu.emu_start(int(args.entrypoint, 0), len(binary))

if __name__ == "__main__":
    main()
