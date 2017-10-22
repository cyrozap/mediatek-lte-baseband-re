# DSP Notes

## ISA

* 24-bit instructions
  * The code binary has a null byte after every three bytes, at a minimum.
  * It would be less complicated for every 32-bit dword on the Cortex-R4
    side correspond to a 24-bit instruction word on the DSP side, since the
    DSP could use the same addressing scheme but with 8 fewer data lines.
  * Confirmed by [Bloomberg][Bloomberg].


[Bloomberg]: https://www.bloomberg.com/research/stocks/private/snapshot.asp?privcapid=25110321
