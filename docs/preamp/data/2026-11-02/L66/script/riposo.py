#!/usr/bin/env python3
"""L45d2b3b2b2: la corrente di riposo dei finali, il VAS e il suo limitatore a caldo, dal punto di lavoro
convergente del metodo di L56 (v4caldo.py: passo 4, ogni giunzione alla sua Tj) e da quello a
temperatura uniforme (passo 1). Solo stdlib, /usr/bin/python3 -I.

Uso: riposo.py <spec> [...]     stampa e scrive riposo.csv

Per ogni spec e condizione: I_q dei finali (Q132 / Q133, la media dei due e lo squilibrio), il VAS
(Q122), il limitatore (Q193), la continua d'uscita, la Tj del finale NPN e del moltiplicatore Q127, e lo
spostamento di I_q contro la stessa condizione della prima spec (la base: senza dissipatore e senza
accoppiamento) e contro i ~20,3 mA di ADR-042.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import v4caldo as vc   # noqa: E402

IQ_ADR042 = 20.3
COND = [("u27", 27, None), ("u57", 57, None), ("t27_rame", 27, "rame"), ("t27_minima", 27, "minima"),
        ("t57_rame", 57, "rame"), ("t57_minima", 57, "minima")]


def punto(spec, ta, rv):
    rop = os.path.join(L, "run", "op_" + spec)
    if rv is None:
        return vc.leggi_op(os.path.join(rop, "op_p1", "op_p1.log"), "L56_OP ta=%d" % ta)
    b = "op_p4_t%d_%s" % (ta, rv)
    return vc.leggi_op(os.path.join(rop, b, b + ".log"), "L56_OP4 ta=%d" % ta)


def tj(spec):
    return {(int(r["aria"]), r["variante"], r["disp"]): r["Tj"]
            for r in csv.DictReader(open(os.path.join(L, "tj", spec + ".csv")))}


out, base = [], {}
for spec in sys.argv[1:]:
    t = tj(spec)
    for cond, ta, rv in COND:
        v = punto(spec, ta, rv)
        i1, i2 = v["@q132[ic]"] * 1e3, -v["@q133[ic]"] * 1e3
        iq = (i1 + i2) / 2
        base.setdefault(cond, iq)
        out.append({"spec": spec, "cond": cond,
                    "Iq_Q132_mA": "%.3f" % i1, "Iq_Q133_mA": "%.3f" % i2, "Iq_mA": "%.3f" % iq,
                    "dIq_base_pct": "%+.2f" % (100 * (iq / base[cond] - 1)),
                    "dIq_ADR042_pct": "%+.1f" % (100 * (iq / IQ_ADR042 - 1)),
                    "VAS_mA": "%.3f" % (-v["@q122[ic]"] * 1e3), "Q193_uA": "%.3g" % (-v["@q193[ic]"] * 1e6),
                    "out_mV": "%.3f" % (v["out"] * 1e3),
                    "Tj_Q132": t.get((ta, rv, "Q132"), "%d" % ta) if rv else "%d" % ta,
                    "Tj_Q127": t.get((ta, rv, "Q127"), "%d" % ta) if rv else "%d" % ta})
with open(os.path.join(L, "riposo.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
print("%-26s %-10s %7s %7s %7s %8s %8s %7s %8s %7s %6s %6s" % (
    "spec", "cond", "Q132", "Q133", "Iq mA", "d base", "d 042", "VAS", "Q193 uA", "out mV", "Tj132", "Tj127"))
for r in out:
    print("%-26s %-10s %7s %7s %7s %7s%% %7s%% %7s %8s %7s %6s %6s" % tuple(r[k] for k in (
        "spec", "cond", "Iq_Q132_mA", "Iq_Q133_mA", "Iq_mA", "dIq_base_pct", "dIq_ADR042_pct", "VAS_mA",
        "Q193_uA", "out_mV", "Tj_Q132", "Tj_Q127")))
