#!/usr/bin/env python3
"""
check_deck_provenance.py - a testbench may say which models it simulates only
if its own .include's say the same.

WHY THIS EXISTS (L33, NC-031)
-----------------------------
From L22 to L33 twelve decks carried the header comment

    LS352 (ADR-018) and this is its VENDOR model - the only real device
    model in this deck besides the LSK489.

and three more said the same thing in other words. The LSK489 those decks
simulate is LSK489X: a hand-written placeholder with KF=0 in
spice/preamp/placeholder_devices.lib. The vendor model, models/jfet/lsk489.lib,
is included by no deck at all. The sentence travelled with the copied header,
and nothing compared a header with the includes written under it. Every
number was right; what a reader believed about the numbers was not - the only
vendor model simulated is the LS352, and no simulated device has 1/f noise.
The dossier stopped believing the comments in L32, when it began reading the
includes; the decks kept saying it.

WHAT IT CHECKS
--------------
For each deck, which models it really simulates and where they come from, by
the SAME function the dossier uses - provenance() in
docs/preamp/dossier/build_dossier.py, imported and not rewritten: a model is
vendor if it lives in models/ next to its .provenance.json, placeholder if it
lives in spice/preamp/placeholder_devices.lib, KF absent counts as 0.

Against that, the claims made in the deck's comment lines ('*'), read as
paragraphs and split into sentences, in the forms found in L33:

    ... vendor / real device / costruttore ... besides [the] PART   vendor
    ... tranne PART [e PART] ... segnaposto                         vendor
    ... solo PART [e PART] ... modello del costruttore              vendor
    ... KF = 0 but|except on|for [the] PART                         KF != 0
    PART ... vendor / real device / del costruttore                 vendor
    PART ... placeholder / segnaposto                               placeholder

The last two forms need PART and the word within 40 characters, with no
negation, no opposite word and no other part name in between. A claim the
includes contradict - or a claim about a part the deck does not simulate - is
a finding.

WHAT IT CANNOT SEE: a claim in words it does not know. It is a net woven from
the sentences found in L33, not a reader of English or Italian; a new way of
saying "vendor" passes. It reads decks, not dated READMEs: those are the
output of a dated run and are annotated, never rewritten.

USAGE
-----
    /usr/bin/python3 scripts/check_deck_provenance.py <repo-root> <deck.cir>...

Exit codes:  0 = no claim is contradicted by the includes
             1 = at least one is
             2 = bad invocation, a deck whose provenance cannot be read, or NO
                 claim found in any deck (a check with nothing to check does
                 not pass)
"""

import os
import re
import sys

WINDOW = 40
VENDOR_W = r"(?:vendor|real\s+device|del\s+costruttore)"
PLACE_W = r"(?:placeholder|segnaposto)"
# Between a part and its word: none of these may appear.
NEG = r"\b(?:not|non|no|no\s+longer|besides|tranne|but|ma|instead|invece|than|rather|except)\b"


def load_dossier(repo):
    here = os.path.join(repo, "docs", "preamp", "dossier")
    sys.path.insert(0, here)
    import build_dossier as bd                          # noqa: E402
    if os.path.realpath(bd.REPO) != os.path.realpath(repo):
        raise ValueError(f"build_dossier.py resolves REPO to {bd.REPO}, not {repo}")
    return bd


def paragraphs(path):
    """[[(line number, text)]] of consecutive '*' comment lines. A blank
    comment line or a rule of dashes ends a paragraph, as a reader reads it."""
    out, cur = [], []
    with open(path, errors="replace") as fh:
        for n, ln in enumerate(fh, 1):
            if ln.startswith("*"):
                body = ln[1:].strip()
                if body and not set(body) <= set("-=*#~ "):
                    cur.append((n, body))
                    continue
            if cur:
                out.append(cur)
                cur = []
    if cur:
        out.append(cur)
    return out


def line_of(para, part):
    """The first line of the paragraph naming the part; else its first line."""
    for n, body in para:
        if part.lower() in body.lower():
            return n
    return para[0][0]


def sentences(text):
    return [s for s in re.split(r"(?<=[.;])\s+", re.sub(r"\s+", " ", text.lower())) if s]


