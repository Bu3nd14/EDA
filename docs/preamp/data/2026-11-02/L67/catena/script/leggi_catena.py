#!/usr/bin/env python3
"""L67 (NC-055): legge la catena di un blocco. Copiato da L56/catena/script/leggi_catena.py; il
giudizio e' INVARIATO (tetti di V4, ADR-055: THD a 20 kHz 0,001 % a 0,2 V e 0,01 % a 2 V; h5 in
su <= -140 dB a 0,2 V, giudicata a 10 e 20 kHz). In piu':
  - il blocco come argomento, run/<blocco>/ -> ../../catena_<blocco>.csv (la radice del lotto);
  - colonne `griglia` (l56 = le posizioni del volume di L56, cima e meta; volbasso = m10, m20),
    `livello_A_V` (la tensione RMS all'uscita del blocco A, quella che il volume poi attenua) e
    `margine_dB` (20 log10(tetto / THD); negativo = fuori).
Prova che il livello al jack principale sia quello chiesto (5 %: una `alter` persa non da' errore,
#22) e rifiuta i log con errori.

Uso: /usr/bin/python3 -I leggi_catena.py <blocco>...
"""
import csv
import math
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
LOTTO = os.path.dirname(BASE)
NODI = ("v(bout)", "v(f1out)", "v(f2out)")
MODI_G = {"0": 1.0, "3": 1.4202, "10": 3.1523}


def leggi(blocco):
    run = os.path.join(BASE, "run", blocco)
    out = []
    nomi = sorted(d for d in os.listdir(run) if os.path.isdir(os.path.join(run, d)))
    if len([n for n in nomi if not n.endswith("_vb")]) != 6:
        raise SystemExit("%s: %d corse della griglia di L56 invece di 6" % (run, len(nomi)))
    for d in nomi:
        log = os.path.join(run, d, d + ".log")
        if not os.path.exists(log):
            raise SystemExit("manca %s" % log)
        righe = open(log, errors="replace").read().split("\n")
        for r in righe:
            for x in ("Error", "aborted", "Timestep too small", "too many args"):
                if x in r:
                    raise SystemExit("%s: %s" % (log, r))
        casi, cur, nodo, op_fallito = [], None, None, False
        for r in righe:
            # limitations #57: un op non convergente (anche «source stepping failed») ngspice lo usa
            # lo stesso. La corsa sta PRIMA dell'echo del suo caso: il segno vale per l'echo che segue.
            if "source stepping failed" in r:
                op_fallito = True
            m = re.search(r"L53_CATENA (.*)$", r)
            if m:
                cur = dict(kv.split("=") for kv in m.group(1).split())
                cur["_t"] = {}
                if op_fallito:
                    raise SystemExit("%s: op non convergente nel caso %s (#57)" % (log, m.group(1)))
                op_fallito = False
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
            if abs(main_pk / float(c["main_atteso"]) - 1) > 0.05:
                raise SystemExit("%s: main %.4g V contro %s chiesti (%s)" % (log, main_pk, c["main_atteso"], c))
            # il blocco A e' sempre a guadagno unitario (il modo agisce sul blocco B): il suo livello
            # e' quello della sorgente (meno il partitore del selettore, < 1 %)
            livA = float(c["ampin"]) / 2 ** 0.5
            for n in NODI:
                if n != "v(bout)" and not (c["vol"] == "cima" and c["modo"] == "0"):
                    continue
                thd, mag = c["_t"][n]
                h5 = math.sqrt(sum(x * x for x in mag[5:])) / mag[1]
                f = int(c["freq"])
                tetto = (0.001 if c["livello"] == "lo" else 0.01) if f == 20000 else None
                h5_giudicata = c["livello"] == "lo" and f != 1000
                ok = (tetto is None or thd <= tetto) and (not h5_giudicata or 20 * math.log10(h5) <= -140)
                out.append({"blocco": blocco,
                            "griglia": "l56" if c["vol"] in ("cima", "meta") else "volbasso",
                            "uscita": n[2:-1], "freq": f, "livello": c["livello"], "modo": c["modo"],
                            "vol": c["vol"], "rs": c["rs"], "livello_A_V": "%.3g" % livA,
                            "vpk": "%.4g" % mag[1], "thd_pct": "%.4g" % thd,
                            "tetto_thd_pct": tetto or "",
                            "margine_dB": "%.1f" % (20 * math.log10(tetto / thd)) if tetto else "",
                            "h5su_db": "%.1f" % (20 * math.log10(h5)),
                            "verdetto": "dentro" if ok else "FUORI"})
    return out


for blocco in sys.argv[1:]:
    out = leggi(blocco)
    p = os.path.join(LOTTO, "catena_%s.csv" % blocco)
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, list(out[0]))
        w.writeheader()
        w.writerows(out)
    for g in ("l56", "volbasso"):
        rr = [r for r in out if r["griglia"] == g]
        fuori = [r for r in rr if r["verdetto"] != "dentro"]
        print("%-17s %-8s %2d fuori su %2d" % (blocco, g, len(fuori), len(rr)))
        for r in fuori:
            print("    %(uscita)-6s %(freq)5s %(livello)s modo=%(modo)-2s vol=%(vol)-4s rs=%(rs)-5s A=%(livello_A_V)s V "
                  "THD=%(thd_pct)-9s margine=%(margine_dB)s dB h5+=%(h5su_db)s" % r)
    print("-> %s" % p)
