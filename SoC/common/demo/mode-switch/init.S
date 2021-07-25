	.syntax unified

	.section .init, "ax"
	.global _start
_start:
	mov r0, #0
	mov r1, #0
	mov r2, #0
	mov r3, #0
	mov r4, #0
	mov r5, #0
	mov r6, #0
	mov r7, #0
	mov r8, #0
	mov r9, #0
	mov r10, #0
	mov r11, #0
	mov r12, #0
	mov lr, #0

_stack_init:
	ldr sp, =_stack_base

_data_init:
	ldr r0, =_data_loadaddr
	ldr r1, =_data_start
	ldr r2, =_data_end
_data_init_loop:
	cmp r1, r2
	beq _bss_init
	ldr r3, [r0], #4
	str r3, [r1], #4
	b   _data_init_loop

_bss_init:
	ldr r2, =_bss_end
	mov r3, #0
_bss_init_loop:
	cmp r1, r2
	beq _cleanup
	str r3, [r1], #4
	b   _bss_init_loop

_cleanup:
	mov r0, #0
	mov r1, #0
	mov r2, #0

_jump_to_main:
	bl  main

_wfi_loop:
	wfi
	b   _wfi_loop
