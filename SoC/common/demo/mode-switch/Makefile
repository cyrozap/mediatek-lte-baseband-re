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
