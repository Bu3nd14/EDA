"""L54b2: le cartelle di una serie di corse nell'ordine delle righe di an_sorgente.csv /
an_fmea_sorgente.csv di L54b1 (l'ordine di lista_noto.txt), per analizza_an.py.
Uso: /usr/bin/python3 -I dirs_noto.py <L> <prefisso> seq|fmea   (prefisso: fin_, fint_, fint18_)"""
import os
import sys

L, pre, che = sys.argv[1], sys.argv[2], sys.argv[3]
SEQ = ["accensione", "rilascio", "spegnimento_l", "buco20", "buco200", "guasto", "perdita",
       "perdita_min", "guasto_u501", "guasto_u503", "guasto_u503_min", "cf_nodelta", "fredda",
       "accensione_u501", "ritenuta_frontale", "fredda_u501"]
RETE = ["accensione", "perdita", "buco20", "buco200"]
FMEA = ["f_u505a_cieco_gu501", "f_u505b_cieco_gu502", "f_u506b_cieco_gu503", "f_k501_bobina_muss",
        "f_k501_bobina_musp10s", "f_c509_corto_mus", "f_c509_corto_musp10"]
s = os.path.join(L, "seq")
if che == "seq":
    d = [os.path.join(s, pre + "sorgente", c) for c in SEQ]
    for c in RETE:
        d += [os.path.join(s, pre + "sorgente_m10", c), os.path.join(s, pre + "sorgente_p10", c)]
else:
    d = [os.path.join(s, pre + "fmea_sorgente", c) for c in FMEA]
for x in d:
    assert os.path.isdir(x), x
print(" ".join(d))
