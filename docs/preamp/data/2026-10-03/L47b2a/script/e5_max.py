"""L47b2a: E5 massimo (uV) per caso della cella in serie, in uno o piu' tb_e3_e5_ldr_e5.csv.

Usage: python3 e5_max.py <e5.csv> [...]
ngspice scrive le etichette in minuscolo (curvab, curvace, curvad).
Il requisito e' E5 <= 9,90 uV (tb_trim.cir, ADR-020, ADR-022).
"""
import csv
import sys

for path in sys.argv[1:]:
    rows = list(csv.DictReader(open(path)))
    print(path)
    for ldr in dict.fromkeys(r["ldr"] for r in rows):
        sel = [r for r in rows if r["ldr"] == ldr]
        worst = max(sel, key=lambda r: float(r["onoise_uv"]))
        print("  %-8s rs=%-6s max %.3f uV (pos %s, modo %s, att %s, rsrc %s)" % (
            ldr, worst["rs_ohm"], float(worst["onoise_uv"]), worst["pos"],
            worst["mode"], worst["att"], worst["rsrc"]))
