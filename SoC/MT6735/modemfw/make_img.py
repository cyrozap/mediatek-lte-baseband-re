#!/usr/bin/env python3

import argparse
import struct
from datetime import datetime


def gen_footer(data):
    f = b'CHECK_HEADER'
    f += struct.pack('<I', 3)
    f += struct.pack('<I', 2)
    f += struct.pack('<I', 5)
    f += struct.pack('16s', b'MT6735_S00')
    f += struct.pack('64s', datetime.utcnow().strftime("%Y/%m/%d %H:%M").encode('utf-8'))
    f += struct.pack('64s', b'')
    f += struct.pack('B', 1)
    f += struct.pack('B', 0)
    f += b'\0\0'
    f += struct.pack('<I', 0x03000000)
    f += struct.pack('<I', len(data))
    f += struct.pack('<I', 0)
    f += struct.pack('<I', 0x00A20000)
    f += struct.pack('<I', 0x00219D1C)
    f += b'\0' * 88
    f += struct.pack('<I', 284)
    return f

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Input file.")
    parser.add_argument("-o", "--output", type=str, default="modem.img", help="Output file.")
    args = parser.parse_args()

    binary = open(args.input, 'rb').read()
    padding = b''
    min_len = 0x20000
    if len(binary) < min_len:
        padding = b'\0' * (min_len-len(binary))
    footer = gen_footer(binary+padding)
    image = open(args.output, 'wb')
    image.write(binary)
    image.write(padding)
    image.write(footer)
    image.close()
