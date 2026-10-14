#!/usr/bin/env python3
"""L45d2b1: la sintesi dei guasti del blocco col rivelatore vero (ADR-072, P10). Stdlib.

Uso: sintesi_guasti.py BANCO

Legge ../analisi_<variante>.csv (analizza_guasti.sh: P10 di L45b, invariato) e, per ogni corsa,
run/<variante>/<modo>/<modo>_riv.csv (t_flt, t_mute dal deck). Il confronto e' con la stessa
variante di L45b SENZA rivelatore (2026-10-13/L45b/analisi_vuoto_<pos>.csv), modo per modo.

Scrive BANCO/guasti.csv (una riga per corsa) e BANCO/guasti.md (la tabella per posizione e i casi
da leggere: P10 fuori col rivelatore, oppure nessuno scatto con P10 fuori senza rivelatore).
"""
import csv
import os
import sys

VARIANTI = (("riv_A", "A", "vuoto_A"), ("riv_F1", "F1", "vuoto_F1"), ("riv_F2", "F2", "vuoto_F2"),
            ("riv_B", "B", "vuoto_B"), ("riv_B_g10", "B a +10 dB", "vuoto_B_g10"),
            ("riv_B_cc", "B, C d'uscita in corto", None), ("riv_F1_cc", "F1, C d'uscita in corto", None))
T_F = 0.3


def leggi_riv(path):
    d = {}
    if not os.path.exists(path):
        return None
    for r in csv.DictReader(open(path)):
        try:
            d[r["grandezza"]] = float(r["valore"])
        except ValueError:
            d[r["grandezza"]] = None
    return d


def stato_vero(log, stato):
    """analizza_p10.py marca «LOG: ...rror» ogni log con un errore. Qui un errore e' anche la misura
    dello scatto che non trova l'istante (DC_FLT non scende: il rivelatore non scatta), e quella
    non e' un difetto della corsa. Si tengono solo gli altri; uno «stato» che non viene dal log
    (CORSA CORTA, MANCA .dat) resta com'e'."""
    if not stato.startswith("LOG:"):
        return stato
    if not os.path.exists(log):
        return stato
    veri = [x for x in open(log, errors="replace")
            if ("rror" in x or "too small" in x or "ransient op" in x)
            and "measure" not in x and "no such variable" not in x]
    return "ok" if not veri else "LOG: " + veri[0].strip()[:60]


def main(banco):
    data = os.path.abspath(os.path.join(banco, "..", "..", ".."))
    l45b = os.path.join(data, "2026-10-13", "L45b")
    righe = []
    for var, nome, base in VARIANTI:
        f = os.path.join(banco, "analisi_%s.csv" % var)
        if not os.path.exists(f):
            print("manca %s" % f)
            continue
        prima = {}
        if base:
            for r in csv.DictReader(open(os.path.join(l45b, "analisi_%s.csv" % base))):
                prima[r["modo"]] = r
        # la corsa di ogni modo: quella della variante, o (se c'e') quella rifatta fino a 0,6 s
        # (_corta, come i tr_corta_* di L45a) o col metodo gear (_gear, come L45b), nell'ordine
        corse = {}
        for suff in ("", "_corta", "_gear", "_corta_gear", "_gear_rshunt", "_rshunt"):
            g = os.path.join(banco, "analisi_%s%s.csv" % (var, suff))
            if os.path.exists(g):
                for r in csv.DictReader(open(g)):
                    corse[r["modo"]] = (var + suff, r)
        for modo, (v_eff, r) in sorted(corse.items()):
            riv = leggi_riv(os.path.join(banco, "run", v_eff, modo, modo + "_riv.csv")) or {}
            tf = riv.get("t_flt")
            tm = riv.get("t_mute")
            p = prima.get(modo, {})
            righe.append({
                "variante": var, "corsa": v_eff, "posizione": nome, "modo": modo,
                "stato": stato_vero(os.path.join(banco, "run", v_eff, modo, modo + ".log"),
                                    r.get("stato", "")),
                "scatto_ms": "" if tf is None else "%.1f" % ((tf - T_F) * 1e3),
                "mute_ms": "" if tm is None else "%.1f" % ((tm - T_F) * 1e3),
                "p10_sopra_ms": r["p10_sopra_ms_max"], "p10": r["p10"],
                "uscita_fine_V": r.get("out_avg", ""),
                "prima_p10_sopra_ms": p.get("p10_sopra_ms_max", ""), "prima_p10": p.get("p10", ""),
            })
    out = os.path.join(banco, "guasti.csv")
    with open(out, "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(righe[0].keys()))
        w.writeheader()
        w.writerows(righe)

    md = ["# I guasti del blocco col rivelatore vero (L45d2b1, ADR-072)", "",
          "Generato da `script/sintesi_guasti.py`. **P10**: tempo con |v(jack)| > 0,87 V, a vuoto, "
          "senza filtro, sul peggiore dei tre jack (`L45b/script/analizza_p10.py`, invariato). "
          "«Prima» e' la stessa corsa di L45b senza rivelatore. Il guasto entra a 0,3 s; lo scatto "
          "e' DC_FLT sotto 2,5 V, il mute il contatto staccato (3 ms di rilascio del G6K).", "",
          "| Posizione | Corse | P10 fuori prima | P10 fuori ora | Scattati | Scatto (min / mediana / max, ms) | Mute max (ms) | P10 max ora (ms) |",
          "|---|---|---|---|---|---|---|---|"]
    da_leggere = []
    for var, nome, _ in VARIANTI:
        rr = [r for r in righe if r["variante"] == var and r["modo"] != "rif"]
        if not rr:
            continue
        sc = sorted(float(r["scatto_ms"]) for r in rr if r["scatto_ms"])
        mu = [float(r["mute_ms"]) for r in rr if r["mute_ms"]]
        p10 = [float(r["p10_sopra_ms"]) for r in rr if r["p10_sopra_ms"]]
        fp = sum(1 for r in rr if r["prima_p10"].startswith("FUORI"))
        fo = sum(1 for r in rr if r["p10"].startswith("FUORI"))
        md.append("| %s | %d | %s | **%d** | %d | %s | %s | %.1f |" % (
            nome, len(rr), fp if any(r["prima_p10"] for r in rr) else "—", fo, len(sc),
            "%.1f / %.1f / %.1f" % (sc[0], sc[len(sc) // 2], sc[-1]) if sc else "—",
            "%.1f" % max(mu) if mu else "—", max(p10) if p10 else 0.0))
        for r in rr:
            if r["p10"].startswith("FUORI") or (not r["scatto_ms"] and r["prima_p10"].startswith("FUORI")) or r["stato"] != "ok":
                da_leggere.append(r)
    md += ["", "## Le corse da leggere", "",
           "P10 fuori col rivelatore, o nessuno scatto dove senza rivelatore P10 era fuori, o una "
           "corsa non finita.", ""]
    if da_leggere:
        md += ["| Variante | Modo | Stato | Scatto (ms) | P10 ora (ms) | P10 prima (ms) | Uscita alla fine (V) |",
               "|---|---|---|---|---|---|---|"]
        for r in da_leggere:
            md.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                r["variante"], r["modo"], r["stato"], r["scatto_ms"] or "—", r["p10_sopra_ms"],
                r["prima_p10_sopra_ms"] or "—", r["uscita_fine_V"]))
    else:
        md.append("Nessuna.")
    open(os.path.join(banco, "guasti.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main(sys.argv[1])
