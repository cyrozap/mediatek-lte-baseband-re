/* SPDX-License-Identifier: 0BSD */

/*
 * Copyright (C) 2021 by Forest Crossman <cyrozap@gmail.com>
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

MEMORY
{
	rom (rx) : ORIGIN = 0x00200000, LENGTH = 0x00000C00
	ram (rw) : ORIGIN = 0x00200C00, LENGTH = 0x00000400
}

ENTRY(_start)

_stack_base = ORIGIN(ram) + LENGTH(ram) - 8;

SECTIONS
{
	.text : {
		*(.init)
		*(.text*)
		. = ALIGN(4);
		*(.rodata*)
		. = ALIGN(4);
	} >rom

	.data : {
		_data_start = .;
		*(.data*)
		. = ALIGN(4);
		_data_end = .;
	} >ram AT >rom
	_data_loadaddr = LOADADDR(.data);

	.bss : {
		*(.bss*)
		. = ALIGN(4);
		_bss_end = .;
	} >ram

	/DISCARD/ : { *(.eh_frame) }

	. = ALIGN(4);
	end = .;
}
