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
certain peripherals, like the UART and UICC interfaces. The BP has either
some or all of the DSP's memory space mapped, and I think the AP may be able
to access that directly (for, e.g., DSP memory dumps), but I'm not entirely
sure.


## Glossary

MediaTek uses a lot of acronyms in their code and documentation but rarely
expands them, so this glossary is my attempt at fixing that. Please note that
some of these entries are complete guesses.

* CCCI: Cross Core Communication Interface. This is how the AP and the BB
  communicate.
* CONN: "Connectivity", usually refers to the connectivity subsystem. The
  connectivity subsystem includes the WiFi CPU core and possibly the Bluetooth
  CPU as well.
* DBF: DSP Binary Filter. As the name implies, this is binary filter data that
  is loaded into and parsed by the DSP.
* DCM: Dynamic Clock Management.
* M4U: Multimedia Memory Management Unit. This is what MediaTek calls their
  IOMMU.
* MCU: Used to refer to different processor subsystems. e.g., "APMCU" refers to
  the main AP core cluster, while "MDMCU" refers to the BB CPU. "MCUSYS" seems
  to refer to the AP MCU system.
* MSDC: Used to refer to their EMMC/SD card controller core. Possibly "MediaTek
  SD Controller".
* SST: System Stability Tracker. This is the name of the system trace
  functionality included in the BB firmware.
* SWLA: Software LA (Logic Analyzer?). It seems to be some kind of debug
  functionality in the BB firmware.


## History

* 2012: [MediaTek acquires Coresonic][acquisition], a DSP IP core company.
* 2014: [MediaTek releases their first LTE modem][mt6290], the MT6290.


[FD216]: http://www.faraday-tech.com/download/techDocument/FD216_PB_v1.5.pdf
[imgtech]: https://www.imgtec.com/news/press-release/mediatek-selects-mips-for-lte-modems/
[acquisition]: https://www.eetimes.com/document.asp?doc_id=1261529
[mt6290]: https://www.mediatek.com/press-room/press-releases/mediatek-announces-the-availability-of-multimode-lte-modem-chipset
