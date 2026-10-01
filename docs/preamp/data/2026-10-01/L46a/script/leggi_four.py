#!/usr/bin/env python3
"""L46a: legge le tabelle `fourier` dei deck thd_*/imd/arch_* di una o piu' varianti.

Per ogni caso (riga `L46A_CASO ...` del deck) prende la tabella di v(vsn) (la
sorgente ideale: il pavimento numerico della fourier) e quella di v(out).
  THD: THD %, h2..h7 in dB sotto la fondamentale, h5+ (radice della somma dei
       quadrati da h5 in su) in dB, ampiezza d'uscita, pavimento.
  IMD: prodotto a 1 kHz (d2) e il peggiore fra 18 e 21 kHz (d3), in dB contro il
       tono a 20 kHz.
Rifiuta un log con righe `Error`, `Transient op started`, `aborted`, `too many args`
(#26, #33, #35, #36) e un caso senza le due tabelle.

Uso: /usr/bin/python3 leggi_four.py <variante>...  -> run/<variante>/distorsione.csv
"""
import csv
import math
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L46A = os.path.dirname(QUI)
RIFIUTI = ("Error", "Transient op started", "aborted", "too many args", "Timestep too small")


def tabelle(log):
    """[(caso dict, {nodo: (thd, [norm mag per armonica], [mag])})] in ordine."""
    grezze = open(log, errors="replace").read().split("\n")
    for r in grezze:
        for x in RIFIUTI:
            if x in r:
                sys.exit("%s: riga rifiutata: %s" % (log, r.strip()))
    # #37: una Note/Warning del gmin stepping puo' cadere DENTRO una riga della
    # tabella (stderr senza buffer, stdout con). Si ricuce: il pezzo prima della
    # Note + la prima riga dopo che non e' una Note/Warning. Trovato qui su imd.
    righe, k, ricuciture = [], 0, 0
    while k < len(grezze):
        r = grezze[k]
        m = re.match(r"(.*\S)\s*(Note:|Warning:)", r)
        if m and not re.match(r"\s*(Note:|Warning:)", r):
            k += 1
            while k < len(grezze) and re.match(r"\s*(Note:|Warning:)", grezze[k]):
                k += 1
            righe.append(m.group(1) + " " + (grezze[k] if k < len(grezze) else ""))
            ricuciture += 1
        else:
            righe.append(r)
        k += 1
    casi, cur, nodo, thd = [], None, None, None
    for r in righe:
        m = re.search(r"L46A_CASO (.*)$", r)
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
        if m and nodo:
            thd = float(m.group(1))
            if cur is None:          # i deck dell'architetto non hanno L46A_CASO
                cur = {"_t": {}}
                casi.append(cur)
            cur["_t"][nodo] = (thd, [], [])
            continue
        m = re.match(r"\s*(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", r)
        if m and nodo and cur is not None and nodo in cur["_t"]:
            t = cur["_t"][nodo]
            if int(m.group(1)) != len(t[1]):     # un'armonica persa sposterebbe tutte le altre
                sys.exit("%s: %s, armonica %s dopo %d righe" % (log, nodo, m.group(1), len(t[1])))
            t[1].append(float(m.group(5)))
            t[2].append(float(m.group(3)))
    for c in casi:
        for nodo, t in c["_t"].items():
            if len(t[1]) < 8:
                sys.exit("%s: %s con %d armoniche" % (log, nodo, len(t[1])))
    if ricuciture:
        print("  %s: %d righe ricucite (#37)" % (os.path.basename(log), ricuciture))
    return casi


def db(x):
    return 20 * math.log10(x) if x > 0 else float("-inf")


def sorgente(c, misura):
    """La sorgente deve avere l'ampiezza chiesta: una `alter` che non arriva non
    da' errore (#22, #34). Prova che il caso misura il livello dell'etichetta."""
    a = float(c["ampin"])
    if abs(misura / a - 1) > 0.01:
        sys.exit("%s %s: sorgente %.4g V contro %.4g chiesti" % (c["_deck"], c, misura, a))


def riga_thd(c):
    tv, nv, mv = c["_t"]["v(vsn)"]
    to, no, mo = c["_t"]["v(out)"]
    sorgente(c, mv[1])
    alte = math.sqrt(sum(x * x for x in no[5:]))
    r = {"deck": c["_deck"], "modo": c.get("modo", ""), "livello": c.get("livello", ""),
         "freq": c.get("freq", ""), "vout_pk": "%.5g" % mo[1], "thd_pct": "%.4g" % to,
         "pavimento_pct": "%.3g" % tv}
    for h in range(2, 8):
        r["h%d_db" % h] = "%.1f" % db(no[h]) if h < len(no) else ""
    r["h5su_db"] = "%.1f" % db(alte)
    return r


def riga_imd(c):
    to, no, mo = c["_t"]["v(out)"]
    tv, nv, mv = c["_t"]["v(vsn)"]
    sorgente(c, mv[20])
    ref = mo[20]
    return {"deck": c["_deck"], "modo": c.get("modo", ""), "livello": c.get("livello", ""),
            "freq": "ccif", "vout_pk": "%.5g" % ref, "imd_d2_db": "%.1f" % db(mo[1] / ref),
            "imd_d3_db": "%.1f" % db(max(mo[18], mo[21]) / ref),
            "pavimento_d2_db": "%.1f" % db(mv[1] / mv[20])}


COL = ["deck", "modo", "livello", "freq", "vout_pk", "thd_pct", "pavimento_pct",
       "h2_db", "h3_db", "h4_db", "h5_db", "h6_db", "h7_db", "h5su_db",
       "imd_d2_db", "imd_d3_db", "pavimento_d2_db"]

for v in sys.argv[1:]:
    d = os.path.join(L46A, "run", v)
    out = []
    for deck in sorted(os.listdir(d)):
        log = os.path.join(d, deck, deck + ".log")
        if not (deck.startswith(("thd", "imd", "arch")) and os.path.exists(log)):
            continue
        casi = tabelle(log)
        if not casi:
            sys.exit("%s: nessuna tabella" % log)
        for c in casi:
            c["_deck"] = deck
            if "v(out)" not in c["_t"]:
                sys.exit("%s: un caso senza la tabella di v(out)" % log)
            if "imd" in deck:
                if "v(vsn)" not in c["_t"]:      # il deck dell'architetto
                    to, no, mo = c["_t"]["v(out)"]
                    out.append({"deck": deck, "freq": "ccif", "vout_pk": "%.5g" % mo[20],
                                "imd_d2_db": "%.1f" % db(mo[1] / mo[20]),
                                "imd_d3_db": "%.1f" % db(max(mo[18], mo[21]) / mo[20])})
                else:
                    out.append(riga_imd(c))
            elif "v(vsn)" not in c["_t"]:
                to, no, mo = c["_t"]["v(out)"]
                out.append({"deck": deck, "vout_pk": "%.5g" % mo[1], "thd_pct": "%.4g" % to})
            else:
                out.append(riga_thd(c))
    p = os.path.join(d, "distorsione.csv")
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, COL)
        w.writeheader()
        w.writerows(out)
    print("== %s (%d casi) -> %s" % (v, len(out), p))
    for r in out:
        print("  " + " ".join("%s=%s" % (k, r[k]) for k in COL if r.get(k, "") != ""))
