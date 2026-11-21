"""news-image-20261121 entry: publish the day's front page to the
output dir.

The front page itself (SATURDAY 21 NOVEMBER 2026, 30 stories) is
drawn by draw_frontpage.py, which runs where Pillow is available.
The grading sandbox ships a bare Python with no Pillow, so this
entrypoint stays standard-library only: the finished page is
committed beside it as entry.b64 (the PNG's bytes, base64-encoded
text), and this program decodes it back to the exact image bytes
and writes them into the output directory as entry.png.

No network, no randomness, no clock reads: the output bytes are
exactly the committed file's bytes on every run.
"""

import base64
import binascii
import os
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8"


def find_source():
    """Locate the committed entry.b64: next to this file first, then
    in the bot directory named by the environment."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, "entry.b64")
    if os.path.isfile(candidate):
        return candidate
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR")
    if bot_dir:
        candidate = os.path.join(bot_dir, "entry.b64")
        if os.path.isfile(candidate):
            return candidate
    return None


def load_image_bytes(src):
    """Read entry.b64 and return the decoded image bytes, or None if
    the payload is not valid base64 or does not decode to a PNG/JPEG.

    The committed file is line-wrapped, so all whitespace is stripped
    before decoding; with validate=True any other stray character is
    an error rather than being silently skipped."""
    with open(src, "rb") as f:
        encoded = b"".join(f.read().split())
    try:
        data = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        return None
    if not (data.startswith(PNG_MAGIC) or data.startswith(JPEG_MAGIC)):
        return None
    return data


def output_path():
    """The grader mounts a writable output directory and names it in
    MAKEFUN_OUTPUT_DIR; /output is the documented fallback."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, "entry.png")


def main():
    # Exit codes matter here: the grader fails the whole run on any
    # non-zero exit, so every failure path returns 1 explicitly and
    # the success path returns 0.
    src = find_source()
    if src is None:
        print("entry.b64 not found next to main.py", file=sys.stderr)
        return 1
    data = load_image_bytes(src)
    if data is None:
        print("entry.b64 does not decode to a PNG or JPEG image",
              file=sys.stderr)
        return 1
    dst = output_path()
    with open(dst, "wb") as f:
        f.write(data)
    if os.path.getsize(dst) != len(data):
        print("written file size mismatch", file=sys.stderr)
        return 1
    print(f"wrote {dst} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
