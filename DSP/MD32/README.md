# MD32

This directory contains tools for reverse engineering the MD32 ISA, as well as
some [reverse engineering notes][notes] about the CPU/ISA.


## find_instructions.py

Use this tool to identify the opcodes and opcode bitmasks for each
instruction. The [Z3 theorem prover][z3] is used to help generate instructions
to feed into the disassembler.


## instruction_info.py

This tool will print a nice summary of the instructions you've found with
`find_instructions.py`.


## md32_dis.py

This is the Python module that wraps the MD32's `objdump` binary, to make it
easier to dynamically disassemble arbitrary instructions.


[notes]: Notes.md
[z3]: https://github.com/Z3Prover/z3
