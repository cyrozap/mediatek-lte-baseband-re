#!/bin/bash
set -e

# https://stackoverflow.com/a/4774063
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

[ -d arm-eabi-4.8 ] || git clone https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-eabi-4.8
[ -d android_kernel_mediatek_mt6735 ] || git clone https://github.com/blumonks/android_kernel_mediatek_mt6735.git

export CROSS_COMPILE="$SCRIPTPATH/arm-eabi-4.8/bin/arm-eabi-"
export ARCH=arm
export ARCH_MTK_PLATFORM=mt6735

cd android_kernel_mediatek_mt6735

patch -p1 < ../0001-fix-build.patch
patch -p1 < ../0002-enable-ccci-debug.patch

make p6601_defconfig

patch .config ../0003-config.patch

make -j4
