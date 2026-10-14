#!/usr/bin/env python3
"""L45d2b1: le corse senza guasto del blocco - la musica, il filo di un rail aperto, l'accensione -
in una tabella: lo scatto del rivelatore si' / no, quando, e TMAX massimo (il margine: lo scatto e'
a VDP / 2 ~ 7,2 V; il temporizzatore a riposo sta a ~0,3 V). Stdlib.

Uso: riassunto_piccole.py BANCO        scrive BANCO/piccole.csv
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genera_rivelatore as gr  # noqa: E402

# atteso: "no" = non deve scattare; "si" = deve; "-" = si registra (fuori dalla banda, o NC-063)
ATTESO = {"seno_10hz_g10_clip": "-", "seno_16hz_g10_clip": "-",
          "filo_p_g0": "si", "filo_p_g10": "si", "filo_m_g0": "si", "filo_m_g10": "si",
          "prima_il_meno": "-", "partenza_datasheet": "-"}


def main(banco):
    righe = []
    for fam, casi in (("musica", gr.MUSICA_CASI), ("rail", None), ("accensione", gr.ACC_CASI)):
        nomi = list(casi) if casi else ["filo_p_g0", "filo_p_g10", "filo_m_g0", "filo_m_g10"]
        for n in nomi:
            f = os.path.join(banco, "run", n, "rif", "rif_riv.csv")
            d = {}
            if os.path.exists(f):
                for r in csv.DictReader(open(f)):
                    d[r["grandezza"]] = r["valore"]
            t0 = float(d.get("t0") or 0)
            tf = d.get("t_flt") or ""
            att = ATTESO.get(n, "no")
            scatta = bool(tf)
            esito = "-" if att == "-" else ("OK" if (att == "si") == scatta else "SBAGLIATO")
            nota = casi[n][-1] if fam == "musica" else ""
            righe.append({"famiglia": fam, "caso": n, "atteso": att,
                          "scatto_ms": "%.1f" % ((float(tf) - t0) * 1e3) if scatta else "",
                          "tmax_max_V": d.get("tmax_max", ""), "esito": esito, "nota": nota})
    with open(os.path.join(banco, "piccole.csv"), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(righe[0].keys()))
        w.writeheader()
        w.writerows(righe)
    for r in righe:
        print("%-10s %-22s atteso %-2s scatto %8s ms  TMAX %8s V  %s" % (
            r["famiglia"], r["caso"], r["atteso"], r["scatto_ms"] or "-", r["tmax_max_V"], r["esito"]))
    return sum(1 for r in righe if r["esito"] == "SBAGLIATO")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
