#!/usr/bin/env python3
"""confronta.py - due cartelle di output di run_simulation.sh, file per file.

Uso: /usr/bin/python3 confronta.py <dir_a> <dir_b> [prefisso ...]

Per ogni .csv presente in <dir_a> (filtrato sui prefissi, se dati): identico,
diverso (con lo scarto relativo massimo cella per cella) o assente in <dir_b>.
Per i .log: righe diverse, ignorando quelle che contengono un percorso
assoluto (il worktree cambia, il circuito no).

Esce 0 se tutti i file confrontati sono identici, 1 altrimenti.
"""
import os
import sys


def celle(path):
    with open(path) as f:
        return [r.rstrip("\n").split(",") for r in f]


def scarto(a, b):
    ra, rb = celle(a), celle(b)
    if len(ra) != len(rb):
        return f"righe {len(ra)} contro {len(rb)}"
    worst = 0.0
    for x, y in zip(ra, rb):
        if len(x) != len(y):
            return "numero di colonne diverso"
        for u, v in zip(x, y):
            if u == v:
                continue
            try:
                fu, fv = float(u), float(v)
            except ValueError:
                return f"cella di testo diversa: {u!r} contro {v!r}"
            den = max(abs(fu), abs(fv), 1e-30)
            worst = max(worst, abs(fu - fv) / den)
    return f"scarto relativo massimo {worst:.3e}"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    da, db = sys.argv[1], sys.argv[2]
    pref = sys.argv[3:]
    tutto_uguale = True
    for name in sorted(os.listdir(da)):
        if not (name.endswith(".csv") or name.endswith(".log")):
            continue
        if pref and not any(name.startswith(p) for p in pref):
            continue
        a, b = os.path.join(da, name), os.path.join(db, name)
        if not os.path.exists(b):
            print(f"ASSENTE   {name}")
            tutto_uguale = False
            continue
        if name.endswith(".log"):
            la = [x for x in open(a) if "/Users/" not in x]
            lb = [x for x in open(b) if "/Users/" not in x]
            diff = [(i, x, y) for i, (x, y) in enumerate(zip(la, lb)) if x != y]
            if len(la) != len(lb) or diff:
                tutto_uguale = False
                print(f"DIVERSO   {name}: {len(la)} contro {len(lb)} righe, "
                      f"{len(diff)} righe diverse")
                for i, x, y in diff[:40]:
                    print(f"    - {x.rstrip()}")
                    print(f"    + {y.rstrip()}")
            else:
                print(f"IDENTICO  {name} (righe senza percorsi)")
            continue
        if open(a, "rb").read() == open(b, "rb").read():
            print(f"IDENTICO  {name}")
        else:
            tutto_uguale = False
            print(f"DIVERSO   {name}: {scarto(a, b)}")
    return 0 if tutto_uguale else 1


if __name__ == "__main__":
    sys.exit(main())
