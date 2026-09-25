#!/usr/bin/env python3
"""L29e: la differenza fra il deck dal sorgente e il banco di L29d2, dichiarata e non per caso.

Uso: confronto_deck.py <tb_v2_casopeggiore.cir (sorgente)> <tb_v2_l29d2.cir (banco)>

Confronta:
- il netlist (tutto cio' che precede .control): deve essere identico riga per riga, tranne le
  righe di commento dell'intestazione;
- il preambolo del .control (fino alla prima corsa): identico;
- ogni corsa del sorgente (dal primo 'alter vamp' al suo 'destroy all', piu' le righe echo che
  la seguono): deve esistere IDENTICA nel banco. Le corse del banco che il sorgente non ha sono
  le varianti c100 / r10k / k5 e il controfattuale N, elencate per prefisso.
Esce con il numero di differenze.
"""
import re
import sys


def parti(path):
    righe = open(path).read().splitlines()
    i = righe.index(".control")
    net = [r for r in righe[1:i] if not r.startswith("*")]
    ctl = righe[i:]
    j = next(k for k, r in enumerate(ctl) if r.startswith("alter vamp"))
    pre, corpo = ctl[:j], ctl[j:]
    corse, cur = {}, []
    for r in corpo:
        if r.startswith("alter vamp") and cur:
            cur = []
        cur.append(r)
        if r.startswith("destroy all"):
            nome = next(re.search(r"wrdata (\S+?)\$d", x).group(1) for x in cur if x.startswith("wrdata"))
            corse[nome] = cur
            cur = []
    # le righe echo e i commenti fra le corse: in ordine, come insieme ordinato
    echo = [r for r in corpo if r.startswith("echo")]
    return net, [r for r in pre if not r.startswith("*")], corse, echo


s_net, s_pre, s_corse, s_echo = parti(sys.argv[1])
b_net, b_pre, b_corse, b_echo = parti(sys.argv[2])
bad = 0
if s_net != b_net:
    bad += 1
    print("DIVERSO il netlist (%d contro %d righe non di commento)" % (len(s_net), len(b_net)))
else:
    print("identico il netlist: %d righe" % len(s_net))
if s_pre != b_pre:
    bad += 1
    print("DIVERSO il preambolo del .control")
    for a, b in zip(s_pre, b_pre):
        if a != b:
            print("  sorgente: %s\n  banco:    %s" % (a, b))
else:
    print("identico il preambolo del .control: %d righe" % len(s_pre))
mancanti = [n for n in s_corse if n not in b_corse]
diverse = [n for n in s_corse if n in b_corse and s_corse[n] != b_corse[n]]
print("corse del sorgente: %d; identiche nel banco: %d; mancanti: %d; diverse: %d"
      % (len(s_corse), len(s_corse) - len(mancanti) - len(diverse), len(mancanti), len(diverse)))
for n in mancanti + diverse:
    print("  " + n)
bad += len(mancanti) + len(diverse)
e_manc = [r for r in s_echo if r not in set(b_echo)]
print("righe del manifesto del sorgente: %d; assenti nel banco: %d" % (len(s_echo), len(e_manc)))
bad += len(e_manc)
solo_banco = sorted(n for n in b_corse if n not in s_corse)
pref = {}
for n in solo_banco:
    k = "_N" if n.endswith("_N") else "_" + n.rsplit("_", 2)[-2] if n.endswith("_iii") else "?"
    pref[k] = pref.get(k, 0) + 1
print("corse solo nel banco (varianti e controfattuale): %d, per suffisso %s" % (len(solo_banco), pref))
print("differenze: %d" % bad)
sys.exit(bad)
