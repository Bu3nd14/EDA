#!/usr/bin/env python3
"""L66: le varianti del rimedio di NC-076 sul limitatore del VAS di ADR-099. La degenerazione del VAS
resta 55 ohm (ADR-054 / ADR-099: R123 33 + R192 22); si sposta la presa, cioe' la soglia di Q193.
Solo stdlib, /usr/bin/python3 -I.

Uso: varianti.py <variante> <modo> [<modo> ...]   -> varianti/<v>/, inc/<v>/, deck/<v>_<pos>/,
                                                    deck/lista_<v>.txt
     variante: lim34 (R123 34.0, R192 21.0) | lim365 (R123 36.5, R192 18.7)

Il banco e' quello di genera.py (L45d2b3b2b2 caricato per percorso); la variante si scrive con
g2a.prepara(v, cambi) dal blocco del sorgente, e si rifiuta se le righe cambiate non sono esattamente
le due attese.
"""
import importlib.util
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
# per percorso e con un altro nome: il banco importa a sua volta un modulo «genera» (L45d2b3b2a)
_spec = importlib.util.spec_from_file_location("genera_l66", os.path.join(QUI, "genera.py"))
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)

VAR = {
    "lim34": {"R123": ["R123 VPF NVS 34.0"], "R192": ["R192 NVS NVE 21.0"]},
    "lim365": {"R123": ["R123 VPF NVS 36.5"], "R192": ["R192 NVS NVE 18.7"]},
}


def main(v, modi):
    if v not in VAR:
        sys.exit(__doc__)
    g.g2a.prepara(v, VAR[v], (), g.NUOVE)
    for f in ("gain_block.subckt", "gain_block_flat.inc"):
        a = open(os.path.join(g.g2a.SP, f)).read().splitlines()
        b = [r for r in open(os.path.join(g.L, "varianti", v, f)).read().splitlines()
             if not r.startswith("* L45d2b3b2a, variante")]
        diverse = [(x, y) for x, y in zip(a, b) if x != y]
        if len(a) != len(b) or len(diverse) != 2:
            sys.exit("RIFIUTATO: %s/%s cambia %d righe, attese 2" % (v, f, len(diverse)))
    g.lista(v, v, modi)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
