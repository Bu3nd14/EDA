#!/usr/bin/env python3
"""L64c: le parti delle schede di prova di L49 (9 ottobre) contro le netlist di oggi.

Uso: /usr/bin/python3 -I parti_schede.py <repo>   -> stampa e scrive parti_schede.csv qui accanto

Le schede: i riferimenti delle impronte nei .kicad_pcb di L49a / L49b. Le netlist: i riferimenti
dei componenti di circuits/preamp/preamp_audio.net e psu.net (formato KiCad, `(comp (ref "X")`).
Una parte che sta sulla scheda e non nella netlist e' «tolta dopo», una che sta nella netlist e non
sulla scheda e' «aggiunta dopo». Si confronta anche il valore, dove le due fonti lo dicono.
Solo stdlib.
"""
import csv
import os
import re
import sys

REPO = os.path.abspath(sys.argv[1])
QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "docs", "preamp", "data")
COPPIE = (("audio", os.path.join(DATA, "2026-10-09", "L49a", "audio_routed.kicad_pcb"),
           os.path.join(REPO, "circuits", "preamp", "preamp_audio.net")),
          ("alimentatore", os.path.join(DATA, "2026-10-09", "L49b", "psu", "psu_routed.kicad_pcb"),
           os.path.join(REPO, "circuits", "preamp", "psu.net")))


def blocchi(text, head):
    """I blocchi s-expr che cominciano con `(head`, a parentesi bilanciate."""
    out = []
    for m in re.finditer(r"\(" + head + r"[\s\"]", text):
        i, d = m.start(), 0
        for j in range(i, len(text)):
            c = text[j]
            if c == "(":
                d += 1
            elif c == ")":
                d -= 1
                if d == 0:
                    out.append(text[i:j + 1])
                    break
    return out


def da_pcb(path):
    with open(path, encoding="utf-8") as f:
        t = f.read()
    parti = {}
    for b in blocchi(t, "footprint"):
        r = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', b)
        v = re.search(r'\(property\s+"Value"\s+"([^"]*)"', b)
        # i fori di montaggio (H1..H4) li mette il layout, non la netlist: fuori dal confronto
        if r and not re.fullmatch(r"H\d+", r.group(1)):
            parti[r.group(1)] = v.group(1) if v else ""
    return parti


def da_net(path):
    with open(path, encoding="utf-8") as f:
        t = f.read()
    parti = {}
    for b in blocchi(t, "comp"):
        r = re.search(r'\(ref\s+"([^"]+)"\)', b)
        v = re.search(r'\(value\s+"([^"]*)"\)', b)
        if r:
            parti[r.group(1)] = v.group(1) if v else ""
    return parti


def main():
    righe = []
    for scheda, pcb, net in COPPIE:
        a, b = da_pcb(pcb), da_net(net)
        if not a or not b:
            print(f"RIFIUTO: {scheda}: nessuna parte letta ({len(a)} / {len(b)})")
            return 1
        tolte = sorted(set(a) - set(b))
        aggiunte = sorted(set(b) - set(a))
        cambiate = sorted(r for r in set(a) & set(b) if a[r] != b[r])
        print(f"{scheda}: sulla scheda {len(a)}, nella netlist di oggi {len(b)}; "
              f"tolte dopo {len(tolte)}, aggiunte dopo {len(aggiunte)}, valore cambiato {len(cambiate)}")
        for r in tolte:
            righe.append((scheda, r, "tolta dopo", a[r], ""))
        for r in aggiunte:
            righe.append((scheda, r, "aggiunta dopo", "", b[r]))
        for r in cambiate:
            righe.append((scheda, r, "valore cambiato", a[r], b[r]))
        righe.append((scheda, "_totale", f"{len(a)} / {len(b)}", "", ""))
    with open(os.path.join(QUI, "parti_schede.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(("scheda", "ref", "che cosa", "scheda_9_ottobre", "netlist_oggi"))
        w.writerows(righe)
    return 0


if __name__ == "__main__":
    sys.exit(main())
