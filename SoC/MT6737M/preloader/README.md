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

If you haven't already, extract the SPFT and
"IoT\_op\_smt\_hd720\_pcb\_v2\_v00\_eng\_20181030221529.tar.gz" archives
and start SPFT. If you're using Linux, to start SPFT you'll need to run
`chmod +x flash_tool.sh` to mark that script as executable and then you
need to run `sudo ./flash_tool.sh`. If you don't want to run SPFT as
root, you need to add udev rules to give your user permission to access
serial ports.

After starting SPFT, you should already be on the "Download" tab. Click
the "choose" button next to the "Scatter-loading File" box to select the
scatter file from the archive you downloaded earlier,
`IoT_op_smt_hd720_pcb_v2/images/MT6737M_Android_scatter.txt`. After
clicking "Open", the list of partitions should populate with all the
checkboxes pre-selected. Deselect all the checkboxes except for the one
for the "preloader" partition, then click the file path in the
"Location" column for that partition to open up a file selection dialog.
From there, select your custom preloader.

Once you're ready to flash the preloader, first make sure that jumper J5
has been removed from your device and that your device is unpowered and
disconnected from your computer. Once you've confirmed this, click the
"Download" button in SPFT. After that, plug your device into your
computer via USB. If your device's preloader is functional, it should
automatically be detected by SPFT and the preloader will start to be
flashed to your device. Once you've flashed the preloader, you're done!

If your device's preloader is not functional, you'll need to enter BROM
download mode and flash from there. To do this, use a bit of wire to
short the "KCOL0" test pad (found on the underside of the board) to
ground, and keep the pin shorted while plugging in the USB cable to your
computer. If you pressed the "Download" button previously, SPFT should
now find the BROM in download mode and use that to flash the preloader
to your device.

[spft]: https://mega.nz/#F!WGwUhAZJ!xcc_4wd_UG_0OLruixz3ww!mCJG3DgT
[tool download page]: http://www.orangepi.org/downloadresources/orangepi4G-IOT/2018-03-27/466a6d3bca476eca4dbd964b163739e2.html
[windows drivers]: https://mega.nz/#F!WGwUhAZJ!xcc_4wd_UG_0OLruixz3ww!rGhSzJBL
[archive of binaries]: https://drive.google.com/file/d/1Puti7wm7OFfa24b4lErAVgkEfbw5Nx5d/view
[image download page]: http://www.orangepi.org/downloadresources/orangepi4G-IOT/2018-03-27/98c90c9ed1dc38b8e82b03c9ddb37ac7.html
