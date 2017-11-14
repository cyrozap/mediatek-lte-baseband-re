# General Notes


## System Overview

The SoC/LTE Modem system consists of three main parts:

1. The Application Processor (AP), which is some ARM Cortex-A variant.
2. The Baseband Processor (BB/BP), which is a Cortex-R4.
3. The Baseband DSP (DSP), which is some Coresonic DSP.

This is actually a simplification, because there's a second, non-Coresonic
DSP to handle 2G/3G signal processing (a [Faraday Technology FD216][FD216]),
but I'm not interested in that. Also, it seems the BP won't be a Cortex-R4
in future devices, as [MediaTek has signed an agreement with Imagination Technologies][imgtech]
to license some MIPS CPU core for the LTE BP in the upcoming Helio X30
(MT6799) and later SoCs, but that doesn't matter now because that hardware
doesn't exist yet.

From what I've been able to glean from kernel sources and disassembled
binaries, the AP and the BP share some memory for loading the BP fimware, DMA,
and IPC (through virtual serial ports). They also appear to share access to
certain peripherals, like the UARTS and UICC interfaces. The BP has either
some or all of the DSP's memory space mapped, and I think the AP may be able
to access that directly (for, e.g., DSP memory dumps), but I'm not entirely
sure.


## History

* 2012: [MediaTek acquires Coresonic][acquisition], a DSP IP core company.
* 2014: [MediaTek releases their first LTE modem][mt6290], the MT6290.


[FD216]: http://www.faraday-tech.com/download/techDocument/FD216_PB_v1.5.pdf
[imgtech]: https://www.imgtec.com/news/press-release/mediatek-selects-mips-for-lte-modems/
[acquisition]: https://www.eetimes.com/document.asp?doc_id=1261529
[mt6290]: https://www.mediatek.com/press-room/press-releases/mediatek-announces-the-availability-of-multimode-lte-modem-chipset
