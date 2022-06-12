#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

# gcpu.py - A tool for interacting with the GCPU by poking registers over serial
# Copyright (C) 2021  Forest Crossman <cyrozap@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import argparse
import struct
import time

from bmo import Bmo
from usbdl import UsbDl


INST_KEY = 0x259355


class Gcpu(Bmo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        soc_id = self.readw(0x08000000)
        self.soc = UsbDl.socs.get(soc_id)
        if not self.soc:
            raise ValueError("Error: Failed to recognize SoC with chip ID 0x{:04x}.".format(soc_id))

        print("Detected SoC: {}".format(self.soc['name']))

        self.gcpu_base = self.soc.get('gcpu_base')
        if not self.gcpu_base:
            raise ValueError("Error: GCPU base address has not been defined for SoC \"{}\".".format(self.soc['name']))

    def soc_reset(self):
        # Reset the whole SoC.
        self.writew(self.soc['toprgu'][0], [0x22000000 | 0x10 | 0x4])
        time.sleep(0.001)
        self.writew(self.soc['toprgu'][0] + 0x14, [0x1209])

        self.close()

    def ccpu_reset(self):
        GCPU_CTL = self.gcpu_base + 0x000
        GCPU_MSC = self.gcpu_base + 0x004

        # HW reset.
        ctl = self.readw(GCPU_CTL) & 0xfffffff0
        self.writew(GCPU_CTL, ctl)
        self.writew(GCPU_CTL, ctl | 0xf)

        # GCPU clock enable.
        ctl = self.readw(GCPU_CTL) & 0xffffffe0
        msc = self.readw(GCPU_MSC) | (1 << 16)
        self.writew(GCPU_CTL, ctl)
        self.writew(GCPU_MSC, msc)
        self.writew(GCPU_CTL, ctl | 0x1f)

    def ccpu_run(self, addr):
        # Start execution at addr.
        self.writew(self.gcpu_base + 0x400, addr)

    def flags_read(self):
        return self.reg_read(33)

    def print_flags(self):
        flags = self.flags_read()
        f_zero = flags & (1 << 1)
        f_carry_or_overflow = flags & ((1 << 2) | (1 << 0))

        flags_list = []
        if f_zero:
            flags_list.append("Zero")
        if f_carry_or_overflow:
            if f_carry_or_overflow != ((1 << 2) | (1 << 0)):
                print("WARNING: Unexpected mismatch between Carry and oVerflow flags!")
            flags_list.append("Carry/oVerflow")

        print("Flags: 0x{:08x} ({})".format(flags, ", ".join(flags_list)))

    def pc_read(self):
        return self.reg_read(32)

    def reg_read(self, reg : int):
        # Set the register to read.
        self.writew(self.gcpu_base + 0x414, reg)

        # Read the register value from the monitor.
        value = self.readw(self.gcpu_base + 0x410)

        return value

    def regs_read(self):
        for reg in range(32):
            yield reg, self.reg_read(reg)

    def print_regs(self):
        regs = ["R{}: 0x{:08x}".format(reg, value) for reg, value in self.regs_read()]
        print(", ".join(regs[:4]))
        print(", ".join(regs[4:8]))
        print(", ".join(regs[8:12]))
        print(", ".join(regs[12:16]))
        print(", ".join(regs[16:20]))
        print(", ".join(regs[20:24]))
        print(", ".join(regs[24:28]))
        print(", ".join(regs[28:]))

    def im_read(self, word_addr : int, word_count : int):
        word_array = []
        self.writew(self.gcpu_base + 0x404, word_addr)
        for i in range(word_count):
            word_array.append(struct.pack('<I', self.readw(self.gcpu_base + 0x408)))
        return b''.join(word_array)

    def im_write(self, word_addr : int, words : bytes):
        assert len(words) % 4 == 0
        assert word_addr & (1 << 13)

        self.writew(self.gcpu_base + 0x404, (1 << 31) | word_addr)
        for (word,) in struct.iter_unpack('<I', words):
            self.writew(self.gcpu_base + 0x408, word)


def instr_set_reg(reg, value, clobber=None):
    value &= 0xffffffff

    insts = []

    # Generate optimized instruction sequences for certain values.
    if (value >> 11) == 0:
        # Load 11-bit value to any register, without clobber.
        insts.append((0x0e << 16) | (value << 5) | reg)
    elif (reg >> 3) == 0 and (value >> 16) == 0:
        # Load 16-bit value to low register, without clobber.
        insts.append((0x2 << 19) | (reg << 16) | value)
    elif (reg >> 3) == 0 and clobber is not None and (clobber >> 3) == 0:
        # Load 32-bit value to low register, with low register clobber.
        val_hi = value >> 16
        val_lo = value & 0xffff
        insts.append((0x2 << 19) | (reg << 16) | val_hi)
        insts.append((0x2 << 19) | (clobber << 16) | val_lo)
        insts.append((0x0a << 16) | (reg << 10) | (16 << 5) | reg)
        insts.append((0x04 << 16) | (reg << 10) | (clobber << 5) | reg)
    elif (reg >> 3) == 0:
        # Load 32-bit value to low register, without clobber.
        val_hi = value >> 16
        val_lo_3 = (value >> 12) & 0xf
        val_lo_2 = (value >> 8) & 0xf
        val_lo_1 = (value >> 4) & 0xf
        val_lo_0 = value & 0xf
        insts.append((0x2 << 19) | (reg << 16) | val_hi)
        insts.append((0x0a << 16) | (reg << 10) | (4 << 5) | reg)
        insts.append((0x08 << 16) | (reg << 10) | (val_lo_3 << 5) | reg)
        insts.append((0x0a << 16) | (reg << 10) | (4 << 5) | reg)
        insts.append((0x08 << 16) | (reg << 10) | (val_lo_2 << 5) | reg)
        insts.append((0x0a << 16) | (reg << 10) | (4 << 5) | reg)
        insts.append((0x08 << 16) | (reg << 10) | (val_lo_1 << 5) | reg)
        insts.append((0x0a << 16) | (reg << 10) | (4 << 5) | reg)
        insts.append((0x08 << 16) | (reg << 10) | (val_lo_0 << 5) | reg)
    else:
        # Load 32-bit value to any register, without clobber.
        val_hi_1 = value >> 21
        val_hi_0 = (value >> 16) & 0x1f
        val_lo_3 = (value >> 12) & 0xf
        val_lo_2 = (value >> 8) & 0xf
        val_lo_1 = (value >> 4) & 0xf
        val_lo_0 = value & 0xf
        insts.append((0x0e << 16) | (val_hi_1 << 5) | reg)
        insts.append((0x0a << 16) | (reg << 10) | (5 << 5) | reg)
        insts.append((0x08 << 16) | (reg << 10) | (val_hi_0 << 5) | reg)
        insts.append((0x0a << 16) | (reg << 10) | (4 << 5) | reg)
        insts.append((0x08 << 16) | (reg << 10) | (val_lo_3 << 5) | reg)
        insts.append((0x0a << 16) | (reg << 10) | (4 << 5) | reg)
        insts.append((0x08 << 16) | (reg << 10) | (val_lo_2 << 5) | reg)
        insts.append((0x0a << 16) | (reg << 10) | (4 << 5) | reg)
        insts.append((0x08 << 16) | (reg << 10) | (val_lo_1 << 5) | reg)
        insts.append((0x0a << 16) | (reg << 10) | (4 << 5) | reg)
        insts.append((0x08 << 16) | (reg << 10) | (val_lo_0 << 5) | reg)

    print("instr_set_reg(r{}, 0x{:08x}): {}".format(reg, value, ["0x{:06x}".format(inst) for inst in insts]))

    return insts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str, help="The serial port you want to connect to.")
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help="The baud rate you want to connect at. Default: 115200")
    parser.add_argument('-s', '--baudrate-next', type=int, default=115200, help="The baud rate you want to switch to. Default: 115200")
    args = parser.parse_args()

    verbose = False

    #print("Resetting SoC...")
    #gcpu = Gcpu(args.port, baudrate=args.baudrate, debug=False, verbose=verbose)
    #gcpu.soc_reset()
    #time.sleep(1)

    gcpu = Gcpu(args.port, baudrate=args.baudrate, debug=False, verbose=verbose)
    if args.baudrate_next != args.baudrate:
        print("Switching to baudrate to {}...".format(args.baudrate_next))
        gcpu.setbaud(args.baudrate_next)

        gcpu = Gcpu(args.port, baudrate=args.baudrate_next, debug=False, verbose=verbose)

    # Reset GCPU state.
    gcpu.ccpu_reset()

    gcpu.print_regs()

    gcpu.print_flags()

    #irom = bytearray(gcpu.im_read(0, 0x1000))
    #for i, (inst,) in enumerate(struct.iter_unpack('<I', irom)):
    #    struct.pack_into('<I', irom, i*4, inst ^ INST_KEY)
    #open('gcpu_irom.bin', 'wb').write(irom)

    instructions = [
            0x10cafe,
            0x0a0200,
            0x11f00d,
            0x040020,
    ]
    instructions.append(0)
    instructions.append((0x35 << 15) | (0x2000 + len(instructions) - 1))
    instructions.append(0)

    if len(instructions) > 512:
        raise ValueError("Too many instructions: {} is greater than the max of 512.".format(len(instructions)))

    print("Raw instructions: {}".format(["0x{:06x}".format(inst) for inst in instructions]))

    for i, inst in enumerate(instructions):
        instructions[i] = inst ^ INST_KEY
    print("Obfuscated instructions: {}".format(["0x{:06x}".format(inst) for inst in instructions]))

    iram = b''.join([struct.pack('<I', inst) for inst in instructions])
    gcpu.im_write(0x2000, iram)
    actual = gcpu.im_read(0x2000, len(iram)//4)

    assert actual == iram

    #print(iram.hex())
    #print(actual.hex())

    # Release from reset.
    gcpu.ccpu_run(0x2000)

    time.sleep(0.01)

    print("Instruction: 0x{:06x}".format(gcpu.reg_read(36)))
    print("PC: 0x{:04x}".format(gcpu.pc_read()))
    print("Instruction: 0x{:06x}".format(gcpu.reg_read(36)))
    print("PC: 0x{:04x}".format(gcpu.pc_read()))

    gcpu.print_regs()

    gcpu.print_flags()

    print("MEM_CMD: 0x{:08x}".format(gcpu.readw(gcpu.gcpu_base + 0xc00)))
    print("MEM_P0: 0x{:08x}".format(gcpu.readw(gcpu.gcpu_base + 0xc00 + 4)))


if __name__ == "__main__":
    main()
