#!/bin/bash
# SPDX-License-Identifier: 0BSD

# Copyright (C) 2018 by Forest Crossman <cyrozap@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
# PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.


set -e

# https://stackoverflow.com/a/4774063
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
MKBOOTIMG_PATH=$SCRIPTPATH/mkbootimg
KERNEL=$SCRIPTPATH/../kernel/android_kernel_mediatek_mt6735/arch/arm/boot/zImage-dtb
DUMP_PATH=$SCRIPTPATH/dump
OLD_BOOTIMG=$DUMP_PATH/boot.img
OLD_RAMDISK=$DUMP_PATH/boot.img-ramdisk.gz
NEW_BOOTIMG=$SCRIPTPATH/boot_new.img
NEW_RAMDISK_PATH=$SCRIPTPATH/ramdisk
NEW_RAMDISK=$NEW_RAMDISK_PATH/ramdisk-no-mdinit.gz

if [ ! -d $MKBOOTIMG_PATH ]; then
	git clone https://github.com/Ud3v0id/mkbootimg.git $MKBOOTIMG_PATH
	make -C $MKBOOTIMG_PATH
fi

if [ ! -e $OLD_RAMDISK ]; then
	if [ ! -e $OLD_BOOTIMG ]; then
		echo "Error: Could not find $OLD_BOOTIMG"
		exit 1
	fi
	$MKBOOTIMG_PATH/unpackbootimg -i $OLD_BOOTIMG -o $DUMP_PATH
fi

if [ ! -e $NEW_RAMDISK ]; then
	(cd $NEW_RAMDISK_PATH && ./build.sh)
fi

$MKBOOTIMG_PATH/mkbootimg \
	--kernel $KERNEL \
	--ramdisk $NEW_RAMDISK \
	--cmdline bootopt=64S3,32N2,32N2 \
	--board BLU_R0011UU_V12 \
	--base 40000000 \
	--pagesize 2048 \
	--ramdisk_offset 04000000 \
	--tags_offset 0e000000 \
	-o $NEW_BOOTIMG

echo "Boot image generated at $NEW_BOOTIMG"
