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
        enum: gfh_type
    enums:
      gfh_type:
        0x0000: gfh_file_info
        0x0001: gfh_bl_info
        0x0002: gfh_anti_clone
        0x0003: gfh_bl_sec_key
        0x0004: gfh_sctrl_cert
        0x0005: gfh_tool_auth
        0x0006: gfh_mtk_reserved1
        0x0007: gfh_brom_cfg
        0x0008: gfh_brom_sec_cfg
        0x0009: gfh_mtk_reserved2
        0x000a: gfh_mtk_reserved3
        0x000b: gfh_root_cert
        0x000c: gfh_exp_chk
        0x000d: gfh_epp_param
        0x000e: gfh_chip_ver
        0x000f: gfh_mtk_reserved4
        0x0010: gfh_md_sec_cfg
        0x0100: gfh_epp_info
        0x0101: gfh_emi_list
        0x0102: gfh_cmem_id_info
        0x0103: gfh_cmem_nor_info
        0x0104: gfh_dsp_info
        0x0200: gfh_maui_info
        0x0201: gfh_maui_sec
        0x0202: gfh_maui_code_key         # maui_sec_key for code part
        0x0203: gfh_maui_secure_ro_key    # maui_sec_key for secure ro part
        0x0204: gfh_maui_resource_key     # maui_sec_key for resource part
        0x0205: gfh_secure_ro_info
        0x0206: gfh_dl_package_info
        0x0207: gfh_flash_info
        0x0208: gfh_macr_info
        0x0209: gfh_arm_bl_info
        0x020a: gfh_emmc_booting_info
        0x020b: gfh_fota_info
        0x020c: gfh_cbr_record_info
        0x020d: gfh_confidential_bin_info
        0x020e: gfh_cbr_info
        0x020f: gfh_mba_info
        0x0210: gfh_binary_location
        0x0300: gfh_boot_cert_ctrl_content
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
              - id: core_code_checksum
                type: u4
              - id: core_data_len
                type: u4
              - id: core_data_checksum
                type: u4
