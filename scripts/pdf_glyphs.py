#!/usr/bin/env python3
"""pdf_glyphs.py - extract text from a PDF using nothing but the stdlib.

WHY THIS EXISTS
---------------
ADR-013 chose the LSK489, whose SPICE model Linear Systems distributes as
a PDF containing the .MODEL text rather than as a .lib file. Transcribing
a model by hand from a PDF is a place where silent errors get introduced,
so ADR-013 made the transcription method part of the decision: TWO
INDEPENDENT READINGS THAT MUST AGREE, compared character by character.

One reading is visual (rasterise with qlmanage, then look at the image).
This script is the other one - the mechanical reading. It never looks at
a picture: it inflates the PDF's content streams with zlib and recovers
the characters from the text-showing operators.

It is deliberately stdlib-only. poppler's pdftotext is a third, easier
reading, but it is a Homebrew dependency that a fresh checkout may not
have; this script keeps the transcription re-verifiable years from now
with nothing but /usr/bin/python3. That is the point of committing it:
the transcription stays FALSIFIABLE instead of merely asserted.

HOW IT MAPS GLYPH CODES TO CHARACTERS
-------------------------------------
A subset font numbers its glyphs by glyph ID, so the codes in the content
stream are NOT character codes: on the LSK489 model PDF `<0011> Tj` draws
a "." - a shift of +0x1D. Guessing that shift would be exactly the kind
of silent transformation this script exists to avoid, so it is not
guessed:

  1. If the PDF carries a /ToUnicode CMap (it usually does), that CMap is
     the producer's own authoritative glyph -> character mapping, and it
     is parsed and used verbatim. The header then reports whether the
     mapping happens to reduce to a single constant shift, which is a
     property worth stating rather than assuming.
  2. --offset <n> applies a constant shift by hand, for a file that has
     no ToUnicode CMap.
  3. --scan reports the shift that maximises printable ASCII, which is
     how a plausible value is FOUND for case 2 instead of invented.

Whatever mapping was used is printed in the header of the output, because
it is a transformation of the evidence and belongs in the report next to
the extracted text.

WHAT IT DOES NOT DO
-------------------
This is not a general-purpose PDF text extractor and must not be sold as
one. It handles PDFs whose text is drawn with Tj / TJ operators from
literal `(...)` or hex `<...>` strings. It does NOT do layout
reconstruction, ligatures, vertical writing, or encrypted files. Word
gaps produced by kerning rather than by a space character are lost, which
is why the comparison against the visual reading is done character by
character on the parameter text and not on whitespace.

USAGE
-----
  /usr/bin/python3 scripts/pdf_glyphs.py <file.pdf>
  /usr/bin/python3 scripts/pdf_glyphs.py <file.pdf> --offset 0x1D
  /usr/bin/python3 scripts/pdf_glyphs.py <file.pdf> --scan
  /usr/bin/python3 scripts/pdf_glyphs.py <file.pdf> --no-cmap
  /usr/bin/python3 scripts/pdf_glyphs.py <file.pdf> --raw   # glyph codes

Exit codes: 0 text extracted, 1 usage/read error, 2 no text found.
"""

import re
import sys
import zlib

# Text-showing operators we understand: (string) Tj / <hex> Tj and the
# [array] TJ form. All live inside a BT ... ET block; we do not track
# position, so the output is reading order as the producer emitted it.
_STRING = re.compile(rb"\((?:\\.|[^()\\])*\)|<[0-9A-Fa-f\s]*>", re.S)
_NUM = rb"[-+]?[0-9]*\.?[0-9]+"
_OPS = re.compile(
    rb"(?P<lit>\((?:\\.|[^()\\])*\)|<[0-9A-Fa-f\s]*>)\s*Tj"
    rb"|(?P<arr>\[(?:[^\[\]\\]|\\.)*\])\s*TJ"
    rb"|(?P<td>" + _NUM + rb")\s+(?P<tdy>" + _NUM + rb")\s+TD?[^a-zA-Z]"
    rb"|(?P<tstar>T\*)"
    rb"|(?P<tm>(?:" + _NUM + rb"\s+){6}Tm)",
    re.S,
)

