#!/usr/bin/env python3
"""
derive_jfet_variant.py - the gain block with a different model on its input
JFETs, DERIVED from the generated include, never edited by hand.

WHY THIS EXISTS (L20, NC-013)
-----------------------------
circuits/preamp/gain_block.py writes the model name of the two LSK489 halves
as a literal, "LSK489X", the hand-written placeholder with KF=0. To measure the
block with the vendor model LSK489A (models/jfet/lsk489.lib) nothing generated
may be touched (AGENTS.md rule 2) and nothing in models/ may be touched. The
other ways out are closed:
  - a second .model LSK489X with vendor values would be two models with one
    name (docs/limitations.md #17) and would lie to provenance();
  - a renamed copy of the vendor model in a new file is refused by provenance()
    of build_dossier.py, which knows only models/ and the placeholder library;
  - a hand-made copy of gain_block_flat.inc goes stale silently at the next
    topology change.
So the variant is DERIVED: this script reads the generated file, replaces the
model name on the JFET lines that name LSK489X - which must be EXACTLY two -
and writes the result with a header that names the source and its sha256.
Everything else is copied byte for byte, including the "External nodes" line
check_deck_refs.py (block 2g) reads for dangling contact nodes.

A derived file can still go stale. --check re-derives from the current
generated file and refuses if the committed one differs: block 2i of
run_tests.sh.

USAGE
-----
  derive_jfet_variant.py <repo> [--src REL] [--model NAME] [--out REL|-] [--check]

  defaults: --src spice/preamp/gain_block_flat.inc  --model LSK489A
            --out spice/preamp/derived/gain_block_flat_lsk489a.inc
  --out -   write to stdout
  --check   compare --out with a fresh derivation, write nothing

  With --model LSK489X the device lines come out identical to the source:
  that is the positive control of the substitution.

Exit codes:  0 = written / derived file current
             1 = --check: the derived file differs from a fresh derivation
             2 = bad invocation, unreadable file, or the source does not have
                 exactly two JFET lines on LSK489X
"""

import hashlib
import os
import sys

SOURCE_MODEL = "LSK489X"
EXPECTED = 2


def derive(src_rel, src_bytes, model):
    text = src_bytes.decode("utf-8")
    lines = text.splitlines(keepends=True)
    hits = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s or s[0] in "*.+":
            continue
        toks = s.split()
        if SOURCE_MODEL.lower() in (t.lower() for t in toks):
            if s[0].upper() != "J" or toks[-1].upper() != SOURCE_MODEL:
                raise ValueError(f"{src_rel}:{i + 1}: {SOURCE_MODEL} on a line that is not "
                                 f"a JFET naming it as its model: {s}")
            hits.append(i)
    if len(hits) != EXPECTED:
        raise ValueError(f"{src_rel}: {len(hits)} JFET lines on {SOURCE_MODEL}, expected "
                         f"exactly {EXPECTED} - the block has changed, re-read before deriving")
    names = []
    for i in hits:
        ln = lines[i]
        body = ln.rstrip("\r\n")
        eol = ln[len(body):]
        head, _, last = body.rpartition(" ")
        if last.upper() != SOURCE_MODEL:
            raise ValueError(f"{src_rel}:{i + 1}: cannot locate the model token: {body}")
        lines[i] = f"{head} {model}{eol}"
        names.append(body.split()[0])
    sha = hashlib.sha256(src_bytes).hexdigest()
    header = (
        f"* DERIVED by scripts/derive_jfet_variant.py from {src_rel} - DO NOT HAND-EDIT.\n"
        f"* Source sha256: {sha}\n"
        f"* Only change: {', '.join(names)} use model {model} instead of {SOURCE_MODEL}.\n"
        f"* Regenerate: /usr/bin/python3 scripts/derive_jfet_variant.py <repo> --model {model}\n"
        "* Checked by run_tests.sh block 2i (--check). L20, NC-013.\n"
    )
    return (header + "".join(lines)).encode("utf-8")


def main(argv):
    args = argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__)
        return 2
    repo = os.path.abspath(args.pop(0))
    opts = {"--src": "spice/preamp/gain_block_flat.inc", "--model": "LSK489A",
            "--out": "spice/preamp/derived/gain_block_flat_lsk489a.inc"}
    check = False
    while args:
        a = args.pop(0)
        if a == "--check":
            check = True
        elif a in opts and args:
            opts[a] = args.pop(0)
        else:
            print(f"bad argument: {a}")
            return 2
    try:
        with open(os.path.join(repo, opts["--src"]), "rb") as f:
            src = f.read()
        new = derive(opts["--src"], src, opts["--model"])
    except (OSError, ValueError, UnicodeDecodeError) as e:
        print(f"REFUSED: {e}")
        return 2

    if check:
        out = os.path.join(repo, opts["--out"])
        try:
            with open(out, "rb") as f:
                old = f.read()
        except OSError as e:
            print(f"REFUSED: {e}")
            return 2
        if old == new:
            print(f"   OK: {opts['--out']} is the current derivation of {opts['--src']}")
            return 0
        a, b = old.decode("utf-8", "replace").splitlines(), new.decode("utf-8").splitlines()
        for n in range(max(len(a), len(b))):
            x = a[n] if n < len(a) else "<missing>"
            y = b[n] if n < len(b) else "<missing>"
            if x != y:
                print(f"   STALE: {opts['--out']}:{n + 1}\n     committed: {x}\n     derived:   {y}")
                break
        return 1

    if opts["--out"] == "-":
        sys.stdout.write(new.decode("utf-8"))
        return 0
    out = os.path.join(repo, opts["--out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(new)
    print(f"written {opts['--out']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
