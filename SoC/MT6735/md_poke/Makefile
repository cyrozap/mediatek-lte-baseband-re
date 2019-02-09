CC := arm-linux-gnueabihf-gcc
CFLAGS := -Wall -Werror -static

all: md_poke

md_poke: md_poke.o common.o
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

push: md_poke
	adb push $^ /data/local/tmp

clean:
	rm -f md_poke *.o

.PHONY: all clean push
