meta:
  id: mediatek_preloader
  endian: le
  title: MediaTek Preloader with optional BROM Header for EMMC
  license: CC0-1.0
seq:
  - id: bootrom_header
    type: bootrom_header
    size: 512 * 4
    if: magic == "EMM" or magic == "SDM"
  - id: file_info
    type: gfh_file_info
  - id: bl_info
    type: gfh_bl_info
  - id: brom_cfg_v3
    type: gfh_brom_cfg_v3
  - id: bl_sec_key
    type: gfh_bl_sec_key_v1
  - id: anti_clone
    type: gfh_anti_clone_v1
  - id: brom_sec_cfg
    type: gfh_brom_sec_cfg_v1
  - id: preloader
    type: preloader
    size: file_info.file_len - file_info.content_offset - file_info.sig_len
  - id: signature
    size: file_info.sig_len
    type:
      switch-on: file_info.sig_type
      cases:
        gfh_sig_type::sig_phash: signature_phash
        gfh_sig_type::sig_single: signature_single
        gfh_sig_type::sig_single_and_phash: signature_single_and_phash
instances:
  magic:
    pos: 0
    type: str
    size: 3
    encoding: ASCII
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
  bootrom_header:
    seq:
      - id: device_header
        type: device_header
        size: 512
      - id: bootrom_layout
        type: bootrom_layout
        size: 512
  device_header:
    seq:
      - id: identifier
        type: strz
        size: 12
        encoding: ASCII
        doc: Should be "EMMC_BOOT" or "SDMMC_BOOT".
      - id: version
        type: u4
      - id: dev_rw_unit
        type: u4
        doc: Device block size in bytes.
  bootrom_layout:
    seq:
      - id: identifier
        type: strz
        size: 8
        encoding: ASCII
        doc: Should be "BRLYT".
      - id: version
        type: u4
      - id: boot_region_addr
        type: u4
      - id: main_region_addr
        type: u4
      - id: bootloader_descriptors
        type: bootloader_descriptor
        size: 20
        repeat: expr
        repeat-expr: 8
  bootloader_descriptor:
    seq:
      - id: bl_exist_magic
        type: str
        size: 4
        encoding: ASCII
        doc: If the entry exists, this field should be "BBBB".
      - id: bl_dev
        type: u2
        enum: gfh_flash_dev
      - id: bl_type
        type: u2
        enum: gfh_file_type
      - id: bl_begin_addr
        type: u4
      - id: bl_boundary_addr
        type: u4
      - id: bl_attribute
        type: u4
  gfh_header:
    seq:
      - id: magic_ver
        type: magic_ver
      - id: size
        type: u2
      - id: type
        type: u2
        enum: gfh_type
    types:
      magic_ver:
        seq:
          - id: magic
            contents: 'MMM'
          - id: ver
            type: u1
  gfh_file_info:
    seq:
      - id: gfh_header
        type: gfh_header
      - id: identifier
        type: strz
        size: 12
        encoding: ASCII
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
        type: attr
        size: 4
    types:
      attr:
        doc: "Flag bits in the following order: [7:0], [15:8], [23:16], [31:24]"
        seq:
          - id: reserved0
            type: b5
          - id: file_info_attr_slt
            type: b1
          - id: file_info_attr_xip
            type: b1
          - id: file_info_attr_post_build_done
            type: b1
          - id: reserved1
            type: b23
          - id: file_info_attr_dual_image
            type: b1
  gfh_bl_info:
    seq:
      - id: gfh_header
        type: gfh_header
      - id: bl_attr
        type: bl_attr
        size: gfh_header.size-8
    types:
      bl_attr:
        doc: "Flag bits in the following order: [7:0]"
        seq:
          - id: reserved
            type: b7
          - id: bl_attr_load_by_bootrom
            type: b1
  gfh_brom_cfg_v3:
    seq:
      - id: gfh_header
        type: gfh_header
      - id: reserved
        type: reserved
        size: gfh_header.size-8
    types:
      reserved:
        seq:
          - id: flags
            type: flags
            size: 4
          - id: usbdl_by_auto_detect_timeout_ms
            type: u4
          - id: usbdl_abnormal_timeout_string
            type: strz
            size: 0x40
            encoding: ASCII
          - id: reserved0
            size: 1
          - id: usbdl_bulk_com_support
            type: u1
          - id: reserved1
            size: 1
          - id: brom_cmd_via_uart1_disable_magic
            type: u1
            doc: Magic is "R" (0x52)
          - id: m_brom_cmd_via_usb_disable_magic
            type: u1
            doc: Magic is "U" (0x55)
          - id: boot_aarch64_magic
            type: u1
            doc: Magic is 0x64. Requires "flags.boot_aarch64" to be set.
          - id: usbdl_hs_en
            type: u1
          - id: reserved3
            size: 1
          - id: usbdl_by_kcol0_timeout_ms
            type: u4
            doc: Values below 3000 ms will be rounded up to 3000 ms.
          - id: usbdl_by_flag_timeout_ms
            type: u4
            doc: Values below 3000 ms will be rounded up to 3000 ms.
          - id: usbdl_vid
            type: u2
          - id: usbdl_pid
            type: u2
        types:
          flags:
            doc: "Flag bits in the following order: [7:0], [15:8], [23:16], [31:24]"
            seq:
              - id: usbdl_by_kcol0_timeout_en
                type: b1
              - id: usbdl_vidpid_cust_en
                type: b1
              - id: usbdl_bulk_com_support
                type: b1
              - id: usbdl_auto_detect_dis
                type: b1
              - id: usbdl_abnormal_timeout_log_cust
                type: b1
              - id: usbdl_abnormal_timeout_log_dis
                type: b1
              - id: usbdl_by_auto_detect_timeout_en
                type: b1
              - id: uart1_log_dis
                type: b1
              - id: reserved0
                type: b3
              - id: boot_aarch64
                type: b1
              - id: reserved1
                type: b1
              - id: usbdl_speed_config
                type: b1
              - id: reserved2
                type: b1
              - id: usbdl_by_flag_timeout_en
                type: b1
  gfh_bl_sec_key_v1:
    seq:
      - id: gfh_header
        type: gfh_header
      - id: pubkey_type
        type: u4
      - id: rsa_n_words
        type: u4
        doc: Number of 16-bit words in the RSA modulus.
      - id: unk2
        type: u2
      - id: rsa_n_words_minus_1
        type: u2
        doc: rsa_n_words - 1
      - id: rsa_e
        type: u4
        doc: RSA exponent.
      - id: rsa_n_padding
        size: gfh_header.size - 8 - 16 - 2 * rsa_n_words
        doc: Padding, derived from scrambling the RSA modulus.
      - id: rsa_n
        size: 2 * rsa_n_words
        doc: RSA modulus, stored as little-endian 16-bit words, in big-endian word order.
  gfh_anti_clone_v1:
    seq:
      - id: gfh_header
        type: gfh_header
      - id: ac_b2k
        type: u2
      - id: ac_b2c
        type: u2
      - id: ac_offset
        type: u4
      - id: ac_len
        type: u4
  gfh_brom_sec_cfg_v1:
    seq:
      - id: gfh_header
        type: gfh_header
      - id: reserved
        type: reserved
        size: gfh_header.size-8
    types:
      reserved:
        seq:
          - id: flags
            type: flags
            size: 4
          - id: customer_name
            type: strz
            size: 0x20
            encoding: ASCII
          - id: brom_magic_cmd_mode_permanent_dis
            type: u4
            doc: Magic is 0xc975e033.
      flags:
        doc: "Flag bits in the following order: [7:0]"
        seq:
          - id: reserved
            type: b6
          - id: debug_en
            type: b1
          - id: jtag_en
            type: b1
  preloader:
    seq:
      - id: code
        size-eos: true
    instances:
      and_rominfo_v:
        pos: 0x1fc
        type: and_rominfo_v
    types:
      and_rominfo_v:
        seq:
          - id: id
            type: strz
            size: 16
            encoding: ASCII
          - id: rom_info_ver
            type: u4
          - id: platform_id
            type: strz
            size: 16
            encoding: UTF-8
          - id: project_id
            type: strz
            size: 16
            encoding: UTF-8
          - id: sec_ro_exist
            type: u4
          - id: sec_ro_offset
            type: u4
          - id: sec_ro_length
            type: u4
          - id: ac_offset
            type: u4
          - id: ac_length
            type: u4
          - id: sec_cfg_offset
            type: u4
          - id: sec_cfg_length
            type: u4
          - id: reserve1
            size: 128
          - id: sec_ctrl
            type: and_secctrl_v
          - id: reserve2
            size: 18
          - id: sec_boot_check_part
            type: and_secboot_check_part_v
          - id: sec_key
            type: and_seckey_v
      and_secctrl_v:
        seq:
          - id: id
            type: strz
            size: 16
            encoding: ASCII
          - id: sec_cfg_ver
            type: u4
          - id: sec_usb_dl
            type: u4
            enum: status
          - id: sec_boot
            type: u4
            enum: status
          - id: sec_modem_auth
            type: u4
          - id: sec_sds_en
            type: u4
          - id: seccfg_ac_en
            type: u1
          - id: sec_aes_legacy
            type: u1
          - id: secro_ac_en
            type: u1
          - id: sml_aes_key_ac_en
            type: u1
          - id: reserve
            type: u4
            repeat: expr
            repeat-expr: 3
        enums:
          status:
            0x00: disable
            0x11: enable
            0x22: only_enable_on_schip
      and_secboot_check_part_v:
        seq:
          - id: name
            type: strz
            size: 10
            encoding: ASCII
            repeat: expr
            repeat-expr: 9
      and_seckey_v:
        seq:
          - id: id
            type: strz
            size: 16
            encoding: ASCII
          - id: sec_key_ver
            type: u4
          - id: img_auth_rsa_n
            size: 256
          - id: img_auth_rsa_e
            type: str
            size: 5
            encoding: ASCII
          - id: sml_aes_key
            size: 32
          - id: crypto_seed
            type: str
            size: 16
            encoding: ASCII
          - id: sml_auth_rsa_n
            size: 256
          - id: sml_auth_rsa_e
            type: str
            size: 5
            encoding: ASCII
  signature_phash:
    seq:
      - id: hash
        size: 0x20
  signature_single:
    seq:
      - id: signature
        size: 0x100
  signature_single_and_phash:
    seq:
      - id: version
        type: u4
        doc: Must be 1.
      - id: hash
        size: 0x20
      - id: signature
        size: 0x100
