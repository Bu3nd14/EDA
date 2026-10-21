#!/usr/bin/env python3
"""L45d2b2b2: ADR-075's rows against the parts' limits, from analizza_075.py's CSV. Solo stdlib.

    riassunto_075.py <analisi.csv> [<out.csv>]

For each case, the parts its fault stresses (PARTI_RIGA), each with:
    ipk_A, ppk_W, p10_W, p100_W, pfin_W (the last 50 ms: what stays), e_J
    pamm_W   the power the part takes continuously with 60 C of air, (Tj max - 60) / Rth(j-a), from
             limiti_parti.csv (the datasheets read in this lot)
    tj100_C  60 + p100_W x Rth(j-a): a CEILING for the worst 100 ms (the steady Rth on a 100 ms mean;
             the transient Zth of 100 ms is lower)
    tjfin_C  60 + pfin_W x Rth(j-a): what stays at the end of the run
    esito    "fuori" if tjfin_C or tj100_C exceed Tj max, or ipk_A exceeds the part's peak current
             (IDM, ICM, the LM4040's 20 mA), "dentro" otherwise
and v5_max against the ATtiny3216's 6.0 V.
"""
import csv
import sys

# part: (Tj max C, Rth(j-a) K/W, peak current A or None, the name) - limiti_parti.csv
LIM = {"q501": (150, 350, 1.2, "2N7002"), "q502": (150, 350, 1.2, "2N7002"),
       "q503": (150, 350, 1.2, "2N7002"), "q505": (150, 125, 27.0, "AO3401A"),
       "d507": (175, 300, None, "BZX55C24 in diretta"), "d509": (175, 300, None, "BZX55C24 in diretta"),
       "u507": (125, 292, 0.020, "LM4040A-2.5"), "q504": (150, 500, 0.200, "BC847"),
       "u503": (125, 32.5, None, "TPS7A4701"), "u504": (125, 62, None, "MCP1703A"),
       # --rk: a 2 W axial as R550 (ADR-092), 2 W at 70 C derated to 0 at 155 C: 42.5 K/W (declared)
       "rk": (155, 42.5, None, "47 ohm, 2 W"), "u512": (125, 62, None, "MCP1703A")}
PARTI_RIGA = {"f_d506": ("q501", "q505", "d507", "u503"), "f_d508": ("q502", "q505", "d509", "u503"),
              "f_d505": ("q503", "rk", "u503"), "f_k501": ("q503", "rk", "u503"), "f_r503": ("u507", "u504"), "f_r510": ("q504",),
              "f_r512": ("q504", "u504"), "f_u504": ("u504", "u512", "u503"),
              # the source after ADR-094: the second half of each doubled part, and U512
              "f_d530": ("q501", "q505", "d507", "u503"), "f_d531": ("q502", "q505", "d509", "u503"),
              "f_d532": ("q503", "rk", "u503"), "f_r553": ("u507", "u504", "u512"), "f_r554": ("q504",),
              "f_r555": ("q504", "u504", "u512"), "f_u512": ("u504", "u512", "u503")}
# limiti_parti.csv: the 2N7002's 1.2 A is for tp <= 10 us; the BC847's 200 mA for <= 1 ms


def f(x):
    return float(x) if x not in ("", None) else 0.0


def main():
    # L45d2b2b2: an option's replaced parts, "mos=Q501:DMN6075S,Q503:DMN6075S" as the last argument:
    # DMN6075S (Diodes Rev 7-2 2025): Tj 150 C, 157 K/W (minimum pad), IDM 12 A (limiti_parti.csv)
    for a in sys.argv[2:]:
        if a.startswith("mos="):
            sys.argv.remove(a)
            for x in a[4:].split(","):
                r, p = x.split(":")
                assert p == "DMN6075S", p
                LIM[r.lower()] = (150, 157, 12.0, "DMN6075S")
    righe = list(csv.DictReader(open(sys.argv[1])))
    out = []
    for r in righe:
        base = "_".join(r["caso"].split("_")[:2])
        for p in [x for x in PARTI_RIGA[base] if r.get(x + "_ipk_A") not in ("", None)]:
            tjm, rth, ipk_lim, nome = LIM[p]
            pamm = (tjm - 60.0) / rth
            ipk, p100, pfin = f(r.get(p + "_ipk_A")), f(r.get(p + "_p100_W")), f(r.get(p + "_pfin_W"))
            tj100, tjfin = 60 + p100 * rth, 60 + pfin * rth
            fuori = tj100 > tjm or tjfin > tjm or (ipk_lim is not None and ipk > ipk_lim)
            out.append({"caso": r["caso"], "parte": "%s (%s)" % (p.upper(), nome), "ipk_A": ipk,
                        "ppk_W": f(r.get(p + "_ppk_W")), "p10_W": f(r.get(p + "_p10_W")), "p100_W": p100,
                        "pfin_W": pfin, "e_J": f(r.get(p + "_e_J")), "pamm_W": pamm, "tj100_C": tj100,
                        "tjfin_C": tjfin, "esito": "fuori" if fuori else "dentro"})
        out.append({"caso": r["caso"], "parte": "V5 (ATtiny3216, 6,0 V)", "ipk_A": "", "ppk_W": "",
                    "p10_W": "", "p100_W": "", "pfin_W": "", "e_J": "", "pamm_W": "",
                    "tj100_C": "v5_max %.3f" % f(r["v5_max"]), "tjfin_C": "v5_min %.3f" % f(r["v5_min"]),
                    "esito": "fuori" if f(r["v5_max"]) > 6.0 else "dentro"})
    campi = list(out[0])
    print("%-24s %-28s %8s %8s %8s %8s %8s %8s %7s %8s %8s %s" % tuple(campi))
    for x in out:
        print("%-24s %-28s %8s %8s %8s %8s %8s %8s %7s %8s %8s %s" % tuple(
            ("%.3g" % v if isinstance(v, float) else v) for v in x.values()))
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", newline="") as fo:
            w = csv.DictWriter(fo, fieldnames=campi)
            w.writeheader()
            for x in out:
                w.writerow({a: ("%.4g" % b if isinstance(b, float) else b) for a, b in x.items()})


main()
