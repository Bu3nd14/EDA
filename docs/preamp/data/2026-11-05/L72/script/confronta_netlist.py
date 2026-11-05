"""L72: il netlist rigenerato contro quello di main, nel senso che conta.

Confronta parti (ref, valore, impronta, campi tranne quelli di SKiDL che cambiano a ogni corsa) e reti
(nome -> insieme di (ref, pin)). L'atteso dopo ADR-123: nessuna parte, valore, impronta o rete cambiata;
il campo Tolerance = 0.1% su esattamente le parti elencate.

Uso: /usr/bin/python3 -I confronta_netlist.py <vecchio.net> <nuovo.net> <ref,ref,...>
"""
import re
import sys

SALTA = {"SKiDL Tag", "SKiDL Line"}


def parti(t):
    out = {}
    for m in re.finditer(r'\(comp\s+\(ref "([^"]+)"\)(.*?)\(tstamps', t, re.S):
        ref, body = m.group(1), m.group(2)
        val = re.search(r'\(value "([^"]*)"\)', body).group(1)
        fp = re.search(r'\(footprint "([^"]*)"\)', body)
        flds = dict(re.findall(r'\(field\s+\(name "([^"]+)"\)\s*"?([^")]*)"?\)', body))
        flds = {k: v for k, v in flds.items() if k not in SALTA}
        out[ref] = (val, fp.group(1) if fp else "", flds)
    return out


def reti(t):
    out = {}
    sez = t[t.find("(nets"):]
    for m in re.finditer(r'\(net\s+\(code "?\d+"?\)\s+\(name "([^"]*)"\)(.*?)(?=\(net\s+\(code|\Z)', sez, re.S):
        out[m.group(1)] = frozenset(re.findall(r'\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', m.group(2)))
    return out


a, b = open(sys.argv[1]).read(), open(sys.argv[2]).read()
attesi = set(sys.argv[3].split(","))
pa, pb = parti(a), parti(b)
err = 0
if set(pa) != set(pb):
    print("PARTI diverse:", sorted(set(pa) ^ set(pb))); err += 1
tol = set()
for r in sorted(set(pa) & set(pb)):
    va, fa, ka = pa[r]
    vb, fb, kb = pb[r]
    if (va, fa) != (vb, fb):
        print("CAMBIATA", r, (va, fa), (vb, fb)); err += 1
    extra = {k: v for k, v in kb.items() if ka.get(k) != v}
    manca = {k for k in ka if k not in kb}
    if manca or (extra and set(extra) != {"Tolerance"}):
        print("CAMPI", r, extra, manca); err += 1
    if kb.get("Tolerance") == "0.1%":
        tol.add(r)
if tol != attesi:
    print("TOLERANCE su", sorted(tol), "atteso", sorted(attesi)); err += 1
# reti: per insieme di connessioni (i nomi scelti da SKiDL possono cambiare, limitations #74)
ra, rb = reti(a), reti(b)
sa, sb = set(ra.values()), set(rb.values())
if sa != sb:
    print("RETI diverse:", len(sa - sb), "solo nel vecchio,", len(sb - sa), "solo nel nuovo"); err += 1
nomi = sum(1 for k in ra if k in rb and ra[k] != rb[k])
print(f"parti {len(pb)}, reti {len(rb)}, Tolerance 0.1% su {len(tol)}: {sorted(tol)}; "
      f"reti con lo stesso nome e altre connessioni: {nomi}")
print("UGUALI salvo Tolerance" if err == 0 else f"DIVERSI: {err}")
sys.exit(1 if err else 0)
