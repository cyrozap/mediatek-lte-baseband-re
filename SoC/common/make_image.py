#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

# make_image.py - A tool for generating bootable "preloader" images
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


'''\
Create "preloader" images suitable for booting on MediaTek platforms.

Provide an ARMv7-A/ARMv8-A (AArch32 or AArch64) binary as an input, and
this tool will convert it into an image that, depending on your selected
options, will be able to be booted from either eMMC flash or an SD card.

For example, to create an AArch32 eMMC image, run:

    ./make_image.py -b eMMC -o preloader-emmc.img code.bin

This can be written to the eMMC BOOT0 hardware partition using
MediaTek's SPFT utility, the same way any other preloader is written.

To create an AArch64 SD image, run:

    ./make_image.py -a aarch64 -b SD -o preloader-sd.img code.bin

To write the image to an SD card, run:

    sudo dd if=preloader-sd.img of=/dev/DEVICE bs=2048 seek=1

Where `/dev/DEVICE` is the path to your SD card, e.g., `/dev/sdX` or
`/dev/mmcblkX`.

This command writes the SD preloader to byte offset 2048 (LBA 4,
512-byte blocks) on the card, so you need to be careful how you
partition it.

With MBR, you can partition the device and write the preloader in any
order, so long as you make sure the first partition starts at sector
(LBA) 4096. This will give enough space for the largest possible
preloader size (1 MiB, the size of the L2 SRAM on some higher-end SoCs),
plus it will ensure your partitions are nicely aligned. 4096 is largely
an arbitrary number, since the smallest LBA number to avoid the first
partition overwriting the preloader is 2052 (LBA 4 + 1 MiB / 512 B), so
in theory you could use that (or an even smaller number for devices with
a 256 KiB L2 SRAM), but 4096 is a nice power of 2 so I like that better.

With GPT, you can also partition the device and write the preloader in
any order, but you have to take care when writing the partition table.
By default, the GPT partition entry table starts at LBA 2, and ends
before LBA 34. This conflicts with the requirements of the BROM since it
will only boot preloaders on SD from LBA 4 (and LBA 0, but that's not
terribly useful since it means you can't partition the card at all), and
that's where the 9th and following partition entries would normally be
in the partition entry array. To account for this, the partition entry
array needs to be relocated to another sector. To support a maximum
preloader size of 1 MiB, the partition entry array needs to be moved to
LBA 2052 (see the previous section for calculations).

Fortunately, `gdisk` provides an easy way to do this. To start, run
gdisk on your SD card:

    sudo gdisk /dev/DEVICE

Where `/dev/DEVICE` is the path to your SD card, e.g., `/dev/sdX` or
`/dev/mmcblkX`.

Next, type "x" to enter the "extra functionality (experts only)" menu,
then type "j" to enter the "move the main partition table" dialog. Next,
enter the number of the sector (LBA) for the partition table to start at
(2052, as calculated previously). Then, return to the main menu with "m"
and continue partitioning normally. By default, gdisk will align
partitions on 1 MiB boundaries, so it will offer to place the first
partition at LBA 4096. If you need more space, because the partition
entry array was set to an offset beyond the maximum preloader size, and
the earliest a partition can start is after that table, you can safely
go down to the minimum sector offset offered without overwriting the
preloader.

'''


import argparse
import enum
import hashlib
import struct


class code_arch(enum.Enum):
    aarch32 = enum.auto()
    aarch64 = enum.auto()

class flash_device(enum.Enum):
    EMMC = enum.auto()
    SD = enum.auto()

class gfh_type(enum.Enum):
    FILE_INFO = enum.auto(),
    BL_INFO = enum.auto(),
    ANTI_CLONE = enum.auto(),
    BL_SEC_KEY = enum.auto(),
    BROM_CFG = enum.auto(),
    BROM_SEC_CFG = enum.auto(),


