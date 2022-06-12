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


adb shell su -c /data/local/tmp/poke 0x10211400 0x6db11249
