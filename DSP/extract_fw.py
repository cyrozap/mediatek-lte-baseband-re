#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

# extract_fw.py - A tool to parse DSP binaries
# Copyright (C) 2017-2019  Forest Crossman <cyrozap@gmail.com>
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
import sys

try:
    import mediatek_lte_dsp_firmware
except ModuleNotFoundError:
    sys.stderr.write("Error: Failed to import \"mediatek_lte_dsp_firmware.py\". Please run \"make\" in this directory to generate that file, then try running this script again.\n")
    sys.exit(1)

key = bytes([0x40, 0xeb, 0xf8, 0x56, 0x8b, 0x74, 0x24, 0x08, 0x66, 0x85, 0xf6, 0x74, 0x30, 0x66, 0x83, 0xfe])

def checksum_valid(data, checksum):
    if checksum == 0:
        return True

    temp = 0
    for i in range(len(data)//4):
        temp ^= struct.unpack_from('<I', data, i*4)[0]

    return temp == checksum

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dsp_binary", type=str, help="The DSP binary you want to extract from.")
    args = parser.parse_args()

    split = args.dsp_binary.split('.')
    ext = split[-1]
    basename = '.'.join(split[:-1])

    fw = mediatek_lte_dsp_firmware.MediatekLteDspFirmware.from_file(args.dsp_binary)
    obfuscated = True if (fw.dsp_firmware.header.unk_1 & 0x100) != 0 else False
    offset = 0
    for i in range(fw.dsp_firmware.header.core_count):
        header = fw.dsp_firmware.header.core_headers[i]

        filename = "{}.file_idx_{}.core_idx_{}.code.{}".format(basename, i, header.core_idx, ext)
        code_len = header.core_code_len
        code = fw.dsp_firmware.body[offset:offset+code_len]
        print("{} checksum: {}".format(filename, "OK" if checksum_valid(code, header.core_code_checksum) else "FAIL"))
        if obfuscated:
            code = fw._io.process_xor_many(code, key)
        open(filename, 'wb').write(code)
        offset += code_len

        filename = "{}.file_idx_{}.core_idx_{}.data.{}".format(basename, i, header.core_idx, ext)
        data_len = header.core_data_len
        data = fw.dsp_firmware.body[offset:offset+data_len]
        print("{} checksum: {}".format(filename, "OK" if checksum_valid(data, header.core_data_checksum) else "FAIL"))
        if obfuscated:
            data = fw._io.process_xor_many(data, key)
        open(filename, 'wb').write(data)
        offset += data_len
