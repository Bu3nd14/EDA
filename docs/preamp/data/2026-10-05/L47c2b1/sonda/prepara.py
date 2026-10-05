"""prepara.py - L47c2b1, la sonda di convergenza del taglio con musica (limitations #38, #42).

Nella matrice le corse con musica a 20 Hz e 1 kHz si fermano su «Timestep too small» ESATTAMENTE
all'apertura del contatto in serie al jack (t = 1,0244 s in mev_1k_iii; il log accusa il JFET
d'ingresso j.xa.jq110a). Con le celle non succedeva: il contatto si apriva a musica gia' attenuata
di ~70 dB. La sonda copia alcune corse della matrice in una cartella per variante, con le opzioni
messe prima della `tran`:
  t1    option trtol=1                         (il rimedio di L47b2b1, #42)
  t1r   option trtol=1 + option rshunt=1e12    (il secondo rimedio di L47b2b1)
  gear  option method=gear
Corse: mev_1k_iii e mev_20_iii (si fermano), mev_lz_iii (corre senza opzioni: misura quanto
ogni opzione sposta le cifre rispetto alla matrice).

    /usr/bin/python3 prepara.py
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
MATRICE = os.path.join(QUI, "..", "matrice_interruttore")
CORSE = ("mev_1k_iii", "mev_20_iii", "mev_lz_iii")
VARIANTI = {
    "t1": ["option trtol=1"],
    "t1r": ["option trtol=1", "option rshunt=1e12"],
    "gear": ["option method=gear"],
}
# Seconda prova (dopo la prima: t1, t1r e gear si fermano tutte a t = 1,0244 s, il rimbalzo del
# contatto in serie che RICHIUDE 400 us dopo l'apertura, col lato condensatore a -12 V e il jack a
# ~0 V e 0 pF di cavo). Il cavo al jack da 100 pF (la variante c100 di L29d2, «cavo realistico»):
CAVO = {
    "c100": [],
    "c100t1": ["option trtol=1"],
}
import sys
quali = sys.argv[1:] or list(VARIANTI)
for v in quali:
    opz = VARIANTI.get(v, CAVO.get(v))
    d = os.path.join(QUI, v)
    os.makedirs(d, exist_ok=True)
    for c in CORSE:
        r = open(os.path.join(MATRICE, "corsa_%s.cir" % c)).read().splitlines()
        if v in CAVO:
            n = 0
            for i, x in enumerate(r):
                for cc in ("ccavm", "ccav1", "ccav2"):
                    if x == "alter %s = 1e-18" % cc:
                        r[i] = "alter %s = 100p" % cc
                        n += 1
            if n != 3:
                raise SystemExit("%s: %d alter del cavo trovati, attesi 3" % (c, n))
        k = next(i for i, x in enumerate(r) if x.startswith("tran "))
        r[k:k] = ["* L47c2b1 sonda: variante %s (prepara.py)" % v] + opz
        open(os.path.join(d, "corsa_%s.cir" % c), "w").write("\n".join(r) + "\n")
    print(v, ":", ", ".join(CORSE))
