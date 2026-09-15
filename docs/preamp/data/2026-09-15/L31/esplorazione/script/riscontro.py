#!/usr/bin/env python3
"""
riscontro.py - L31: are the data tb_noise_vectors.cir now writes the data
ngspice computed, and do they add up?

Independent of the deck's own comment, from four files:
  log        tb_noise_vectors.log     (`print all` of plot noise1)
  csv        tb_noise_vectors.csv     (the wrdata, converted)
  deck       tb_noise_vectors.cir     (the wrdata line: which vector is which column)
  breakdown  tb_noise_breakdown_b_0db_430r.csv of L27 (same circuit: 0 dB, Rsrc 430)
  include    gain_block_flat.inc      (the devices that must have a total)

Checks, at 1000 Hz (row 0):
  1. the log has 0 `Error` lines and the CSV has exactly 2 rows;
  2. every CSV data column equals the log value of the vector the wrdata
     line names in that position (log prints 7 digits: tolerance 1e-6);
  3. the per-device totals in the log are exactly the devices of the
     include plus the deck's own elements - no more, no fewer;
  4. sqrt(sum of squares of ALL per-device totals) = onoise_spectrum;
  5. the devices the wrdata writes are the top of the ranking;
  6. onoise/inoise_spectrum against the breakdown B spectrum at the point
     nearest 1000 Hz (the dec-100 sweep).

WHY 6 AND NOT A PER-DEVICE TABLE: tb_noise_breakdown.cir does NOT print a
per-device breakdown at 1 kHz - its log says only "No. of Data Rows : 2"
and the deck destroys the plot. What it does keep is the spectrum.

Every number here is a FLOOR: placeholder models with KF = 0, no 1/f noise
(NC-004, NC-031).

Exit 0 all checks hold, 1 otherwise, 2 usage.
"""
import csv
import math
import re
import sys
from pathlib import Path

NODE_COUNT = {"r": 2, "c": 2, "l": 2, "d": 2, "q": 3, "j": 3, "v": 2}
TOL = 1e-6


def log_values(log):
    """{vector: value at row 0} from the `print all` pages."""
    vals, hdr = {}, None
    for line in log.splitlines():
        if line.startswith("Index"):
            hdr = line.split()[2:]
        elif hdr is not None and re.match(r"^0\t", line):
            for name, v in zip(hdr, line.split()[2:]):
                vals[name] = float(v)
            hdr = None
    return vals


def elements(path, skip_title):
    names, in_control = set(), False
    for i, raw in enumerate(Path(path).read_text().splitlines()):
        if skip_title and i == 0:
            continue
        s = raw.split(";")[0].strip()
        low = s.lower()
        if not s or s.startswith("*"):
            continue
        if low.startswith(".control"):
            in_control = True
        elif low.startswith(".endc"):
            in_control = False
        elif not in_control and not s.startswith((".", "+")):
            if s[0].lower() in NODE_COUNT:
                names.add(s.split()[0].lower())
    return names


def main(argv):
    if len(argv) != 6:
        print(__doc__)
        return 2
    log_p, csv_p, deck_p, brk_p, inc_p = argv[1:]
    fails = 0

    def check(ok, text):
        nonlocal fails
        fails += not ok
        print(f"   [{'ok' if ok else 'FALLITO'}] {text}")

    log = Path(log_p).read_text(errors="replace")
    errors = [l for l in log.splitlines() if "Error" in l]
    rows = list(csv.reader(open(csv_p)))[1:]
    print("== 1. il log e i dati ==")
    check(not errors, f"righe con 'Error' nel log: {len(errors)}")
    check(len(rows) == 2, f"righe di dati nel CSV: {len(rows)}")
    vals = log_values(log)

    wr = next(l.split() for l in Path(deck_p).read_text().splitlines()
              if l.lower().startswith("wrdata "))[2:]
    print(f"\n== 2. CSV contro log, 1000 Hz ({len(wr)} vettori) ==")
    check(len(rows[0]) == 2 * len(wr),
          f"colonne nel CSV: {len(rows[0])} (attese {2 * len(wr)})")
    for i, name in enumerate(wr):
        f_csv, v_csv = float(rows[0][2 * i]), float(rows[0][2 * i + 1])
        v_log = vals.get(name)
        ok = (v_log is not None and f_csv == 1000.0
              and abs(v_csv - v_log) <= TOL * abs(v_log))
        check(ok, f"col{2 * i + 1:<2} {name:16s} csv {v_csv:.7e}  log "
                  f"{v_log if v_log is None else format(v_log, '.6e')}")

    devices = elements(inc_p, False) | elements(deck_p, True)
    devices = {d for d in devices if not d.startswith(("c", "v"))}
    totals = {k[len("onoise_"):]: v for k, v in vals.items()
              if k.startswith("onoise_") and "_" not in k[len("onoise_"):]
              and k != "onoise_spectrum"}
    print("\n== 3. un totale per ogni dispositivo che fa rumore ==")
    check(set(totals) == devices,
          f"{len(totals)} totali nel log, {len(devices)} dispositivi R/D/Q/J "
          f"nell'include e nel deck; mancano {sorted(devices - set(totals))}, "
          f"in piu' {sorted(set(totals) - devices)}")

    spectrum = vals["onoise_spectrum"]
    quad = math.sqrt(sum(v * v for v in totals.values()))
    print("\n== 4. quadratura ==")
    check(abs(quad - spectrum) <= TOL * spectrum,
          f"sqrt(somma dei quadrati di {len(totals)} totali) = {quad:.6e}, "
          f"onoise_spectrum = {spectrum:.6e}, scarto "
          f"{(quad - spectrum) / spectrum:+.1e}")

    written = [n[len("onoise_"):] for n in wr
               if n.startswith("onoise_") and n != "onoise_spectrum"]
    ranking = sorted(totals.items(), key=lambda kv: -kv[1])
    # .get: a name that is no device (a dead one) contributes nothing and
    # fails the ranking check below, instead of crashing the report.
    share = sum(totals.get(d, 0.0) ** 2 for d in written) / quad ** 2
    print("\n== 5. classifica a 1 kHz (quota della potenza di rumore) ==")
    for i, (d, v) in enumerate(ranking[:12], 1):
        mark = "  <- scritto" if d in written else ""
        print(f"   {i:2d}. {d:8s} {v:.4e} V/sqrt(Hz)  "
              f"{100 * v * v / quad ** 2:5.2f} %{mark}")
    top = {d for d, _ in ranking[:len(written)]}
    check(top == set(written),
          f"i {len(written)} dispositivi scritti sono i primi "
          f"{len(written)}: {sorted(top) == sorted(written)}; quota "
          f"{100 * share:.2f} % della potenza")

    print("\n== 6. contro tb_noise_breakdown, configurazione B (L27) ==")
    brk = [list(map(float, r)) for r in list(csv.reader(open(brk_p)))[1:]]
    near = min(brk, key=lambda r: abs(math.log10(r[0] / 1000.0)))
    for label, got, ref in (("onoise_spectrum", spectrum, near[1]),
                            ("inoise_spectrum", vals["inoise_spectrum"],
                             near[3])):
        rel = (got - ref) / ref
        check(abs(rel) <= 1e-4,
              f"{label}: {got:.6e} qui, {ref:.8e} nel breakdown a "
              f"{near[0]:.4f} Hz, scarto {rel:+.2e}")

    print("\nPAVIMENTO senza 1/f: modelli segnaposto con KF = 0 (NC-004, "
          "NC-031).")
    print(f"\n{'TUTTI I CONTROLLI TENGONO' if not fails else f'{fails} FALLITI'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
