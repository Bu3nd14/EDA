#!/usr/bin/env python3
"""L58b: the census list of the latent rows sent to the diagnosis, for corri_lista_an.sh.
Every line: <caso> <etichetta> sorgente <options>, L58a's options (lista_l58a.py).

  base     accensione (the known answer: L58a's l58a_base/accensione, music at 1209.3 ms),
           spegnimento_l, inserimento - no fault
  standby  the seven simulated modes of ADR-078 (K501 welded = Q503 shorted) against accensione
           (0 .. TE is the standby at rest, then the power-up) and spegnimento_l (into standby)
  mute     Q501 D-S / G-D (ADR-076) against accensione, spegnimento_l, inserimento, perdita

Usage: lista_l58b.py > lista.txt
"""
BASE = ("sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore "
        "--bat54 costruttore --sonde-piu")
righe = ["%s l58b_base %s" % (s, BASE) for s in ("accensione", "spegnimento_l", "inserimento")]
for b in ("f_q505_corto", "f_q506_corto", "f_r540_aperto", "f_r536_aperto", "f_r537_corto",
          "f_u508b_cieco", "f_q503_corto"):
    for e in ("accs", "spls"):
        righe.append("%s_%s l58b %s" % (b, e, BASE))
for b in ("f_q501_corto", "f_q501_gd"):
    for e in ("accs", "spls", "inss", "perds"):
        righe.append("%s_%s l58b %s" % (b, e, BASE))
print("\n".join(righe))
