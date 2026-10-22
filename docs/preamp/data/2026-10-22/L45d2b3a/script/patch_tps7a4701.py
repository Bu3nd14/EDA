#!/usr/bin/python3
"""L45d2b3a: the ngspice derivative of TI's TPS7A4701 transient model (SBVM364B).

Reads the frozen vendor file, applies the two patches PROVENANCE.json of L41a recorded and a
third this lot found, and writes the derivative. Nothing else changes:
  1. "TC=0,0" on three capacitors: PSpice's positional tempco, which ngspice does not parse.
     The value is 0,0 in every case: dropping it is a no-op.
  2. ".MODEL x VSWITCH(RON ROFF VON VOFF)": ngspice has SW(VT VH RON ROFF), with
     VT = (VON + VOFF) / 2 and VH = (VON - VOFF) / 2.
  3. LIMIT(x, a, b) -> an order-free MIN / MAX clamp (see below).

usage: patch_tps7a4701.py <vendor .lib> <out .lib>
"""
import re
import sys

src, out = sys.argv[1], sys.argv[2]
text = open(src, newline="").read().replace("\r\n", "\n").replace("\r", "\n")

n_tc = len(re.findall(r"\s+TC=0,0", text))
text = re.sub(r"\s+TC=0,0", "", text)


SUFFIX = {"T": 1e12, "G": 1e9, "MEG": 1e6, "K": 1e3, "M": 1e-3, "U": 1e-6, "N": 1e-9, "P": 1e-12,
          "F": 1e-15, "": 1.0}


def spice_value(s):
    # "1G" is 1e9 (the first try of this lot read it as 1 and left NR shorted to ground)
    m = re.fullmatch(r"([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)(MEG|[TGKMUNPF]?)", s.upper())
    if m is None:
        raise SystemExit("RIFIUTATO: valore non letto %r" % s)
    return float(m.group(1)) * SUFFIX[m.group(2)]


def vswitch(m):
    name, body = m.group(1), m.group(2)
    kv = dict((k.upper(), spice_value(v)) for k, v in re.findall(r"(\w+)\s*=\s*([-+0-9.eE]+[A-Za-z]*)", body))
    vt = (kv["VON"] + kv["VOFF"]) / 2
    vh = (kv["VON"] - kv["VOFF"]) / 2
    return ".MODEL %s SW(VT=%g VH=%g RON=%g ROFF=%g)" % (name, vt, vh, kv["RON"], kv["ROFF"])


text, n_sw = re.subn(r"\.MODEL\s+(\S+)\s+VSWITCH\s*\(?([^)\n]*)\)?", vswitch, text)


def args_at(s, i):
    # s[i] is the "(" after LIMIT: return (end index past ")", [top-level arguments])
    depth, start, parts = 0, i + 1, []
    for j in range(i, len(s)):
        c = s[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                parts.append(s[start:j])
                return j + 1, parts
        elif c == "," and depth == 1:
            parts.append(s[start:j])
            start = j + 1
    raise SystemExit("RIFIUTATO: LIMIT senza parentesi chiusa")


# 3. LIMIT(x, a, b): ngspice without a compatibility mode does not read it as PSpice's clamp
#    (LIMIT(5, -1, 2) gives 0, prova/tb_limit.cir), and the model writes it both ways round
#    (G_LIM: INEG, IPOS; POLE_LIM: VMAX, VMIN). The order-free clamp is
#    MIN(MAX(x, MIN(a, b)), MAX(a, b)). This, not the switches, put the pin at 1.0 V in L41a.
#    The model's lines are joined first ("+" continuations), so a LIMIT split over two lines reads whole.
text = re.sub(r"\n\+", " ", text)
n_lim = 0
while True:
    m = re.search(r"LIMIT\s*\(", text)
    if m is None:
        break
    end, parts = args_at(text, m.end() - 1)
    if len(parts) != 3:
        raise SystemExit("RIFIUTATO: LIMIT con %d argomenti" % len(parts))
    x, a, b = (p.strip() for p in parts)
    text = text[:m.start()] + "MIN(MAX(%s, MIN(%s, %s)), MAX(%s, %s))" % (x, a, b, a, b) + text[end:]
    n_lim += 1

if (n_tc, n_sw, n_lim) != (3, 2, 2):
    raise SystemExit("RIFIUTATO: attese 3 TC, 2 VSWITCH, 2 LIMIT; trovate %d, %d, %d" % (n_tc, n_sw, n_lim))
open(out, "w").write(
    "* L45d2b3a (2026-10-22): ngspice derivative of vendor/ldo_regulator/ti/TPS7A4701/"
    "tps7a4701_trans.lib\n* patches: 3 x 'TC=0,0' removed; 2 x VSWITCH -> SW (VT, VH); "
    "2 x LIMIT(x,a,b) -> MIN(MAX(x,MIN(a,b)),MAX(a,b)); continuation lines joined\n" + text)
print("TC tolti %d, VSWITCH -> SW %d, LIMIT riscritti %d" % (n_tc, n_sw, n_lim))
