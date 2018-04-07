CC := arm-linux-gnueabihf-gcc
CFLAGS := -Wall -Werror -static

all: poke

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

push: poke
	adb push $^ /data/local/tmp

clean:
	rm -f poke

.PHONY: all clean push
