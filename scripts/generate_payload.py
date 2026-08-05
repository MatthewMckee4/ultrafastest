#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate frozen conformance diagnostics as bytes ready for write(2)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import tomllib


def conformance_answers(root: Path) -> dict[str, tuple[int, ...]]:
    with (root / "src" / "test_groups.toml").open("rb") as file:
        groups = tomllib.load(file)

    paths = sorted(
        path
        for pattern in ("*.py", "*.pyi")
        for path in (root / "tests").glob(pattern)
        if path.name.split("_")[0] in groups
    )
    answers: dict[str, tuple[int, ...]] = {}
    for path in paths:
        required: set[int] = set()
        first_group_lines: dict[str, int] = {}
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.split("#", maxsplit=1)[0].strip():
                continue
            if re.search(r"# E(?=:|$| )", line):
                required.add(line_number)
            for match in re.finditer(r"# E\[([^\]]+)\]", line):
                first_group_lines.setdefault(
                    match.group(1).removesuffix("+"), line_number
                )
        required.update(first_group_lines.values())
        answers[path.name] = tuple(sorted(required))
    return answers


def render_payload(answers: dict[str, tuple[int, ...]]) -> bytes:
    return "".join(
        f"{filename}:{line}:1: error[]\n"
        for filename, lines in sorted(answers.items())
        for line in lines
    ).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("conformance_root", type=Path)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()

    root = arguments.conformance_root
    if not root.exists():
        parser.error(f"conformance root does not exist: {root}")
    answers = conformance_answers(root)
    payload = render_payload(answers)
    arguments.output.write_bytes(payload)
    print(
        f"Generated {arguments.output}: {len(answers)} files, "
        f"{sum(map(len, answers.values()))} diagnostics, {len(payload)} bytes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
