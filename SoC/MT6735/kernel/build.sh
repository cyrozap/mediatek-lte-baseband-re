#!/bin/bash
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

patch -p1 < ../0001-fix-build.patch
patch -p1 < ../0002-enable-ccci-debug.patch

make p6601_defconfig

patch .config ../0003-config.patch

make -j4
