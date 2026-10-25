#!/usr/bin/env python3
"""L57a: il costo di ciascuna protezione - THD (V4) e rumore (E5) - dai deck di dist.py.

THD: le tabelle `fourier` di v(vsn) (il pavimento) e v(fix1), lette come L46a/leggi_four.py
(stessi rifiuti: Error, Transient op started, aborted, too many args, Timestep too small); per caso
THD %, h5+ (radice della somma dei quadrati dalla 5a in su) in dB sotto la fondamentale.
Tetti di V4 (ADR-055): 20 kHz a 0,2 V RMS <= 0,001 %; h5+ <= -140 dB; 20 kHz a 2 V RMS <= 0,01 %.

Rumore: onoise_total su v(aout) 20 Hz - 20 kHz con l'ingresso in corto. Il rumore aggiunto dalla
protezione, sqrt(n^2 - n_senza^2), si porta al jack principale col guadagno peggiore (volume in cima,
+10 dB: x3,152, E2) e si somma in quadratura alla cifra peggiore di E5 (4,577 uV, L44, ADR-057):
una stima per eccesso (la cifra di E5 e' a meta' volume, dove il blocco A e' attenuato), contro
9,95 uV (ADR-020).

Uso: /usr/bin/python3 leggi_costo.py   -> costo/costo.csv
"""
import csv
import math
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(os.path.dirname(QUI), "costo")
RIFIUTI = ("Error", "Transient op started", "aborted", "too many args", "Timestep too small")
E5, E5_TETTO, G_MAX = 4.577, 9.95, 3.152
VARIANTI = ["senza", "r1k_rail", "r2k2_rail", "r4k7_rail", "r10k_rail", "r1k_lim5", "r2k2_lim5", "r4k7_lim5",
            "r1k_z12", "r1k5_z12"]     # le ultime due: la variante di AN-015 (esegui.py costo_an015)


def tabelle(log):
    righe = open(log, errors="replace").read().split("\n")
    for r in righe:
        for x in RIFIUTI:
            if x in r:
                sys.exit("%s: riga rifiutata: %s" % (log, r.strip()))
    casi, cur, nodo = [], None, None
    for r in righe:
        m = re.search(r"L57A_CASO (.*)$", r)
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
            cur["_t"][nodo] = (float(m.group(1)), [], [])
            continue
        m = re.match(r"\s*(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", r)
        if m and nodo and cur is not None and nodo in cur["_t"]:
            t = cur["_t"][nodo]
            if int(m.group(1)) != len(t[1]):
                sys.exit("%s: %s, armonica %s dopo %d righe" % (log, nodo, m.group(1), len(t[1])))
            t[1].append(float(m.group(5)))
            t[2].append(float(m.group(3)))
    for c in casi:
        for nodo, t in c["_t"].items():
            if len(t[1]) < 8:
                sys.exit("%s: %s con %d armoniche" % (log, nodo, len(t[1])))
    return casi


def db(x):
    return 20 * math.log10(x) if x > 0 else -999.0


rum = {}
for v in VARIANTI:
    log = os.path.join(D, "out_rumore_" + v, "rumore_" + v + ".log")
    testo = open(log).read()
    m = re.search(r"onoise_aout_uv=([-+0-9.eE]+)", testo)
    g = re.search(r"L57A_GUADAGNO g=([-+0-9.eE]+)", testo)
    if not m or not g:
        sys.exit("%s: nessun rumore o nessun guadagno" % log)
    # il blocco vivo: 2,5 k di sorgente contro R_SEL || R_IN (320 k), ~0,99. Un punto di lavoro
    # ripiegato su un blocco spento dava 0,00079 (prima corsa di L57a)
    if not 0.95 < float(g.group(1)) < 1.0:
        sys.exit("%s: guadagno del blocco %s, il punto di lavoro non e' quello vivo" % (log, g.group(1)))
    rum[v] = float(m.group(1))

out = []
for v in VARIANTI:
    log = os.path.join(D, "out_thd_" + v, "thd_" + v + ".log")
    casi = tabelle(log)
    if len(casi) != 5:
        sys.exit("%s: %d casi invece di 5" % (log, len(casi)))
    agg = math.sqrt(max(rum[v] ** 2 - rum["senza"] ** 2, 0.0))
    e5 = math.sqrt(E5 ** 2 + (agg * G_MAX) ** 2)
    for c in casi:
        tv, nv, mv = c["_t"]["v(vsn)"]
        to, no, mo = c["_t"]["v(fix1)"]
        if abs(mv[1] / float(c["ampin"]) - 1) > 0.01:
            sys.exit("%s: sorgente %g contro %s" % (log, mv[1], c["ampin"]))
        # la fissa e' a guadagno 1 (meno il partitore 2,5 k / 320 k e i 47 Ohm sui 10 k): un caso
        # con l'uscita lontana dalla sorgente e' un blocco spento, non una distorsione
        if not 0.95 < mo[1] / mv[1] < 1.0:
            sys.exit("%s %s: uscita %g contro sorgente %g" % (log, c, mo[1], mv[1]))
        alte = math.sqrt(sum(x * x for x in no[5:]))
        out.append({"variante": v, "freq": c["freq"], "livello": c["livello"],
                    "vout_pk": "%.4g" % mo[1], "thd_pct": "%.3g" % to, "pavimento_pct": "%.2g" % tv,
                    "h2_db": "%.1f" % db(no[2]), "h3_db": "%.1f" % db(no[3]), "h5su_db": "%.1f" % db(alte),
                    "rumore_aout_uv": "%.4g" % rum[v], "rumore_aggiunto_uv": "%.3g" % agg,
                    "e5_stima_uv": "%.3f" % e5})
p = os.path.join(D, "costo.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
for r in out:
    print("%(variante)-10s %(freq)6s %(livello)-2s thd %(thd_pct)9s %% (pav %(pavimento_pct)7s) h2 %(h2_db)7s h3 %(h3_db)7s h5+ %(h5su_db)7s"
          " | rumore %(rumore_aout_uv)7s uV +%(rumore_aggiunto_uv)6s -> E5 %(e5_stima_uv)s uV" % r)
