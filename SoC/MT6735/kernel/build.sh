#!/bin/bash
# SPDX-License-Identifier: 0BSD

# Copyright (C) 2018-2019 by Forest Crossman <cyrozap@gmail.com>
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
TOOLPATH=$SCRIPTPATH/arm-eabi-4.8
KERNELPATH=$SCRIPTPATH/android_kernel_mediatek_mt6735

[ -d $TOOLPATH ] || git clone https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-eabi-4.8 $TOOLPATH
[ -d $KERNELPATH ] || git clone https://github.com/blumonks/android_kernel_mediatek_mt6735.git $KERNELPATH

export CROSS_COMPILE="$TOOLPATH/bin/arm-eabi-"
export ARCH=arm
export ARCH_MTK_PLATFORM=mt6735

cd $KERNELPATH

for i in {0001..0005}; do
	patch -p1 < ../$i*.patch
done

make p6601_defconfig

patch .config ../0006-config.patch

make -j4
