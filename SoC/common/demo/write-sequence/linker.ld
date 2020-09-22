MEMORY
{
	rom (rx) : ORIGIN = 0x00100A00, LENGTH = 0x00000A00
}

ENTRY(_start)

SECTIONS
{
	.text : {
		*(.text.start)
		. = ALIGN(4);
	} >rom

	/DISCARD/ : { *(.text*) *(.rodata*) *(.data*) *(.bss*) *(.eh_frame) }
}
