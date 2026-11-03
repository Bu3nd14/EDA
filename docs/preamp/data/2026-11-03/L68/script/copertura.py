#!/usr/bin/env python3
"""L64c: quali parti delle netlist di oggi non hanno nessuna riga nella FMEA di oggi (fmea_oggi.csv).

Uso: /usr/bin/python3 -I copertura.py <repo>   -> stampa e scrive copertura.csv accanto a fmea_oggi.csv
Una riga copre le parti che nomina nella colonna ref (anche gli intervalli R544-R547). Solo stdlib.
"""
import collections
import csv
import os
import re
import sys

REPO = os.path.abspath(sys.argv[1])
L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def refs(n):
    with open(os.path.join(REPO, "circuits", "preamp", n), encoding="utf-8") as f:
        return set(re.findall(r'\(ref "([^"]+)"\)', f.read()))


def main():
    cov = set()
    with open(os.path.join(L, "fmea_oggi.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t = re.findall(r"\b([A-Z]{1,3}\d{1,3}[A-Z]?)\b", r["ref"])
            for a, b, c in re.findall(r"\b([A-Z]+)(\d+)-[A-Z]*?(\d+)\b", r["ref"]):
                t += [a + str(i) for i in range(int(b), int(c) + 1)]
            cov |= set(t)
    # le righe del blocco hanno i nomi del primo blocco (gain_block.net, R1xx): la scheda audio ne ha
    # otto copie, R1xx..R8xx con le stesse due ultime cifre. Una parte di una copia e' coperta se lo e'
    # la sua gemella del blocco. Le doppie del blocco (Q110 = JQ110A + JQ110B, Q121 = Q121A + Q121B)
    # sono coperte se lo sono le due meta'.
    blocco = refs("gain_block.net")
    for x in list(cov):
        m = re.fullmatch(r"(J?Q)(\d{3})[AB]", x)
        if m and m.group(1) + m.group(2) + "A" in cov and m.group(1) + m.group(2) + "B" in cov:
            cov.add("Q" + m.group(2))

    def coperta(x, scheda):
        if x in cov:
            return True
        if scheda != "scheda audio":      # le copie dei blocchi stanno solo sulla scheda audio
            return False
        m = re.fullmatch(r"([A-Z]+)([1-8])(\d\d)", x)
        return bool(m) and m.group(1) + "1" + m.group(3) in blocco and m.group(1) + "1" + m.group(3) in cov

    righe = []
    for nome, net in (("alimentatore", "psu.net"), ("scheda audio", "preamp_audio.net"),
                      ("blocco", "gain_block.net")):
        S = refs(net)
        m = sorted((x for x in S if not coperta(x, nome)),
                   key=lambda x: (re.sub(r"\d.*", "", x), int(re.sub(r"\D", "", x) or 0)))
        c = collections.Counter(re.sub(r"\d.*", "", x) for x in m)
        print(f"{nome}: {len(S)} parti, {len(m)} senza riga {dict(c)}")
        print("   " + " ".join(m))
        righe += [(nome, x) for x in m]
    with open(os.path.join(L, "copertura.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(("scheda", "parte_senza_riga"))
        w.writerows(righe)
    return 0


if __name__ == "__main__":
    sys.exit(main())
