# MD32

This directory contains tools for reverse engineering the MD32 ISA, as well as
some [reverse engineering notes][notes] about the CPU/ISA.


## find_instructions.py

Use this tool to identify the opcodes and opcode bitmasks for each
instruction. The [Z3 theorem prover][z3] is used to help generate instructions
to feed into the disassembler.


## find_16bit_instructions.py

This tool will search through the 16-bit instruction space of the MD32 to find
and define decoding rules for each instruction. Like `find_instructions.py`,
this script also uses [Z3][z3], but instead of using it to generate
instructions, it uses Z3 to prove the correctness of the generated
instruction-decoding rules.


## instruction_info.py

This tool will print a nice summary of the instructions you've found with
`find_instructions.py`.


## md32_dis.py

This is the Python module that wraps the MD32's `objdump` binary, to make it
easier to dynamically disassemble arbitrary instructions.


## swap_endian.py

Use this to swap the endianness of an MD32 binary. The VPU firmware binaries
distributed in linux-firmware and the binaries extrated from the DSP binary
file are all in little-endian form, but the MD32 parses instructions in
big-endian byte order, so you need to run `swap_endian.py` on these files
before disassembly in order to correct for this.


[notes]: Notes.md
[z3]: https://github.com/Z3Prover/z3