def gen_gfh_header(type, version):
    magic = b'MMM'

    size = {
        gfh_type.FILE_INFO: 56,
        gfh_type.BL_INFO: 12,
        gfh_type.ANTI_CLONE: 20,
        gfh_type.BL_SEC_KEY: 532,
        gfh_type.BROM_CFG: 100,
        gfh_type.BROM_SEC_CFG: 48,
    }.get(type)
    if size == None:
        raise ValueError("Unknown gfh_type: {}".format(type))

    type = {
        gfh_type.FILE_INFO: 0,
        gfh_type.BL_INFO: 1,
        gfh_type.ANTI_CLONE: 2,
        gfh_type.BL_SEC_KEY: 3,
        gfh_type.BROM_CFG: 7,
        gfh_type.BROM_SEC_CFG: 8,
    }.get(type)

    h = struct.pack('3s', magic)
    h += struct.pack('B', version)
    h += struct.pack('<H', size)
    h += struct.pack('<H', type)

    return h

def gen_gfh_file_info(file_type, flash_dev, offset, base_addr, start_addr, max_size, payload_size):
    identifier = b'FILE_INFO'
    file_ver = 1
    sig_type = 1  # SIG_PHASH
    load_addr = base_addr - offset
    sig_len = 32  # SHA256
    file_len = offset + payload_size + sig_len
    jump_offset = start_addr - load_addr
    attr = 1

    file_info = gen_gfh_header(gfh_type.FILE_INFO, 1)
    file_info += struct.pack('12s', identifier)
    file_info += struct.pack('<I', file_ver)
    file_info += struct.pack('<H', file_type)
    file_info += struct.pack('B', flash_dev)
    file_info += struct.pack('B', sig_type)
    file_info += struct.pack('<I', load_addr)
    file_info += struct.pack('<I', file_len)
    file_info += struct.pack('<I', max_size)
    file_info += struct.pack('<I', offset)
    file_info += struct.pack('<I', sig_len)
    file_info += struct.pack('<I', jump_offset)
    file_info += struct.pack('<I', attr)

    return file_info

def gen_gfh_bl_info():
    bl_info = gen_gfh_header(gfh_type.BL_INFO, 1)
    bl_info += struct.pack('<I', 1)

    return bl_info

def gen_gfh_brom_cfg(arch):
    brom_cfg = gen_gfh_header(gfh_type.BROM_CFG, 3)
    # TODO: Make this configurable.
    brom_cfg += bytes.fromhex("9001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000881300000000000000000000")

    if arch == code_arch.aarch64:
        brom_cfg = bytearray(brom_cfg)

        # Set the flag.
        flags = struct.unpack_from('<I', brom_cfg, 8)[0]
        flags |= 1 << 12
        struct.pack_into('<I', brom_cfg, 8, flags)

        # Set the magic value.
        brom_cfg[0x55] = 0x64

        brom_cfg = bytes(brom_cfg)

    return brom_cfg

def gen_gfh_bl_sec_key():
    bl_sec_key = gen_gfh_header(gfh_type.BL_SEC_KEY, 1)
    bl_sec_key += bytes(bytearray(524))

    return bl_sec_key

def gen_gfh_anti_clone():
    anti_clone = gen_gfh_header(gfh_type.ANTI_CLONE, 1)
    anti_clone += bytes(bytearray(12))

    return anti_clone

def gen_gfh_brom_sec_cfg():
    brom_sec_cfg = gen_gfh_header(gfh_type.BROM_SEC_CFG, 1)
    brom_sec_cfg += struct.pack('<I', 3)
    brom_sec_cfg += bytes(bytearray(36))

    return brom_sec_cfg

