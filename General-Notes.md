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


## IC names and functions

* Cellular RF Frontends (RFICs)
  * MT6169
* Connectivity RF Frontends (RFICs)
  * MT6625
  * MT6631
* Antenna Switches
  * Any Skyworks SKY77xxx-xx IC
* Power Management ICs (PMICs)
  * MT6328
  * MT6351

### Details

The cellular RF frontends have two main functions:

* Convert between the [low-IF][low-IF]/[zero-IF][direct-conversion] signals
  the SoC transmits/receives and the much higher-frequency
  [cellular RF signals][cellular-frequencies].
* Filter and amplify the transmitted and received cellular signals.

It's important to know that the cellular RF frontends only perform these
tuning, filtering, and amplification functions, plus a few smaller
functions--they don't do any ADC/DAC, so the signals shared between the SoC
and them are entirely analog.

The connectivity RF frontends are similar to the cellular RF frontends, but
handle WiFi, Bluetooth, and GNSS instead. Like with the cellular RFICs, the
amplified, filtered, and shifted RF signals for these functions are sent into
the SoC for further processing. In addition to that, the connectivity RFICs
also include a full FM radio receiver which contains a demodulator DSP.

The antenna switches take the large number of TX/RX signals from the cellular
RF frontend and multiplex them over a smaller number of antennas. This way a
phone only needs 1-3 cellular antennas instead of 10+ antennas.

The power management ICs are sort of "kitchen sink" ICs--in addition to
performing typical power management functions like DC-DC conversion, battery
charging, and battery monitoring and management ("fuel gauge"), they perform a
number of additional funcions:

* Vibration motor driver.
* LED drivers.
* Audio CODEC (ADC/DAC).
* AUXADC for accessory detection/temperature sensing.
* Real-time clock.
* Extra GPIO.

To summarize, the PMIC handles most of the higher-power analog functionality
that isn't already handled by the RFICs or the SoC itself.


## Glossary

MediaTek uses a lot of acronyms in their code and documentation but rarely
expands them, so this glossary is my attempt at fixing that. Please note that
some of these entries are complete guesses.

* AICE: Andes ICE. This is a JTAG adapter/"In-Circuit Emulator" made by Andes
  Technology.
* BROM: Boot ROM. The mask ROM baked into the silicon of the SoC that holds the
  first code executed by the CPU. As it is a ROM, it is completely immutable.
* C2CRF: "Coresonic to Cortex-R(4)F"? "Core to Core RF"? Related to access
  between the CR4 and the Coresonic core, meant for debugging.
* CCCI: Cross Core Communication Interface. This is the memory/DMA interface
  through which the AP and the BP communicate.
* CONN: "Connectivity", usually refers to the connectivity subsystem. The
  connectivity subsystem includes the WiFi CPU core and possibly the Bluetooth
  CPU as well.
* CQDMA: Command-Queue DMA. This is what MediaTek calls their DMA controller.
* DA: Download Agent. In the official MediaTek USB-based eMMC flashing flow,
  the DA is code loaded over USB by the preloader (which itself may be loaded
  over USB in BROM USB Download Mode) that interacts with the host software to
  read from/write to eMMC.
* DAA: "Download Agent Authentication"?
* DBF: DSP Binary Filter. As the name implies, this is binary filter data that
  is loaded into and parsed by the firmware running on the Coresonic DSP.
* DCM: Dynamic Clock Management.
* DEM: Debug Exchange Module/Data Exchange Module. This is a hardware block
  with registers that control reset, clocking, and I/O selection for the debug
  subsystem. For example, the JTAG enable/disable registers are part of this
  module.
* GCE: Global Command Engine. A SoC peripheral that can be used to program
  registers with strict timing requirements.
* GCPU: General Copy Protection Unit. A SoC peripheral used for decrypting
  encrypted media. It's a microcontroller core (MD32?) with some ROM, SRAM,
  and hardware accelerators for AES, SHA, MD5, RC4, DES, CRC32, DMA, etc.
