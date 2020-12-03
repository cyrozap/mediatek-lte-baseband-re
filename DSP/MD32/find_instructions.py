#!/usr/bin/env python3

import argparse
import json
import os
import struct
import time

from z3 import *

from md32_dis import disassemble_dword, parse_args


class Opcodes:
    def __init__(self):
        self.opcode_set = set()

    def __iter__(self):
        return self.opcode_set.__iter__()

    def add(self, mnemonic, argfmt, mask, opcode):
        self.opcode_set.add((mnemonic, argfmt, mask, opcode))

    def get_by_mnemonic_and_argfmt(self, mnemonic, argfmt):
        for (mn, af, mask, opcode) in self.opcode_set:
            if mnemonic == mn and argfmt == af:
                return (mn, af, mask, opcode)
        return None

    def get_by_mnemonic_and_instr(self, mnemonic, instr):
        for (mn, argfmt, mask, opcode) in self.opcode_set:
            if (instr & mask) == opcode and mnemonic == mn:
                return (mn, argfmt, mask, opcode)
        return None

    def get_by_instr(self, instr):
        for (mn, argfmt, mask, opcode) in self.opcode_set:
            if (instr & mask) == opcode:
                return (mn, argfmt, mask, opcode)
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--timeout", type=float, default=1, help="The number of seconds to wait for Z3 to generate an instruction before trying a random one.")
    parser.add_argument("instructions", type=str, help="The JSON file with the list of instructions you want to read/write.")
    arguments = parser.parse_args()

    s = Solver()

    instr = BitVec("instr", 32)

    timeout = arguments.timeout

    extra_seeds = set()

    opcodes = Opcodes()
    try:
        opcodes_file = open(arguments.instructions, 'r')
        opcode_list = json.load(opcodes_file)
        opcodes_file.close()

        print("Loaded saved results:")
        for (mnemonic, argfmt, mask, opcode) in opcode_list:
            opcodes.add(mnemonic, argfmt, mask, opcode)
            print("{} ({}): mask = 0x{:08x}, masked opcode = 0x{:08x}".format(mnemonic, argfmt, mask, opcode))
            s.add((instr & BitVecVal(mask, 32)) != BitVecVal(opcode, 32))

            # Add extra instruction seeds.
            candidate_bits = set(range(32))
            while candidate_bits:
                candidate = candidate_bits.pop()
                test_instr = opcode ^ (1 << candidate)
                test_dis = disassemble_dword(test_instr)
                if not test_dis:
                    continue
                new_args = parse_args(test_dis[3])
                new_argfmt = None
                if new_args:
                    new_argfmt = type(new_args).__name__
                new_mnemonic = test_dis[2]
                if new_argfmt and opcodes.get_by_mnemonic_and_argfmt(new_mnemonic, new_argfmt):
                    continue
                extra_seeds.add(test_instr)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pass

    while s.check() == sat:
        # First, obtain a "seed" instruction. Time out and use a random seed if Z3 is too slow.
        start = time.monotonic()
        mnemonic = None
        while True:
            disassembled = None
            while not disassembled:
                if extra_seeds:
                    seed = extra_seeds.pop()
                elif time.monotonic() - start > timeout:
                    #print("Using random seed due to timeout.")
                    seed = struct.unpack('>I', os.urandom(4))[0]
                    start = time.monotonic()
                else:
                    try:
                        #print("Using Z3 seed.")
                        seed = s.model()[instr].as_long()
                    except (AttributeError, Z3Exception):
                        # Use a random value the first time.
                        #print("Using random seed.")
                        seed = struct.unpack('>I', os.urandom(4))[0]

                disassembled = disassemble_dword(seed)

                # We don't ever want Z3 to give us this seed again.
                s.add(instr != BitVecVal(seed, 32))

                # Check the model to "commit" the result.
                s.check()

            instr_size = disassembled[1]
            mnemonic = disassembled[2]
            if instr_size < 4:
                # We're not testing 16-bit instructions yet.
                print("Not testing {}.".format(mnemonic))
                continue
            args = parse_args(disassembled[3])
            argfmt = None
            if args:
                argfmt = type(args).__name__
            opcode_item = None
            if argfmt:
                opcode_item = opcodes.get_by_mnemonic_and_argfmt(mnemonic, argfmt)
            if opcode_item:
                # Don't test instructions we've already tested.
                print("Already tested {0} ({1}) (mask = 0x{2:08x}, masked opcode = 0x{3:08x}).".format(*opcode_item))
                continue

            break

        print("Seed instruction: 0x{:08x} ({})".format(seed, mnemonic))

        # For each bit in the instruction, flip it, then try decoding the
        # instruction again. If it decodes to the same mnemonic, then that bit
        # is not essential to decoding the instruction. If it decodes to a
        # different mnemonic, then that bit is essential to decoding the
        # instruction. If we run out of candidate bits, then we're done--use
        # Z3 to find us another instruction that doesn't match this one.

        candidate_bits = set(range(32))

        unessential_bits = set()

        while candidate_bits:
            candidate = candidate_bits.pop()
            test_instr = seed ^ (1 << candidate)
            test_dis = disassemble_dword(test_instr)
            if not test_dis:
                continue
            new_args = parse_args(test_dis[3])
            new_argfmt = None
            if new_args:
                new_argfmt = type(new_args).__name__
            new_mnemonic = test_dis[2]
            if new_mnemonic != mnemonic or new_argfmt != argfmt:
                if not new_argfmt or not opcodes.get_by_mnemonic_and_argfmt(new_mnemonic, new_argfmt):
                    # Found a new opcode?
                    extra_seeds.add(test_instr)
                continue
            unessential_bits.add(candidate)

        essential_bits = set(range(32)).difference(unessential_bits)

        # Generate an opcode mask and value for the mnemonic.
        op_mask = 0
        while essential_bits:
            bit = essential_bits.pop()
            op_mask |= 1 << bit
        op_value = op_mask & seed

        if not argfmt:
            print("Error: Unknown argument format: \"{}\"".format(disassembled[3]))
            return

        opcodes.add(mnemonic, argfmt, op_mask, op_value)

        print("{} ({}): mask = 0x{:08x}, masked opcode = 0x{:08x}".format(mnemonic, argfmt, op_mask, op_value))

        s.add((instr & BitVecVal(op_mask, 32)) != BitVecVal(op_value, 32))

        opcodes_file = open(arguments.instructions, 'w')
        json.dump(list(opcodes), opcodes_file)
        opcodes_file.close()

    print("Done!")


if __name__ == "__main__":
    main()
