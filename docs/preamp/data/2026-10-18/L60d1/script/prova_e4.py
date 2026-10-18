#!/usr/bin/env python3
"""L60d1: la cella trim=0 att=25 +3 dB di tb_e4_uscite «dopo» ha il canale spento (guadagno
-151,6 dB invece di -9,0, Zout ~300 ohm anche sui buffer fissi, che non dipendono dalla cella).
Il deck rifa' il punto di lavoro a ogni cella partendo dalla soluzione della precedente. Due prove
sulla sola cella, dal circuito del deck risolto (le righe prima di .control, invariate):

  op      la cella impostata subito, un punto di lavoro da zero, poi la stessa AC del deck
  accendi i rail in rampa 0 -> +/-15 V in 20 ms, transitorio fino a 400 ms: lo stato che
          il circuito raggiunge davvero

Uso: prova_e4.py <tb_e4_uscite_resolved.cir> <cartella>  -> <cartella>/{op,accendi}.cir
"""
import os
import sys

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
testo = open(src).read()
circ = testo[:testo.index("\n.control")]

CELLA = """alter rt1r = 0.1
alter rt1s = 1G
alter rt2r = 0.1
alter rt2s = 1G
alter ratth = 7.5k
alter rattl = 2.5k
alter rrgb = 0.1
alter rrg10b = 1G
"""
NODI = "v(aout) v(bout) v(f1out) v(f2out) v(bin) i(vpp) i(vmm)"

op = circ + """
.control
""" + CELLA + """op
print """ + NODI + """
alter @vsrc[acmag] = 1
ac dec 20 20 200k
meas ac g1k find vdb(mainjack) at=1000
echo "OP_ZERO trim=0 att=25 mode=3db"
print g1k
.endc
.end
"""
open(os.path.join(out, "op.cir"), "w").write(op)

acc = circ.replace("VPP VPLUS 0 DC 15", "VPP VPLUS 0 PWL(0 0 20m 15)")
acc = acc.replace("VMM VMINUS 0 DC -15", "VMM VMINUS 0 PWL(0 0 20m -15)")
assert acc.count("PWL(") == 2
acc += """
.control
""" + CELLA + """tran 10u 400m 0 10u uic
meas tran vaout find v(aout) at=399m
meas tran vbout find v(bout) at=399m
meas tran vf1 find v(f1out) at=399m
meas tran ipp find i(vpp) at=399m
echo "ACCENDI trim=0 att=25 mode=3db"
print vaout vbout vf1 ipp
.endc
.end
"""
open(os.path.join(out, "accendi.cir"), "w").write(acc)
print("->", out)
