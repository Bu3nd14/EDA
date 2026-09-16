#!/usr/bin/env python3
"""Assembla un deck tb_v2_mute_*: testa + include + CANALE copiato dal deck dei
pavimenti + controllo. Uso: assembla.py <pavimento.cir> <testa> <controllo> <out>"""
import sys

pav, testa, ctrl, out = sys.argv[1:5]
righe = open(pav).read().splitlines()
i0 = next(i for i, l in enumerate(righe) if l.startswith("* >>> CANALE"))
i1 = next(i for i, l in enumerate(righe) if l.startswith("* <<< CANALE"))
inc0 = next(i for i, l in enumerate(righe) if l.startswith(".include"))
# dalla nota sui modelli agli include compresi, identici al deck dei pavimenti
nota = next(i for i, l in enumerate(righe) if l.startswith("* PROVVISORIO SUI MODELLI"))
blocco_comune = righe[nota:i0]
testo = open(testa).read().rstrip("\n").splitlines()
corpo = testo + blocco_comune + righe[i0:i1 + 1] + [""] + open(ctrl).read().rstrip("\n").splitlines()
open(out, "w").write("\n".join(corpo) + "\n")
print("scritto %s: %d righe (canale %d righe)" % (out, len(corpo), i1 - i0 + 1))
