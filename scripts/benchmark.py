#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Benchmark ultrafastest and ultrafaster on identical conformance inputs."""

from __future__ import annotations

import argparse
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

import tomllib


def run_once(command: list[str], directory: Path) -> float:
    started = time.perf_counter_ns()
    result = subprocess.run(
        command,
        cwd=directory,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
    if result.returncode != 1:
        raise RuntimeError(
            f"expected exit status 1, got {result.returncode}: "
            f"{result.stderr.decode(errors='replace')}"
        )
    return elapsed_ms


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("conformance_root", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("upstream", type=Path)
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--warmups", type=int, default=10)
    arguments = parser.parse_args()

    root = arguments.conformance_root.resolve()
    with (root / "src" / "test_groups.toml").open("rb") as file:
        groups = tomllib.load(file)
    paths = sorted(
        path.name
        for pattern in ("*.py", "*.pyi")
        for path in (root / "tests").glob(pattern)
        if path.name.split("_")[0] in groups
    )
    with tempfile.TemporaryDirectory() as temporary_directory:
        candidate = Path(temporary_directory) / "candidate"
        upstream = Path(temporary_directory) / "reference"
        shutil.copy2(arguments.candidate.resolve(), candidate)
        shutil.copy2(arguments.upstream.resolve(), upstream)
        commands = {
            "ultrafastest": [str(candidate), "check", *paths],
            "ultrafaster": [str(upstream), "check", *paths],
        }
        for _ in range(arguments.warmups):
            for command in commands.values():
                run_once(command, root / "tests")

        results = {name: [] for name in commands}
        for run in range(arguments.runs):
            order = tuple(commands) if run % 2 == 0 else tuple(reversed(commands))
            for name in order:
                results[name].append(run_once(commands[name], root / "tests"))

        for name, timings in results.items():
            print(
                f"{name}: {statistics.median(timings):7.3f} ms median "
                f"({min(timings):.3f} ms minimum)"
            )
        print(
            "speedup: "
            f"{statistics.median(results['ultrafaster']) / statistics.median(results['ultrafastest']):.3f}x"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
