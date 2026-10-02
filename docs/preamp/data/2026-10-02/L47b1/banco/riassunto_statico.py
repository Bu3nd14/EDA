"""riassunto_statico.py - L47b1: le due celle a confronto dalle tabelle di statico.py.

Per ogni combinazione (angoli del JFET x correttivo; curve della NSL-32SR3):
  - in gioco (d = 0): la perdita d'inserzione e la THD a 1 e 20 kHz;
  - in mute (d = 1): |H| a 20 Hz, 1 kHz, 20 kHz, e B al jack principale = 3,818 V x 3,15 x |H|max,
    in uV e in dB SPL di picco a 1 m (100 uV = 33 dB SPL);
  - E3: |Zin| minimo su 20 Hz-20 kHz in gioco, in mute, e il minimo su tutta la sfumatura;
  - la THD massima lungo la sfumatura finche' il livello e' sopra -60 dB (sotto e' inudibile
    nella scala di S);
  - il comando: |H| dal comando ad AIN, il massimo sulla sfumatura (solo JFET).

    /usr/bin/python3 riassunto_statico.py
"""
import csv
import os

from comune import A_PIENO, G_JACK, QUI, spl

for cella in ("jfet", "ldr", "ldr_cima12"):
    if not os.path.exists(os.path.join(QUI, "tabelle", "statico_%s.csv" % cella)):
        continue
    rows = list(csv.DictReader(open(os.path.join(QUI, "tabelle", "statico_%s.csv" % cella))))
    combos = []
    for r in rows:
        if r["combo"] not in combos:
            combos.append(r["combo"])
    print("=" * 8, cella)
    for c in combos:
        sel = [r for r in rows if r["combo"] == c]
        p, m = sel[0], sel[-1]
        hm = max(float(m["h20"]), float(m["h1k"]), float(m["h20k"]))
        b = A_PIENO * G_JACK * hm
        zmin = min(float(r["zmin_ohm"]) for r in sel)
        if cella.startswith("jfet"):
            fade = [float(r["thd1000_pct"]) for r in sel if float(r["liv1000_db"]) > -60]
            thd = "play THD 1k %.3g%% 20k %.3g%% | fade THD max %.3g%%" % (
                float(p["thd1000_pct"]), float(p["thd20000_pct"]), max(fade))
            cmd = max(max(float(r["cvcs1k"]), float(r["cvcp1k"]), float(r["cvcs20k"]),
                          float(r["cvcp20k"])) for r in sel)
            thd += " | comando->AIN max %.3g" % cmd
        else:
            thd = "THD non modellata | log10 R in mute: serie %s, deriv %s" % (
                m.get("xls_log10r"), m.get("xlp_log10r"))
        print("%-16s play %+.3f dB | mute |H| 20 %.2g 1k %.2g 20k %.2g -> B %.3g uV = %.1f dB SPL"
              " | Zin play %.3g mute %.3g min %.3g | %s" % (
                  c, float(p["liv1000_db"]), float(m["h20"]), float(m["h1k"]), float(m["h20k"]),
                  b * 1e6, spl(b), float(p["zmin_ohm"]), float(m["zmin_ohm"]), zmin, thd))
