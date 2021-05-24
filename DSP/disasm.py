#!/usr/bin/env python3

import argparse
import struct


class InstDecodeError(Exception):
    pass


def dis(instr : int):
    # Instructions are all 24 bits wide.
    if instr >> 24 != 0:
        raise InstDecodeError("Instruction 0x{:08x} wider than 32 bits.".format(instr))

    bits = "{:024b}".format(instr)

    return bits

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("firmware", type=str, help="The firmware binary.")
    args = parser.parse_args()

    fw = open(args.firmware, 'rb').read()

    for (instr,) in struct.iter_unpack('<I', fw):
        print("0x{:06x}: {}".format(instr, dis(instr)))


if __name__ == "__main__":
    main()
