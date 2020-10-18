#!/usr/bin/env python3

import argparse
import sys

from bmo import Bmo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=str, help="The serial port you want to connect to.")
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help="The baud rate you want to connect at. Default: 115200")
    parser.add_argument('-s', '--baudrate-next', type=int, default=115200, help="The baud rate you want to switch to. Default: 115200")
    args = parser.parse_args()

    bmo = Bmo(args.port, baudrate=args.baudrate, debug=False)
    if args.baudrate_next != args.baudrate:
        print("Switching to baudrate to {}...".format(args.baudrate_next))
        bmo.setbaud(args.baudrate_next)

        bmo = Bmo(args.port, baudrate=args.baudrate_next, debug=False)

    #bmo.debug = True
    #bmo.debug = False

    print(bmo.memory_read(0, 0x10000, print_speed=True).hex())
