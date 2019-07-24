PREFIX := aarch64-linux-gnu-
AS := $(PREFIX)as
ASFLAGS := -march=armv8-a
CC := $(PREFIX)gcc
CFLAGS := -march=armv8-a -fpie -nostdlib -nostartfiles -nodefaultlibs -fno-builtin -Os
LD := $(PREFIX)ld
LDFLAGS := -T linker.ld -Map hello-aarch64.map
OBJCOPY := $(PREFIX)objcopy
OBJDUMP := $(PREFIX)objdump

all: hello-aarch64.bin hello-aarch64.elf

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.o: %.S
	$(AS) $(ASFLAGS) -o $@ $<

hello-aarch64.elf: init.o main.o
	$(LD) $(LDFLAGS) -o $@ $^

%.bin: %.elf
	$(OBJCOPY) -S -O binary $< $@
	chmod -x $@

disasm-bin: hello-aarch64.bin
	$(OBJDUMP) -maarch64 -b binary -D $<

disasm-elf: hello-aarch64.elf
	$(OBJDUMP) -d $<

clean:
	rm -f *.bin *.elf *.map *.o

.PHONY: all clean exec disasm-bin disasm-elf
