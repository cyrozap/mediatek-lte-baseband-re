#!/usr/bin/env python3

import argparse
import json
import multiprocessing
import os

from z3 import *

from md32_dis import Instruction, disassemble_dword


def process_dword(dword):
    disassembled = disassemble_dword(dword)
    if disassembled is None:
        return None

    if not isinstance(disassembled, Instruction):
        # We're not testing instruction bundles.
        return None

    if disassembled.size > 2:
        # We're not testing 32-bit instructions.
        #print("Not testing {}.".format(mnemonic))
        return None

    args = disassembled.args
    argfmt = None
    if args:
        argfmt = type(args).__name__
    if not argfmt:
        raise ValueError("Unknown argument format: \"{}\"".format(args))

    return (disassembled.value, disassembled.mnemonic, argfmt)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("instructions", type=str, help="The JSON file with the list of instructions you want to read/write.")
    arguments = parser.parse_args()

    opcodes = set()

    processes = os.cpu_count()
    chunk_size = 16

    with multiprocessing.Pool(processes) as pool:
        print("Generating candidates...")
        candidates = pool.imap_unordered(process_dword, range(0x8000 << 16, 1 << 32, 1 << 16), chunk_size)

        instruction_map = dict()
        for instr, mnemonic, argfmt in filter(lambda x: x != None, candidates):
            if instruction_map.get((mnemonic, argfmt)) is None:
                instruction_map[(mnemonic, argfmt)] = set()
            instruction_map[(mnemonic, argfmt)].add(instr)

        for (mnemonic, argfmt), instrs in instruction_map.items():
            instr = BitVec("instr", 32)

            actual = []
            for i in instrs:
                actual.append(instr == BitVecVal(i, 32))
            actual = Or(actual)

            model = []
            model.append((instr & 0x0000ffff) == BitVecVal(0, 32))
            model.append(ULE(instr, max(instrs)))
            model.append(UGE(instr, min(instrs)))
            model = And(model)

            #print("{} ({}): {}".format(mnemonic, argfmt, simplify(actual)))
            print("{} ({}): {}".format(mnemonic, argfmt, simplify(model)))

            s = Solver()
            s.push()
            s.add(Not(actual == model))
            if s.check() == sat:
                print("Error: Model does not match reality. Counterexample: instr = 0x{:08x}".format(s.model()[instr].as_long()))

                s.push()
                counterexamples = set()
                while s.check() == sat:
                    counterexample = s.model()[instr].as_long()
                    counterexamples.add(counterexample)
                    s.add(instr != BitVecVal(counterexample, 32))
                s.pop()

                # Split the instruction definition.
                s.pop()
                new_model = And(
                    (instr & 0x0000ffff) == BitVecVal(0, 32),
                    Or(
                        And(
                            ULE(instr, max(instrs)),
                            UGT(instr, max(counterexamples)),
                        ),
                        And(
                            ULT(instr, min(counterexamples)),
                            UGE(instr, min(instrs)),
                        ),
                    ),
                )
                s.add(Not(actual == new_model))

                if s.check() == sat:
                    print("Error: Still not equal. Counterexample: instr = 0x{:08x}".format(s.model()[instr].as_long()))
                    continue

                print("Found new model: {} ({}): {}".format(mnemonic, argfmt, simplify(new_model)))
                opcodes.add((mnemonic, argfmt, min(instrs), min(counterexamples) - (1 << 16)))
                opcodes.add((mnemonic, argfmt, max(counterexamples) + (1 << 16), max(instrs)))
                continue

            opcodes.add((mnemonic, argfmt, min(instrs), max(instrs)))

    opcodes_file = open(args.instructions, 'w')
    json.dump(list(opcodes), opcodes_file)
    opcodes_file.close()

    print("Done!")


if __name__ == "__main__":
    main()
