#!/usr/bin/env python3
"""L70, S1: the audio board with ONE rail, for good. Without the latch a rail fault leaves K501 closed:
the supervisor mutes, and the other rail stays on the audio board until the front switch. Today that
state lasts ~129 ms (the latch); with S1 it lasts indefinitely, so every part's temperature in it is
checked against its limit.

The bench is L66's heat bench (data/2026-11-02/L66, deck/dopo_<pos>/rif.cir: the block of the source
after ADR-111, byte for byte today's spice/preamp/gain_block.subckt - checked in the README), in its
five positions (A, B, B_g10, F1, F2). Its `rif` is already the state after a rail fault: mute
inserted (MUTE=0, relays released), no music. Each mode changes ONLY the rail sources:
  rif      L66's deck (the reference: +-15 V);
  meno0    VMM at 0 V: the - rail dead at ground (the bench's source can sink: the worst for
           currents into the dead rail);
  menoap   the - rail open: VMM at 0 V behind 100 kohm (the rail floats where the board puts it);
  piu0 / piuap   the same on the + rail (VPP).
The rest of the deck is L66's (its .meas at 2.29-2.3 s, the steady state); the wrdata file and the
measures' file (rif_fine.csv) are renamed after the mode.

    /usr/bin/python3 -I calore/prepara.py   -> calore/deck/rail_<pos>/<modo>.cir, calore/lista.txt
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
L66 = os.path.join(os.path.dirname(os.path.dirname(L)), "2026-11-02", "L66")
VPP, VMM = "VPP VPLUS 0 DC 15", "VMM VMINUS 0 DC -15"
MODI = {"rif": {},
        "meno0": {VMM: "VMM VMINUS 0 DC 0"},
        "menoap": {VMM: "RMMAP VMINUS VMMX 100k\nVMM VMMX 0 DC 0"},
        "piu0": {VPP: "VPP VPLUS 0 DC 0"},
        "piuap": {VPP: "RPPAP VPLUS VPPX 100k\nVPP VPPX 0 DC 0"}}
lista = []
for pos in ("A", "B", "B_g10", "F1", "F2"):
    src = open(os.path.join(L66, "deck", "dopo_" + pos, "rif.cir")).read()
    assert src.count(VPP + "\n") == 1 and src.count(VMM + "\n") == 1, pos
    assert src.count("wrdata rif.dat ") == 1, pos
    out = os.path.join(QUI, "deck", "rail_" + pos)
    os.makedirs(out, exist_ok=True)
    for modo, sost in MODI.items():
        t = src.replace("wrdata rif.dat ", "wrdata %s.dat " % modo).replace(
            "rif_fine.csv", "%s_fine.csv" % modo)
        for a, b in sost.items():
            t = t.replace(a + "\n", b + "\n")
        lines = t.split("\n")
        lines[0] = "L70 rail morto %s %s (da L66 dopo_%s/rif.cir) - %s" % (modo, pos, pos, lines[0])
        p = os.path.join(out, modo + ".cir")
        open(p, "w").write("\n".join(lines))
        lista.append(p)
open(os.path.join(QUI, "lista.txt"), "w").write("\n".join(lista) + "\n")
print("calore/lista.txt: %d deck" % len(lista))
