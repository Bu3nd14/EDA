#!/usr/bin/env python3
"""L37: il dossier rigenerato cambia solo dove tocca E4.

Uso: confronto.py <cartella baseline> <cartella nuova>

Esce 0 solo se:
  - ogni fig_*.svg tranne fig_zout.svg e' identica byte per byte;
  - index.html, diviso ai <h2 id="sN">, ha identiche tutte le sezioni tranne
    la testata, s10, s13 e s14;
  - nella testata, s13 e s14 cambiano solo le righe attese (eyebrow, paragrafo
    dei dati, KPI di Zout; riga E4; voce E4);
  - dossier.summary.json cambia solo nelle chiavi attese;
  - le cifre sbagliate di NC-033 compaiono 0 volte, quelle giuste ci sono.
"""
import difflib
import json
import os
import re
import sys

base, new = sys.argv[1], sys.argv[2]
bad = []


def read(d, n):
    with open(os.path.join(d, n), encoding="utf-8") as f:
        return f.read()


# --- figure
for n in sorted(os.listdir(base)):
    if n.startswith("fig_") and n.endswith(".svg"):
        same = read(base, n) == read(new, n)
        print(f"{n:<28} {'identica' if same else 'DIVERSA'}")
        if n != "fig_zout.svg" and not same:
            bad.append(f"{n} e' cambiata")


# --- index.html per sezioni
def sections(html):
    parts = re.split(r'(?=<h2 id="s\d+")', html)
    out = {"testata": parts[0]}
    for p in parts[1:]:
        out[re.match(r'<h2 id="(s\d+)"', p).group(1)] = p
    return out


sb, sn = sections(read(base, "index.html")), sections(read(new, "index.html"))
if sb.keys() != sn.keys():
    bad.append(f"sezioni diverse: {sorted(sb)} contro {sorted(sn)}")
ALLOWED = {
    "testata": ('class="eyebrow"', "Il progetto sostituisce", "<dt>E4, Re(Z<sub>out</sub>)",
                "<dt>Z<sub>out</sub> al jack"),
    "s13": ("<tr><td>E4</td>",),
    "s14": ("<strong>E4",),
}
for k in sb:
    if k not in sn:
        continue
    if sb[k] == sn[k]:
        print(f"{k:<8} identica")
        continue
    diff = [l for l in difflib.unified_diff(sb[k].splitlines(), sn[k].splitlines(),
                                            lineterm="", n=0)
            if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    print(f"{k:<8} DIVERSA, {len(diff)} righe +/-")
    if k == "s10":
        continue
    if k not in ALLOWED:
        bad.append(f"sezione {k} cambiata")
    for l in diff:
        ok = k in ALLOWED and any(a in l for a in ALLOWED[k])
        print(f"   {'  ' if ok else '!!'} {l[:150]}")
        if not ok:
            bad.append(f"{k}: riga inattesa {l[:100]!r}")

# --- JSON
jb, jn = json.loads(read(base, "dossier.summary.json")), json.loads(read(new, "dossier.summary.json"))
JALLOWED = {"dati", "zout_jack_1kHz_ohm_0db", "e4_rez_max_ohm", "e4_dispersione_volume_ohm"}
for k in sorted(set(jb) | set(jn)):
    if jb.get(k) != jn.get(k):
        print(f"json {k}: {jb.get(k)!r} -> {jn.get(k)!r}")
        if k not in JALLOWED:
            bad.append(f"json: chiave inattesa {k}")

# --- cifre
page = read(new, "index.html")
for s in ("58,76", "59,1132", "60,5851", "1,0355", "dà 1,035"):
    c = page.count(s)
    print(f"cifra vecchia {s!r}: {c}")
    if c:
        bad.append(f"la cifra vecchia {s} compare {c} volte")
for s in ("57,94", "60,1281", "53,1318", "0,0386"):
    c = page.count(s)
    print(f"cifra nuova {s!r}: {c}")
    if not c:
        bad.append(f"la cifra nuova {s} manca")

if bad:
    print("\nRIFIUTATO:")
    for b in bad:
        print("  - " + b)
    sys.exit(1)
print("\nOK: cambia solo cio' che riguarda E4")
