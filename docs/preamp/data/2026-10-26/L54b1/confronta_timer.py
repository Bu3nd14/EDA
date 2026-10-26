#!/usr/bin/env python3
"""L54b1: il caso noto strutturale. Ogni elemento di TIMER_AN (il temporizzatore di L54a, sul solo
banco) contro le parti del temporizzatore in psu.net: stesso tipo, stesso valore, stessi nodi, con
AT_ON letto come VRELAY_EN (il banco li univa con 1 ohm solo per sondarli tutti e due: RATve).
Esce 0 se non resta niente di spaiato da nessuna delle due parti, 1 altrimenti.

Uso: /usr/bin/python3 -I confronta_timer.py <genera_tb_psu.py di L54a> <psu.net>
"""
import ast
import re
import sys
from collections import Counter

SINONIMI = {"at_on": "vrelay_en", "0": "gnd"}
PARTI = ("U513", "U514", "U515", "R556", "R557", "R558", "R559", "R560", "R561", "R562", "R563",
         "R564", "R565", "R566", "R567", "R568", "R569", "R570", "R571", "C537", "C538", "C539",
         "C540", "C541", "C542", "C543", "C544", "D533", "D534", "D535", "D536", "D537", "D538",
         "D539", "D540", "D541", "Q507", "Q508")
# i disaccoppiamenti dei tre TLV1704 non sono nel banco di L54a (il comparatore comportamentale
# assorbe dal suo V5 da se'): si contano a parte
DISACCOPPIAMENTI = ("C545", "C546", "C547")


def n(x):
    x = x.lower()
    return SINONIMI.get(x, x)


def numero(v):
    """'4.7MEG' / '4.7M' (KiCad: M e' mega) / '820k' / '1u' -> float."""
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)\s*(MEG|[kKMunp]?)", v)
    return float(m.group(1)) * {"MEG": 1e6, "M": 1e6, "k": 1e3, "K": 1e3, "u": 1e-6, "n": 1e-9,
                                "p": 1e-12, "": 1.0}[m.group(2)]


def dal_banco(path):
    t = open(path).read()
    i = t.index("TIMER_AN = [")
    j = t.index("\n]", i)
    righe = ast.literal_eval(t[i + len("TIMER_AN = "):j + 2])
    out = Counter()
    for r in righe:
        if r.startswith("*"):
            continue
        p = r.split()
        k = p[0][0]
        if p[0] == "RATve":
            continue                    # AT_ON e VRELAY_EN sono la stessa rete nel sorgente
        if k == "X":
            assert p[6] == "CMPOD", r
            out[("cmp",) + tuple(n(x) for x in p[1:6])] += 1
        elif k in "RC":
            out[(k, tuple(sorted((n(p[1]), n(p[2])))), round(numero(p[3]), 15))] += 1
        elif k == "D":
            out[("D", n(p[1]), n(p[2]), p[3])] += 1
        elif k == "Q":
            out[("Q", n(p[1]), n(p[2]), n(p[3]), p[4])] += 1
        else:
            raise SystemExit("elemento sconosciuto: %s" % r)
    return out


def dalla_netlist(path):
    t = open(path).read()
    comps = {}
    for m in re.finditer(r'\(comp\b.*?\(ref "([^"]+)"\).*?\(value "([^"]*)"\)'
                         r'.*?\(libsource\s*\(lib "([^"]*)"\)\s*\(part "([^"]*)"\)', t, re.S):
        comps[m.group(1)] = (m.group(2), m.group(4))
    pn = {}
    for blk in re.split(r"\(net\s*\(code", t.split("(nets", 1)[-1])[1:]:
        nome = re.search(r'\(name "([^"]*)"\)', blk).group(1)
        for m in re.finditer(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk):
            pn[(m.group(1), m.group(2))] = n(nome)
    out, mancano = Counter(), [r for r in PARTI + DISACCOPPIAMENTI if r not in comps]
    for ref in PARTI:
        if ref not in comps:
            continue
        val, part = comps[ref]
        g = lambda p: pn.get((ref, p), "nc_%s_%s" % (ref, p))
        if part == "LM339":
            # canali 1-4: (+, -, uscita) del simbolo, come il PW del TLV1704 (SBOS589D p. 5)
            for pp, pm, po in (("5", "4", "2"), ("7", "6", "1"), ("9", "8", "14"), ("11", "10", "13")):
                out[("cmp", g(pp), g(pm), g(po), g("3"), g("12"))] += 1
        elif part in ("R", "C"):
            out[(part, tuple(sorted((g("1"), g("2")))), round(numero(val), 15))] += 1
        elif part == "D":
            out[("D", g("2"), g("1"), "D1N914")] += 1           # come element() del banco
        elif part == "D_Schottky":
            out[("D", g("2"), g("1"), "DBAT54" if val == "BAT54" else "DSCH")] += 1
        elif part == "BC847":
            out[("Q", g("3"), g("1"), g("2"), "QNGEN")] += 1
        elif part == "BC857":
            out[("Q", g("3"), g("1"), g("2"), "QPGEN")] += 1
        else:
            raise SystemExit("%s: parte %s non attesa" % (ref, part))
    dis = [(r, comps[r][0], pn.get((r, "1")), pn.get((r, "2"))) for r in DISACCOPPIAMENTI if r in comps]
    return out, mancano, dis


def main():
    banco = dal_banco(sys.argv[1])
    net, mancano, dis = dalla_netlist(sys.argv[2])
    solo_banco, solo_net = banco - net, net - banco
    print("TIMER_AN: %d elementi (senza RATve); netlist: %d" % (sum(banco.values()), sum(net.values())))
    print("disaccoppiamenti (non nel banco): %s" % ", ".join("%s %s %s-%s" % d for d in dis))
    for r in mancano:
        print("  MANCA nella netlist: %s" % r)
    for k, c in sorted(solo_banco.items(), key=str):
        print("  SOLO NEL BANCO   %dx %s" % (c, k))
    for k, c in sorted(solo_net.items(), key=str):
        print("  SOLO NELLA NETLIST %dx %s" % (c, k))
    ok = not (solo_banco or solo_net or mancano)
    print("OK: ogni elemento ha la sua parte, e viceversa" if ok else "FALLITO")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
