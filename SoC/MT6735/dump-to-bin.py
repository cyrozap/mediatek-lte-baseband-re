#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD

# Copyright (C) 2018 by Forest Crossman <cyrozap@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
# PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.


'''\
A simple utility to convert register dumps to binary data.

For example:

    ./dump.sh 10200000 1000 | ./dump-to-bin.py | hexdump -C

You can also read files directly:

    ./dump-to-bin.py dump.txt | hexdump -C

'''

import fileinput
import struct
import sys

if __name__ == "__main__":
    for line in fileinput.input():
        data = int(line.rstrip('\n').split(' = ')[1], 16)
        sys.stdout.buffer.write(struct.pack('<I', data))
