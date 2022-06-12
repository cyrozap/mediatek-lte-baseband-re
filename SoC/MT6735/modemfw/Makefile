# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2018-2019  Forest Crossman <cyrozap@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


AS := arm-none-eabi-as
ASFLAGS := -mcpu=cortex-r4
CC := arm-none-eabi-gcc
CFLAGS := -mcpu=cortex-r4 -mthumb -mfloat-abi=soft -fpie -nostdlib -nostartfiles -nodefaultlibs -fno-builtin -Os
LD := arm-none-eabi-ld
LDFLAGS := -T modem.ld -Map test.map

all: test.img test.bin test.elf

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.o: %.S
	$(AS) $(ASFLAGS) -o $@ $<

test.elf: vectors.o init.o test.o
	$(LD) $(LDFLAGS) -o $@ $^

%.bin: %.elf
	arm-none-eabi-objcopy -S -O binary $< $@
	chmod -x $@

%.img: %.bin make_img.py
	./make_img.py -o $@ $<

install: test.img
	adb push $< /data/local/tmp
	adb shell su -c mount -o remount,rw /dev/block/platform/mtk-msdc.0/11230000.msdc0/by-name/system /system
	adb shell su -c cp /data/local/tmp/$< /system/etc/firmware/modem_1_lwg_n.img
	adb shell su -c chmod 644 /system/etc/firmware/modem_1_lwg_n.img
	adb shell su -c mount -o remount,ro /dev/block/platform/mtk-msdc.0/11230000.msdc0/by-name/system /system

load:
	adb shell su -c /system/bin/ccci_mdinit 0

dmesg:
	adb shell dmesg | grep ccci_mdinit

disasm-bin: test.bin
	arm-none-eabi-objdump -marm -Mforce-thumb -b binary -D $<

disasm-elf: test.elf
	arm-none-eabi-objdump -d $<

clean:
	rm -f test.img test.bin *.o *.elf *.map

.PHONY: all clean install load dmesg disasm-bin disasm-elf
