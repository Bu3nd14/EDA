#!/usr/bin/env python3
"""Sonda di SCRATCH: il deck dei pavimenti fino a .control, piu' un controllo dato.
Uso: mk_probe.py <pavimento.cir> <controllo.txt> <out.cir>"""
import sys

deck, ctrl, out = sys.argv[1:4]
righe = open(deck).read().splitlines()
i = next(k for k, l in enumerate(righe) if l.strip() == ".control")
righe[0] = "probe_gear.cir - SCRATCH, non versionata: method=gear sul canale di tb_v2_mute_pavimento.cir"
testo = "\n".join(righe[:i]) + "\n" + open(ctrl).read()
open(out, "w").write(testo)
print("scritto %s" % out)
