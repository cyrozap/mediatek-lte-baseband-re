# BP Notes


## Firmware

* File name is `modem.img`, which can be found in `/system/etc/firmware`
  on the device filesystem.
* The firmware file is loaded by the kernel in
  `drivers/misc/mediatek/ccci_util/ccci_util_lib_load_img.c` after being
  triggered by `/system/bin/ccci_mdinit 0` (where "0" is the index of
  the modem you want to run the code on).
* Debug symbols for the modem code can be found in `/system/etc/mddb` in
  a file with a name that starts with `DbgInfo`.
  * The format of this file is described in the Kaitai Struct definition
    file [mediatek_dbginfo.ksy](mediatek_dbginfo.ksy).
