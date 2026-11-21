#!/usr/bin/env python3
"""Entrypoint for the make.fun news-image-20261121 entry.

The front page itself is drawn locally by draw_frontpage.py and shipped
in this repository as entry.png, because the grading sandbox has no
Pillow and installs nothing. This program is therefore a careful
copier, written against the Python standard library only:

* it finds entry.png beside itself, or in MAKEFUN_BOT_DIR;
* it checks the file really is a PNG or a JPEG, by its first bytes;
* it writes those bytes to entry.png in MAKEFUN_OUTPUT_DIR
  (or /output when the variable is not set).

It exits 0 on success and 1 on any failure, and writes the same bytes
on every run.
"""

import os
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"
IMAGE_NAME = "entry.png"


def candidate_paths():
    here = os.path.dirname(os.path.abspath(__file__))
    yield os.path.join(here, IMAGE_NAME)
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR")
    if bot_dir:
        yield os.path.join(bot_dir, IMAGE_NAME)
    yield os.path.join("/bot", IMAGE_NAME)


def read_image():
    """Return the shipped image's bytes, or None if unusable."""
    for path in candidate_paths():
        try:
            with open(path, "rb") as handle:
                data = handle.read()
        except OSError:
            continue
        if data.startswith(PNG_MAGIC) or data.startswith(JPEG_MAGIC):
            return data
        return None
    return None


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return os.path.join(out_dir, IMAGE_NAME)


def main():
    data = read_image()
    if not data:
        print("entry.png missing or not a PNG/JPEG image", file=sys.stderr)
        return 1
    target = output_path()
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as handle:
            handle.write(data)
    except OSError as exc:
        print("could not write %s: %s" % (target, exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
