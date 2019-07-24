#include <stddef.h>
#include <stdint.h>

volatile uint32_t * const mem = (volatile uint32_t * const)(0x00000000);
volatile uint32_t * const sram = (volatile uint32_t * const)(0x00100000);
volatile uint32_t * const l2_sram = (volatile uint32_t * const)(0x00200000);

#define UART_BASE 0x11002000
#define UART_RBR  (UART_BASE + 0x00)
#define UART_THR  (UART_BASE + 0x00)
#define UART_LSR  (UART_BASE + 0x14)

#define UART_LSR_DR   (1 << 0)
#define UART_LSR_THRE (1 << 5)

static char getchar(void) {
	char ret;

	// Wait for the UART to assert the "data ready" flag.
	while ((mem[UART_LSR/4] & UART_LSR_DR) == 0);

	ret = mem[UART_RBR/4] & 0xff;

	return ret;
}

static void putchar(char c) {
	// Wait for the UART to become ready.
	while ((mem[UART_LSR/4] & UART_LSR_THRE) == 0);

	if (c == '\n')
		putchar('\r');

	mem[UART_THR/4] = c;
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
	size_t len = strnlen(buf, 256);

	for (size_t i = 0; i < len; i++) {
		putchar(buf[i]);
	}

	putchar('\n');
}

static void wfi() {
	asm("wfi");
}

static void jump_to_aarch64(uint32_t addr) {
	asm(
		"ldr r0, =0x10200038\n"
		"str %0, [r0]\n"
		"dsb sy\n"
		"isb sy\n"
		"mrc 15, 0, r0, cr12, cr0, 2\n"
		"orr r0, r0, #3\n"
		"mcr 15, 0, r0, cr12, cr0, 2\n"
		"isb sy\n"
		: /* No outputs. */
		: "r" (addr)
		: "r0"
	);

	println("Switching to AArch64!");
	while(1) {
		wfi();
	}
}

void main(void) {
	println("Executing mode-switch...");
	jump_to_aarch64(0x00201000);
	while (1) {
	}
}
