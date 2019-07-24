#include <stddef.h>
#include <stdint.h>

volatile uint32_t * const mem = (volatile uint32_t * const)(0x00000000);
#define SRAM 0x00100000
#define L2_SRAM 0x00200000

static uint32_t UART_RBR;
static uint32_t UART_THR;
static uint32_t UART_LSR;

#define UART_LSR_DR   (1 << 0)
#define UART_LSR_THRE (1 << 5)

static uint32_t readw(uint32_t reg) {
	return mem[reg/4];
}

static void writew(uint32_t reg, uint32_t word) {
	mem[reg/4] = word;
}

static char getchar(void) {
	char ret;

	// Wait for the UART to assert the "data ready" flag.
	while ((readw(UART_LSR) & UART_LSR_DR) == 0);

	ret = readw(UART_RBR) & 0xff;

	return ret;
}

static void putchar(char c) {
	// Wait for the UART to become ready.
	while ((readw(UART_LSR) & UART_LSR_THRE) == 0);

	if (c == '\n')
		putchar('\r');

	writew(UART_THR, c);
}

static size_t strnlen(const char * buf, size_t max_len) {
	size_t len = 0;
	for (size_t i = 0; i < max_len; i++) {
		if (buf[i] == 0)
			break;
		len++;
	}
	return len;
}

static void println(const char * buf) {
	size_t len = 256;

	for (size_t i = 0; i < len; i++) {
		if (buf[i] == 0)
			break;
		putchar(buf[i]);
	}

	putchar('\n');
}

static void init(void) {
	uint32_t UART_BASE;
	uint32_t soc_id = readw(0x08000000);
	switch(soc_id) {
	case 0x0279:
		// MT6797
		UART_BASE = 0x11002000;
		break;
	case 0x0321:
		// MT6735
		UART_BASE = 0x11002000;
		break;
	case 0x0335:
		// MT6737M
		UART_BASE = 0x11002000;
		break;
	case 0x8163:
		// MT8163
		UART_BASE = 0x11002000;
		break;
	default:
		UART_BASE = 0x11002000;
		break;
	}
	UART_RBR = UART_BASE + 0x00;
	UART_THR = UART_BASE + 0x00;
	UART_LSR = UART_BASE + 0x14;
}

void main(void) {
	init();
	println("Hello from AArch64!");
	while (1) {
		char c = getchar();
		if (('A' <= c && c <= 'Z') || ('a' <= c && c <= 'z')) {
			c ^= 0x20;
		} else if (c == '\r') {
			c = '\n';
		}
		putchar(c);
	}
}
