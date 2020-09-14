MEMORY
{
	rom (rx) : ORIGIN = 0x00201000, LENGTH = 0x00030000
	ram (rw) : ORIGIN = 0x00231000, LENGTH = 0x0000f000
}

ENTRY(_start)

_stack_base = ORIGIN(ram) + LENGTH(ram) - 16;

SECTIONS
{
	.text : {
		*(.init)
		*(.text*)
		. = ALIGN(16);
		*(.rodata*)
		. = ALIGN(16);
	} >rom

	.data : {
		_data_start = .;
		*(.data*)
		. = ALIGN(16);
		_data_end = .;
	} >ram AT >rom
	_data_loadaddr = LOADADDR(.data);

	.bss : {
		*(.bss*)
		. = ALIGN(16);
		_bss_end = .;
	} >ram

	/DISCARD/ : { *(.eh_frame) }

	. = ALIGN(16);
	end = .;
}
