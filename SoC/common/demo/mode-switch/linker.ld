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
