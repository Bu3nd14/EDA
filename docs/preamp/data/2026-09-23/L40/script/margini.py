#!/usr/bin/env python3
# L40: copiato da L39/script senza modifiche al codice. Qui prima/ e' il main di
# L39 (C124 470 p, modelli del costruttore), dopo/ e' L40 (C124 1 nF, ADR-042).
"""L39: V1 (ADR-019, >= 60 gradi) prima e dopo, dai margini tabellati dai deck
d'anello. Per ogni tabella e ogni gruppo di celle, il minimo del margine con la
cella che lo da', col criterio di ADR-024: per il blocco B e il buffer conta la
posizione 1 (il cavo al jack), il minimo sul cavo da 1 fF a 4,7 nF; la pos 2 e'
informazione e si stampa a parte.

Uso: /usr/bin/python3 margini.py        -> stampa, e scrive margini.csv accanto a prima/ e dopo/
"""
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = [
    # deck, file, colonne che fanno il gruppo, filtro
    ("tb_loop", "tb_loop_margini.csv", ("mode", "pos"), None),
    ("tb_idss_loop", "tb_idss_loop_margini.csv", ("var", "pos"), None),
    ("tb_loop_blockA", "tb_loop_blockA.csv", ("carico",), None),
    # Verdetto del blocco A (L12): cablaggio fino a 1 nF, non fino a 4,7 nF.
    ("tb_loop_blockA", "tb_loop_blockA.csv", ("carico", "rsrc"),
     lambda r: r["cwire"] in ("1f", "47p", "100p", "220p", "470p", "1n")),
    ("tb_loop_blockA", "tb_loop_blockA_trim.csv", ("cand", "pos"), None),
    ("tb_loop_bufferfissa", "tb_loop_bufferfissa.csv", ("pos",), None),
]


def leggi(fase, deck, f):
    p = os.path.join(BASE, fase, deck, f)
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def minimi(righe, chiavi, filtro=None):
    g = {}
    for r in righe:
        if filtro and not filtro(r):
            continue
        k = tuple(r[c] for c in chiavi)
        pm = float(r["pm_deg"])
        if k not in g or pm < g[k][0]:
            g[k] = (pm, r)
    return g


def main():
    out = []
    for deck, f, chiavi, filtro in TAB:
        a = minimi(leggi("prima", deck, f), chiavi, filtro)
        b = minimi(leggi("dopo", deck, f), chiavi, filtro)
        if filtro:
            f += " (cwire<=1n)"
        for k in sorted(set(a) | set(b)):
            pa, ra = a.get(k, (None, {}))
            pb, rb = b.get(k, (None, {}))
            cella = ",".join("%s=%s" % (c, rb.get(c, "")) for c in rb
                             if c not in chiavi and c not in ("fcross_hz", "pm_deg", "tdb_10hz"))
            v = "" if pb is None else ("OK" if pb >= 60 else "SOTTO 60")
            out.append([deck, f, "/".join(k), pa, pb, (pb - pa) if pa is not None and pb is not None else "",
                        ra.get("tdb_10hz", ""), rb.get("tdb_10hz", ""), cella, v])
    with open(os.path.join(BASE, "margini.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["deck", "tabella", "gruppo", "pm_min_prima", "pm_min_dopo", "delta",
                    "t10hz_prima_db", "t10hz_dopo_db", "cella_del_minimo_dopo", "v1"])
        w.writerows(out)
    for r in out:
        print("%-20s %-26s %-18s %8s %8s %7s  %-6s %-6s %-40s %s" % tuple(
            ("%.2f" % x if isinstance(x, float) else x) for x in r))


if __name__ == "__main__":
    main()
