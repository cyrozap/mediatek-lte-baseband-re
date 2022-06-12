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

	.section .init, "ax"
	.global _start
_start:
	mov x0, xzr
	mov x1, xzr
	mov x2, xzr
	mov x3, xzr
	mov x4, xzr
	mov x5, xzr
	mov x6, xzr
	mov x7, xzr
	mov x8, xzr
	mov x9, xzr
	mov x10, xzr
	mov x11, xzr
	mov x12, xzr
	mov x13, xzr
	mov x14, xzr
	mov x15, xzr
	mov x16, xzr
	mov x17, xzr
	mov x18, xzr
	mov x19, xzr
	mov x20, xzr
	mov x21, xzr
	mov x22, xzr
	mov x23, xzr
	mov x24, xzr
	mov x25, xzr
	mov x26, xzr
	mov x27, xzr
	mov x28, xzr
	mov x29, xzr
	mov x30, xzr

_stack_init:
	ldr x0, =_stack_base
	mov sp, x0

_data_init:
	ldr x0, =_data_loadaddr
	ldr x1, =_data_start
	ldr x2, =_data_end
_data_init_loop:
	cmp x1, x2
	beq _bss_init
	ldp x3, x4, [x0], 16
	stp x3, x4, [x1], 16
	b   _data_init_loop

_bss_init:
	ldr x2, =_bss_end
_bss_init_loop:
	cmp x1, x2
	beq _cleanup
	stp xzr, xzr, [x1], 16
	b   _bss_init_loop

_cleanup:
	mov x0, xzr
	mov x1, xzr
	mov x2, xzr
	mov x3, xzr
	mov x4, xzr

_jump_to_main:
	bl  main

_wfi_loop:
	wfi
	b   _wfi_loop
