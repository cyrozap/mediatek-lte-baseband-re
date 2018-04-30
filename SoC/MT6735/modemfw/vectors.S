/****************************************************************************
 * arch/arm/src/arm7-r/arm_vectortab.S
 *
 *   Copyright (C) 2015 Gregory Nutt. All rights reserved.
 *   Author: Gregory Nutt <gnutt@nuttx.org>
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 * 3. Neither the name NuttX nor the names of its contributors may be
 *    used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
 * OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 ****************************************************************************/

/****************************************************************************
 * Included Files
 ****************************************************************************/


	.file	"vectors.S"
	.syntax unified


/****************************************************************************
 * Pre-processor Definitions
 ****************************************************************************/

/****************************************************************************
 * Public Symbols
 ****************************************************************************/

	.globl		_vector_start
	.globl		_vector_end

/****************************************************************************
 * Assembly Macros
 ****************************************************************************/

/****************************************************************************
 * Name: _vector_start
 *
 * Description:
 *   Vector initialization block
 ****************************************************************************/

	.section	.vectors, "ax"
	.globl		_vector_start

/* These will be relocated to VECTOR_BASE. */

.thumb_func
_vector_start:
	ldr		pc, reset_handler	/* 0x00: Reset */
	ldr		pc, other_handler	/* 0x04: Undefined instruction */
	ldr		pc, other_handler	/* 0x08: Software interrupt */
	ldr		pc, other_handler	/* 0x0c: Prefetch abort */
	ldr		pc, other_handler	/* 0x10: Data abort */
	ldr		pc, other_handler	/* 0x14: Address exception (reserved) */
	ldr		pc, other_handler	/* 0x18: IRQ */
	ldr		pc, other_handler	/* 0x1c: FIQ */

reset_handler:
	.long	main
other_handler:
	.long	_vector_start

	.globl	_vector_end
_vector_end:
	.size	_vector_start, . - _vector_start
	.end
