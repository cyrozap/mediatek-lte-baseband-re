# SPDX-License-Identifier: 0BSD

# Copyright (C) 2020 by Forest Crossman <cyrozap@gmail.com>
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
LD := $(PREFIX)ld
LDFLAGS := -T linker.ld -Map write-sequence.map
OBJCOPY := $(PREFIX)objcopy
OBJDUMP := $(PREFIX)objdump

all: write-sequence.bin

%.o: %.S
	$(AS) $(ASFLAGS) -o $@ $<

%.elf: %.o
	$(LD) $(LDFLAGS) -o $@ $^

%.bin: %.elf
	$(OBJCOPY) -S -O binary $< $@
	chmod -x $@

disasm-bin: write-sequence.bin
	$(OBJDUMP) -marm -b binary -D $<

disasm-elf: write-sequence.elf
	$(OBJDUMP) -d $<

clean:
	rm -f *.bin *.elf *.map *.o

.PHONY: all clean disasm-bin disasm-elf
