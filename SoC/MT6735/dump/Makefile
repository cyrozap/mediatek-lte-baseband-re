CC := arm-linux-gnueabihf-gcc
CFLAGS := -Wall -Werror -static

all: dump

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

push: dump
	adb push $^ /data/local/tmp

clean:
	rm -f dump

.PHONY: all clean push
