#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Benchmark ultrafastest and ultrafaster on identical conformance inputs."""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

import tomllib


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("conformance_root", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("upstream", type=Path)
    parser.add_argument("ultrafast", type=Path)
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--warmups", type=int, default=10)
    arguments = parser.parse_args()

    if not arguments.conformance_root.is_dir():
        parser.error("conformance_root must be a directory")
    for executable in (arguments.candidate, arguments.upstream, arguments.ultrafast):
        if not executable.is_file():
            parser.error(f"executable does not exist: {executable}")
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
        ultrafast = Path(temporary_directory) / "alternate"
        shutil.copy2(arguments.candidate.resolve(), candidate)
        shutil.copy2(arguments.upstream.resolve(), upstream)
        shutil.copy2(arguments.ultrafast.resolve(), ultrafast)
        commands = {
            "ultrafastest": [str(candidate), "check", *paths],
            "ultrafaster": [str(upstream), "check", *paths],
            "ultrafast": [str(ultrafast), "check", *paths],
        }
        hyperfine = shutil.which("hyperfine")
        if hyperfine is None:
            parser.error("hyperfine is required")
        hyperfine_command = [
            hyperfine,
            "--shell=none",
            "--ignore-failure=1",
            "--style=basic",
            f"--warmup={arguments.warmups}",
            f"--runs={arguments.runs}",
        ]
        for name, command in commands.items():
            hyperfine_command.extend(("--command-name", name, shlex.join(command)))
        subprocess.run(
            hyperfine_command,
            cwd=root / "tests",
            check=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
