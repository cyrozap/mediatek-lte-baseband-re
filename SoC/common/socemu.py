#!/usr/bin/env python3

import argparse
import io
import struct
from copy import copy

from unicorn import *
from unicorn.arm_const import *

from init import Bmo


BROM = 0x00000000
BROM_SIZE = 64*1024
SRAM = 0x00100000
SRAM_SIZE = 64*1024
L2_SRAM = 0x00200000
L2_SRAM_SIZE = 256*1024
MMIO = 0x10000000
MMIO_SIZE = 0x10000000
DRAM = 0x40000000
DRAM_SIZE = 3*1024*1024*1024

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
    (bmo, uart0, uart1, uart2) = user_data

    region = "MMIO"
    if addr in range(BROM, BROM + BROM_SIZE):
        region = "BROM"
    if addr in range(SRAM, SRAM + SRAM_SIZE):
        region = "SRAM"
    if addr in range(L2_SRAM, L2_SRAM + L2_SRAM_SIZE):
        region = "L2 SRAM"
    if addr in range(DRAM, DRAM + DRAM_SIZE):
        region = "DRAM"

    # WDT
    wdt_base = 0x10212000
    if addr in (wdt_base, wdt_base+0x14) and access == UC_MEM_WRITE:
        print("Skipping WDT write: *0x{:08x} = 0x{:08x}".format(addr, value))
        return

    # UARTs
    uarts = (
        (0x11002000, uart0, "UART0"),
        (0x11003000, uart1, "UART1"),
        (0x11004000, uart2, "UART2"),
    )
    for (base, uart, name) in uarts:
        if addr in range(base, base + 0x1000):
            if addr == (base + 0x14) and access == UC_MEM_READ:
                mu.mem_write(addr, struct.pack('<I', (1 << 6) | (1 << 5)))
            elif addr == base and access == UC_MEM_WRITE:
                char = value & 0xff
                uart.write(bytes([char]))
                uart.flush()
                if char == ord('\r'):
                    buf = uart.getvalue().replace(b'\r', b'\n')
                    if buf[-2] != ord('\n'):
                        print("{} log line: {}".format(name, buf.rstrip(b'\n').split(b'\n')[-1].decode('utf-8')))
            else:
                print("Skipping {} config write: *0x{:08x} = 0x{:08x}".format(name, addr, value))
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
        if bmo and region in rw_through:
            aligned_data = struct.pack('<I', bmo.readw(aligned_addr))
            data = aligned_data[addr_offset:addr_offset+size]
            mu.mem_write(addr, data)
        data_bytes = mu.mem_read(addr, size)
        data_int = struct.unpack(dfmt, data_bytes)[0]
        data_str = dstr.format(data_int)
        print("{} read: *({} *)(0x{:08x}) = {}".format(region, dtype, addr, data_str))
    elif access == UC_MEM_WRITE:
        data_str = dstr.format(value)
        print("{} write: *({} *)(0x{:08x}) = {}".format(region, dtype, addr, data_str))
        if bmo and region in rw_through:
            aligned_data = bytearray(struct.pack('<I', bmo.readw(aligned_addr)))
            aligned_data[addr_offset:addr_offset+size] = struct.pack('<I', value)[:size]
            bmo.writew(aligned_addr, struct.unpack('<I', aligned_data)[0])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('binary', type=str, help="The binary you want to load.")
    parser.add_argument('-l', '--load-address', type=str, default="0", help="The address you want to load the binary at. Default: 0")
    parser.add_argument('-e', '--entrypoint', type=str, default="0", help="The address you want to start executing from (add 1 for Thumb mode). Default: 0")
    parser.add_argument('-p', '--port', type=str, help="The BMO serial port you want to connect to.")
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help="The baud rate you want to connect at. Default: 115200")
    parser.add_argument('-s', '--baudrate-next', type=int, default=115200, help="The baud rate you want to switch to. Default: 115200")
    args = parser.parse_args()

    bmo = None
    if args.port:
        print("Initializing BMO...")
        bmo = Bmo(args.port, baudrate=args.baudrate, debug=False)
        if args.baudrate_next != args.baudrate:
            print("Switching to baudrate to {}...".format(args.baudrate_next))
            bmo.setbaud(args.baudrate_next)

            bmo = Bmo(args.port, baudrate=args.baudrate_next, debug=False)

    # Virtual UARTs
    uart0 = io.BytesIO()
    uart1 = io.BytesIO()
    uart2 = io.BytesIO()

    # Create the machine.
    print("Initializing virtual CPU...")
    mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)

    # Map memory.
    #mu.mem_map(BROM, BROM_SIZE, UC_PROT_READ | UC_PROT_EXEC)  # Preloader likes to write to BROM sometimes.
    mu.mem_map(BROM, BROM_SIZE)
    mu.mem_map(SRAM, SRAM_SIZE)
    mu.mem_map(L2_SRAM, L2_SRAM_SIZE)
    mu.mem_map(0x08000000, 0x1000)  # Chip ID
    mu.mem_map(MMIO, MMIO_SIZE)
    mu.mem_map(DRAM, DRAM_SIZE)

    # Load SRAM from SoC.
    print("Loading SRAM from SoC...")
    sram = bmo.memory_read(SRAM, SRAM_SIZE, fast=True, print_speed=True)
    mu.mem_write(SRAM, sram)

    # Load and execute the binary.
    binary = open(args.binary, 'rb').read()
    mu.mem_write(int(args.load_address, 0), binary)
    mu.hook_add(UC_HOOK_CODE, hook_code)
    mu.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, hook_mmio, (bmo, uart0, uart1, uart2))
    print("Starting emulator!")
    mu.emu_start(int(args.entrypoint, 0), len(binary))

if __name__ == "__main__":
    main()
