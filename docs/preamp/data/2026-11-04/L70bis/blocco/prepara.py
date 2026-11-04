#!/usr/bin/env python3
"""L70: the gain block with ONE rail, at regime (with S1 a rail fault leaves the toroid on, and the
audio board on the other rail, until the front switch: never measured before - ADR-109 measured the
jack, not the heat).

L66's reference decks (deck/dopo_<pos>/rif.cir: the block of today, ADR-111, in the five positions
A, B, B_g10, F1, F2, the mute open as in any rail fault: VCTL low -> CTL 0 until 0.3 s, then 1 - the
deck's own) copied here with:
  rif      - unchanged (the control: its powers must be L66's)
  m0       - VMINUS at 0 V (U502 off: the - rail held at ground)
  m06      - VMINUS at +0.6 V (the - rail pulled up through the board until a diode clamps it)
  p0       - VPLUS at 0 V
  p06      - VPLUS at -0.6 V
The rails of the deck are ideal sources at +-15 V (the regulators hold them at every mains: P7's
bench). @REPO@ as L66's runner writes it.

    /usr/bin/python3 -I blocco/prepara.py      -> blocco/<pos>_<caso>/<pos>_<caso>.cir
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = QUI
for _ in range(6):
    REPO = os.path.dirname(REPO)
L66 = os.path.join(REPO, "docs", "preamp", "data", "2026-11-02", "L66", "deck")
CASI = {"rif": None, "m0": ("VMM VMINUS 0 DC -15", "VMM VMINUS 0 DC 0"),
        "m06": ("VMM VMINUS 0 DC -15", "VMM VMINUS 0 DC 0.6"),
        "p0": ("VPP VPLUS 0 DC 15", "VPP VPLUS 0 DC 0"),
        "p06": ("VPP VPLUS 0 DC 15", "VPP VPLUS 0 DC -0.6")}
n = 0
for pos in ("A",):   # the deck holds the whole channel: a lost rail is the same in every position
    src = open(os.path.join(L66, "dopo_%s" % pos, "rif.cir")).read().replace("@REPO@", REPO)
    for caso, sost in CASI.items():
        t = src
        if sost:
            if t.count(sost[0]) != 1:
                raise SystemExit("RIFIUTATO: %s in %s" % (sost[0], pos))
            t = t.replace(sost[0], sost[1])
        t = t.replace("wrdata rif.dat", "wrdata %s_%s.dat" % (pos, caso))
        d = os.path.join(QUI, "%s_%s" % (pos, caso))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "%s_%s.cir" % (pos, caso)), "w") as f:
            f.write(t)
        n += 1
print(n, "deck")
