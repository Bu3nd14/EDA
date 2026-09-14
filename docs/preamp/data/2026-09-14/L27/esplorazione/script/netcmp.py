"""Semantic comparison of two KiCad s-expression netlists: components by ref
(value, lib, part) and connectivity as a PARTITION of (ref,pin) nodes -
never by net name (limitations #23)."""
import re, sys
def parse(path):
    t = open(path).read()
    comps = {}
    for m in re.finditer(r'\(comp\s*\(ref\s*"([^"]+)"\)\s*\(value\s*"([^"]*)"\)', t, re.S):
        comps[m.group(1)] = m.group(2)
    nets = []
    sec = t.split("(nets", 1)[1]
    for chunk in re.split(r"\(net\s*\(code", sec)[1:]:
        name = re.search(r'\(name\s*"([^"]*)"\)', chunk).group(1)
        nodes = frozenset((a, b) for a, b in re.findall(r'\(ref\s*"([^"]+)"\)\s*\(pin\s*"([^"]+)"\)', chunk))
        nets.append((name, nodes))
    return comps, nets
a_c, a_n = parse(sys.argv[1]); b_c, b_n = parse(sys.argv[2])
print(f"A: {len(a_c)} componenti, {len(a_n)} net, {sum(len(n) for _,n in a_n)} nodi")
print(f"B: {len(b_c)} componenti, {len(b_n)} net, {sum(len(n) for _,n in b_n)} nodi")
assert a_c and b_c and a_n and b_n, "parser ha letto zero: confronto non valido"
added = sorted(set(b_c) - set(a_c)); removed = sorted(set(a_c) - set(b_c))
changed = sorted(r for r in set(a_c) & set(b_c) if a_c[r] != b_c[r])
print("aggiunti:", [(r, b_c[r]) for r in added])
print("tolti:", removed)
print("valori cambiati:", [(r, a_c[r], b_c[r]) for r in changed])
new = set(added)
def proj(nets, drop):
    out = set()
    for name, nodes in nets:
        k = frozenset(x for x in nodes if x[0] not in drop)
        if k: out.add(k)
    return out
pa, pb = proj(a_n, set()), proj(b_n, new)
print("partizione, tolti i componenti aggiunti: identica =", pa == pb)
if pa != pb:
    for s in sorted(pa - pb, key=len)[:10]: print("  solo A:", sorted(s))
    for s in sorted(pb - pa, key=len)[:10]: print("  solo B:", sorted(s))
lookup = {x: name for name, nodes in b_n for x in nodes}
for r in added:
    pins = sorted({x for _, nodes in b_n for x in nodes if x[0] == r})
    print(f"  {r}:", [(p, lookup[(r,p)]) for _, p in pins])
