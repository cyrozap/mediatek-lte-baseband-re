#!/usr/bin/env python3

import pathlib
import re
import struct
import subprocess
import tempfile


# Instruction parsers.
RE_INSTR_16_16 = re.compile(rb'^   0:\t(?P<b0>[0-9a-f]{2}) (?P<b1>[0-9a-f]{2}) (?P<b2>[0-9a-f]{2}) (?P<b3>[0-9a-f]{2}) \t(?P<instr0>[a-zA-Z0-9.]+)(\s+(?P<args0>[^|;\t]*))? \| (?P<instr1>[a-zA-Z0-9.]+)(\s+(?P<args1>[^|;\t]*))?(\t;.*)?')
RE_INSTR_32 = re.compile(rb'^   0:\t(?P<b0>[0-9a-f]{2}) (?P<b1>[0-9a-f]{2}) (?P<b2>[0-9a-f]{2}) (?P<b3>[0-9a-f]{2}) \t(?P<instr0>[a-zA-Z0-9.]+)(\s+(?P<args0>[^|;\t]*))?(\t;.*)?')
RE_INSTR_16 = re.compile(rb'^   0:\t(?P<b0>[0-9a-f]{2}) (?P<b1>[0-9a-f]{2})       \t(?P<instr0>[a-zA-Z0-9.]+)(\s+(?P<args0>[^|;\t]*))?(\t;.*)?')

# Argument parsers.
RE_ARGS_REG_IMM_IMM_IMM = re.compile(r'r(?P<reg0>[0-9]+), #0x(?P<imm0>[0-9a-f]+), #0x(?P<imm1>[0-9a-f]+), #0x(?P<imm2>[0-9a-f]+)')
RE_ARGS_REG_REG_IMM_IMM = re.compile(r'r(?P<reg0>[0-9]+), r(?P<reg1>[0-9]+), #0x(?P<imm0>[0-9a-f]+), #0x(?P<imm1>[0-9a-f]+)')
RE_ARGS_REG_REG_REG_IMM = re.compile(r'r(?P<reg0>[0-9]+), r(?P<reg1>[0-9]+), r(?P<reg2>[0-9]+), #0x(?P<imm0>[0-9a-f]+)')
RE_ARGS_REG_OFF_REG_MOD = re.compile(r'r(?P<reg0>[0-9]+), \(r(?P<reg1>[0-9]+)\+=#0x(?P<imm0>[0-9a-f]+)\)')
RE_ARGS_IMM_REG_IMM = re.compile(r'#0x(?P<imm0>[0-9a-f]+), r(?P<reg0>[0-9]+), #0x(?P<imm1>[0-9a-f]+)')
RE_ARGS_REG_REG_IMM = re.compile(r'r(?P<reg0>[0-9]+), r(?P<reg1>[0-9]+), #0x(?P<imm0>[0-9a-f]+)')
RE_ARGS_REG_REG_REG = re.compile(r'r(?P<reg0>[0-9]+), r(?P<reg1>[0-9]+), r(?P<reg2>[0-9]+)')
RE_ARGS_SFR_REG_REG = re.compile(r'(?P<sfr>[a-zA-Z0-9]+), r(?P<reg0>[0-9]+), r(?P<reg1>[0-9]+)')
RE_ARGS_REG_IMM_IMM = re.compile(r'r(?P<reg0>[0-9]+), #0x(?P<imm0>[0-9a-f]+), #0x(?P<imm1>[0-9a-f]+)')
RE_ARGS_REG_OFF_REG = re.compile(r'r(?P<reg0>[0-9]+), #0x(?P<imm0>[0-9a-f]+)\(r(?P<reg1>[0-9]+)\)')
RE_ARGS_REG_ADR_REG = re.compile(r'r(?P<reg0>[0-9]+), \(r(?P<reg1>[0-9]+)\)')
RE_ARGS_OFF_REG_MOD = re.compile(r'\(r(?P<reg0>[0-9]+)\+=#0x(?P<imm0>[0-9a-f]+)\)')
RE_ARGS_OFF_REG = re.compile(r'#0x(?P<imm0>[0-9a-f]+)\(r(?P<reg0>[0-9]+)\)')
RE_ARGS_IMM_IMM = re.compile(r'#0x(?P<imm0>[0-9a-f]+), #0x(?P<imm1>[0-9a-f]+)')
RE_ARGS_REG_IMM = re.compile(r'r(?P<reg0>[0-9]+), #0x(?P<imm0>[0-9a-f]+)')
RE_ARGS_REG_REG = re.compile(r'r(?P<reg0>[0-9]+), r(?P<reg1>[0-9]+)')
RE_ARGS_REG_SFR = re.compile(r'r(?P<reg0>[0-9]+), (?P<sfr>[a-zA-Z0-9]+)')
RE_ARGS_SFR_REG = re.compile(r'(?P<sfr>[a-zA-Z0-9]+), r(?P<reg0>[0-9]+)')
RE_ARGS_IMM = re.compile(r'#0x(?P<imm0>[0-9a-f]+)')
RE_ARGS_REG = re.compile(r'r(?P<reg0>[0-9]+)')

