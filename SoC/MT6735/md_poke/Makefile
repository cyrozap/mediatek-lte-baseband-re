CC := arm-linux-gnueabihf-gcc
CFLAGS := -Wall -Werror -static

all: md_poke

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

push: md_poke
	adb push $^ /data/local/tmp

clean:
	rm -f md_poke

.PHONY: all clean push
