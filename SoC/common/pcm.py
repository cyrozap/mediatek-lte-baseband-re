#!/usr/bin/env python3

import argparse
import os
import struct
import sys
import time

from bmo import Bmo


class Pcm(Bmo):
    def __init__(self, *args, spm_base=None, **kwargs):
        self.spm_base = spm_base
        if not self.spm_base:
            raise ValueError("Error: SPM base address \"spm_base\" has not been set.")

        super().__init__(*args, **kwargs)

    def soc_reset(self):
        # Reset the whole SoC.
        self.writew(0x10212000, 0x22000000 | 0x10 | 0x4)
        self.writew(0x10212000 + 0x14, 0x1209)

        self.close()

    def pcm_reset(self):
        # Enable the PCM for configuration.
        self.writew(self.spm_base + 0x000, (0x0b16 << 16) | 1)

        # PCM reset.
        pcm_fsm_state = self.readw(self.spm_base + 0x3c4)
        print("FSM state: 0x{:08x}".format(pcm_fsm_state))
        self.writew(self.spm_base + 0x310, (0x0b16 << 16) | (1 << 15))
        self.writew(self.spm_base + 0x310, (0x0b16 << 16))
        pcm_fsm_state = self.readw(self.spm_base + 0x3c4)
        if pcm_fsm_state != 0x2848490:
            raise Exception("PCM reset failed: 0x{:08x}".format(pcm_fsm_state))

        # Configure PCM.
        self.writew(self.spm_base + 0x310, (0x0b16 << 16) | (1 << 3))
        self.writew(self.spm_base + 0x314, (0x0b16 << 16) | (1 << 12) | (1 << 11) | (1 << 10) | (1 << 3))

        # Clear IM pointer and length.
        self.writew(self.spm_base + 0x318, 0)
        self.writew(self.spm_base + 0x31c, 0)

        # Configure clocks.
        self.writew(self.spm_base + 0x400, (1 << 1) | (1 << 0) | (1 << 2) | (1 << 6) | (1 << 12) |
                (1 << 10) | (1 << 9) | (1 << 18))

        # Mask and clear sleep interrupts.
        self.writew(self.spm_base + 0x900, 0xff0c)
        self.writew(self.spm_base + 0x904, 0xc)

        # Clear PCM interrupts.
        self.writew(self.spm_base + 0x3e4, 0xff)

        # Power on MD32 SRAM.
        self.writew(self.spm_base + 0x2c8, 0xff0)

    def pcm_run(self):
        # Kick IM.
        con0 = self.readw(self.spm_base + 0x310) & ~((1 << 1) | (1 << 0))
        self.writew(self.spm_base + 0x310, con0 | (0x0b16 << 16) | (1 << 1))
        self.writew(self.spm_base + 0x310, con0 | (0x0b16 << 16))

        # Kick PCM.
        con0 = self.readw(self.spm_base + 0x310) & ~((1 << 1) | (1 << 0))
        self.writew(self.spm_base + 0x310, con0 | (0x0b16 << 16) | (1 << 0))
        self.writew(self.spm_base + 0x310, con0 | (0x0b16 << 16))

        # Set the pause mask.
        self.writew(self.spm_base + 0x354, 0xffffffff)

        # Enable CPU power down and dormant.
        self.writew(self.spm_base + 0x400, self.readw(self.spm_base + 0x400) & ~(1 << 14))

    def reg_read(self, reg : int):
        return self.readw(self.spm_base + 0x380 + 4 * reg)

    def regs_read(self):
        for i in range(16):
            yield self.reg_read(i)

    def print_regs(self):
        regs = ["R{}: 0x{:08x}".format(reg, value) for reg, value in enumerate(self.regs_read())]
        print(", ".join(regs[:4]))
        print(", ".join(regs[4:8]))
        print(", ".join(regs[8:12]))
        print(", ".join(regs[12:]))

    def im_read(self, word_addr : int, word_count : int):
        word_array = []
        for i in range(word_count):
            self.writew(self.spm_base + 0x3c8, (1 << 31) | (word_addr + i))
            word_array.append(struct.pack('<I', self.readw(self.spm_base + 0x3cc)))
            time.sleep(0.001)
            self.writew(self.spm_base + 0x3c8, (1 << 31) | (word_addr + i))
            actual = struct.pack('<I', self.readw(self.spm_base + 0x3cc))
            if actual != word_array[-1]:
                raise Exception("Error: Sequential read mismatch!")
        return b''.join(word_array)

    def im_write(self, word_addr : int, words : bytes):
        assert len(words) % 4 == 0

        for i, word in enumerate(map(lambda x: x[0], struct.iter_unpack('<I', words))):
            while True:
                self.writew(self.spm_base + 0x3c8, (1 << 31) | (1 << 30) | (word_addr + i))
                self.writew(self.spm_base + 0x3cc, word)
                time.sleep(0.001)
                self.writew(self.spm_base + 0x3c8, (1 << 31) | (word_addr + i))
                actual = self.readw(self.spm_base + 0x3cc)
                if word == actual:
                    break

    def im_mode(self, mode=0):
        if mode:
            mode = 1
        else:
            mode = 0

        # Configure IM mode.
        con1 = self.readw(self.spm_base + 0x314) & ~(1 << 0)
        self.writew(self.spm_base + 0x314, con1 | (0x0b16 << 16) | (mode << 0))

    def im_load(self, addr : int, data : int):
        assert len(data) % 4 == 0

        self.memory_write(addr, data, print_speed=True)

        self.writew(self.spm_base + 0x318, addr)
        self.writew(self.spm_base + 0x31c, len(data) // 4)

        self.im_mode(0)


def raw(value):
    return struct.pack('<I', value)

def instr(opcode, imm=0, rd=0, inv=0, shl=0, sh=0, rx=0, ry=0, rs=0, rxry=0, rxryrs=0):
    instruction = (
        (opcode << 28) |
        (imm << 27) |
        (rd << 22) |
        (inv << 21) |
        (shl << 20) |
        (sh << 15) |
        (rx << 10) |
        (ry << 5) | (rxry << 5) |
        (rs << 0) | (rxryrs << 0)
    )

    print("instr: 0x{:08x}".format(instruction))
    return struct.pack('<I', instruction)

def instr_set_reg(reg, value):
    instruction = 0x18000000 | (reg << 22) | (31 << 0)
    print("instr_set_reg(r{}, 0x{:08x}): 0x{:08x}, 0x{:08x}".format(reg, value, instruction, value))
    return struct.pack('<II', instruction, value)

def instr_loop_forever(instrs):
    instruction = 0xd0000000 | ((len(instrs) // 4) << 5)
    nop = 0x17c07c1f
    print("instr_loop_forever: 0x{:08x}, 0x{:08x}".format(instruction, nop))
    return struct.pack('<II', instruction, nop)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str, help="The serial port you want to connect to.")
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help="The baud rate you want to connect at. Default: 115200")
    parser.add_argument('-s', '--baudrate-next', type=int, default=115200, help="The baud rate you want to switch to. Default: 115200")
    args = parser.parse_args()

    spm_base = 0x10006000

    verbose = False

    print("Resetting SoC...")
    pcm = Pcm(args.port, baudrate=args.baudrate, debug=False, verbose=verbose, spm_base=spm_base)
    pcm.soc_reset()
    time.sleep(1)

    pcm = Pcm(args.port, baudrate=115200, debug=False, verbose=verbose, spm_base=spm_base)
    if args.baudrate_next != args.baudrate:
        print("Switching to baudrate to {}...".format(args.baudrate_next))
        pcm.setbaud(args.baudrate_next)

        pcm = Pcm(args.port, baudrate=args.baudrate_next, debug=False, verbose=verbose, spm_base=spm_base)

    pcm.pcm_reset()

    program = bytes()
    program += instr_set_reg(1, 0x12345678)
    program += instr_set_reg(2, 0xcafef00d)
    program += instr_loop_forever(program)

    pcm.im_load(0x00108000, program)

    print("Before:")
    pcm.print_regs()

    pcm.pcm_run()

    print("After:")
    pcm.print_regs()


if __name__ == "__main__":
    main()
