all: mediatek_lte_dsp_firmware.py

%.py: %.ksy
	kaitai-struct-compiler -t python $<
