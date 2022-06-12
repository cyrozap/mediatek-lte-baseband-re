# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (C) 2019-2020  Forest Crossman <cyrozap@gmail.com>
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


PREFIX := aarch64-linux-gnu-
AS := $(PREFIX)as
ASFLAGS := -march=armv8-a
CC := $(PREFIX)gcc
CFLAGS := -Wall -march=armv8-a -nostdlib -nostartfiles -nodefaultlibs -fno-builtin -Os
LD := $(PREFIX)ld
LDFLAGS := -T linker.ld -Map hello-aarch64.map
OBJCOPY := $(PREFIX)objcopy
OBJDUMP := $(PREFIX)objdump

all: hello-aarch64.bin hello-aarch64.elf

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.o: %.S
	$(AS) $(ASFLAGS) -o $@ $<

build_info.c: build_info.inc.c
	sed s/BUILD_VERSION/$(shell printf "r%s.g%s" "$(shell git rev-list --count HEAD)" "$(shell git rev-parse --short HEAD)")/g $< | \
		sed s/BUILD_TIME/$(shell date -u '+%FT%H:%M:%SZ')/g > $@

hello-aarch64.elf: init.o main.o build_info.o
	$(LD) $(LDFLAGS) -o $@ $^

%.bin: %.elf
	$(OBJCOPY) -S -O binary $< $@
	chmod -x $@

disasm-bin: hello-aarch64.bin
	$(OBJDUMP) -maarch64 -b binary -D $<

disasm-elf: hello-aarch64.elf
	$(OBJDUMP) -d $<

clean:
	rm -f *.bin *.elf *.map *.o build_info.c

.PHONY: all clean exec disasm-bin disasm-elf build_info.c
