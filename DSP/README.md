# Coresonic (now MediaTek AB) DSP code

## Quick start

To start looking at the DSP code, you'll need a DSP binary. You can find
these on a MediaTek LTE baseband-based phone in `/system/etc/firmware`, and
the file will be called something like `dsp_*.bin`. If you don't have access
to a phone with a MediaTek LTE modem, you can also find these firmware files
on the Internet, typically in the "vendor.zip" files posted by Android ROM
developers.

Once you have the DSP binary, run `make` in this directory to generate the
parser code used by `extract_fw.py`. Then, simply run
`./extract_fw.py dsp_*.bin` to extract each section from the binary into
separate files.
