meta:
  id: mediatek_lte_dsp_firmware
  endian: le
  title: MediaTek LTE modem DSP firmware
  license: CC0-1.0
  application: Firmware image LTE modem DSP
doc: Firmware image for the Coresonic DSP found in MediaTek LTE modems.
seq:
  - id: gfh_file_info
    type: gfh_file_info
  - id: gfh_dsp_info
    type: gfh_dsp_info
  - id: dsp_firmware
    type: dsp_firmware
    size: gfh_file_info.file_len - gfh_file_info.content_offset
types:
  gfh_header:
    seq:
      - id: magic_ver
        type: magic_ver
      - id: size
        type: u2
      - id: type
        type: u2
    types:
      magic_ver:
        seq:
          - id: magic
            contents: 'MMM'
          - id: ver
            size: 1
  gfh_file_info:
    seq:
      - id: gfh_header
        type: gfh_header
      - id: identifier
        type: str
        size: 12
        encoding: UTF-8
      - id: file_ver
        type: u4
      - id: file_type
        type: u2
      - id: flash_dev
        type: u1
      - id: sig_type
        type: u1
      - id: load_addr
        type: u4
      - id: file_len
        type: u4
      - id: max_size
        type: u4
      - id: content_offset
        type: u4
      - id: sig_len
        type: u4
      - id: jump_offset
        type: u4
      - id: attr
        type: u4
  gfh_dsp_info:
    seq:
      - id: gfh_header
        type: gfh_header
      - id: product_ver
        type: u4
      - id: image_type
        type: u4
      - id: platform_id
        type: str
        size: 16
        encoding: UTF-8
      - id: project_id
        type: str
        size: 64
        encoding: UTF-8
      - id: build_time
        type: str
        size: 64
        encoding: UTF-8
      - id: reserved
        size: 64
  dsp_firmware:
    seq:
      - id: header
        type: header
      - id: body
        size-eos: true
    types:
      header:
        seq:
          - id: header_start
            contents: 'HDR2BEGN'
          - id: unk_1
            type: u4
          - id: core_count
            type: u4
          - id: core_headers
            type: core_header
            repeat: expr
            repeat-expr: core_count
          - id: header_end
            contents: 'HDR2EEBD'
        types:
          core_header:
            seq:
              - id: core_idx
                type: u4
              - id: core_code_len
                type: u4
              - id: core_code_crc
                type: u4
              - id: core_data_len
                type: u4
              - id: core_data_crc
                type: u4
