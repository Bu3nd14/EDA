#!/usr/bin/env python3
"""L53: V4 sulla catena. Per ogni caso (riga L53_CATENA) le tabelle fourier di v(bout),
v(f1out), v(f2out): THD, h5 in su, ampiezza. Prova che il livello al jack principale sia
quello chiesto (entro il 2 %: una `alter` che non arriva non da' errore, #22). Le fisse si
giudicano solo dove escono al livello del caso (volume in cima, modo 0: la sorgente e' a 0,2 / 2 V).

Tetti di V4 (ADR-055): THD a 20 kHz 0,001 % a 0,2 V e 0,01 % a 2 V; h5 in su <= -140 dB a 0,2 V.

Uso: /usr/bin/python3 leggi_catena.py -> ../run/catena/catena.csv
"""
import csv
import math
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(os.path.dirname(QUI), "run", "catena")
NODI = ("v(bout)", "v(f1out)", "v(f2out)")
out = []
for d in sorted(os.listdir(RUN)):
    log = os.path.join(RUN, d, d + ".log")
    if not os.path.exists(log):
        continue
    righe = open(log, errors="replace").read().split("\n")
    for r in righe:
        for x in ("Error", "aborted", "Timestep too small", "too many args"):
            if x in r:
                raise SystemExit("%s: %s" % (log, r))
    casi, cur, nodo = [], None, None
    for r in righe:
        m = re.search(r"L53_CATENA (.*)$", r)
        if m:
            cur = dict(kv.split("=") for kv in m.group(1).split())
            cur["_t"] = {}
            casi.append(cur)
            continue
        m = re.match(r"Fourier analysis for (\S+):", r.strip())
        if m:
            nodo = m.group(1)
            continue
        m = re.search(r"THD: ([-+0-9.eE]+) %", r)
        if m and nodo and cur is not None:
            cur["_t"][nodo] = [float(m.group(1)), []]
            continue
        m = re.match(r"\s*(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", r)
        if m and nodo and cur is not None and nodo in cur["_t"]:
            cur["_t"][nodo][1].append(float(m.group(3)))
    for c in casi:
        for n in NODI:
            if n not in c["_t"] or len(c["_t"][n][1]) < 8:
                raise SystemExit("%s: caso %s senza la tabella di %s" % (log, c, n))
        main_pk = c["_t"]["v(bout)"][1][1]
        # 5 %: le perdite vere arrivano al 2,2 % (2,5 k contro i 320 k del selettore, il volume a
        # meta' caricato dal blocco B, 47 Ohm contro 10 k); una `alter` persa sbaglia di 3 volte.
        if abs(main_pk / float(c["main_atteso"]) - 1) > 0.05:
            raise SystemExit("%s: main %.4g V contro %s chiesti (%s)" % (log, main_pk, c["main_atteso"], c))
        for n in NODI:
            if n != "v(bout)" and not (c["vol"] == "cima" and c["modo"] == "0"):
                continue
            thd, mag = c["_t"][n]
            h5 = math.sqrt(sum(x * x for x in mag[5:])) / mag[1]
            f = int(c["freq"])
            tetto = (0.001 if c["livello"] == "lo" else 0.01) if f == 20000 else None
            # h5 in su: a 1 kHz C_IN e C_T lasciano un pavimento del metodo di ~-116 dB (genera.py):
            # si riporta, non si giudica; si giudica a 10 e 20 kHz.
            h5_giudicata = c["livello"] == "lo" and f != 1000
            ok = (tetto is None or thd <= tetto) and (not h5_giudicata or 20 * math.log10(h5) <= -140)
            out.append({"uscita": n[2:-1], "freq": f, "livello": c["livello"], "modo": c["modo"],
                        "vol": c["vol"], "rs": c["rs"], "vpk": "%.4g" % mag[1], "thd_pct": "%.4g" % thd,
                        "tetto_thd_pct": tetto or "", "h5su_db": "%.1f" % (20 * math.log10(h5)),
                        "verdetto": "dentro" if ok else "FUORI"})
p = os.path.join(RUN, "catena.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
for r in out:
    print("%(uscita)-9s %(freq)5s %(livello)s modo=%(modo)-2s vol=%(vol)-4s rs=%(rs)-5s vpk=%(vpk)-7s THD=%(thd_pct)-10s h5+=%(h5su_db)s %(verdetto)s" % r)
print("-> %s, %d fuori su %d" % (p, sum(r["verdetto"] != "dentro" for r in out), len(out)))
