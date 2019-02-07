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
