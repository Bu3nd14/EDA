#!/usr/bin/env python3
"""L33 - la baseline delle frasi che dicono «del costruttore» l'LSK489 simulato.

Contata, non copiata da NC-031: NC-031 dice tredici deck e tre README.

    /usr/bin/python3 conta.py <radice-del-repo>

Cerca le forme trovate leggendo, su ogni file di testo di spice/, circuits/,
scripts/ e sui README di docs/preamp/data/. Le copie sotto esplorazione/ sono
output datato: si elencano a parte e non entrano nel conto.
Esce 0 e stampa; non giudica.
"""

import os
import re
import sys
from collections import defaultdict

# Forme ESPLICITE: la frase dice che l'LSK489 simulato e' del costruttore.
EXPLICIT = {
    "L22 «only real device model … besides the LSK489»": r"besides\s+the\s+lsk489",
    "«tutto tranne LS352 e LSK489 e' segnaposto»": r"tranne\s+ls352\s+e\s+lsk489",
    "«KF = 0 but on the LSK489»": r"kf\s*=\s*0\s+but\s+on\s+the\s+lsk489",
    "«segnaposto più LS352 e LSK489 vendor»": r"lsk489\s+vendor",
    "«solo lo specchio e l'LSK489 hanno un modello del costruttore»":
        r"l'lsk489\s+hanno\s+un\s+modello\s+del\s+costruttore",
}
# Forma IMPLICITA: nomina l'LSK489 e poi dice segnaposto «ogni altro» dispositivo.
IMPLICIT = {
    "«LSK489 fuso in una Part … ogni altro dispositivo … segnaposto»":
        r"lsk489\s+fuso\s+in\s+una\s+part[\s\S]{0,200}?ogni\s+altro\s+dispositivo",
}
# Vera della libreria, falsa delle simulazioni: si elenca, non si conta.
LIBRARY = {
    "«solo l'LSK489 ha rumore 1/f / flicker»": r"solo\s+l'lsk489\s+ha\s+(rumore\s+1/f|flicker)",
}

EXT = (".cir", ".lib", ".inc", ".subckt", ".py", ".sh", ".md")


def files(root):
    for top in ("spice", "circuits", "scripts"):
        for d, _, fs in os.walk(os.path.join(root, top)):
            for f in sorted(fs):
                if f.endswith(EXT):
                    yield os.path.join(d, f)
    for d, _, fs in os.walk(os.path.join(root, "docs", "preamp", "data")):
        for f in sorted(fs):
            if f == "README.md" or f.endswith(".cir"):
                yield os.path.join(d, f)


def main():
    root = os.path.abspath(sys.argv[1])
    hits = defaultdict(list)          # (classe, forma) -> [(file, riga)]
    for path in files(root):
        with open(path, errors="ignore") as fh:
            text = fh.read()
        low = text.lower()
        for cls, forms in (("esplicita", EXPLICIT), ("implicita", IMPLICIT),
                           ("libreria", LIBRARY)):
            for label, rx in forms.items():
                for m in re.finditer(rx, low):
                    line = low.count("\n", 0, m.start()) + 1
                    hits[(cls, label)].append((os.path.relpath(path, root), line))

    decks, readmes, other, dated = set(), set(), set(), set()
    for (cls, label), where in sorted(hits.items()):
        print(f"[{cls}] {label}: {len(where)}")
        for f, n in where:
            print(f"    {f}:{n}")
            if cls == "libreria":
                continue
            if "/esplorazione/" in f:
                dated.add(f)
            elif re.match(r"spice/[^/]+/tb/[^/]+\.cir$", f):
                decks.add((cls, f))
            elif f.endswith("README.md"):
                readmes.add((cls, f))
            else:
                other.add(f)

    def count(s, cls):
        return len({f for c, f in s if c == cls})

    print()
    print(f"DECK con una frase falsa: {len({f for _, f in decks})} "
          f"(esplicita {count(decks, 'esplicita')}, implicita {count(decks, 'implicita')})")
    print(f"README datati: esplicita {count(readmes, 'esplicita')}, "
          f"implicita {count(readmes, 'implicita')}")
    print(f"altri file (codice, script): {len(other)}  {sorted(other)}")
    print(f"copie datate sotto esplorazione/, fuori conto: {len(dated)}  {sorted(dated)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
