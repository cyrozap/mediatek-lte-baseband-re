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
   - `CC`: `SEJ + 0x00` (`SEJ_CON`) bits [3:0] when bits [3:0] are 1, 2,
     or 3, 0x04 if bits [3:0] are 7, and 0xff otherwise.
 - `BP: XXXX XXXX [YYYY]`
   - Boot parameters?
   - `XXXXXXXX`: 32-bit bitfield of boot parameters.
     - `0x00000001`: Preloader found on boot medium.
     - `0x00000002`: USB synced for DL mode.
     - `0x00000008`: JTAG is disabled.
     - `0x00000010`: USB failed to sync for DL mode.
     - `0x00000020`: UART synced for DL mode.
     - `0x00000040`: UART failed to sync for DL mode.
     - `0x00000080`: `YYYY` is non-zero.
     - `0x00000100`: Unknown.
     - `0x00000200`: `SEJ + 0xc0` (`SEJ_CON1`) bits [11:8] are not
       clear.
     - `0x04000000`: Preloader on boot medium is 64-bit.
     - `0x08000000`: USB DL HS (High Speed?) enabled.
     - `0x10000000`: `gfh_brom_cfg.gfh_brom_cfg_v3.reserved3` bit 0 and
       `gfh_brom_cfg.gfh_brom_cfg_v3.flags.reserved1` are set, or
       `M_SW_RES` bit 6 is set.
     - `0x20000000`: `M_SW_RES` bit 5 set.
     - `0x40000000`: `M_SW_RES` bit 4 set.
     - `0x80000000`: `M_SW_RES` bit 3 set.
   - `YYYY`: Preloader offset. The BROM searches for preloaders on
     2048-byte boundaries, so this number will be the byte offset of
     the preloader divided by 2048.
 - `Fn: XXXX YYYY`
   - Failure information?
   - `n`: Boot mode ID.
     - 0: RAM (literally loading a GFH FILE_INFO image from RAM, as if
       it were a disk)
     - 3: MSDC0 (eMMC)
     - 5: MSDC1 (SD)
   - `XXXX`: Most recent status code.
   - `YYYY`: Previous status code.
 - `G0: XXXX YYZZ`
   - `XXXX`: Bits [15:0] of `gfh_brom_cfg.gfh_brom_cfg_v3.flags`.
   - `YY`: `gfh_brom_cfg.gfh_brom_cfg_v3.usbdl_bulk_com_support`.
   - `ZZ`: `gfh_brom_cfg.gfh_brom_cfg_v3.reserved1`.
 - `nn: XXXX YYYY`
   - `nn`: An integer that starts at zero and auto-increments after
     every `nn` line printed. e.g., `00`, `01`, `02`, etc.
   - `XXXX`: Status code.
   - `YYYY`: Extra context-specific data.
 - `T0: XXXX XXXX [YYYY]`
   - Boot time?
   - `XXXXXXXX`: 32-bit BROM execution time in ms.
   - `YYYY`: Lower 16 bits of the JTAG delay in ms.
     - The JTAG delay is the amount of time the BROM will busy-wait
       before executing the main function. This gives a developer time
       to connect a JTAG dongle and halt the CPU.
 - `Vn: XXXX YYYY [ZZZZ]`
   - `n`: Bootloader descriptor index (0-7).
   - `XXXX`: Most recent status code (`code_1`).
   - `YYYY`: Previous status code (`code_2`).
   - `ZZZZ`: Bootloader descriptor `bl_type`.


## Hashes and sizes of various SoC BROMs

 - MT6735
   - Size: 65536 bytes
   - MD5: `4111199bba0afe2437d1082c1dcc4bb2`
   - SHA1: `fadb35104a805974d1e8514b2c78d083e8aa8a32`
   - SHA256: `72ccdd7dece9cf295f76cae3c7a98a2815835e9b8c2b769a6813ef1d84c38f9d`
   - SHA512: `3da06abbf9eafa83a79f4b9502e02c7983db349d293bd6c9655e056c7c5660c6cae2537bcd9a016adfec5db06fc27b412dda426b5a65af9592b69f1e830e4589`
 - MT6737M
   - Size: 65536 bytes
   - MD5: `e258ecea1ec865500c750b309cf1859a`
   - SHA1: `169d7983a8f709bb6b32398c200b969026da6fb8`
   - SHA256: `179dc0aa7c65fb85cb1e9e9c95ea2c9424eecc6b9267a343c7c9511cd546267a`
   - SHA512: `fdba3cf632adc23bebde115c765db1a0969c1c377a93f736a0e02f17d9c4ccd62f1d9081f26f1a0386b42da24806a8c63d5656f3a60c1461a55c938e6fa24dde`
 - MT6771/MT8183
   - Size: 98304 bytes
   - MD5: `88f78c13206b84fe6063966b775aba5f`
   - SHA1: `cbcf5f2cb4bc9e71bbe8cee41cccea2d51b947d7`
   - SHA256: `0b84ebc200233fdfd4284407be63cce4ccbd1c3ceb3ad939e167c523da688ac2`
   - SHA512: `462672ccb63f4f1e633846380c6506257fe8266926ea881a9671092f8841b1ec92ff3ad0a66e9379f1cc02aeb79ab3fdad6961249aa5d504633dc689e830906d`
 - MT6797
   - Size: 81920 bytes
   - MD5: `9c0b56cbfbd3d1a2e0b278e120123b87`
   - SHA1: `80f64a862b63bccd2ea0a8a15a3f3c5404ff1971`
   - SHA256: `8192a6b554dea105e8f731771e7955b21709f97febdbbf593ccd4f57f5db9bf1`
   - SHA512: `64f1ff741f862ca4b02c3896ad8ac8c5f287e4e2b5d3a59d24e81897c1045182caef0c4c32ceea4b7cf5305a7d80aaca38aabb84ded4df9803d1f90ca9131233`
 - MT8163
   - Size: 81920 bytes
   - MD5: `9ad089946a4b117a036a6165a22d846a`
   - SHA1: `7543c1f93e1525bcaa14c1acffef9ac9deb7cb31`
   - SHA256: `0969b97512db38fde33e89e9e1fdfbc5508624015c74390d69719ef9d457ef8f`
   - SHA512: `744e498414ce6339ab33b594726200cf7f683f0162fea1c8d92bd3c418c140c48fdc0a90525d59fb6abee3160fc652eff9840617b5eb172576b20fbffb79a2c1`
