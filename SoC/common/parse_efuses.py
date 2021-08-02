#!/usr/bin/env python3

import argparse
import struct


SOCS = {
    "MT6737M": {
        'efusec_base': 0x10206000,
        'efuses': (
            # name, offset, size
            ("EFUSEC_CON", 0x000, 4),
            ("EFUSEC_PGMT", 0x004, 4),
            ("EFUSEC_BPKEY", 0x008, 4),
            ("CTRL", 0x020, 4),
            ("LOCK", 0x028, 4),
            ("USB_PID", 0x030, 4),
            ("USB_VID", 0x038, 4),
            ("SPARE0", 0x040, 4),
            ("SPARE1", 0x044, 4),
            ("SPARE2", 0x048, 4),
            ("SPARE3", 0x04C, 4),
            ("SPARE4", 0x050, 4),
            ("SEC_CTRL", 0x060, 4),
            ("SEC_LOCK", 0x068, 4),
            ("AC_KEY", 0x070, 16),
            ("SBC_PUBK_HASH", 0x090, 32),
            ("M_HW_RES0", 0x100, 4),
            ("M_HW_RES1", 0x104, 4),
            ("M_HW_RES2", 0x108, 4),
            ("M_SW_RES", 0x120, 4),
            ("M_LOCK", 0x128, 4),
            ("M_SEC_CTRL", 0x130, 4),
            ("M_SEC_LOCK", 0x138, 4),
            ("HUID", 0x140, 8),
            ("HUK", 0x160, 16),
            ("M_HW_RES3", 0x170, 4),
            ("M_HW_RES4", 0x174, 4),
            ("M_HW_RES5", 0x178, 4),
            ("M_HW_RES6", 0x17C, 4),
            ("M_HW_RES7", 0x180, 4),
            ("M_HW_RES8", 0x184, 4),
            ("M_HW_RES9", 0x188, 4),
            ("M_SRM_RP0", 0x190, 4),
            ("M_SRM_RP1", 0x194, 4),
            ("M_SRM_RP2", 0x198, 4),
            ("M_SRM_RP3", 0x19C, 4),
            ("M_SRM_RP4", 0x1A0, 4),
            ("ECC_DATA1", 0x380, 4),
            ("ECC_DATA2", 0x384, 4),
            ("MULTI_BIT_ECC_DATA_WRITE", 0x400, 4),
            ("DBG_MODE", 0x404, 4),
            ("LAST_BLOW_DATA", 0x408, 4),
            ("EFUSE_MR_KEY", 0x40C, 4),
        ),
        'efuse_bits': (
            # offset, name, lsb, width
            (0x28, 'usb_id_lock', 1, 1),
            (0x28, 'com_ctrl_lock', 2, 1),
            (0x44, '3g_disable', 0, 1),
            (0x60, 'hw_jtag_disabled', 0, 1),
            (0x60, 'sbc_enabled', 1, 1),
            (0x60, 'daa_enabled', 2, 1),
            (0x60, 'sla_enabled', 3, 1),
            (0x60, 'sw_jtag_enabled', 6, 1),
            (0x60, 'root_cert_enabled', 7, 1),
            (0x60, 'jtag_brom_lock_disabled', 9, 1),
            (0x68, 'sbc_pubk_hash_lock', 0, 1),
            (0x68, 'ackey_lock', 1, 1),
            (0x68, 'sec_attr_lock', 2, 1),
        ),
    },
    "MT8163": {
        'efusec_base': 0x10206000,
        'efuses': (
            # name, offset, size
            ("EFUSEC_CON", 0x000, 4),
            ("EFUSEC_PGMT", 0x004, 4),
            ("EFUSEC_BPKEY", 0x008, 4),
            ("CTRL", 0x020, 4),
            ("LOCK", 0x028, 4),
            ("USB_PID", 0x030, 4),
            ("USB_VID", 0x038, 4),
            ("SPARE0", 0x040, 4),
            ("SPARE1", 0x044, 4),
            ("SPARE2", 0x048, 4),
            ("SPARE3", 0x04C, 4),
            ("SPARE4", 0x050, 4),
            ("SEC_CTRL", 0x060, 4),
            ("SEC_LOCK", 0x068, 4),
            ("AC_KEY", 0x070, 16),
            ("SBC_PUBK_HASH", 0x090, 32),
            ("M_HW_RES0", 0x100, 4),
            ("M_HW_RES1", 0x104, 4),
            ("M_HW_RES2", 0x108, 4),
            ("M_SW_RES", 0x120, 4),
            ("M_LOCK", 0x128, 4),
            ("M_SEC_CTRL", 0x130, 4),
            ("M_SEC_LOCK", 0x138, 4),
            ("HUID", 0x140, 8),
            ("HUK", 0x160, 16),
            ("M_HW_RES3", 0x170, 4),
            ("M_HW_RES4", 0x174, 4),
            ("M_HW_RES5", 0x178, 4),
            ("M_HW_RES6", 0x17C, 4),
            ("M_HW_RES7", 0x180, 4),
            ("M_HW_RES8", 0x184, 4),
            ("M_HW_RES9", 0x188, 4),
            ("M_SRM_RP0", 0x190, 4),
            ("M_SRM_RP1", 0x194, 4),
            ("M_SRM_RP2", 0x198, 4),
            ("M_SRM_RP3", 0x19C, 4),
            ("M_SRM_RP4", 0x1A0, 4),
            ("ECC_DATA1", 0x380, 4),
            ("ECC_DATA2", 0x384, 4),
            ("MULTI_BIT_ECC_DATA_WRITE", 0x400, 4),
            ("DBG_MODE", 0x404, 4),
            ("LAST_BLOW_DATA", 0x408, 4),
            ("EFUSE_MR_KEY", 0x40C, 4),
        ),
        'efuse_bits': (
            # offset, name, lsb, width
            (0x44, '3g_disable', 0, 1),
            (0x60, 'sbc_enabled', 1, 1),
            (0x60, 'daa_enabled', 2, 1),
            (0x60, 'sla_enabled', 3, 1),
        ),
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('efuse_dump', type=str, help="The EFUSE dump you want to parse.")
    parser.add_argument('-S', '--soc', type=str, choices=SOCS.keys(), default="MT6737M", help="The SoC the EFUSE dump corresponds to. Default: MT6737M")
    args = parser.parse_args()

    soc = SOCS[args.soc]
    base = soc['efusec_base']

    dump = open(args.efuse_dump, 'rb').read()

    for (name, offset, size) in soc['efuses']:
        addr = base + offset
        if size == 2:
            print("0x{:08x} ({}): 0x{:04x}".format(addr, name, struct.unpack_from('<H', dump, offset)[0]))
        elif size == 4:
            print("0x{:08x} ({}): 0x{:08x}".format(addr, name, struct.unpack_from('<I', dump, offset)[0]))
        else:
            print("0x{:08x} ({}): {}".format(addr, name, dump[offset:offset+size].hex()))

        for (bits_offset, bits_name, lsb, width) in soc.get('efuse_bits', []):
            if bits_offset == offset:
                assert width > 0
                value = (struct.unpack_from('<I', dump, offset)[0] >> lsb) & ((1 << width) - 1)
                print("  [{}]: {}: {}".format(lsb, bits_name, value))


if __name__ == "__main__":
    main()
