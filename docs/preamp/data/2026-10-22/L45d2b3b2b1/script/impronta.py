#!/usr/bin/env python3
"""L45d2b3b2b1: l'impronta del finale col dissipatore (ADR-099), letta da pcbnew.

Uso (il Python 3.9 di KiCad): impronta.py
Stampa le piazzole e RIFIUTA (exit 1) se non sono B, C, E sui reofori e due C sul dissipatore, a
12,7 mm l'una dall'altra e 4,6 mm dietro la fila dei reofori (Ohmite sink-w.pdf rev 8/21-1).
"""
import os
import sys

import pcbnew

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
LIB = os.path.join(REPO, "library", "preamp.pretty")
NOME = "TO-220-3_Vertical_Ohmite_WA-T220-101E"

fp = pcbnew.FootprintLoad(LIB, NOME)
if fp is None:
    sys.exit("RIFIUTATO: pcbnew non carica %s da %s" % (NOME, LIB))
piazzole = []
for p in fp.Pads():
    x, y = pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)
    piazzole.append((p.GetNumber(), round(x, 3), round(y, 3), round(pcbnew.ToMM(p.GetDrillSize().x), 3)))
for r in piazzole:
    print("piazzola %s  x %.3f  y %.3f  foro %.2f mm" % r)
attese = [("B", 0.0, 0.0, 1.3), ("C", 2.54, 0.0, 1.3), ("E", 5.08, 0.0, 1.3),
          ("C", -3.81, -4.6, 2.0), ("C", 8.89, -4.6, 2.0)]
if sorted(piazzole) != sorted(attese):
    sys.exit("RIFIUTATO: piazzole diverse da quelle attese %s" % attese)
cy = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
print("courtyard %.2f x %.2f mm" % (pcbnew.ToMM(cy.GetWidth()), pcbnew.ToMM(cy.GetHeight())))
print("OK: 5 piazzole, i due piedini del dissipatore sul collettore, 12,7 mm, 4,6 mm dietro i reofori")
