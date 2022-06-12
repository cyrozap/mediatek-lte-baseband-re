#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

# init.py - A tool for initializing SoCs by poking registers over serial
# Copyright (C) 2019-2020  Forest Crossman <cyrozap@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


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
