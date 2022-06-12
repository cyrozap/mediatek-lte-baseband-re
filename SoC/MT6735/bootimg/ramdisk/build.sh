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
OLD_RD=$SCRIPTPATH/../dump/*-ramdisk.gz

if [ ! -d ramdisk ]; then
	mkdir ramdisk

	# Generate a list of all the files in the ramdisk.
	zcat $OLD_RD | cpio -t > ramdisk.list

	# Extract the ramdisk without root.
	# https://unix.stackexchange.com/a/289280
	zcat $OLD_RD | fakeroot -s ramdisk.fakeroot -- cpio -i -D ramdisk
fi

# Patch files.
fakeroot -i ramdisk.fakeroot -- patch -p1 < 0001-disable-modem-init.patch

# Generate new ramdisk.
fakeroot -i ramdisk.fakeroot -- cpio -o -H newc -D ramdisk < ramdisk.list | gzip > ramdisk-no-mdinit.gz
