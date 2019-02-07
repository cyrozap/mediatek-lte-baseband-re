	.file	"init.S"
	.syntax unified

	.globl		_start

	.section	.init, "ax"
	.globl		_start

_start:
	mov		r0, #0
	mov		r1, #0
	mov		r2, #0
	mov		r3, #0
	mov		r4, #0
	mov		r5, #0
	mov		r6, #0
	mov		r7, #0
	mov		r8, #0
	mov		r9, #0
	mov		r10, #0
	mov		r11, #0
	mov		r12, #0
	mov		sp, #0
	mov		lr, #0

	mov		sp, #0x38000000

	ldr		pc, =main
