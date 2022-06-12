/* SPDX-License-Identifier: GPL-3.0-or-later */

/*
 * Copyright (C) 2019  Forest Crossman <cyrozap@gmail.com>
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
#include <stdio.h>

#include "common.h"

int main(int argc, char *argv[])
{
	uint32_t address;
	uint32_t value;

	if (argc < 2 || argc > 3) {
		fprintf(stderr, "Usage: %s address [value]\n", argv[0]);
		return -1;
	}

	if (sscanf(argv[1], "%x", &address) != 1) {
		fprintf(stderr, "Error: address \"%s\" is not an integer\n", argv[1]);
		return -1;
	}

	if (address % 4 != 0) {
		fprintf(stderr, "Error: address 0x%08x must be a multiple of 4\n", address);
		return -1;
	}

	if (argc == 3) {
		if (sscanf(argv[2], "%x", &value) != 1) {
			fprintf(stderr, "Error: value \"%s\" is not an integer\n", argv[2]);
			return -1;
		}
	}

	mem_info_t mem_info;

	if (get_mem_info(&mem_info) != 0) {
		fprintf(stderr, "Error: get_mem_info() failed\n");
		return -1;
	}

	printf("*0x%08x = 0x%08x\n", address, mem_read(&mem_info, address));
	if (argc == 3) {
		mem_write(&mem_info, address, value);
		printf("*0x%08x = 0x%08x\n", address, mem_read(&mem_info, address));
	}

	return 0;
}
