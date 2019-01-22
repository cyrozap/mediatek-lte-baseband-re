CFLAGS := -Wall -Wextra -Werror

all: handshake

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f handshake

.PHONY: all clean