class Claims:
    def __init__(self, part_names):
        self.names = part_names                         # lowercase token -> part
        alt = "|".join(sorted(map(re.escape, part_names), key=len, reverse=True))
        P = rf"(?:{alt})"
        LIST = rf"{P}(?:\s*(?:,|\be\b|\band\b)\s*{P})*"
        self.P = re.compile(rf"\b{P}\b")
        self.forms = [
            ("vendor", re.compile(rf"\b{VENDOR_W}\b.*?\bbesides\s+(?:the\s+)?({LIST})\b")),
            ("vendor", re.compile(rf"\btranne\s+({LIST})\b.*?\b{PLACE_W}\b")),
            ("vendor", re.compile(rf"\bsolo\s+({LIST})\b.*?\bmodell[oi]\s+del\s+costruttore\b")),
            ("kf", re.compile(rf"\bkf\s*=\s*0\s+(?:but|except)\s+(?:on|for|in)\s+(?:the\s+)?({LIST})\b")),
        ]
        self.direct = [
            ("vendor", re.compile(rf"\b({P})\b(.{{0,{WINDOW}}}?)\b{VENDOR_W}\b")),
            ("placeholder", re.compile(rf"\b({P})\b(.{{0,{WINDOW}}}?)\b{PLACE_W}\b")),
        ]
        self.opposite = {"vendor": re.compile(rf"\b{PLACE_W}\b"),
                         "placeholder": re.compile(rf"\b{VENDOR_W}\b")}

    def parts_in(self, s):
        return [self.names[m.group(0)] for m in self.P.finditer(s)]

    def of(self, sentence):
        """[(kind, part, excerpt)] claimed by one sentence."""
        found, spans = [], []
        for kind, rx in self.forms:
            for m in rx.finditer(sentence):
                spans.append(m.span())
                for part in self.parts_in(m.group(1)):
                    found.append((kind, part, m.group(0)))
        for kind, rx in self.direct:
            for m in rx.finditer(sentence):
                if any(a <= m.start(1) < b for a, b in spans):
                    continue
                mid = m.group(2)
                if (re.search(NEG, mid) or self.P.search(mid)
                        or self.opposite[kind].search(mid)):
                    continue
                found.append((kind, self.names[m.group(1)], m.group(0)))
        return found


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    repo = os.path.abspath(argv[1])
    try:
        bd = load_dossier(repo)
    except (ImportError, ValueError, OSError) as e:
        print(f"UNREADABLE: cannot use provenance() from build_dossier.py: {e}")
        return 2
    names = {}
    for model, part in bd.PART.items():
        names[model.lower()] = part
        names[part.lower()] = part
    claims = Claims(names)

    contradicted, claims_total = 0, 0
    for deck in argv[2:]:
        before = len(bd.FAILURES)
        try:
            prov = bd.provenance(os.path.abspath(deck))
        except OSError as e:
            print(f"UNREADABLE: {e}")
            return 2
        if len(bd.FAILURES) > before:
            for f in bd.FAILURES[before:]:
                print(f"UNREADABLE: {f}")
            return 2
        truth = {}
        for m in prov:
            t = truth.setdefault(m["part"], {"vendor": set(), "kf": set(), "files": set()})
            t["vendor"].add(m["vendor"])
            t["kf"].add(m["kf"] != 0)
            t["files"].add(f'{m["model"]} ({m["file"]})')

        name = os.path.basename(deck)
        bad = 0
        n_claims = 0
        for para in paragraphs(deck):
            for s in sentences(" ".join(body for _, body in para)):
                for kind, part, excerpt in claims.of(s):
                    n_claims += 1
                    t = truth.get(part)
                    why = None
                    if t is None:
                        why = f"claims about {part}, which this deck does not simulate"
                    elif kind == "vendor" and True not in t["vendor"]:
                        why = f"calls {part} vendor; the includes give {', '.join(sorted(t['files']))}: placeholder"
                    elif kind == "placeholder" and False not in t["vendor"]:
                        why = f"calls {part} a placeholder; the includes give {', '.join(sorted(t['files']))}: vendor"
                    elif kind == "kf" and True not in t["kf"]:
                        why = f"says {part} has KF != 0; the includes give KF = 0 ({', '.join(sorted(t['files']))})"
                    if why:
                        bad += 1
                        print(f"   {name}:{line_of(para, part)}: {why} - \"{excerpt}\"")
        claims_total += n_claims
        contradicted += bad
        vend = sorted(p for p, t in truth.items() if True in t["vendor"])
        status = "OK" if not bad else f"{bad} CONTRADICTED"
        print(f"   {status}: {name} ({n_claims} claims; vendor by includes: "
              f"{', '.join(vend) or 'none'})")
    if claims_total == 0:
        print("   no provenance claim found in any deck - refusing to pass")
        return 2
    return 1 if contradicted else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
