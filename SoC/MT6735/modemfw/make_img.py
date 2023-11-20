#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

# make_image.py - A tool for generating bootable modem images
# Copyright (C) 2018, 2023  Forest Crossman <cyrozap@gmail.com>
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
import struct
from datetime import datetime, UTC


def gen_footer(data):
    # drivers/misc/mediatek/include/mt-plat/mt_ccci_common.h
    # md_check_header_v3
    f = b'CHECK_HEADER'  # check_header
    f += struct.pack('<I', 3)  # header_verno
    f += struct.pack('<I', 2)  # product_ver
    f += struct.pack('<I', 5)  # image_type
    f += struct.pack('16s', b'MT6735_S00')  # platform
    f += struct.pack('64s', datetime.now(UTC).strftime("%Y/%m/%d %H:%M").encode('utf-8'))  # build_time
    f += struct.pack('64s', b'')  # build_ver
    f += struct.pack('B', 1)  # bind_sys_id
    f += struct.pack('B', 0)  # ext_attr
    f += b'\0\0'  # reserved
    f += struct.pack('<I', 0x03000000)  # mem_size
    f += struct.pack('<I', len(data))  # md_img_size
    f += struct.pack('<I', 0)  # rpc_sec_mem_addr
    f += struct.pack('<I', 0x00A20000)  # dsp_img_offset
    f += struct.pack('<I', 0x00219D1C)  # dsp_img_size
    f += b'\0' * 88  # reserved
    f += struct.pack('<I', 284)  # size
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
