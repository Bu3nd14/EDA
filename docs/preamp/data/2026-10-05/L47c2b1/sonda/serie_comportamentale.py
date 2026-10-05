"""serie_comportamentale.py - L47c2b1, quarta prova della sonda: il contatto IN SERIE al jack
portato dal contatto comportamentale del blocco CANALE (BSERx: conduttanza
pow(10, -12 + 13*(1 - SSER)), SSER dai rimbalzi di L29c filtrati da 1 k + 4,55 nF: un fronte di
~4,55 us invece dell'interruttore ideale), al posto dell'interruttore nativo SKSx, che resta
APERTO per tutta la corsa. La derivazione lato condensatore resta l'interruttore nativo SKCx.
Variante «bser».

Perche': le prove t1, t1r, gear, c100 e nb (README della sonda) mostrano che la corsa si ferma
ogni volta che l'interruttore nativo in serie CHIUDE con volt di musica fra i suoi capi (il
rimbalzo dell'apertura a +400 us; la chiusura del rilascio).

Gli istanti si leggono dalla corsa stessa (gli alter vksa / vksb di geo_alter): la serie si apre a
vksa e si richiude a vksb. Gli alter nuovi vanno DOPO quelli di geo_alter, prima della `tran`.

    /usr/bin/python3 serie_comportamentale.py
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
MATRICE = os.path.join(QUI, "..", "matrice_interruttore")
d = os.path.join(QUI, "bser")
os.makedirs(d, exist_ok=True)
for c in ("mev_20_iii", "mev_1k_iii", "mev_lz_iii"):
    r = open(os.path.join(MATRICE, "corsa_%s.cir" % c)).read().splitlines()
    ksa = [x for x in r if x.startswith("alter vksa dc = ")]
    ksb = [x for x in r if x.startswith("alter vksb dc = ")]
    if len(ksa) != 1 or len(ksb) != 1:
        raise SystemExit("%s: attesi un alter vksa e un vksb" % c)
    ta, tb = ksa[0].split()[-1], ksb[0].split()[-1]
    k = next(i for i, x in enumerate(r) if x.startswith("tran "))
    r[k:k] = ["* L47c2b1 sonda bser: la serie dal contatto comportamentale del blocco (BSERx)",
              "alter vtiser dc = %s" % ta, "alter vtrser dc = %s" % tb,
              "alter vksa dc = -10", "alter vksb dc = 1000"]
    open(os.path.join(d, "corsa_%s.cir" % c), "w").write("\n".join(r) + "\n")
    print("bser: %s, serie aperta a %s, richiusa a %s" % (c, ta, tb))
