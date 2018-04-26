#!/usr/bin/env python3

import sys

if __name__ == "__main__":
    old = open(sys.argv[1], 'rb').read()
    for i in range(0, len(old), 4):
        number = old[i] << 16 | old[i+1] << 8 | old[i+2]
        print(number)
