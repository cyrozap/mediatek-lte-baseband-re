# General Notes


## System Overview

The SoC/LTE Modem system consists of three main parts:

1. The Application Processor (AP), which is some ARM Cortex-A variant.
2. The Baseband Processor (BP/BB), which is a Cortex-R4.
3. The Baseband DSP (DSP), which is some Coresonic DSP.

This is actually a simplification, because there's a second, non-Coresonic
DSP to handle 2G/3G signal processing (a [Faraday Technology FD216][FD216]),
but I'm not interested in that. Also, it seems the BP won't be a Cortex-R4
in future devices, as [MediaTek has signed an agreement with Imagination Technologies][imgtech]
to license some MIPS CPU core for the LTE BP in the upcoming Helio X30
(MT6799) and later SoCs, but that doesn't matter now because the cheaper SoCs
aren't using them yet.

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

* AICE: Andes ICE. This is a JTAG adapter/"In-Circuit Emulator" made by Andes
  Technology.
* C2CRF: "Coresonic to Cortex-R(4)F"? "Core to Core RF"? Related to access
  between the CR4 and the Coresonic core, meant for debugging.
* CCCI: Cross Core Communication Interface. This is the memory/DMA interface
  through which the AP and the BP communicate.
* CONN: "Connectivity", usually refers to the connectivity subsystem. The
  connectivity subsystem includes the WiFi CPU core and possibly the Bluetooth
  CPU as well.
* DBF: DSP Binary Filter. As the name implies, this is binary filter data that
  is loaded into and parsed by the firmware running on the Coresonic DSP.
* DCM: Dynamic Clock Management.
* DEM: Debug Exchange Module/Data Exchange Module. This is a hardware block
  with registers that control reset, clocking, and I/O selection for the debug
  subsystem. For example, the JTAG enable/disable registers are part of this
  module.
* GCU: GPRS Cipher Unit. An accelerator for cryptographic ciphers used in some
  GSM protocols.
* INFRACFG: "Infrastructure system configuration". Refers to the block of
  registers that control reset, clocking, and some miscellaneous control
  signals.
* M4U: Multimedia Memory Management Unit. This is what MediaTek calls their
  IOMMU.
* MCU: Used to refer to different processor subsystems. e.g., "APMCU" refers to
  the main AP core cluster, while "MDMCU" refers to the BP CPU. "MCUSYS" seems
  to refer to the AP MCU system.
* MSDC: Used to refer to their EMMC/SD card controller core. Possibly "MediaTek
  SD Controller".
* RXDFE: "RX Digital Front End"?
* SST: System Stability Tracker. This is the name of the system trace
  functionality included in the BP firmware.
* SWLA: Software LA (Logic Analyzer?). It seems to be some kind of debug
  functionality in the BP firmware.
* TRNG: Truly Random Number Generator.


## History

* 2007: [MediaTek acquires Analog Devices' cellular chip operations][adi-acquisition].
* 2012: [MediaTek acquires Coresonic][acquisition], a DSP IP core company.
* 2014: [MediaTek releases their first LTE modem][mt6290], the MT6290.


## Prior Work

 * [Path of Least Resistance: Cellular Baseband to Application Processor Escalation on Mediatek Devices](https://comsecuris.com/blog/posts/path_of_least_resistance/)
   * More of an analysis of the kernel and userspace side of things and not so
     much about the modem firmware, but still very good and helpful.
   * [MTK Baseband Code Elevation Research Repo](https://github.com/Comsecuris/mtk-baseband-sanctuary)
     * [BP image decryptor](https://github.com/Comsecuris/mtk-baseband-sanctuary/blob/master/ccci_md_dump/decrypt/decrypt.c)
     * [Debug symbol loader](https://github.com/Comsecuris/mtk-baseband-sanctuary/blob/master/ida_load_syms/loadsyms.py)
 * "Reverse engineering MT8173 PCM firmwares and ISA for a fully free bootchain"
   * [Video](https://www.youtube.com/watch?v=9rKxfo7Gkqo)
   * [Slides](https://ecc2017.coreboot.org/uploads/talk/presentation/30/reverse-engineering-mt8173-pcm-firmwares-isa-fully-free-boot-chain.pdf)
 * [Black box reverse engineering for unknown/custom instruction sets](https://recon.cx/2016/recordings/recon2016-02-david-carne-Black-box-reverse-engineering-for-unknown-custom-instruction-sets.mp4)
   * "Reversing the ADF7242"
   * Good talk on how to reverse engineer ISAs in general.
 * [How to not break LTE crypto](https://www.sstic.org/media/SSTIC2016/SSTIC-actes/how_to_not_break_lte_crypto/SSTIC2016-Article-how_to_not_break_lte_crypto-michau_devine.pdf)
   * MediaTek-specific modem information is in section 3.3.
 * [Fun with the MTK 6573 Baseband (Patching / Replacing)](http://baseband-devel.722152.n3.nabble.com/Fun-with-the-MTK-6573-Baseband-Patching-Replacing-td4026683.html)
   * [Fun with the MTK 6573 Baseband (Patching / Replacing), continued](https://lists.osmocom.org/pipermail/baseband-devel/2017-April/005188.html)
   * Not much new information here, but still somewhat interesting.


[FD216]: http://www.faraday-tech.com/download/techDocument/FD216_PB_v1.5.pdf
[imgtech]: https://www.mips.com/press/mediatek-selects-mips-for-lte-modems/
[adi-acquisition]: https://www.eetimes.com/document.asp?doc_id=1248601
[acquisition]: https://www.eetimes.com/document.asp?doc_id=1261529
[mt6290]: https://www.mediatek.com/press-room/press-releases/mediatek-announces-the-availability-of-multimode-lte-modem-chipset
