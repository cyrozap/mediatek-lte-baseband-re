# MT6735 Notes

Just some random notes for the MT6735 SoC.

- CoreSight JTAG-AP: Only the 0th and 1st scan chains are connected.

- AP memory (Functional Spec page 109):
  - 0x00000000-0x0000ffff: 64 kB boot ROM
  - 0x00100000-0x0010ffff: 64 kB SRAM
  - 0x00200000-0x0023ffff: 256 kB L2 share SRAM
  - Boot ROM and SRAM access from Linux are disabled during Preloader
    execution.

- AP<-\>BP memory mappings:
  - 0x10000000 (AP) <-> 0xA0000000 (BP): `infracfg_ao_reg` base address
    - This enables the BP core to access clock controls, GPIOs and other
      peripherals directly.
