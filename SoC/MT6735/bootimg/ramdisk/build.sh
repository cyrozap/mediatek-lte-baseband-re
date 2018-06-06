#!/bin/bash
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
