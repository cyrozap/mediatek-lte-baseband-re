#!/usr/bin/env python3

'''\
A simple utility to convert register dumps to binary data.

For example:

    ./dump.sh 10200000 1000 | ./dump-to-bin.py | hexdump -C

You can also read files directly:

    ./dump-to-bin.py dump.txt | hexdump -C

'''

import fileinput
import struct
import sys

if __name__ == "__main__":
    for line in fileinput.input():
        data = int(line.rstrip('\n').split(' = ')[1], 16)
        sys.stdout.buffer.write(struct.pack('<I', data))