_ESCAPES = {
    b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b",
    b"f": b"\f", b"(": b"(", b")": b")", b"\\": b"\\",
}


def unescape(raw):
    """Resolve PDF string escapes, including \\ddd octal, to raw bytes."""
    out = bytearray()
    i = 0
    while i < len(raw):
        c = raw[i:i + 1]
        if c != b"\\":
            out += c
            i += 1
            continue
        nxt = raw[i + 1:i + 2]
        if nxt in _ESCAPES:
            out += _ESCAPES[nxt]
            i += 2
        elif nxt.isdigit():
            j = i + 1
            digits = b""
            while j < len(raw) and len(digits) < 3 and raw[j:j + 1].isdigit():
                digits += raw[j:j + 1]
                j += 1
            out.append(int(digits, 8) & 0xFF)
            i = j
        elif nxt == b"\n":
            i += 2          # line continuation: emits nothing
        else:
            out += nxt
            i += 2
    return bytes(out)


def string_bytes(tok):
    """One PDF string token -> its raw bytes, literal or hex form."""
    if tok.startswith(b"<"):
        hexdigits = re.sub(rb"[^0-9A-Fa-f]", b"", tok[1:-1])
        if len(hexdigits) % 2:
            hexdigits += b"0"          # per spec: pad a lone nibble
        return bytes.fromhex(hexdigits.decode("ascii"))
    return unescape(tok[1:-1])


def content_streams(data):
    """Yield every stream in the file, inflated when it is deflated.

    We do not parse the object graph: we take every `stream ... endstream`
    span and try zlib on it. A stream that is not deflate (an embedded
    image, a font program) simply fails to inflate and is skipped, and a
    stream that inflates but holds no text yields no operators later.
    """
    pos = 0
    while True:
        start = data.find(b"stream", pos)
        if start == -1:
            return
        body = start + len(b"stream")
        if data[body:body + 2] == b"\r\n":
            body += 2
        elif data[body:body + 1] in (b"\n", b"\r"):
            body += 1
        end = data.find(b"endstream", body)
        if end == -1:
            return
        raw = data[body:end]
        try:
            yield zlib.decompress(raw)
        except zlib.error:
            try:
                yield zlib.decompressobj().decompress(raw)   # truncated
            except zlib.error:
                yield raw                                    # store()d
        pos = end + len(b"endstream")


def parse_tounicode(stream):
    """Parse a /ToUnicode CMap: {glyph code -> unicode text}.

    Returns {} for a stream that is not a CMap. Both forms are handled:
    `beginbfchar` single mappings and `beginbfrange` runs (the
    <lo> <hi> <dst> form; the array form is rare in producer output and
    is skipped rather than guessed at).
    """
    if b"begincmap" not in stream:
        return {}
    cmap = {}
    hexnum = rb"<([0-9A-Fa-f]+)>"

    for block in re.findall(rb"beginbfchar(.*?)endbfchar", stream, re.S):
        for src, dst in re.findall(hexnum + rb"\s*" + hexnum, block):
            cmap[int(src, 16)] = _utf16be(dst)

    for block in re.findall(rb"beginbfrange(.*?)endbfrange", stream, re.S):
        for lo, hi, dst in re.findall(
            hexnum + rb"\s*" + hexnum + rb"\s*" + hexnum, block
        ):
            start, end, base = int(lo, 16), int(hi, 16), int(dst, 16)
            for k in range(start, end + 1):
                cmap[k] = chr(base + (k - start))
    return cmap


def _utf16be(hexstr):
    raw = bytes.fromhex(hexstr.decode("ascii"))
    if len(raw) % 2:
        raw += b"\x00"
    return raw.decode("utf-16-be", errors="replace")


def constant_shift(cmap):
    """The single constant glyph->char shift, or None if there isn't one."""
    shifts = {ord(v) - k for k, v in cmap.items() if len(v) == 1}
    return shifts.pop() if len(shifts) == 1 else None


