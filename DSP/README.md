# Coresonic (MediaTek) DSP code


## Quick start

Software dependencies:

* Python 3
* [Kaitai Struct Compiler][ksc]
* [Kaitai Struct Python Runtime][kspr]

To start looking at the DSP code, you'll need a DSP binary. You can find
these on a MediaTek LTE baseband-based phone in `/system/etc/firmware`, and
the file will be called something like `dsp_*.bin`. If you don't have access
to a phone with a MediaTek LTE modem, you can also find these firmware files
on the Internet, typically in the "vendor.zip" files posted by Android ROM
developers. You can also find them, for example, using
[this GitHub search query][firmware query]. Note: You must be logged in to
GitHub in order to get any results from that query.

Once you have the DSP binary, run `make` in this directory to generate the
parser code used by `extract_fw.py`. Then, simply run
`./extract_fw.py dsp_*.bin` to extract each section from the binary into
separate files.

To verify that the DSP binary has been parsed correctly, run
`strings -e l *.data.bin` and make sure that some human-readable text
strings are output. You should see some file paths, build IDs, and build
timestamps at the very least. For additional confirmation, all the code
binaries (`*.code.bin`) except for `*.core_idx_7.code.bin` should have every
fourth byte set to zero, which will be very noticeable in a hex dump.


## Notes

See [Notes.md](Notes.md).


[ksc]: https://github.com/kaitai-io/kaitai_struct_compiler
[kspr]: https://github.com/kaitai-io/kaitai_struct_python_runtime
[firmware query]: https://github.com/search?q=filename%3Adsp_1_lwg_n.bin
