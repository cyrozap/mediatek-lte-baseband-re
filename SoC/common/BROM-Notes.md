# BROM Notes

## Decoding the BROM log

 - `[DL] XXXXXXXX YYYYYYYY AABBCC`
   - Download mode info?
   - `XXXXXXXX`: USB DL timeout in ms. 0xffffffff if there is no
     timeout.
   - `YYYYYYYY`: The contents of register `BOOT_MISC0`, which is used as
     the USB DL mode flag register.
     - `(0x444C << 16) | ((timeout_seconds & 0x3fff) << 2) | 1`
     - The upper 16 bits are the magic ("DL"), and the lowest bit is the
       enable. Both must be set to enable flag-triggered USB DL mode.
     - The timeout is in seconds, and must be less than 16383 (0x3fff).
     - A timeout of 0x3fff means "no timeout".
   - `AA`: 0x00 if there is no DL mode timeout, 0x01 if there is a valid
     timeout.
   - `BB`: Unknown, usually 0x03 or 0x07.
   - `CC`: `SEC_GPT + 0x00` bits [3:0] when bits [3:0] are 1, 2, or 3,
     0x04 if bits [3:0] are 7, and 0xff otherwise.
 - `BP: XXXX XXXX [YYYY]`
   - Boot parameters?
   - `XXXXXXXX`: 32-bit bitfield of boot parameters.
     - 0x00000001: Unknown.
     - 0x00000002: Unknown.
     - 0x00000008: Unknown.
     - 0x00000010: Unknown.
     - 0x00000020: UART synced for DL mode.
     - 0x00000040: UART failed to sync for DL mode.
     - 0x00000080: `YYYY` is non-zero.
     - 0x00000100: Unknown.
     - 0x00000200: `SEC_GPT + 0xc0` bits [11:8] are not clear.
     - 0x04000000: Preloader on boot medium is 64-bit.
     - 0x08000000: USB DL HS (High Speed?) enabled.
     - 0x10000000: `gfh_brom_cfg_v3.reserved.reserved3` bit 0 is set.
     - 0x20000000: M_SW_RES bit 5 cleared.
     - 0x40000000: M_SW_RES bit 4 cleared.
     - 0x80000000: M_SW_RES bit 3 cleared.
   - `YYYY`: Preloader sector offset. The BROM searches for preloaders
     at 2048-byte boundaries, so this number will be the byte offset of
     the preloader divided by 2048.
 - `T0: XXXX XXXX [YYYY]`
   - Boot time?
   - `XXXXXXXX`: 32-bit BROM execution time in ms.
   - `YYYY`: Lower 16 bits of the JTAG delay in ms.
     - The JTAG delay is the amount of time the BROM will busy-wait
       before executing the main function. This gives a developer time
       to connect a JTAG dongle and halt the CPU.
