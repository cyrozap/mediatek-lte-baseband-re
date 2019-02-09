CC := arm-linux-gnueabihf-gcc
CFLAGS := -Wall -Werror -static

all: md_dump md_poke

md_dump: md_dump.o common.o
	$(CC) $(CFLAGS) -o $@ $^

md_poke: md_poke.o common.o
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

push: md_dump md_poke
	adb push $^ /data/local/tmp

clean:
	rm -f md_dump md_poke *.o

.PHONY: all clean push
