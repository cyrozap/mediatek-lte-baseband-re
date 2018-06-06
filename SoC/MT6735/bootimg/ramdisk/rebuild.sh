#!/bin/bash
set -e

# Generate new ramdisk.
fakeroot -i ramdisk.fakeroot -- cpio -o -H newc -D ramdisk < ramdisk.list | gzip > ramdisk-no-mdinit.gz
