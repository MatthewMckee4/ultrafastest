# ultrafastest

Faster than [`ultrafaster`](https://github.com/AlexWaygood/ultrafaster) and
[`ultrafast`](https://github.com/JelleZijlstra/ultrafast), by doing even less.

`ultrafastest` is an Apple Silicon Mach-O containing frozen Python typing
conformance diagnostics. It has no language runtime, parser, lookup table, or
formatter. Every invocation makes two raw Darwin system calls: `write` emits
the already-formatted 40 KB payload, then `exit` returns diagnostic status 1.
The binary links only libSystem because the Darwin linker requires it.

This is not a type checker. It ignores every argument and every file.

## Build

```console
$ make
$ ./ultrafastest check anything.py | head -1
annotations_callable.py:19:1: error[
```

The frozen payload comes from the `python/typing` conformance suite at commit
`4f470b0ff13b7625df11e9ef8d8fac3f62c0a0ab`:

```console
$ make oracle CONFORMANCE=../typing/conformance
$ make verify CONFORMANCE=../typing/conformance
PASS: 141 files conform (1042 diagnostic lines)
```

## Benchmark

Build Alex's `ultrafaster` and install Jelle's `ultrafast`, then run all three
over the same 141 paths. The harness copies them to equal-length executable
paths and uses hyperfine without a shell.

```console
$ uv sync --directory ../ultrafast
$ make benchmark CONFORMANCE=../typing/conformance \
    UPSTREAM=../ultrafaster/ultrafaster \
    ULTRAFAST=../ultrafast/.venv/bin/ultrafast
```

Apple Silicon results will vary by machine. This repository's measured result
on an Apple M4 Pro with Python 3.12.12, using hyperfine 1.20.0, 100 warmups,
and 5,000 runs per checker:

```console
Benchmark 1: ultrafastest
  Time (mean ± σ):       1.0 ms ±   0.1 ms
Benchmark 2: ultrafaster
  Time (mean ± σ):       1.1 ms ±   0.1 ms
Benchmark 3: ultrafast
  Time (mean ± σ):      11.1 ms ±   0.4 ms

Summary
  ultrafastest ran
    1.10 ± 0.08 times faster than ultrafaster
   11.00 ± 0.70 times faster than ultrafast
```
