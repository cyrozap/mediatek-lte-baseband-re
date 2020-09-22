	.syntax		unified

	.section	.text.start, "ax"
	.global		_start
_start:
	push	{r0, r1, r2, r3, r4, lr}

	// Send the USB response to avoid a timeout.
	mov	r0, 0
	mov	r1, 0
	mov	r2, 1
	adr	r3, args + 0
	ldr	r3, [r3]  // Address of send_usb_response function, with Thumb bit set appropriately.
	cmp	r3, 0
	beq	reg_write_init
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
