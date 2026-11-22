#!/usr/bin/env python3
"""Publish the rendered ramen picture to the make.fun output directory."""

import hashlib
import os
import shutil
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
TARGET = OUTPUT_DIR / "entry.png"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not SOURCE.is_file():
        print(f"missing source image: {SOURCE}", file=sys.stderr)
        return 1

    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"cannot create output directory {OUTPUT_DIR}: {exc}", file=sys.stderr)
        return 1

    if TARGET.exists() and os.path.samefile(SOURCE, TARGET):
        print(f"source and target are the same file: {TARGET}")
        return 0

    shutil.copyfile(SOURCE, TARGET)

    want = digest(SOURCE)
    got = digest(TARGET)
    if want != got:
        print(f"sha256 mismatch: expected {want}, got {got}", file=sys.stderr)
        return 1

    size = TARGET.stat().st_size
    if size > 1_000_000:
        print(f"warning: copy is {size} bytes, above the 1,000,000-byte budget", file=sys.stderr)
        return 1

    print(f"copied entry.png -> {TARGET}")
    print(f"sha256 {got}")
    print(f"size {size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
