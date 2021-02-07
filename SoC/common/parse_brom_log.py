#!/usr/bin/env python3

import fileinput
import re
import struct


DL_REGEX = r"\[DL\] (?P<x>[0-9A-F]{8}) (?P<y>[0-9A-F]{8}) (?P<a>[0-9A-F]{2})(?P<b>[0-9A-F]{2})(?P<c>[0-9A-F]{2})"
MSG_REGEX = r"(?P<type>[0-9A-Z]{2}): (?P<x>[0-9A-F]{4}) (?P<y>[0-9A-F]{4})( \[(?P<z>[0-9A-F]{4})\])?"


def get_orig(match):
    span = match.span()
    orig = match.string[span[0]:span[1]]
    return orig

def parse_dl(groups):
    usbdl_timeout_ms = int(groups['x'], 16)
    usbdl_mode = int(groups['y'], 16)
    flag = usbdl_mode >> 16
    timeout_s = (usbdl_mode >> 2) & 0x3fff
    enable = usbdl_mode & 1
    a = int(groups['a'], 16)
    b = int(groups['b'], 16)
    c = int(groups['c'], 16)

    usbdl_timeout_string = "{} ms".format(usbdl_timeout_ms)
    if usbdl_timeout_ms == 0xffffffff:
        usbdl_timeout_string = "None"

    mode_timeout_string = "{} s".format(timeout_s)
    if timeout_s == 0x3fff:
        mode_timeout_string = "None"

    aa_string = {
        0x00: "No DL mode timeout.",
        0x01: "Valid DL mode timeout set.",
    }.get(a, "UNKNOWN")

    print(" - {}: USB DL timeout: {}".format(groups['x'], usbdl_timeout_string))
    print(" - {}: USB DL mode".format(groups['y']))
    print("   - Flag: {}".format("Present" if flag == 0x444C else "Absent"))
    print("   - Timeout: {}".format(mode_timeout_string))
    print("   - Enabled: {}".format(True if enable else False))
    print(" - {}: {}".format(groups['a'], aa_string))
    print(" - {}".format(groups['b']))
    print(" - {}".format(groups['c']))

def parse_bp(groups):
    flags_hi = int(groups['x'], 16)
    flags_lo = int(groups['y'], 16)
    offset = int(groups['z'], 16)
    flags = (flags_hi << 16) | flags_lo

    flag_bits = {
        0x00000001: "Preloader found on boot medium.",
        0x00000002: "USB synced for DL mode.",
        0x00000008: "JTAG is disabled.",
        0x00000010: "USB failed to sync for DL mode.",
        0x00000020: "UART synced for DL mode.",
        0x00000040: "UART failed to sync for DL mode.",
        0x00000080: "Preloader offset is non-zero.",
        0x00000200: "SEJ + 0xc0 (SEJ_CON1) bits [11:8] are not clear.",
        0x04000000: "Preloader on boot medium is 64-bit.",
        0x08000000: "USB DL HS (High Speed?) enabled.",
        0x10000000: "gfh_brom_cfg.gfh_brom_cfg_v3.reserved3 bit 0 and gfh_brom_cfg.gfh_brom_cfg_v3.flags.reserved1 are set: or M_SW_RES bit 6 is set.",
        0x20000000: "M_SW_RES bit 5 set.",
        0x40000000: "M_SW_RES bit 4 set.",
        0x80000000: "M_SW_RES bit 3 set.",
    }

    print(" - {} {}: Flags".format(groups['x'], groups['y']))
    for bit in range(32):
        mask = 1 << bit
        if flags & mask:
            description = flag_bits.get(mask, "Unknown.")
            print("   - {}".format(description))
    print(" - {}: Preloader offset: {} bytes".format(groups['z'], offset * 2048))

def parse_fn(groups):
    mode = int(groups['type'][1], 16)
    code_1 = int(groups['x'], 16)
    code_2 = int(groups['y'], 16)

    mode_string = {
        0: "RAM",
        3: "MSDC0 (eMMC)",
        5: "MSDC1 (SD)",
    }.get(mode, "UNKNOWN")

    print(" - {}: Boot mode ID: {}".format(mode, mode_string))
    print(" - {}: Most recent status code: 0x{:04x}".format(groups['x'], code_1))
    print(" - {}: Previous status code: 0x{:04x}".format(groups['y'], code_2))

def parse_g0(groups):
    y = int(groups['y'], 16)
    usbdl_bulk_com_support = y >> 8
    reserved1 = y & 0xff

    print(" - {}: Lower 16 bits of the BROM config flags.".format(groups['x']))
    print(" - {0:02X}: USB DL bulk communications support: {0}".format(usbdl_bulk_com_support))
    print(" - {0:02X}: BROM config reserved1: {0}".format(reserved1))

def parse_nn(groups):
    counter = int(groups['type'], 16)
    code_1 = int(groups['x'], 16)
    code_2 = int(groups['y'], 16)

    print(" - {}: Message counter: {}".format(groups['type'], counter))
    print(" - {}: Status code: 0x{:04x}".format(groups['x'], code_1))
    print(" - {}: Extra context-specific data: 0x{:04x}".format(groups['y'], code_2))

def parse_t0(groups):
    time_hi = int(groups['x'], 16)
    time_lo = int(groups['y'], 16)
    jtag_delay = int(groups['z'], 16)
    boot_time = (time_hi << 16) | time_lo

    print(" - {} {}: BROM execution time: {} ms".format(groups['x'], groups['y'], boot_time))
    print(" - {}: JTAG delay % 65536: {} ms".format(groups['z'], jtag_delay))

def parse_vn(groups):
    bd_idx = int(groups['type'][1], 10)
    code_1 = int(groups['x'], 16)
    code_2 = int(groups['y'], 16)
    bl_type = int(groups['z'], 16)

    bl_type_string = {
        0x0000: "gfh_file_none",
        0x0001: "arm_bl",
        0x0002: "arm_ext_bl",
        0x0003: "dualmac_dsp_bl",
        0x0004: "sctrl_cert",
        0x0005: "tool_auth",
        0x0006: "file_mtk_reserved1",
        0x0007: "epp",
        0x0008: "file_mtk_reserved2",
        0x0009: "file_mtk_reserved3",
        0x000a: "root_cert",
        0x000b: "ap_bl",
    }.get(bl_type, "unknown")

    print(" - {0}: Bootloader descriptor index: {0}".format(bd_idx))
    print(" - {}: Most recent status code: 0x{:04x}".format(groups['x'], code_1))
    print(" - {}: Previous status code: 0x{:04x}".format(groups['y'], code_2))
    print(" - {}: Bootloader descriptor bl_type: {}".format(groups['z'], bl_type_string.upper()))

def parse_msg(groups):
    msg_type = groups['type']

    matchers = (
        (r"BP", parse_bp),
        (r"F[0-9A-F]", parse_fn),
        (r"G0", parse_g0),
        (r"[0-9][0-9A-F]", parse_nn),
        (r"T0", parse_t0),
        (r"V[0-9]", parse_vn),
    )

    for regex, handler in matchers:
        match = re.fullmatch(regex, msg_type)
        if match:
            handler(groups)
            break

def main():
    matchers = (
        (re.compile(DL_REGEX), parse_dl),
        (re.compile(MSG_REGEX), parse_msg),
    )
    for line in fileinput.input():
        for regex, handler in matchers:
            match = regex.search(line)
            if match:
                print(get_orig(match))
                groups = match.groupdict()
                handler(groups)
                break


if __name__ == "__main__":
    main()
