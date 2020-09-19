MEMORY
{
	rom (rx) : ORIGIN = 0x00100A00, LENGTH = 0x00000A00
}

ENTRY(_start)

SECTIONS
{
	.text : {
		*(.text.start)
		*(.text*)
		*(.rodata*)
		. = ALIGN(4);
	} >rom

	args = .;

	/DISCARD/ : { *(.data*) *(.bss*) *(.eh_frame) }
}
