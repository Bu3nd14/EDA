"""aggiungi_rshunt.py - L47b2b1 (#38, #42): mette `option rshunt=1e12` prima della `tran` nelle
corse date, accanto a trtol=1. La terza sonda (rele2/) mostra che E cev_20 e ch2_20, ferme alla
chiusura del rele' al jack (t = 4,5 s) con ogni altra opzione, con rshunt corrono fino in fondo.
#38: rshunt regge ma aggiunge 1e-12 S a ogni nodo; si mette in tutte le corse a 20 Hz della curva
E (il banco resta uno) e si confronta con D cev_20 senza.

    /usr/bin/python3 aggiungi_rshunt.py <corsa.cir> [...]
"""
import sys

RIGA = "option rshunt=1e12"
NOTA = ("* L47b2b1: rshunt=1e12 (sonda_20hz/rele2/: E cev_20 e ch2_20 si fermano alla chiusura del "
        "rele' con ogni altra opzione; #38)")
for p in sys.argv[1:]:
    r = open(p).read().splitlines()
    if RIGA in r:
        print("gia' fatto:", p)
        continue
    k = next(i for i, x in enumerate(r) if x.startswith("tran "))
    r[k:k] = [NOTA, RIGA]
    open(p, "w").write("\n".join(r) + "\n")
    print("rshunt in", p)