def show_ops(stream):
    """Yield each string token drawn by this content stream, in order.

    A TJ array interleaves strings with kerning numbers; the numbers move
    the pen and are dropped.

    Line breaks are not characters in a PDF - they are pen movements, and
    a producer like Skia emits ONE Tj per glyph with a Td between them.
    So a newline is emitted where the pen actually moves down: T*, a
    Td/TD with a non-zero vertical component, or a fresh Tm. Without this
    the output is one character per line, which cannot be compared with a
    visual reading.
    """
    for m in _OPS.finditer(stream):
        if m.group("lit") is not None:
            yield string_bytes(m.group("lit"))
        elif m.group("arr") is not None:
            for s in _STRING.finditer(m.group("arr")):
                yield string_bytes(s.group(0))
        elif m.group("tstar") is not None:
            yield b"\n"
        elif m.group("td") is not None:
            if float(m.group("tdy")) != 0.0:
                yield b"\n"
        else:                                    # Tm: a new text matrix
            yield b"\n"


def codes(raw, width):
    """Split raw string bytes into glyph codes of `width` bytes."""
    if width == 1:
        return list(raw)
    return [int.from_bytes(raw[i:i + width], "big")
            for i in range(0, len(raw) - width + 1, width)]


def printable_score(text):
    good = sum(1 for c in text if 32 <= ord(c) < 127 or c in "\t\n\r")
    return good / len(text) if text else 0.0


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 1

    path = args[0]
    offset = 0
    do_scan = "--scan" in args
    raw_mode = "--raw" in args
    use_cmap = "--no-cmap" not in args
    if "--offset" in args:
        offset = int(args[args.index("--offset") + 1], 0)

    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        print(f"ERROR: cannot read {path}: {e}", file=sys.stderr)
        return 1

    streams = list(content_streams(data))

    cmap = {}
    if use_cmap:
        for s in streams:
            cmap.update(parse_tounicode(s))

    # A CMap keyed above 0xFF means the codes in the content stream are
    # two bytes wide (an Identity-H CID font), which is how the width is
    # decided rather than assumed.
    width = 2 if any(k > 0xFF for k in cmap) or (
        cmap and b"<0000> <FFFF>" in b"".join(streams)) else 1

    tokens = []
    for s in streams:
        if b"begincmap" in s:
            continue                    # the CMap itself is not page text
        tokens.extend(show_ops(s))
    if not tokens:
        print(f"ERROR: no Tj/TJ text operators found in {path}", file=sys.stderr)
        return 2

    glyphs = []                          # (code, is_newline)
    for tok in tokens:
        if tok == b"\n":
            glyphs.append((None, True))
        else:
            glyphs.extend((c, False) for c in codes(tok, width))

    if do_scan:
        nums = [c for c, nl in glyphs if not nl]
        print(f"# pdf_glyphs.py --scan {path}")
        print(f"# {len(nums)} glyph codes, {width} byte(s) wide; "
              f"best constant shifts by printable ASCII:")
        scored = sorted(
            ((printable_score("".join(chr((n + o) & 0xFF) for n in nums)), o)
             for o in range(256)),
            reverse=True,
        )
        for score, o in scored[:5]:
            print(f"#   offset +0x{o:02X} ({o:+4d}) -> {score * 100:5.1f}% printable")
        return 0

    if cmap:
        shift = constant_shift(cmap)
        how = (f"/ToUnicode CMap embedded in the PDF, {len(cmap)} entries"
               + (f"; it reduces to a single constant shift of +0x{shift:02X}"
                  if shift is not None else
                  "; it is NOT a single constant shift"))
        def render(code):
            return cmap.get(code, "�")
    else:
        how = (f"constant glyph-code shift +0x{offset:02X} ({offset:+d})"
               if offset else "no mapping (raw codes as characters)")
        def render(code):
            return chr((code + offset) & 0xFF)

    out = "".join("\n" if nl else render(c) for c, nl in glyphs)

    print(f"# pdf_glyphs.py {path}")
    print(f"# stdlib-only mechanical reading; {width}-byte glyph codes; "
          f"mapping: {how}")
    print(f"# {printable_score(out) * 100:.1f}% printable")
    if raw_mode:
        line = []
        for c, nl in glyphs:
            if nl:
                if line:
                    print(" ".join(line))
                line = []
            else:
                line.append(f"{c:0{width * 2}X}")
        if line:
            print(" ".join(line))
        return 0
    sys.stdout.write(out)
    if not out.endswith("\n"):
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
