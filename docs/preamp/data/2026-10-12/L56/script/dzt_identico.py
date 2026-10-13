#!/usr/bin/env python3
"""L56 (ADR-068): il modello del costruttore del DZT5401 / DZT5551 e' lo stesso testo del MMBT5401 /
MMBT5551 gia' in models/?

Legge le .MODEL dal file collettivo di Diodes (vendor/bjt_pnp/diodes_inc/DZT5401/
Transistors-100V.spice.txt, scaricato dal costruttore) e dai file del costruttore dei MMBT
(vendor/.../MMBT5401.spice.txt, MMBT5551.spice.txt), e le confronta parametro per parametro dopo
aver tolto il nome del modello e normalizzato spazi e maiuscole. Il collettivo porta il DZT5551 due
volte (DATE=08FEB2011 e 27JUL2010): si confrontano tutte le copie.

Uso: /usr/bin/python3 dzt_identico.py   (esce 1 se una copia diverge)
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(QUI, *[".."] * 6))
V = os.path.join(ROOT, "vendor")
COLL = os.path.join(V, "bjt_pnp", "diodes_inc", "DZT5401", "Transistors-100V.spice.txt")
MMBT = {"DZT5401": os.path.join(V, "bjt_pnp", "diodes_inc", "MMBT5401", "MMBT5401.spice.txt"),
        "DZT5551": os.path.join(V, "bjt_npn", "diodes_inc", "MMBT5551", "MMBT5551.spice.txt")}


SUFF = {"T": 1e12, "G": 1e9, "MEG": 1e6, "K": 1e3, "M": 1e-3, "U": 1e-6, "N": 1e-9, "P": 1e-12,
        "F": 1e-15}


def numero(v):
    """Un valore SPICE col suffisso (177f, 1.2MEG); altrimenti il testo com'e'."""
    m = re.match(r"^([-+0-9.eE]+?)(MEG|[TGKMUNPF])?$", v.upper())
    try:
        return float(m.group(1)) * SUFF.get(m.group(2) or "", 1.0) if m else v
    except ValueError:
        return v


def modelli(testo):
    """{nome: [dict dei parametri, ...]} per ogni .MODEL (con le righe + di continuazione)."""
    out = {}
    righe = testo.replace("\r", "").split("\n")
    i = 0
    while i < len(righe):
        r = righe[i]
        if r.upper().startswith(".MODEL"):
            corpo = r
            while i + 1 < len(righe) and righe[i + 1].startswith("+"):
                i += 1
                corpo += " " + righe[i][1:]
            p = corpo.split()
            nome, tipo = p[1].upper(), p[2].upper().strip("(")
            s = re.sub(r"\s*=\s*", "=", " ".join(p[3:])).replace("(", " ").replace(")", " ")
            par = {"_tipo": tipo}
            for kv in s.split():
                k, _, v = kv.partition("=")
                par[k.upper()] = numero(v)
            out.setdefault(nome, []).append(par)
        i += 1
    return out


coll = modelli(open(COLL, errors="replace").read())
esito = 0
for dzt, f in MMBT.items():
    rif = modelli(open(f, errors="replace").read())
    (rnome, rpar), = rif.items()
    copie = coll.get(dzt, [])
    if not copie:
        sys.exit("%s non trovato nel file collettivo" % dzt)
    for k, c in enumerate(copie):
        diff = {x for x in set(c) | set(rpar[0]) if c.get(x) != rpar[0].get(x)}
        print("%s copia %d contro %s: %s" % (dzt, k + 1, rnome,
                                              "IDENTICO (%d parametri)" % len(c) if not diff
                                              else "DIVERSO in %s" % sorted(diff)))
        esito |= bool(diff)
sys.exit(esito)
