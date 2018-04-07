#!/bin/bash
#
# Reconfigure the pinmux for the SD card pins (MSDC1) to enable JTAG.
# Note that these pins can also be used for SWD, with TMS and TCK as
# SWDIO and SWCLK respectively.
#
# Pin mapping:
# +------+-------+
# |  SD  |  JTAG |
# |------+-------|
# | DAT1 |  TDO  |
# | DAT0 |  TDI  |
# | CLK  |  TCK  |
# | CMD  |  TMS  |
# +------+-------+
#

adb shell su -c /data/local/tmp/poke 0x10211400 0x6db11249
