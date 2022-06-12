#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD

# Copyright (C) 2020 by Forest Crossman <cyrozap@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
# PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.


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
