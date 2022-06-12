/* SPDX-License-Identifier: GPL-3.0-or-later */

/*
 * Copyright (C) 2019-2020  Forest Crossman <cyrozap@gmail.com>
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

MEMORY
{
	rom (rx) : ORIGIN = 0x00201000, LENGTH = 0x00030000
	ram (rw) : ORIGIN = 0x00231000, LENGTH = 0x0000f000
}

ENTRY(_start)

_stack_base = ORIGIN(ram) + LENGTH(ram) - 16;

SECTIONS
{
	.text : {
		*(.init)
		*(.text*)
		. = ALIGN(16);
		*(.rodata*)
		. = ALIGN(16);
	} >rom

	.data : {
		_data_start = .;
		*(.data*)
		. = ALIGN(16);
		_data_end = .;
	} >ram AT >rom
	_data_loadaddr = LOADADDR(.data);

	.bss : {
		*(.bss*)
		. = ALIGN(16);
		_bss_end = .;
	} >ram

	/DISCARD/ : { *(.eh_frame) }

	. = ALIGN(16);
	end = .;
}
