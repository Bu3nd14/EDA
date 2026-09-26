#!/usr/bin/env python3
"""L41b2 (ADR-050): E3 and E5 again with the LDR top at 12 mA instead of 20 mA.

Solo stdlib. /usr/bin/python3 copia_12mA.py
Copies spice/preamp/tb/tb_e3_e5_ldr.cir (L29b2, which stays as it is) to
tb_e3_e5_ldr_cima12mA.cir next to this file, changing only:
  - the LED currents 20 mA -> 12 mA (the series in play, the shunt in mute);
  - E5's series resistors, read off models/optocoupler/vtl5c4_comportamentale.lib
    at 12 mA by the same log-log interpolation the model does:
      curve B: 88.3 -> 113.5 ohm;  curve D: 118 -> 163.7 ohm.
Every substitution is asserted to hit exactly the lines it means.
"""
import math
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
SRC = os.path.join(REPO, "spice", "preamp", "tb", "tb_e3_e5_ldr.cir")
LIB = os.path.join(REPO, "models", "optocoupler", "vtl5c4_comportamentale.lib")


def r_at(curve, i_ma):
    txt = open(LIB).read()
    blk = txt.split(".subckt VTL5C4_%s " % curve)[1].split(".ends")[0]
    m = re.search(r"BXT xt 0 V = pwl\(log10\(max\(abs\(i\(VSEN\)\)\*1000, 1e-9\)\), ([^)]*)\)", blk)
    v = [float(x) for x in m.group(1).split(",")]
    pts = list(zip(v[0::2], v[1::2]))
    x = math.log10(i_ma)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return 10 ** (y0 + (x - x0) / (x1 - x0) * (y1 - y0))
    raise SystemExit("fuori tabella")


rb20, rd20 = r_at("B", 20), r_at("D", 20)
rb12, rd12 = r_at("B", 12), r_at("D", 12)
print("curva B: %.1f ohm a 20 mA, %.1f a 12 mA; curva D: %.1f a 20 mA, %.1f a 12 mA" % (rb20, rb12, rd20, rd12))
assert abs(rb20 - 88.3) < 0.2 and abs(rd20 - 118) < 0.5, "il modello non e' quello di L29b2"

s = open(SRC).read()
subs = [
    ("tb_e3_e5_ldr.cir - L29b2:", "tb_e3_e5_ldr_cima12mA.cir - L41b2 (ADR-050, cima 12 mA), copia di L29b2:", 1),
    ("ILS  0 ALS DC 20m", "ILS  0 ALS DC 12m", 1),
    ("    alter ils dc = 20m", "    alter ils dc = 12m", 1),
    ("    alter ilp dc = 20m", "    alter ilp dc = 12m", 1),
    ("alter ils dc = 20m", "alter ils dc = 12m", 2),     # after the E3 loop and before the coupling
    ('echo "punto di lavoro: serie curva B a 20 mA = $&rsb ohm (atteso 88,3 dalla tabella)"',
     'echo "punto di lavoro: serie curva B a 12 mA = $&rsb ohm (atteso %.1f dalla tabella)"' % rb12, 1),
    ('    set rsl = "88.3"', '    set rsl = "%.1f"' % rb12, 1),
    ('    set rsl = "118"', '    set rsl = "%.1f"' % rd12, 1),
]
for a, b, n in subs:
    c = s.count(a)
    assert c == n, (a, c)
    s = s.replace(a, b)
assert "20m" not in re.sub(r"^\*.*$", "", s, flags=re.M), "e' rimasto un 20m fuori dai commenti"
for tab in ("tb_e3_e5_ldr_e3.csv", "tb_e3_e5_ldr_e5.csv", "tb_e3_e5_ldr_cio.csv"):
    s = s.replace(tab, tab.replace("ldr_", "ldr_cima12mA_"))
open(os.path.join(QUI, "tb_e3_e5_ldr_cima12mA.cir"), "w").write(s)
print("scritto tb_e3_e5_ldr_cima12mA.cir")
