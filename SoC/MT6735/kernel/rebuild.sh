#!/bin/bash
set -e

# https://stackoverflow.com/a/4774063
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
TOOLPATH=$SCRIPTPATH/arm-eabi-4.8
KERNELPATH=$SCRIPTPATH/android_kernel_mediatek_mt6735

export CROSS_COMPILE="$TOOLPATH/bin/arm-eabi-"
export ARCH=arm
export ARCH_MTK_PLATFORM=mt6735

cd $KERNELPATH

make -j4
