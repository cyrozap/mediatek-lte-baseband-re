/* SPDX-License-Identifier: 0BSD */

/*
 * Copyright (C) 2019-2021 by Forest Crossman <cyrozap@gmail.com>
 *
 * Permission to use, copy, modify, and/or distribute this software for
 * any purpose with or without fee is hereby granted.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
 * WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
 * AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
 * DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
 * PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
 * TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
 * PERFORMANCE OF THIS SOFTWARE.
 *
 */

#include <stddef.h>
#include <stdint.h>

static uint32_t volatile * const mem = (uint32_t volatile * const)(0x00000000);
static uint32_t volatile * const sram = (uint32_t volatile * const)(0x00100000);
static uint32_t volatile * const l2_sram = (uint32_t volatile * const)(0x00200000);

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

static void print(const char * buf) {
	for (size_t i = 0; ; i++) {
		if (buf[i] == 0)
			break;
		putchar(buf[i]);
	}
}

static void println(const char * buf) {
	print(buf);
	putchar('\n');
}

static void wfi() {
	asm("wfi");
}

static const uint32_t get_rvbar(void) {
	uint32_t soc_id = mem[0x08000000/4];
	switch(soc_id) {
	case 0x0279:
		// MT6797
		return 0x10220038;
	case 0x0321:
		// MT6735
		return 0x10200038;
	case 0x0326:
		// MT6750
		return 0x10200038;
	case 0x0335:
		// MT6737M
		return 0x10200038;
	case 0x0788:
		// MT6771/MT8183
		return 0x0c530038;
	case 0x8163:
		// MT8163
		return 0x10200038;
	default:
		return 0x10200038;
	}
}

static void jump_to_aarch64(uint32_t addr) {
	uint32_t rvbar = get_rvbar();
	asm(
		"str %[addr], [%[rvbar]]\n"
		"dsb sy\n"
		"isb sy\n"
		"mrc 15, 0, r0, cr12, cr0, 2\n"
		"orr r0, r0, #3\n"
		"mcr 15, 0, r0, cr12, cr0, 2\n"
		"isb sy\n"
		: /* No outputs. */
		: [addr] "r" (addr), [rvbar] "r" (rvbar)
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
