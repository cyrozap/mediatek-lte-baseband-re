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
import struct
import sys


def main():
    parser = argparse.ArgumentParser(description="Swap the endianness of every 32-bit word in a file.")
    parser.add_argument("-o", "--output", type=str, help="The endian-swapped output binary.")
    parser.add_argument("input", type=str, help="The input binary.")
    args = parser.parse_args()

    binary = open(args.input, 'rb').read()
    words = struct.iter_unpack('<I', binary)

    output = sys.stdout.buffer
    if args.output:
        output = open(args.output, 'wb')

    for word in map(lambda x: x[0], words):
        output.write(struct.pack('>I', word))

    output.close()


if __name__ == "__main__":
    main()
