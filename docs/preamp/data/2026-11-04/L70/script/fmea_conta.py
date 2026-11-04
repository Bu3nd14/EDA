#!/usr/bin/env python3
"""L70: what each simplification does to today's FMEA (data/2026-11-03/L69/fmea_oggi.csv, 692 rows,
47 high), row by row, BEFORE the new rows of the fuses (those are in the report, by calculation).

For each variant (s2, s1, s1s2) a row is:
  tolta   its part (or its comparator channel) leaves the board with the variant;
  bassa   S1 only: its part stays, and its ONLY effect in the row ("la ritenuta cieca": after a rail
          fault K501 stays closed and the toroid stays on until the front switch) becomes the
          design's own behaviour without the latch - listed by hand below, each read from the row's
          effetto_dopo (the rows whose effect also says "in standby" or "allo spegnimento" stay);
  resta   unchanged.
The parts that leave: S2 the detector (Q504, R510, R511, R512, R554, R555, C518, D533, R569, U506
channel A, U513 channel D) and its diodes into the timer (D534, D535); S1 the latch and its trigger
(Q513, Q514, R580-R585, C552-C555, D534, D535, D541, U515 channels C and D). D534 / D535 leave with
either: they join the detector to the latch's nodes.

    /usr/bin/python3 -I script/fmea_conta.py   -> fmea_l70.csv, fmea_l70_conti.csv
"""
import collections
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
FMEA = os.path.join(os.path.dirname(os.path.dirname(L)), "2026-11-03", "L69", "fmea_oggi.csv")
S2_PARTI = {"Q504", "R510", "R511", "R512", "R554", "R555", "C518", "D533", "R569", "D534", "D535"}
S1_PARTI = {"Q513", "Q514", "R580", "R581", "R582", "R583", "R584", "R585", "C552", "C553", "C554",
            "C555", "D534", "D535", "D541"}
S2_CANALI = {("U506", "canale A"), ("U513", "canale D")}
S1_CANALI = {("U515", "canale C"), ("U515", "canale D")}
# S1: part stays, its only effect is the blind latch (effetto_dopo read row by row)
S1_BASSE = {("U513", "canale A (rail +): uscita aperta"), ("U513", "canale B (rail -): uscita aperta"),
            ("U513", "alimentazione persa (pin 3)"), ("D533", "corto"), ("R569", "aperto"),
            ("R570", "corto"), ("R571", "corto")}


def tolta(x, parti, canali):
    if x["ref"] in parti:
        return True
    return any(x["ref"] == r and x["modo"].startswith(c) for r, c in canali)


righe = list(csv.DictReader(open(FMEA)))
assert len(righe) == 692, len(righe)
out, conti = [], collections.Counter()
for x in righe:
    e = {}
    for v in ("s2", "s1", "s1s2"):
        parti = (S2_PARTI if v in ("s2", "s1s2") else set()) | (S1_PARTI if v.startswith("s1") else set())
        canali = (S2_CANALI if v in ("s2", "s1s2") else set()) | (S1_CANALI if v.startswith("s1") else set())
        if tolta(x, parti, canali):
            e[v] = "tolta"
        elif v.startswith("s1") and any(x["ref"] == r and x["modo"].startswith(m) for r, m in S1_BASSE):
            assert x["priorita_dopo"] == "alta", (x["ref"], x["modo"])
            e[v] = "bassa"
        else:
            e[v] = "resta"
        conti[(v, x["priorita_dopo"], e[v])] += 1
    out.append(dict(ref=x["ref"], modo=x["modo"], priorita_oggi=x["priorita_dopo"], stato_oggi=x["stato"], **e))
# every hand-listed row must exist once
for r, m in S1_BASSE:
    n = sum(1 for x in righe if x["ref"] == r and x["modo"].startswith(m) and x["priorita_dopo"] == "alta")
    assert n == 1, (r, m, n)
with open(os.path.join(L, "fmea_l70.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, list(out[0]))
    w.writeheader()
    w.writerows(out)
with open(os.path.join(L, "fmea_l70_conti.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["variante", "righe", "tolte", "alte_oggi", "alte_tolte", "alte_basse", "alte_dopo",
                "medie_dopo", "basse_dopo"])
    for v in ("s2", "s1", "s1s2"):
        tol = sum(n for (vv, p, e), n in conti.items() if vv == v and e == "tolta")
        alte = sum(n for (vv, p, e), n in conti.items() if vv == v and p == "alta")
        at = conti[(v, "alta", "tolta")]
        ab = conti[(v, "alta", "bassa")]
        med = conti[(v, "media", "resta")]
        bas = conti[(v, "bassa", "resta")] + ab
        w.writerow([v, len(righe) - tol, tol, alte, at, ab, alte - at - ab, med, bas])
print(open(os.path.join(L, "fmea_l70_conti.csv")).read())
