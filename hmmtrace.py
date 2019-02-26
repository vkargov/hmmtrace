#!/usr/bin/env python3

import itertools
import operator
import subprocess
import sys

# TODO revise & add unknown things to deck

class Allocation:
    def __init__(self, size, location=''):
        self.size = size
        self.location = location

    def __repr__(self):
        return f'(size={self.size}, location={self.location})'


def read_mtrace(trace_path, text_offset, limit=None):
    started = False
    exe_path = None
    alloc = {}
    i = 0

    with open(trace_path, 'r') as trace:
        for line in trace:
            line = line.split()
            if line[0] == '=':
                if line[1] == 'Start':
                    started = True
                elif line[1] == 'End':
                    break
            elif line[0] == '@':
                location = line[1]

                #current_exe, offset = location.split(':')
                #offset = int(offset[1:-1], 16)

                # if exe_path is None:
                #     exe_path = current_exe
                # elif exe_path != current_exe:
                #     print("Don't know how to handle multi-binary traces, abort.")
                #     exit(1)
                # real_offset = offset - text_offset

                # source_line = subprocess.run(['addr2line', '-j', '.text', '-e', exe_path, hex(real_offset)])
                addr = int(line[3], 16)

                op = line[2]
                if op == '+' or op == '>':
                    # malloc() | realloc_alloc()
                    size = int(line[4], 16)
                    if addr in alloc:
                        print(f'Address {addr:x} allocated twice, wth.')
                    else:
                        alloc[addr] = Allocation(size, location)
                elif op == '-' or op == '<':
                    # free() | realloc_free()
                    if addr not in alloc:
                        print(f'Unallocated address {addr:x} is freed, wth.')
                    else:
                        del alloc[addr]
                else:
                    raise Exception(f'Unknown operation {op}')

            i += 1
            if limit is not None and i > limit:
                break
    return alloc


if __name__ == '__main__':
    def usage_error():
        print("""hmmtrace - the mtrace() parser.
Usage:
hmmtrace MTRACE OFFSET
where MTRACE is the mtrace trace file
and OFFSET is the offset of the binary's .text section (see README)""")

    if len(sys.argv) != 3:
        UsageError()

    alloc = read_mtrace(sys.argv[1], int(sys.argv[2], 16))
    #for addr, allocation in alloc.items():
    #    print(f'0x{addr:x}, {allocation}')

    def getloc(i): return i[1].location
    for loc, lines in itertools.groupby(sorted(alloc.items(), key=getloc), getloc):
        total_size = 0
        for line in lines:
            total_size += line[1].size
        print(loc, total_size)

