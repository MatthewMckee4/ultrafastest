# ultrafastest

Faster than [`ultrafaster`](https://github.com/AlexWaygood/ultrafaster), by
doing even less.

`ultrafastest` is an Apple Silicon Mach-O containing frozen Python typing
conformance diagnostics. It has no language runtime, parser, lookup table, or
formatter. Every invocation makes two raw Darwin system calls: `write` emits
the already-formatted 41 KB payload, then `exit` returns diagnostic status 1.
The binary links only libSystem because the Darwin linker requires it.

This is not a type checker. It ignores every argument and every file.

## Build

```console
$ make
$ ./ultrafastest check anything.py | head -1
annotations_callable.py:19:1: error[]
```

The frozen payload comes from the `python/typing` conformance suite at commit
`4f470b0ff13b7625df11e9ef8d8fac3f62c0a0ab`:

```console
$ make oracle CONFORMANCE=../typing/conformance
$ make verify CONFORMANCE=../typing/conformance
PASS: 141 files conform (1042 diagnostic lines)
```

## Benchmark

Build Alex's `ultrafaster`, then run both executables over the same 141 paths.
Runs alternate order to reduce timing bias.

```console
$ make benchmark CONFORMANCE=../typing/conformance UPSTREAM=../ultrafaster/ultrafaster
```

Apple Silicon results will vary by machine. This repository's measured result
on an Apple M4 Pro, using 50 warmups and 1,000 alternating runs:

```console
ultrafastest:   1.666 ms median (1.389 ms minimum)
ultrafaster:    1.759 ms median (1.485 ms minimum)
speedup: 1.1x
```
