#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify exact output against typing-conformance annotations."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from generate_payload import conformance_answers, render_payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("conformance_root", type=Path)
    parser.add_argument("executable", type=Path)
    arguments = parser.parse_args()

    root = arguments.conformance_root.resolve()
    executable = arguments.executable.resolve()
    answers = conformance_answers(root)
    expected = render_payload(answers)
    result = subprocess.run(
        [executable, "check", "."],
        cwd=root / "tests",
        check=False,
        capture_output=True,
    )
    if result.returncode != 1:
        raise RuntimeError(f"expected exit status 1, got {result.returncode}")
    if result.stdout != expected:
        raise RuntimeError("output differs from frozen conformance answers")
    print(
        f"PASS: {len(answers)} files conform "
        f"({len(expected.splitlines())} diagnostic lines)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
