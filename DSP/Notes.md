# DSP Notes


## ISA

* 24-bit instructions
  * The code binary has a null byte after every three bytes, at a minimum.
  * It would be less complicated for every 32-bit word on the Cortex-R4
    side correspond to a 24-bit instruction word on the DSP side, since the
    DSP could use the same addressing scheme but with 8 fewer data lines.
  * Confirmed by [Bloomberg][Bloomberg].


## Firmware

* The firmware binary contains 7 firmware sections.
  * Each section has a code and data segment.
    * The max length of the code segment is 0x28000 32-bit words (0xA0000
      bytes).
    * The max length of the data segment is 0x6400 32-bit words (0x19000
      bytes).
    * Each segment has a checksum.
      * The checksum is simply the XOR of all the obfuscated 32-bit words in
        that segment.
      * Checksum verification can be disabled by setting the checksum to zero.
  * Each section contains the code and data for a single DSP core.
    * There are 7 DSP cores.
    * The cores are named as follows:
      * 1. FMC
      * 2. MC
      * 3. BC
      * 4. FNC
      * 5. MMC
      * 6. MSC
      * 7. MD32
    * MD32, the 7th core (`core_idx` 7) seems to be different from the other
      cores.
      * Its code segment cotains 32-bit instructions.
      * The code and data are loaded into a separate region of the Cortex-R4's
        address space compared to the other 6 cores.
      * It's possible that this is a [MediaDSP][MediaDSP] core used for audio
        coding.
  * Each section is loaded sequentially based on its location in the binary.
    * In other words, they're loaded in `file_idx` order, not `core_idx`
      order.


[Bloomberg]: https://www.bloomberg.com/research/stocks/private/snapshot.asp?privcapid=25110321
[MediaDSP]: https://pdfs.semanticscholar.org/bc0e/70ee308ae793bbd68592bb7346d30c591e1b.pdf