def gen_image(boot_device, payload, payload_arch):
    # Header
    identifier = {
        flash_device.EMMC: b'EMMC_BOOT',
        flash_device.SD: b'SDMMC_BOOT',
    }.get(boot_device)
    if identifier == None:
        raise ValueError("Unknown boot_device: {}".format(boot_device))

    version = 1

    dev_rw_unit = {
        flash_device.EMMC: 512,
        flash_device.SD: 512,
    }.get(boot_device)

    header = struct.pack('12s', identifier)
    header += struct.pack('<I', version)
    header += struct.pack('<I', dev_rw_unit)

    assert(len(header) <= dev_rw_unit)
    padding_length = dev_rw_unit - len(header)
    header += bytes(bytearray(padding_length))

    # Boot ROM layout
    identifier = b'BRLYT'
    version = 1
    gfh_block_offset = 4
    # Must be >=2 to account for the device header and boot ROM layout blocks.
    assert(gfh_block_offset >= 2)
    boot_region_addr = {
        flash_device.EMMC: dev_rw_unit * gfh_block_offset,
        flash_device.SD: dev_rw_unit * gfh_block_offset + 2048,  # SDMMC_BOOT is flashed to byte offset 2048 on the SD card.
    }.get(boot_device)
    max_preloader_size = 0x40000  # 0x40000 is the size of the L2 SRAM, so the maximum possible size of the preloader.
    main_region_addr = max_preloader_size + boot_region_addr

    layout = struct.pack('8s', identifier)
    layout += struct.pack('<I', version)
    layout += struct.pack('<I', boot_region_addr)
    layout += struct.pack('<I', main_region_addr)

    # bootloader_descriptors[0]
    bl_exist_magic = b'BBBB'
    bl_dev = {
        flash_device.EMMC: 5,
        flash_device.SD: 8,
    }.get(boot_device)
    bl_type = 1  # ARM_BL
    bl_begin_addr = boot_region_addr
    bl_boundary_addr = main_region_addr
    bl_attribute = 1

    layout += struct.pack('4s', bl_exist_magic)
    layout += struct.pack('<H', bl_dev)
    layout += struct.pack('<H', bl_type)
    layout += struct.pack('<I', bl_begin_addr)
    layout += struct.pack('<I', bl_boundary_addr)
    layout += struct.pack('<I', bl_attribute)

    layout_max_size = dev_rw_unit * (gfh_block_offset - 1)
    assert(len(layout) <= layout_max_size)
    padding_length = layout_max_size - len(layout)
    layout += bytes(bytearray(padding_length))

    # GFH image
    offset = 0x300
    base_addr = 0x201000
    start_addr = base_addr
    image = gen_gfh_file_info(bl_type, bl_dev, offset, base_addr, start_addr, max_preloader_size, len(payload))
    image += gen_gfh_bl_info()
    image += gen_gfh_brom_cfg(payload_arch)
    image += gen_gfh_bl_sec_key()
    image += gen_gfh_anti_clone()
    image += gen_gfh_brom_sec_cfg()

    assert(len(image) <= offset)
    padding_length = offset - len(image)
    image += bytes(bytearray(padding_length))

    image += payload

    image += hashlib.sha256(image).digest()

    return header + layout + image

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Input binary.")
    parser.add_argument("-o", "--output", type=str, default="preloader.img", help="Output image.")
    parser.add_argument("-b", "--boot-device", type=str, choices=["eMMC", "SD"], default="eMMC", help="Boot device.")
    parser.add_argument("-a", "--arch", type=str, choices=["aarch32", "aarch64"], default="aarch32", help="Code architecture. Choose \"aarch32\" if you're booting 32-bit ARM code, \"aarch64\" for 64-bit ARM code.")
    args = parser.parse_args()

    binary = open(args.input, 'rb').read()
    padding_length = 4 - (len(binary) % 4)
    if padding_length != 4:
        binary += bytes(bytearray(padding_length))

    boot_device = {
        "eMMC": flash_device.EMMC,
        "SD": flash_device.SD,
    }.get(args.boot_device)

    arch = {
        "aarch32": code_arch.aarch32,
        "aarch64": code_arch.aarch64,
    }.get(args.arch)

    image = gen_image(boot_device, binary, arch)

    output = open(args.output, 'wb')
    output.write(image)
    output.close()
