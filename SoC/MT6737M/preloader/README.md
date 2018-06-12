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

The finished preloader should be available at
`code/out/target/product/bd6737m_35g_b_m0/obj/PRELOADER_OBJ/bin/preloader_bd6737m_35g_b_m0.bin`
and can be flashed by either dd-ing it to the preloader partition using
a shell on the device (adb or otherwise) or by using SPFT to flash the
partition while the device is in download mode.

## Flashing the preloader

### Flashing via SP Flash Tool (SPFT)

### Flashing via dd (untested)

On the host PC, run the following command:

```bash
adb push code/out/target/product/bd6737m_35g_b_m0/obj/PRELOADER_OBJ/bin/preloader_bd6737m_35g_b_m0.bin /data/local/tmp/
```

Then, still on the host PC, run the following command:

```bash
adb shell dd if=/data/local/tmp/preloader_bd6737m_35g_b_m0.bin of=/dev/block/mmcblk0boot0 bs=2048 seek=1
```
