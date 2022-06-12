/* SPDX-License-Identifier: 0BSD */

/*
 * Copyright (C) 2020 by Forest Crossman <cyrozap@gmail.com>
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

	.syntax		unified

	.section	.text.start, "ax"
	.global		_start
_start:
	push	{r0, r1, r2, r3, r4, lr}

	// Send the USB response to avoid a timeout.
	adr	r3, args + 0
	ldr	r3, [r3]  // Address of send_usb_response function, with Thumb bit set appropriately.
	cmp	r3, 0
	beq	reg_write_init
	mov	r0, 0  // send_usb_response arg 0.
	mov	r1, 0  // send_usb_response arg 1.
	mov	r2, 1  // send_usb_response arg 2.
	blx	r3

reg_write_init:
	adr	r2, args + 8  // Pointer to the operations array.
	mov	r3, 0
	adr	r4, args + 4
	ldr	r4, [r4]  // The number of operations.

reg_write_loop:
	cmp	r3, r4
	beq	done
	ldrd	r0, r1, [r2], 8
	str	r1, [r0]
	add	r3, r3, 1
	b	reg_write_loop

done:
	pop	{r0, r1, r2, r3, r4, pc}

args:
