#!/usr/bin/env python3

import operator
import subprocess
import sys

def UsageError():
    print("""hmmtrace - the mtrace() parser.
Usage:
hmmtrace MTRACE OFFSET
where MTRACE is the mtrace trace file
and OFFSET is the offset of the binary's .text section (see README)""")
    

class Allocation:
    def __init__(self, size, location=''):
        self.size = size
        self.location = location
    
if len(sys.argv) != 3:
    UsageError()

text_offset = int(sys.argv[2], 16)
started = False
exe_path = None

alloc = {}

with open(sys.argv[1], 'r') as trace:
    for line in trace.readline():
        print(line)
        line = line.split()
        if line[0] == '=':
            if line[1] == 'Start':
                started = True
            elif line[1] == 'End':
                break
            elif line[0] == '@':
                location = line[1]
                current_exe, offset = location.split(':')
                offset = int(offset[1:-1], 16)

                if exe_path is None:
                    exe_path = current_exe
                elif exe_path != current_exe:
                    print("Don't know how to handle multi-binary traces, abort.")
                    exit(1)
                real_offset = offset - text_offset

                source_line = subprocess.run(['addr2line', '-j', '.text', '-e', exe_path, hex(real_offset)])
                addr = int(line[3], 16)

                op = line[2]
                if op == '+':
                    # malloc() | realloc_alloc()
                    size = int(line[4])
                    if addr in alloc:
                        print(f'Address {addr} allocated twice, wth.')
                    else:
                        alloc[addr] = Allocation(size, location)
                elif op == '-' or op == '<':
                    # free() | realloc_free()
                    if addr not in alloc:
                        print(f'Unallocated address {addr} is freed, wth.')
                    else:
                        del alloc[addr]
                else:
                    print(f'Unknown operation {op}')
                    exit(1)

for addr, (size, location) in alloc.items():
    print(addr, size, location)
