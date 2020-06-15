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
