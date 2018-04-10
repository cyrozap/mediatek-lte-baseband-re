#!/bin/bash
set -e

# https://stackoverflow.com/a/4774063
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

export CROSS_COMPILE="$SCRIPTPATH/arm-eabi-4.8/bin/arm-eabi-"
export ARCH=arm
export ARCH_MTK_PLATFORM=mt6735

cd android_kernel_mediatek_mt6735

make -j4
