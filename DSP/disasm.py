#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD

# Copyright (C) 2021, 2026 by Forest Crossman <cyrozap@gmail.com>
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
import struct


class InstDecodeError(Exception):
    pass


def dis(instr : int):
    # Instructions are all 25 bits wide.
    if instr >> 25 != 0:
        raise InstDecodeError("Instruction 0x{:08x} wider than 25 bits.".format(instr))

    bits = "{:025b}".format(instr)

    return bits

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("firmware", type=str, help="The firmware binary.")
    args = parser.parse_args()

    fw = open(args.firmware, 'rb').read()

    print("Instruction index: Instruction word in hex (Instruction word in binary)")
    for i, (instr,) in enumerate(struct.iter_unpack('<I', fw)):
        print("{:>6d}: 0x{:07x} (0b{})".format(i, instr, dis(instr)))


if __name__ == "__main__":
    main()