class Arguments:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return "<{}.{} {}>".format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.__dict__,
        )

class ArgsRegImmImmImm(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_IMM_IMM_IMM.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsRegRegImmImm(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_REG_IMM_IMM.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsRegRegRegImm(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_REG_REG_IMM.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsRegOffRegMod(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_OFF_REG_MOD.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsImmRegImm(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_IMM_REG_IMM.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsRegRegImm(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_REG_IMM.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsRegRegReg(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_REG_REG.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsSfrRegReg(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_SFR_REG_REG.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsRegImmImm(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_IMM_IMM.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsRegOffReg(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_OFF_REG.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsRegAdrReg(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_ADR_REG.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsOffRegMod(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_OFF_REG_MOD.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsOffReg(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_OFF_REG.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsImmImm(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_IMM_IMM.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsRegImm(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_IMM.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsRegReg(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_REG.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsRegSfr(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG_SFR.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsSfrReg(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_SFR_REG.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsImm(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_IMM.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsReg(Arguments):
    @classmethod
    def from_args(cls, args : str):
        args_match = RE_ARGS_REG.fullmatch(args)
        if not args_match:
            return None

        return cls(**args_match.groupdict())

class ArgsNone(Arguments):
    @classmethod
    def from_args(cls, args : str):
        if args:
            return None

        return cls()

class Instruction:
    def __init__(self, size, value, mnemonic, args):
        self.size = size
        self.value = value
        self.mnemonic = mnemonic
        self.args = parse_args(args)

    def __repr__(self):
        value = "{:08x}".format(self.value)
        if self.size == 2:
            value = "{:04x}".format(self.value)
        return "<{}.{} size:{} value:0x{} mnemonic:{} args:{}>".format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.size,
            value,
            self.mnemonic,
            self.args,
        )

class InstructionBundle:
    def __init__(self, instrs):
        self.instrs = instrs

    def __repr__(self):
        return "<{}.{} {}>".format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.instrs,
        )


def gen_elf_for_code(code):
    shstrtab_array = [
        b'\0',
        b'.shstrtab\0',
        b'.text\0',
    ]
    shstrtab = b''.join(shstrtab_array)
    body = code + shstrtab
    header_len = 0x34
    section_header_offset = header_len + len(body)
    section_headers_array = [
        bytearray(10),
        (shstrtab.index(b'.text'), 1, 6, 0, header_len, len(code), 0, 0, 2, 0),
        (shstrtab.index(b'.shstrtab'), 3, 0, 0, header_len + len(code), len(shstrtab), 0, 0, 1, 0),
    ]
    section_headers = b''.join([struct.pack('<IIIIIIIIII', *sh) for sh in section_headers_array])
    header = struct.pack('<B3sBBBBB7s', 0x7f, b"ELF", 1, 1, 1, 0, 0, bytearray(7))
    header += struct.pack('<HHIIIIIHHHHHH', 1, 0x2454, 1, 0, 0, section_header_offset, 0x02454008, header_len, 0, 0, 0x28, len(section_headers_array), 2)

    return header + body + section_headers

def gen_elf_for_instruction(instruction):
    code = struct.pack('>I', instruction)
    return gen_elf_for_code(code)

def parse_args(args : str):
    arg_formats = (
        ArgsRegImmImmImm,
        ArgsRegRegImmImm,
        ArgsRegRegRegImm,
        ArgsRegOffRegMod,
        ArgsImmRegImm,
        ArgsRegRegImm,
        ArgsRegRegReg,
        ArgsSfrRegReg,
        ArgsRegImmImm,
        ArgsRegOffReg,
        ArgsRegAdrReg,
        ArgsOffRegMod,
        ArgsOffReg,
        ArgsImmImm,
        ArgsRegImm,
        ArgsRegReg,
        ArgsRegSfr,
        ArgsSfrReg,
        ArgsImm,
        ArgsReg,
        ArgsNone,
    )

    for arg_class in arg_formats:
        parsed = arg_class.from_args(args)
        if parsed:
            return parsed

def disassemble_dword(dword : int, debug=False):
    # Use the disassembler binary to disassemble the generated ELF.
    elf = gen_elf_for_instruction(dword)
    elf_file = tempfile.NamedTemporaryFile(prefix="md32_0x{:08x}.".format(dword), suffix=".elf")
    elf_file.write(elf)
    elf_file.flush()
    objdump_path = pathlib.Path(__file__).parent.joinpath("md32-binutils", "objdump")
    objdump_command = "{} -d {}".format(objdump_path, elf_file.name).split()
    proc = subprocess.run(objdump_command, capture_output=True, check=True)
    elf_file.close()

    if debug:
        #print(proc.stdout.decode('utf-8'))
        print(proc.stdout)

    instruction_types = (
        (RE_INSTR_16_16, 2),
        (RE_INSTR_32, 4),
        (RE_INSTR_16, 2),
    )

    # Parse the disassembler output.
    for line in proc.stdout.strip(b'\n').split(b'\n'):
        # Try each instruction format until a match is found.
        for (instr_matcher, instr_size) in instruction_types:
            instr_match = instr_matcher.fullmatch(line)
            if instr_match:
                groups = instr_match.groupdict()
                if debug:
                    print(groups)
                if instr_size == 4:
                    instr = struct.unpack('>I', bytes.fromhex((groups['b0'] + groups['b1'] + groups['b2'] + groups['b3']).decode('ascii')))[0]
                else:
                    instr = struct.unpack('>H', bytes.fromhex((groups['b0'] + groups['b1']).decode('ascii')))[0]
                mnemonic = groups['instr0'].decode('ascii')
                args = groups['args0']
                if not args:
                    args = b''
                args = args.decode('ascii')
                if mnemonic == "illegal":
                    return None
                dec_instr = Instruction(instr_size, instr, mnemonic, args)
                mnemonic = groups.get('instr1')
                if mnemonic is None:
                    return dec_instr
                mnemonic = mnemonic.decode('ascii')
                instr = struct.unpack('>H', bytes.fromhex((groups['b2'] + groups['b3']).decode('ascii')))[0]
                args = groups['args1']
                if not args:
                    args = b''
                args = args.decode('ascii')
                dec_instrs = InstructionBundle([dec_instr, Instruction(instr_size, instr, mnemonic, args)])
                return dec_instrs

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", default=False, help="Print debug output.")
    parser.add_argument("instruction", type=str, help="The instruction word you want to decode.")
    args = parser.parse_args()

    instruction = int(args.instruction, 16)

    if len(args.instruction) <= 6:
        # Assume 16-bit instruction.
        instruction <<= 16

    print(disassemble_dword(instruction, debug=args.debug))

if __name__ == "__main__":
    main()
