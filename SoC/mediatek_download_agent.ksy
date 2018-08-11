meta:
  id: mediatek_download_agent
  endian: le
  title: MediaTek Download Agent
  license: CC0-1.0
seq:
  - id: header
    type: header
  - id: da_list
    type: da_list
    size: header.da_count * 220
types:
  header:
    seq:
      - id: identifier
        type: strz
        size: 32
        encoding: ASCII
      - id: name
        type: strz
        size: 64
        encoding: ASCII
      - id: unk0
        type: u4
      - id: unk1
        type: u4
      - id: da_count
        type: u4
  da_list:
    seq:
      - id: da_headers
        type: da_header
        size: 220
        repeat: eos
  da_header:
    seq:
      - id: magic
        contents: [0xDA, 0xDA]
      - id: chip_id
        type: u2
      - id: unk0
        type: u4
      - id: unk1
        type: u4
      - id: unk2
        type: u4
      - id: unk3
        type: u4
      - id: file_offset
        type: u4
      - id: unk5
        type: u4
      - id: unk6
        type: u4
      - id: unk7
        type: u4
      - id: unk8
        type: u4
      - id: unk9
        type: u4
      - id: unk10
        type: u4
      - id: unk11
        type: u4
      - id: unk12
        type: u4
      - id: unk13
        type: u4
      - id: unk14
        type: u4
      - id: unk15
        type: u4
      - id: unk16
        type: u4
      - id: unk17
        type: u4
