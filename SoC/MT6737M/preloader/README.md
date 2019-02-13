# preloader

## Build instructions

**NOTE**: These instructions have only been tested with the
`OrangePi_4G-IoT_Android6.0_V1.0` release.

Apply patches to the Orange Pi 4G-IoT SDK/source release. Then, cd to
the `code/vendor/mediatek/proprietary/bootable/bootloader/preloader`
directory and run the following command:

```bash
TARGET_PRODUCT=bd6737m_35g_b_m0 ./build.sh
```

The finished preloader should then be available at
`code/out/target/product/bd6737m_35g_b_m0/obj/PRELOADER_OBJ/bin/preloader_bd6737m_35g_b_m0.bin`
and can be flashed by either dd-ing it to the preloader partition using
a shell on the device (adb or otherwise) or by using SPFT to flash the
partition while the device is in download mode. See
[Flashing the preloader](#flashing-the-preloader) for more information.

## Flashing the preloader

First, download the [SP Flash Tool (SPFT)][spft] (from the
[OrangePi 4G-IOT "Toolschain" download page][tool download page]) for
your operating system. This is the tool that interacts with the
"download mode" of the MediaTek BROM and preloader and can be used to
read and write to the eMMC in that mode.

If you're doing this on Windows, you'll probably need to install the
[drivers][windows drivers] as well. Linux users don't need to install
any drivers since the BROM and preloader download modes appear as a
standard USB CDC-ACM serial port using the built-in `cdc_acm` driver.

Next, download
[IoT\_op\_smt\_hd720\_pcb\_v2\_v00\_eng\_20181030221529.tar.gz][archive of binaries]
(from the
[OrangePi 4G-IOT Android 6.0 download page][image download page]). This
archive contains the SPFT scatter file for this device. It also contains
the original preloader for the device, which you'll need in case the
preloader gets erased from the device or your custom preloader fails to
boot.

TODO

[spft]: https://mega.nz/#F!WGwUhAZJ!xcc_4wd_UG_0OLruixz3ww!mCJG3DgT
[tool download page]: http://www.orangepi.org/downloadresources/orangepi4G-IOT/2018-03-27/466a6d3bca476eca4dbd964b163739e2.html
[windows drivers]: https://mega.nz/#F!WGwUhAZJ!xcc_4wd_UG_0OLruixz3ww!rGhSzJBL
[archive of binaries]: https://drive.google.com/file/d/1Puti7wm7OFfa24b4lErAVgkEfbw5Nx5d/view
[image download page]: http://www.orangepi.org/downloadresources/orangepi4G-IOT/2018-03-27/98c90c9ed1dc38b8e82b03c9ddb37ac7.html
