#!/usr/bin/env python3

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
