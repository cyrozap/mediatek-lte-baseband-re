# MD32 binutils

Place the `objdump` binary from the MD32's binutils in this directory.

The binary can be found in the Orange Pi 4G-IoT Android 8.1 source code
archive (22 GB, available [here][download-page]). Please note that the MD32
compiler and binutils are only available in the Android 8.1 archive, and not
any of the other ones. Once you've downloaded the first part of the archive
(`x00`, 2 GB), the binary can be extracted with the following command:

```
$ tar -xzf x00 OrangePi_4G-IOT_Android8.1/code/ccu_tool/md32ccu/ToolChain/install_md32/md32-elf/bin/objdump
```

Ignore the EOF errors in the `tar` output--this is to be expected since the
`x00` file is not a complete tar archive.

After extracting the binary, move it into this directory so the Python scripts
can find it.


[download-page]: http://www.orangepi.org/downloadresources/orangepi4G-IOT/2020-04-23/3928a702a73dfbce5554489a1f9e6edc.html
