#!/usr/bin/env python3
"""L67 (NC-055): avvolge un blocco piatto (gain_block_flat.inc, o un blocco caldo di L66 con le
temp= per dispositivo) in `.subckt GAINBLOCK`, per metterlo nelle quattro istanze della catena.

Rifiuta se il blocco non dichiara gli stessi nodi esterni del subckt generato
(IN OUT FB RG RG10 VPLUS VMINUS, piu' la massa 0, globale anche dentro un subckt), o se contiene
una riga con il punto davanti (.subckt, .include, .temp...), che dentro un subckt cambierebbe senso.

I blocchi (nome -> sorgente, percorsi dalla radice del repo):
  oggi_avv          spice/preamp/gain_block_flat.inc (prova dell'avvolgimento: deve dare gli
                    stessi numeri di spice/preamp/gain_block.subckt)
  caldo_t27_rame    L66/inc/lim365--sot223--diss__t27_rame.inc   (aria 27, VAS su rame)
  caldo_t27_minima  ...__t27_minima.inc                           (aria 27, piazzola minima)
  caldo_t57_rame    ...__t57_rame.inc
  caldo_t57_minima  ...__t57_minima.inc
lim365 = il sorgente dopo ADR-111 (diff in L67: solo una riga di commento); i blocchi caldi sono il
passo 4 dell'iterazione di v4caldo.py di L66, ogni giunzione alla sua Tj, finali col dissipatore,
VAS e carico in SOT-223.

Uso: /usr/bin/python3 -I avvolgi.py  -> ../inc/<nome>.subckt
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(LOTTO, "..", "..", "..", "..", ".."))
L66 = os.path.join(ROOT, "docs/preamp/data/2026-11-02/L66/inc")
BLOCCHI = {
    "oggi_avv": os.path.join(ROOT, "spice/preamp/gain_block_flat.inc"),
}
for t in ("t27", "t57"):
    for p in ("rame", "minima"):
        BLOCCHI["caldo_%s_%s" % (t, p)] = os.path.join(L66, "lim365--sot223--diss__%s_%s.inc" % (t, p))
NODI = "External nodes: IN OUT FB RG RG10 VPLUS VMINUS 0"

os.makedirs(os.path.join(LOTTO, "inc"), exist_ok=True)
for nome, src in BLOCCHI.items():
    righe = open(src).read().split("\n")
    if not any(NODI in r for r in righe[:5]):
        raise SystemExit("%s: i nodi esterni non sono quelli del subckt" % src)
    for r in righe:
        if r.strip().startswith("."):
            raise SystemExit("%s: riga con il punto: %s" % (src, r))
    out = ["* L67 avvolgi.py: %s, da %s" % (nome, os.path.relpath(src, ROOT)),
           ".subckt GAINBLOCK IN OUT FB RG RG10 VPLUS VMINUS"]
    out += [r for r in righe if r.strip()]
    out += [".ends GAINBLOCK", ""]
    p = os.path.join(LOTTO, "inc", nome + ".subckt")
    open(p, "w").write("\n".join(out))
    n = sum(1 for r in righe if r and r[0] in "QJ")
    t = sum(1 for r in righe if "temp=" in r)
    print("%-18s %3d transistor, %2d con temp= -> %s" % (nome, n, t, os.path.relpath(p, ROOT)))
