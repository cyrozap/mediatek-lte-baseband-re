# Common SoC tools and information

## handshake

This tool performs the USB download mode handshake.

## make_image.py

This utility can be used to generate "preloader" images that can be
written to eMMC devices and SD cards.

## parse_brom_log.py

Use this to parse log messages output by the BROM. Documentation of the
message format can be found in the [BROM notes][brom-notes].

## socemu.py

This tool uses the [Unicorn Engine][unicorn] to emulate MediaTek SoCs.
It can also pass MMIO accesses to a real device over a serial interface.

## usbdl.py

This is a tool to interact with the USB download mode of MediaTek SoCs.


[brom-notes]: doc/BROM-Notes.md
[unicorn]: https://www.unicorn-engine.org/
