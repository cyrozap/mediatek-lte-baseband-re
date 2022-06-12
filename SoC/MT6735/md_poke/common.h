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

#ifndef COMMON_H
#define COMMON_H

typedef enum {
	CMD_READ = 0x40,
	CMD_WRITE = 0x80,
} cmd_t;

typedef struct mem_info_s {
		volatile uint32_t * regs;
		uint32_t ap2md_offset;
		uint32_t md2ap_offset;
} mem_info_t;

void mem_write(mem_info_t * mem_info, uint32_t addr, uint32_t data);

uint32_t mem_read(mem_info_t * mem_info, uint32_t addr);

int get_mem_info(mem_info_t * mem_info);

#endif
