"""Legge prova/tb_tlv1701_solo.csv (wrdata: t, v(inp), t, v(out), t, i(vs)).
Uso: leggi_solo.py <csv> [vref]. Stampa la soglia nei due sensi, i livelli, i ritardi, la corrente."""
import sys

rows = []
for line in open(sys.argv[1]):
    p = line.split()
    if len(p) >= 6:
        rows.append((float(p[0]), float(p[1]), float(p[3]), -float(p[5])))
vref = float(sys.argv[2]) if len(sys.argv) > 2 else 1.25
mid = 2.5


def crossings(t0, t1):
    out = []
    for a, b in zip(rows, rows[1:]):
        if t0 <= a[0] < t1 and (a[2] - mid) * (b[2] - mid) < 0:
            f = (mid - a[2]) / (b[2] - a[2])
            t = a[0] + f * (b[0] - a[0])
            vin = a[1] + f * (b[1] - a[1])
            out.append((t, vin, "sale" if b[2] > a[2] else "scende"))
    return out


print("rampa (0-8 ms): ogni passaggio dell'uscita per 2,5 V")
for t, vin, s in crossings(0, 8.5e-3):
    print("  t=%.4f ms  uscita %s  IN+ = %.4f V  (IN+ - IN- = %+.2f mV)" % (t * 1e3, s, vin, (vin - vref) * 1e3))
print("gradini (9-10 ms): ritardo dal fronte d'ingresso al passaggio per 2,5 V")
for t, vin, s in crossings(8.9e-3, 10e-3):
    edge = 9.0005e-3 if t < 9.5e-3 else 9.5005e-3
    print("  uscita %s: %.0f ns" % (s, (t - edge) * 1e9))
lo = [r for r in rows if 0.5e-3 < r[0] < 1.5e-3]
hi = [r for r in rows if 3.5e-3 < r[0] < 4.5e-3]
print("uscita bassa %.4f V, alta %.4f V" % (sum(r[2] for r in lo) / len(lo), sum(r[2] for r in hi) / len(hi)))
print("corrente da V5: uscita bassa %.1f uA (con 10k: %.1f uA del pull-up), alta %.1f uA"
      % (sum(r[3] for r in lo) / len(lo) * 1e6, (5 - lo[0][2]) / 10e3 * 1e6, sum(r[3] for r in hi) / len(hi) * 1e6))
