#!/usr/bin/env python3

import argparse
import json


def count_mask_prefix_bits(mask):
    bits = 0
    for i in range(32)[::-1]:
        if mask & (1 << i) == 0:
            break
        bits += 1
    return bits

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("instructions", type=str, help="The JSON file with instructions you want to parse.")
    args = parser.parse_args()

    opcodes_file = open(args.instructions, 'r')
    opcode_list = json.load(opcodes_file)
    opcodes_file.close()

    print("Instructions, sorted by mnemonic, then opcode:")
    for opcode in sorted(opcode_list, key=lambda e: (e[0], e[3])):
        print("  {0} ({1}): mask = 0x{2:08x}, masked opcode = 0x{3:08x}".format(*opcode))

    print("Instructions, sorted by opcode, then mnemonic:")
    for opcode in sorted(opcode_list, key=lambda e: (e[3], e[0])):
        print("  {0} ({1}): mask = 0x{2:08x}, masked opcode = 0x{3:08x}".format(*opcode))

    print("Instructions, sorted by mask prefix bits, then opcode:")
    for opcode in sorted(opcode_list, key=lambda e: (count_mask_prefix_bits(e[2]), e[3])):
        print("  {0} ({1}): mask = 0x{2:08x}, masked opcode = 0x{3:08x}".format(*opcode))


if __name__ == "__main__":
    main()
