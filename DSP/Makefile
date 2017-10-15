all: mediatek_lte_dsp_firmware.py

mediatek_lte_dsp_firmware.py: dsp_fw.ksy
	kaitai-struct-compiler -t python dsp_fw.ksy