* GCU: GPRS Cipher Unit. An accelerator for cryptographic ciphers used in some
  GSM protocols.
* HIF: Host Interface. This is the interface between the SoC and the
  Connectivity (WLAN/BT/GPS) core. The HIF is an abstraction layer over the
  physical interface (AHB/eHPI/PCIe/SDIO/USB).
* INFRACFG: "Infrastructure system configuration". Refers to the block of
  registers that control reset, clocking, and some miscellaneous control
  signals.
* M4U: Multimedia Memory Management Unit. This is what MediaTek calls their
  IOMMU.
* MCU: Used to refer to different processor subsystems. e.g., "APMCU" refers to
  the main AP core cluster, while "MDMCU" refers to the BP CPU. "MCUSYS" seems
  to refer to the AP MCU system.
* MFG: MFlexGraphics. Refers to the 3D GPU subsystem.
* MSDC: Used to refer to their EMMC/SD card controller core. Possibly "MediaTek
  SD Controller".
* RXDFE: "RX Digital Front End"?
* SBC: "Secure Boot Code"? Refers to secure boot functionality. When this is
  enabled, the BROM will only load and run properly signed boot code.
* SIB: System Interface Box. A custom SWD/JTAG adapter used by MediaTek? Or a
  hardware component inside the SoC's debug subsystem?
* SLA: "Software Loader Authentication"? Some challenge-response auth to
  authenticate the program loading the DA? Challenge-response auth to
  authenticate the program communicating with the BROM? When this is enabled, it
  disables Download Agent (DA) functionality in the BROM.
* SST: System Stability Tracker. This is the name of the system trace
  functionality included in the BP firmware.
* SWLA: Software LA (Logic Analyzer?). It seems to be some kind of debug
  functionality in the BP firmware.
* TRNG: Truly Random Number Generator.
* WMT: Wireless Management Task. Refers to the WiFi/Bluetooth drivers/API.


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
   * [Video](https://www.youtube.com/watch?v=9rKxfo7Gkqo),
     [Slides](https://web.archive.org/web/20171030164527/https://ecc2017.coreboot.org/uploads/talk/presentation/30/reverse-engineering-mt8173-pcm-firmwares-isa-fully-free-boot-chain.pdf)
   * Good talk on reverse engineering the ISA of a custom MediaTek microcontroller core.
 * [Black box reverse engineering for unknown/custom instruction sets](https://recon.cx/2016/recordings/recon2016-02-david-carne-Black-box-reverse-engineering-for-unknown-custom-instruction-sets.mp4)
   * "Reversing the ADF7242"
   * Good talk on how to reverse engineer ISAs in general.
 * [reverse-engineering a custom, unknown CPU from a single program](https://www.robertxiao.ca/hacking/dsctf-2019-cpu-adventure-unknown-cpu-reversing/)
   * Explains how, for a CTF competition, a custom ISA was reverse-engineered
     with only access to the executed binary and a running, remote instance of
     the code.
   * By interacting with the code, they could observe how the code behaved and
     map its functionality, which enabled them to search for those patterns of
     functionality in the binary.
 * [Reversing a Japanese Wireless SD Card - From Zero to Code Execution](https://docs.google.com/presentation/d/13OJNOb2IMwp79SDrbxSLF3i7StTgWLdD7QlYpic39r8/edit)
   * This talk includes some ISA identification techniques.
   * Has links to some interesting tools:
     * [rbasefind](https://github.com/sgayou/rbasefind): A firmware base address search tool.
     * [Miasm](https://github.com/cea-sec/miasm): Reverse engineering framework in Python.
     * [Sibyl](https://github.com/cea-sec/Sibyl): A Miasm2 based function divination.
     * [r2m2](https://github.com/guedou/r2m2): Use miasm2 as a radare2 plugin.
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
[low-IF]: https://en.wikipedia.org/wiki/Low_IF_receiver
[direct-conversion]: https://en.wikipedia.org/wiki/Direct-conversion_receiver
[cellular-frequencies]: https://en.wikipedia.org/wiki/Cellular_frequencies
