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
