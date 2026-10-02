"""modelli.py - L47b1: scrive inc/jfet_angoli.lib e lo verifica con una sonda (limitations #29).

Per ogni angolo, e per la scheda originale del costruttore:
  - IDSS a VDS = 15 V, VGS = 0 (datasheet: >= 5 mA);
  - rDS(on) a VDS = 10 mV, VGS = 0 (datasheet <= 50 ohm; il modello 59,5 ohm, dichiarato);
  - la corrente a VGS = VTO - 0,1 V e VDS = 5 V (deve essere ~0: il modello non ha sottosoglia).
La copia TIP deve ridare la scheda originale cella per cella (la prova che rinominare non cambia
niente). Esce 1 se un controllo fallisce.

    /usr/bin/python3 modelli.py
"""
import os
import sys

from comune import ANGOLI, JFET_LIB, K_RON, QUI, corri, guardia, scrivi_angoli, valori

scrivi_angoli()
os.makedirs(os.path.join(QUI, "run", "modelli"), exist_ok=True)
deck = os.path.join(QUI, "run", "modelli", "sonda_angoli.cir")
mod = [("ORIG", "MMBFJ112")] + [(n, "MMBFJ112_%s" % n) for n in ANGOLI]
r = ["sonda_angoli - L47b1: IDSS, rDS(on) e spegnimento di ogni angolo del MMBFJ112",
     ".include %s" % JFET_LIB, ".include %s" % os.path.join(QUI, "inc", "jfet_angoli.lib"),
     ".options reltol=1e-6 vntol=1e-6 abstol=1e-12"]
for n, m in mod:
    vto = -1.68 if n == "ORIG" else ANGOLI[n][0]
    r += ["VI%s DI%s 0 DC 15" % (n, n), "JI%s DI%s 0 0 %s" % (n, n, m),
          "VR%s DR%s 0 DC 10m" % (n, n), "JR%s DR%s 0 0 %s" % (n, n, m),
          "VO%s DO%s 0 DC 5" % (n, n), "VG%s GO%s 0 DC %.4f" % (n, n, vto - 0.1),
          "JO%s DO%s GO%s 0 %s" % (n, n, n, m)]
r += [".control", "op"]
for n, _ in mod:
    r += ["let idss_%s = -i(vi%s)" % (n.lower(), n.lower()),
          "let ron_%s = 0.01 / (-i(vr%s))" % (n.lower(), n.lower()),
          "let ioff_%s = -i(vo%s)" % (n.lower(), n.lower()),
          "print idss_%s ron_%s ioff_%s" % (n.lower(), n.lower(), n.lower())]
r += ["showmod ji%s : vto beta" % n.lower() for n, _ in mod]
r += [".endc", ".end"]
open(deck, "w").write("\n".join(r) + "\n")
rc, log = corri(deck)
cattive = guardia(log)
nomi = {"%s_%s" % (g, n.lower()) for g in ("idss", "ron", "ioff") for n, _ in mod}
v = valori(log, nomi)
ok = True


def controlla(cond, testo):
    global ok
    print(("OK    " if cond else "FALLITO ") + testo)
    ok = ok and cond


controlla(rc == 0 and not cattive, "ngspice rc=%d, righe rifiutate %d %s" % (rc, len(cattive), cattive[:3]))
controlla(len(v) == len(nomi), "letti %d valori su %d" % (len(v), len(nomi)))
if len(v) == len(nomi):
    for n, _ in mod:
        vto, beta = (-1.68, 5.002e-3) if n == "ORIG" else ANGOLI[n]
        idss, ron, ioff = v["idss_" + n.lower()], v["ron_" + n.lower()], v["ioff_" + n.lower()]
        # IDSS di modello: BETA VTO^2 (1 + LAMBDA 15)
        atteso = beta * vto ** 2 * (1 + 0.00398 * 15)
        print("  %-4s VTO %+.2f  IDSS %.3f mA (atteso %.3f)  rDS(on) %.2f ohm  I a VTO-0,1 V %.3g A"
              % (n, vto, idss * 1e3, atteso * 1e3, ron, ioff))
        controlla(abs(idss / atteso - 1) < 0.01, "%s IDSS entro 1 %% del valore dichiarato" % n)
        controlla(idss >= 5e-3, "%s IDSS >= 5 mA (datasheet)" % n)
        controlla(abs(ron - (1 / K_RON + 0.0668)) < 1.5, "%s rDS(on) ~ 59,5 ohm (+ RD + RS)" % n)
        controlla(abs(ioff) < 1e-9, "%s spento a VTO - 0,1 V (< 1 nA, datasheet ID(off))" % n)
    for g in ("idss", "ron", "ioff"):
        a, b = v["%s_orig" % g], v["%s_tip" % g]
        controlla(abs(a - b) <= 1e-9 * max(abs(a), 1e-12) + 1e-18,
                  "TIP = scheda originale su %s (%.9g contro %.9g)" % (g, b, a))
print("ESITO:", "tutti i controlli passati" if ok else "FALLITO")
sys.exit(0 if ok else 1)
