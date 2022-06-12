# SPDX-License-Identifier: 0BSD

# Copyright (C) 2019, 2021 by Forest Crossman <cyrozap@gmail.com>
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


PREFIX := arm-none-eabi-
AS := $(PREFIX)as
ASFLAGS := -march=armv7-a
CC := $(PREFIX)gcc
#CFLAGS := -march=armv7-a -mthumb -mfloat-abi=soft -fpie -nostdlib -nostartfiles -nodefaultlibs -fno-builtin -Os
CFLAGS := -march=armv7-a -mfloat-abi=soft -fpie -nostdlib -nostartfiles -nodefaultlibs -fno-builtin -Os
LD := $(PREFIX)ld
LDFLAGS := -T linker.ld -Map mode-switch.map
OBJCOPY := $(PREFIX)objcopy
OBJDUMP := $(PREFIX)objdump

all: mode-switch.bin mode-switch.elf

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.o: %.S
	$(AS) $(ASFLAGS) -o $@ $<

mode-switch.elf: init.o main.o
	$(LD) $(LDFLAGS) -o $@ $^

%.bin: %.elf
	$(OBJCOPY) -S -O binary $< $@
	chmod -x $@

disasm-bin: mode-switch.bin
	$(OBJDUMP) -marm -b binary -D $<

disasm-elf: mode-switch.elf
	$(OBJDUMP) -d $<

clean:
	rm -f *.bin *.elf *.map *.o

.PHONY: all clean exec disasm-bin disasm-elf
