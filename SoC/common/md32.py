#!/usr/bin/env python3

import argparse
import struct
import time

from bmo import Bmo
from usbdl import UsbDl


class Md32(Bmo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        soc_id = self.readw(0x08000000)
        self.soc = UsbDl.socs.get(soc_id)
        if not self.soc:
            raise ValueError("Error: Failed to recognize SoC with chip ID 0x{:04x}.".format(soc_id))

        print("Detected SoC: {}".format(self.soc['name']))

        md32_info = self.soc.get('md32')
        if not md32_info:
            raise ValueError("Error: MD32 info has not been defined for SoC \"{}\".".format(self.soc['name']))

        self.tcm_base = md32_info.get('tcm_base')
        self.cfgreg_base = md32_info.get('cfgreg_base')
        if not self.tcm_base:
            raise ValueError("Error: MD32 TCM base address \"tcm_base\" has not been set.")
        if not self.cfgreg_base:
            raise ValueError("Error: MD32 CFGREG base address \"cfgreg_base\" has not been set.")

        self.clk_ctrl_base = self.cfgreg_base + 0x1000

    def soc_reset(self):
        # Reset the whole SoC.
        self.writew(self.soc['toprgu'][0], [0x22000000 | 0x10 | 0x4])
        time.sleep(0.001)
        self.writew(self.soc['toprgu'][0] + 0x14, [0x1209])

        self.close()

    def md32_reset(self):
        # Put the MD32 into reset.
        self.writew(self.cfgreg_base + 0x00, 0)

        # Power on TCM SRAM.
        self.writew(self.clk_ctrl_base + 0x2c, 0)

        # Enable peripheral clocks.
        self.writew(self.clk_ctrl_base + 0x30, 0x1ff)

        # Set the TCM allocation for code and data.
        self.writew(self.cfgreg_base + 0x08, 0x02)

        # Clear OCD instruction/data write flags.
        self.writew(self.cfgreg_base + 0x44, 0)
        self.writew(self.cfgreg_base + 0x4c, 0)

        # Bypass JTAG.
        self.writew(self.cfgreg_base + 0x40, 1)

    def md32_run(self):
        # Release MD32 from reset.
        self.writew(self.cfgreg_base + 0x0, 1)

    def ocd_instr(self, instr, data=None):
        # Wait for OCD to become ready.
        while not self.readw(self.cfgreg_base + 0x58):
            continue

        # Write the instruction.
        self.writew(self.cfgreg_base + 0x48, (1 << 11) | instr)
        self.writew(self.cfgreg_base + 0x44, 1)
        self.writew(self.cfgreg_base + 0x44, 0)

        if data is not None:
            # Write the data.
            self.writew(self.cfgreg_base + 0x50, data)
            self.writew(self.cfgreg_base + 0x4c, 1)
            self.writew(self.cfgreg_base + 0x4c, 0)

        # Wait for OCD to become ready again.
        while not self.readw(self.cfgreg_base + 0x58):
            continue

        return self.readw(self.cfgreg_base + 0x54)

    def ocd_wait_ready(self):
        start = time.monotonic()
        while not (self.ocd_instr(0x003) & 0x1):
            continue

    def exec_instr(self, instruction : int):
        self.ocd_wait_ready()
        self.ocd_instr(0x002, instruction)
        self.ocd_instr(0x015)
        self.ocd_wait_ready()

    def pc_read(self):
        return self.readw(self.cfgreg_base + 0x60)

    def reg_read(self, reg : int):
        # Special case for r14.
        if reg == 14:
            return self.readw(self.cfgreg_base + 0x64)

        # Save the value of r15.
        r15_saved = self.readw(self.cfgreg_base + 0x68)

        # If we wanted to read r15, we're done.
        if reg == 15:
            return r15_saved

        # Copy the value from the register of interest to r15.
        self.exec_instr(0x0d000000 | (reg << 4) | 15)

        # Read the copied value from the r15 register.
        value = self.readw(self.cfgreg_base + 0x68)

        # Restore the value of r15.
        self.reg_write(15, r15_saved)

        return value

    def reg_write(self, reg : int, value : int):
        value &= 0xffffffff
        if ((value >> 20) == 0) or ((value >> 20) == 0xfff):
            masked = value & 0x1fffff
            self.exec_instr(0x00000000 | (masked << 4) | reg)
        else:
            val_hi = value >> 16
            val_lo = value & 0xffff
            self.exec_instr(0x0f000000 | (val_hi << 8) | reg)
            if val_lo:
                self.exec_instr(0x0d000000 | (val_lo << 8) | (reg << 4) | reg)

    def regs_read(self):
        # Save the value of r15.
        r15_saved = self.readw(self.cfgreg_base + 0x68)

        for reg in range(14):
            # Copy the value from the register of interest to r15.
            self.exec_instr(0x0d000000 | (reg << 4) | 15)

            # Read the copied value from the r15 register.
            value = self.readw(self.cfgreg_base + 0x68)

            yield reg, value

        # Special case for r14.
        yield 14, self.readw(self.cfgreg_base + 0x64)

        # Restore the value of r15.
        self.reg_write(15, r15_saved)

        yield 15, r15_saved

    def print_regs(self):
        regs = ["R{}: 0x{:08x}".format(reg, value) for reg, value in self.regs_read()]
        print(", ".join(regs[:4]))
        print(", ".join(regs[4:8]))
        print(", ".join(regs[8:12]))
        print(", ".join(regs[12:]))

    def tcm_load(self, data : int):
        assert len(data) % 4 == 0

        self.memory_write(self.tcm_base, data, print_speed=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str, help="The serial port you want to connect to.")
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help="The baud rate you want to connect at. Default: 115200")
    parser.add_argument('-s', '--baudrate-next', type=int, default=115200, help="The baud rate you want to switch to. Default: 115200")
    args = parser.parse_args()

    verbose = False

    #print("Resetting SoC...")
    #md32 = Md32(args.port, baudrate=args.baudrate, debug=False, verbose=verbose)
    #md32.soc_reset()
    #time.sleep(1)

    md32 = Md32(args.port, baudrate=args.baudrate, debug=False, verbose=verbose)
    if args.baudrate_next != args.baudrate:
        print("Switching to baudrate to {}...".format(args.baudrate_next))
        md32.setbaud(args.baudrate_next)

        md32 = Md32(args.port, baudrate=args.baudrate_next, debug=False, verbose=verbose)

    # Reset MD32 state.
    md32.md32_reset()

    # Insert software breakpoints to make sure we don't mess up the CPU state.
    breakpoints = struct.pack('<I', 0xa003a003)
    md32.memory_write(md32.tcm_base, breakpoints)
    assert breakpoints == md32.memory_read(md32.tcm_base, 4)

    # Release from reset.
    md32.md32_run()

    for i in range(16):
        md32.reg_write(i, 1 << i)
    md32.print_regs()


if __name__ == "__main__":
    main()
