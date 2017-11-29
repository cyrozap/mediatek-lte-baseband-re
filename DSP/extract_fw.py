#!/usr/bin/env python3

import struct
import sys

import mediatek_lte_dsp_firmware

key = bytes([0x40, 0xeb, 0xf8, 0x56, 0x8b, 0x74, 0x24, 0x08, 0x66, 0x85, 0xf6, 0x74, 0x30, 0x66, 0x83, 0xfe])

def checksum_valid(data, checksum):
    if checksum == 0:
        return True

    temp = 0
    for i in range(len(data)//4):
        temp ^= struct.unpack_from('<I', data, i*4)[0]

    return temp == checksum

if __name__ == "__main__":
    orig = sys.argv[1]
    split = orig.split('.')
    ext = split[-1]
    basename = '.'.join(split[:-1])

    fw = mediatek_lte_dsp_firmware.MediatekLteDspFirmware.from_file(orig)
    offset = 0
    for i in range(fw.dsp_firmware.header.core_count):
        header = fw.dsp_firmware.header.core_headers[i]

        filename = "{}.file_idx_{}.core_idx_{}.code.{}".format(basename, i, header.core_idx, ext)
        code_len = header.core_code_len
        code = fw.dsp_firmware.body[offset:offset+code_len]
        code = fw._io.process_xor_many(code, key)
        open(filename, 'wb').write(code)
        offset += code_len

        filename = "{}.file_idx_{}.core_idx_{}.data.{}".format(basename, i, header.core_idx, ext)
        data_len = header.core_data_len
        data = fw.dsp_firmware.body[offset:offset+data_len]
        data = fw._io.process_xor_many(data, key)
        open(filename, 'wb').write(data)
        offset += data_len
