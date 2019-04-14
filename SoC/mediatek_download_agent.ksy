meta:
  id: mediatek_download_agent
  endian: le
  title: MediaTek Download Agent Archive
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
      - id: da_description
        type: strz
        size: 32
        encoding: ASCII
      - id: da_identifier
        type: strz
        size: 64
        encoding: ASCII
      - id: info_ver
        type: u4
      - id: info_magic
        type: u4
      - id: da_count
        type: u4
  da_list:
    seq:
      - id: da_entries
        type: da_entry
        size: 220
        repeat: eos
  da_entry:
    seq:
      - id: magic
        contents: [0xDA, 0xDA]
      - id: bbchip_hw_code
        type: u2
      - id: bbchip_hw_sub_code
        type: u2
      - id: bbchip_hw_version
        type: u2
      - id: bbchip_sw_version
        type: u4
      - id: unk2
        type: u4
      - id: unk3
        type: u1
      - id: unk4
        type: u1
      - id: load_region_count
        type: u2
      - id: regions
        type: da_region
        repeat: expr
        repeat-expr: load_region_count
  da_region:
    seq:
      - id: buf_offset
        type: u4
      - id: len
        type: u4
      - id: start_addr
        type: u4
      - id: sig_offset
        type: u4
      - id: sig_len
        type: u4
    instances:
      buf:
        io: _root._io
        pos: buf
        size: len
      sig:
        io: _root._io
        pos: sig_offset
        size: sig_len
