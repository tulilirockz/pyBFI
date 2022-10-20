#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
from collections import deque
import os
import sys
import re
import numpy as np
import logging
import warnings

def main() -> int:
    _parser: ArgumentParser = ArgumentParser(prog="bfi")
    _parser.add_argument(
        "input",
        type=str,
        metavar="INPUT",
        help="File that will be used as input"
    )

    logging.basicConfig(level=logging.CRITICAL, format="", stream=sys.stdout, force=True)
    args = _parser.parse_args()

    args.input = Path(args.input)
    if os.path.splitext(args.input)[1] != ".bf":
        raise TypeError("File is not a .bf (brainfuck) file")

    try:
        bf_data: str = args.input.read_text()
    except OSError as e:
        print(f"Exception Caught: {e}\nFile could not be read as a string", file=sys.stderr)
        return 1

    bf_data = re.sub(r'[^\<\>\+\-\-\.\,\[\]]', '', bf_data)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        return interpret_bf(bf_data)


def interpret_bf(base_string: str) -> int:
    memory_tape = deque([np.uint8(0)])
    tape_ptr, inst_ptr = 0, 0

    while inst_ptr != len(base_string):
        logging.debug(f"\n{inst_ptr=} {tape_ptr=} {base_string[inst_ptr]=} {memory_tape[tape_ptr]=}\n{memory_tape=} ")
        if base_string[inst_ptr] == "+":
            memory_tape[tape_ptr] += np.uint8(1)
        elif base_string[inst_ptr] == "-":
            memory_tape[tape_ptr] -= np.uint8(1)
        elif base_string[inst_ptr] == ">":
            if (tape_ptr + 1) >= len(memory_tape):
                memory_tape.append(np.uint8(0))
            tape_ptr += 1
        elif base_string[inst_ptr] == "<":
            if tape_ptr <= 0:
                memory_tape.appendleft(np.uint8(0))
            else:
                tape_ptr -= 1
        elif base_string[inst_ptr] == ".":
            sys.stdout.write(chr(memory_tape[tape_ptr]))
            sys.stdout.flush()
        elif base_string[inst_ptr] == ",":
            try:
                memory_tape[tape_ptr] = bytes(input()[0], "UTF-8")[0]
            except IndexError as e:
                memory_tape[tape_ptr] = bytes("\0", "ASCII")[0]
        elif base_string[inst_ptr] == "[":
            if memory_tape[tape_ptr] == 0:
                inst_ptr = base_string.find(']', inst_ptr, len(base_string))
        elif base_string[inst_ptr] == "]":
            if memory_tape[tape_ptr] != 0:
                inst_ptr = base_string.rfind('[', 0, inst_ptr)
        else:
            continue
        inst_ptr += 1
    return 0


if __name__ == "main":
    raise SystemExit(main())
