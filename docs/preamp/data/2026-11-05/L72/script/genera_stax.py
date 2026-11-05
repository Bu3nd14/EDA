"""L72: il limite alto della finestra della Stax, controllato sulle corse.

Copia (non riesegue: limitations, uno script vecchio scrive nella sua cartella) i cinque casi piu'
lunghi sulla Stax e ne cambia SOLO il condensatore d'uscita della fissa 2 (CFIX2):
  - i tre di L45d2b3b2b2 (124,5 / 124,4 / 124,2 ms a 1,05 uF, p10_stax_lunghi.csv): il blocco di
    allora nelle copie guaste inc_stax/sorg/, con i loro include;
  - i due di L66 sul blocco di oggi (D158_cc, Q132_be: 120,0 / ~120 ms a 1,05 uF).
Ogni caso a 1,05 uF (controllo: deve ridare la cifra versionata) e al limite alto 1,265 uF.

Uso: /usr/bin/python3 -I .../L72/script/genera_stax.py  -> L72/stax/deck/*.cir, L72/stax/lista.txt
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.dirname(os.path.dirname(L))
CASI = [
    ("2026-10-23/L45d2b3b2b2/deck/stax_lunghi", "G0_A_JQ110A_ds_k105"),
    ("2026-10-23/L45d2b3b2b2/deck/stax_lunghi", "G0_A_JQ110B_as_k105"),
    ("2026-10-23/L45d2b3b2b2/deck/stax_lunghi", "G0_A_Q146_ce_k105"),
    ("2026-11-02/L66/deck/stax", "G0_F2_D158_cc_k105"),
    ("2026-11-02/L66/deck/stax", "G0_F2_Q132_be_k105"),
]
VALORI = (("c1050", "1.05u"), ("c1265", "1.265u"))
RIGA = "CFIX2 FIX2_A FIX2C 1.05u"

out = os.path.join(L, "stax", "deck")
os.makedirs(out, exist_ok=True)
lista = []
for cartella, caso in CASI:
    src = open(os.path.join(DATA, cartella, caso + ".cir")).read()
    if src.count(RIGA) != 1:
        sys.exit(f"RIFIUTATO: {caso} non ha una e una sola riga «{RIGA}»")
    base = caso[:-5]
    for tag, val in VALORI:
        nome = f"{base}_{tag}"
        txt = src.replace(RIGA, f"CFIX2 FIX2_A FIX2C {val}")
        txt = txt.replace(f"wrdata {caso}.dat", f"wrdata {nome}.dat")
        righe = txt.split("\n")
        righe[0] = f"L72 stax limite alto {nome} (da {cartella}/{caso}.cir, CFIX2 {val})"
        p = os.path.join(out, nome + ".cir")
        open(p, "w").write("\n".join(righe))
        lista.append(p)
open(os.path.join(L, "stax", "lista.txt"), "w").write("\n".join(lista) + "\n")
print(f"{len(lista)} deck in {out}")
