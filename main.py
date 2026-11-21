#!/usr/bin/env python3
"""Entry program for the news-image-20261121 bounty.

Writes the finished infographic (entry.png, rendered locally by
tools/generate.py from the real news of Saturday 21 November 2026) to
/output/entry.png. Standard library only, no network, deterministic: the
same bytes go out on every run, because the file is copied as-is.
"""

import hashlib
import os
import shutil
import struct
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
IMAGE = os.path.join(BASE, "entry.png")
BYTE_LIMIT = 1048576
PIXEL_LIMIT = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def read_png_size(path):
    """Return (width, height) from a PNG's IHDR chunk, without any imaging
    library."""
    with open(path, "rb") as handle:
        head = handle.read(33)
    if head[:8] != PNG_MAGIC:
        raise ValueError("entry.png is not a PNG file")
    if head[12:16] != b"IHDR":
        raise ValueError("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run():
    size = os.path.getsize(IMAGE)
    if size > BYTE_LIMIT:
        raise ValueError(f"entry.png is {size} bytes, over the 1 MiB cap")
    width, height = read_png_size(IMAGE)
    if width > PIXEL_LIMIT or height > PIXEL_LIMIT:
        raise ValueError(
            f"entry.png is {width}x{height}, over the 1024px cap")
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, "entry.png")
    shutil.copyfile(IMAGE, target)
    before = sha256_of(IMAGE)
    after = sha256_of(target)
    if before != after:
        raise ValueError("copy mismatch: output differs from entry.png")
    size = os.path.getsize(target)
    print(f"wrote {target} ({size} bytes, {width}x{height}, sha256 {after})")
    return 0


if __name__ == "__main__":
    sys.exit(run())
