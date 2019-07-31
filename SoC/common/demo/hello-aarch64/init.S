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
	ldr x0, =0x00108000
	mov sp, x0

_data_init:
	ldr x0, =_data_loadaddr
	ldr x1, =_data_start
	ldr x2, =_data_end
_data_init_loop:
	cmp x1, x2
	beq _bss_init
	ldr x3, [x0]
	add x0, x0, 8
	str x3, [x1]
	add x1, x1, 8
	b   _data_init_loop

_bss_init:
	ldr x2, =_bss_end
_bss_init_loop:
	cmp x1, x2
	beq _cleanup
	str xzr, [x1]
	add x1, x1, 8
	b   _bss_init_loop

_cleanup:
	mov x0, xzr
	mov x1, xzr
	mov x2, xzr
	mov x3, xzr

_jump_to_main:
	bl  main

_wfi_loop:
	wfi
	b   _wfi_loop
