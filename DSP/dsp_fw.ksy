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
enums:
  gfh_file_type:
    # recognized by bootrom
    0x0000: gfh_file_none
    0x0001: arm_bl
    0x0002: arm_ext_bl
    0x0003: dualmac_dsp_bl
    0x0004: sctrl_cert
    0x0005: tool_auth
    0x0006: file_mtk_reserved1
    0x0007: epp
    0x0008: file_mtk_reserved2
    0x0009: file_mtk_reserved3
    0x000a: root_cert
    0x000b: ap_bl

    # maui binary group
    0x0100: primary_maui
    0x0101: secondary_maui
    0x0102: on_demand_paging
    0x0103: third_rom
    0x0104: dsp_rom
    0x0105: cached_dsp_rom
    0x0106: primary_factory_bin
    0x0107: secondary_factory_bin
    0x0108: viva
    0x0109: lte_dsp_rom
    0x017f: v_maui_binary_end

    # resource binary group
    0x0180: custom_pack
    0x0181: language_pack
    0x0182: jump_table

    # binary not belonging to maui
    0x0200: fota_ue
    0x0201: arm_ext_bl_backup

    # secure structure group
    0x0300: secure_ro_s
    0x0301: secure_ro_me

    # external_file
    0x0400: card_download_package
    0x0401: confidential_binary

    # file system
    0x0480: file_system

    # secure structure group
    0x500: boot_cert_ctrl

    # customized_file
    0x7000: customer_bin1
    0x7001: customer_bin2
    0x7002: customer_bin3

    # slt_load_file
    0x8000: gfh_file_type_for_mt6290
  gfh_flash_dev:
    0: flash_dev_none
    1: f_nor
    2: f_nand_sequential
    3: f_nand_ttbl
    4: f_nand_fdm50
    5: f_emmc_boot_region
    6: f_emmc_data_region
    7: f_sf
    8: f_xboot
  gfh_sig_type:
    0: sig_none
    1: sig_phash
    2: sig_single
    3: sig_single_and_phash
    4: sig_multi
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
        enum: gfh_file_type
      - id: flash_dev
        type: u1
        enum: gfh_flash_dev
      - id: sig_type
        type: u1
        enum: gfh_sig_type
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
