# hmmtrace
A quick and dirty tool for making sense of mtrace() traces.

Note that this tool is probably abandoned because `mtrace()`, as it turns out, has limited use in modern practical projects because of its inability to preserve call chain information that lead to the allocation. It is a "must" in projects that allocate memory with a wrapper like `xmalloc` or `new`. Consider using [gperftools](https://github.com/gperftools/gperftools), [Valgrind's Massif](http://valgrind.org/docs/manual/ms-manual.html) and other similar tools instead.

## Introduction
mtrace() is a ...

## Obtaining the trace

1. Set the `MALLOC_TRACE` environment variable to the file you want your trace to be saved into.
Then open the program you want to run in the debugger:

```
$ MALLOC_TRACE=/tmp/gdb.trace gdb
```

2. Set a breakpoint at the location from which you want to start the trace and "continue" to it. If you want to start at `main()`, set it at `main()`.

```
(gdb) b main
(gdb) c
```

3. Call mtrace to begin writing to the trace.

```
(gdb) call (void)mtrace()
```

4. Continue execution and run you program as you would until you decide to stop the trace.

5. Stop writing to the trace.

```
(gdb) call (void)muntrace()
```

6. Locate the `.text` segment:

```
(gdb) info file
...
0x000055555563f0c0 - 0x0000555555db67f5 is .text
...
```

Write down the first address. It is the offset of the `.text` segment `hmmtrace` will need it to decrypt those addresses into source code lines.

## Using hmmtrace

Currently only sort by total currently allocated size for each line of code is supported:
```
$ hmmtrace <tracefile>
```

You can find out the code location, use `addr2line`:
```
$ addr2line -j .text -e /home/undercat/derp/binutils-gdb/gdb/gdb `printf %x $((ADDRESS_SHOWN - TEXT_SEGMENT_OFFSET))`
```
where `TEXT_SEGMENT_OFFSET` is the offset of the binary's `.text` segment as described above. Example:
```
$ addr2line -j .text -e /home/undercat/derp/binutils-gdb/gdb/gdb `printf %x $((0x55555574d4ce-0x000055555563f0c0))`
/home/../binutils-gdb/gdb/common/common-utils.c:44
```

## TODO
Automate trace acquisition and text segment identification. It should be possible to run it like this:
```
$ hmmtrace <binary>
```
