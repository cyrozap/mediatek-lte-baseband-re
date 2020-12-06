# MD32 CPU/ISA

* 16/32-bit big-endian instructions.
  * Instructions are stored little-endian byte order in the DSP blobs and in
    the VPU firmware binary.
  * All instructions are aligned on 2-byte boundaries.
* 16 32-bit registers.
  * `r14` appears to be used as the stack pointer.
  * `r15` appears to be used as the link register.
* Including the reset vector (zero), the vector table looks like it has at
  least 16 slots.
* Stack seems to grow upward, though that doesn't appear to be hard-coded.
* Separate program and data memory address spaces.
