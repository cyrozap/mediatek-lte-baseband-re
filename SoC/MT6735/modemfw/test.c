/* SPDX-License-Identifier: GPL-3.0-or-later */

/*
 * Copyright (C) 2018-2019  Forest Crossman <cyrozap@gmail.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 */

#include <stdint.h>

volatile uint32_t * const ap_base = (volatile uint32_t * const)(0x90000000);
volatile uint32_t * const smem = (volatile uint32_t * const)(0x03800000);
volatile uint32_t * const data = (volatile uint32_t * const)(0x00000000);

// These are just GPIO registers I'm using as generic un-cached memory.
#define AP2MD_REG 0x10211160
#define MD2AP_REG 0x10211150

static char getchar(void) {
	char ret;

	// Wait for the AP to set the "data valid" flag.
	while ((ap_base[AP2MD_REG/4] & 0x100) == 0);

	ret = ap_base[AP2MD_REG/4] & 0xff;
	ap_base[AP2MD_REG/4] &= 0xfffffeff;

	return ret;
}

static void putchar(char c) {
	// Wait for the AP to clear the "data valid" flag.
	while ((ap_base[MD2AP_REG/4] & 0x100) != 0);

	ap_base[MD2AP_REG/4] &= 0xffffff00;
	ap_base[MD2AP_REG/4] |= c;
	ap_base[MD2AP_REG/4] |= 0x100;
}

static void handle_read() {
	// Get the address.
	uint32_t addr = 0;
	for (uint8_t i = 0; i < 4; i++) {
		uint8_t c = getchar();
		addr |= c << (8 * i);
	}
	// Save the data at that address.
	uint32_t dword = data[addr/4];
	// Send the data.
	for (uint8_t i = 0; i < 4; i++) {
		uint8_t c = (dword >> (8 * i)) & 0xff;
		putchar(c);
	}
}

static void handle_write() {
	// Get the address.
	uint32_t addr = 0;
	for (uint8_t i = 0; i < 4; i++) {
		uint8_t c = getchar();
		addr |= c << (8 * i);
	}
	// Get the data.
	uint32_t dword = 0;
	for (uint8_t i = 0; i < 4; i++) {
		uint8_t c = getchar();
		dword |= c << (8 * i);
	}
	// Write the data to the address.
	data[addr/4] = dword;
}

typedef enum {
	CMD_READ = 0x40,
	CMD_WRITE = 0x80,
} cmd_t;

void main(void) {
	// Enable JTAG on SD card port.
	ap_base[0x10211400/4] = 0x6db11249;

	// Clear registers.
	ap_base[AP2MD_REG/4] &= 0xfffffe00;
	ap_base[MD2AP_REG/4] &= 0xfffffe00;

	while (1) {
		char cmd = getchar();

		switch (cmd) {
		case CMD_READ:
			handle_read();
			break;
		case CMD_WRITE:
			handle_write();
			break;
		default:
			break;
		}
	}
}
