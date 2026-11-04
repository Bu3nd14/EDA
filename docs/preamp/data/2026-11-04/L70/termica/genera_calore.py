#!/usr/bin/env python3
"""L64b: the power the supply dissipates in the chassis, MEASURED on the bench of today.

Copy of data/2026-10-09/L51b/termica/genera_calore.py, on the supply of today (psu.py after L58b):
since L51b the rails have the 4,7 ohm in front of each regulator (R550 / R551, ADR-092), the SB340
after it (DD515 / DD516, ADR-093, with the doubled reverse diodes DD510 / DD513, DD511 / DD514 of
ADR-094), the two 5 V regulators U504 -> U512 fed from VRELAY_REG (ADR-094), and the timer of
comparators instead of the micro (ADR-102). The bench settles in TSS = 3 s (the sequences' --tss 3.0:
from cold the music comes at ~2,05 s, L58a), so the averages are over 2,5-3,0 s.

Reads ../rete/tb_psu_rete.cir (genera_tb_psu.py --nome rete --timer sorgente --tss 3.0 with the
options of L58b, the load of ../carico.txt) and writes tb_calore.cir: the same circuit, the three
steady states (regime_m10 / _nom / _p10), and instead of the waveforms the AVERAGE of:

  pt1, pt2     the power out of T1's and T2's secondaries (behind the sense sources);
  cu1, cu2     the copper of the secondaries (RT1_SEC_A*, RT2_SEC_A);
  dbr1, dbr2   the bridges (DD501a-d; DD503a-d and the Schottky DD504);
  rpre         R550 + R551, the 4,7 ohm in front of U501 / U502 (ADR-092);
  reg1, reg2   U501 and U502: the current they draw (their own 0 V sense) x (in - out), at their pins;
  dsch         DD515 + DD516, the SB340 after the regulators (ADR-093);
  dprot        DD510 / DD513 / DD511 / DD514, the reverse diodes (they conduct only in a fault: the
               balance names them so that a non-zero value shows);
  reg3         U503 (VRELAY 12 V): the same as reg1;
  paud         the audio board as the bench loads it: v(vplus) x I_PIU + |v(vminus)| x I_MENO;
  pvr          what U503 hands on: v(vrelay_reg) x its output current - the coils, the selector,
               the rest, the timer of comparators and the 5 V line (U504, U512).

The transformers' IRON is not in the bench (an ideal source with a series R and L): the estimate
keeps it as an hypothesis, declared.

    /usr/bin/python3 -I genera_calore.py [--uscita <file>]   # tb_calore.cir next to itself
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(QUI, "..", "rete", "tb_psu_rete.cir")
OUT = (sys.argv[sys.argv.index("--uscita") + 1] if "--uscita" in sys.argv
       else os.path.join(QUI, "tb_calore.cir"))
TF = 3.0
DA = 2.5

testo = open(SRC).read().splitlines()
k = testo.index(".control")
corpo, ctl = testo[:k], testo[k:]

# the three steady-state blocks, verbatim up to tran
casi = {}
i = 0
while i < len(ctl):
    m = re.match(r"\* ---- (regime_(?:m10|nom|p10)) ----$", ctl[i])
    if m:
        j = i
        while not ctl[j].startswith("tran "):
            j += 1
        casi[m.group(1)] = ctl[i:j + 1]
        i = j
    i += 1
if sorted(casi) != ["regime_m10", "regime_nom", "regime_p10"]:
    sys.exit("RIFIUTATO: non trovo i tre casi a regime in %s" % SRC)
for nome, b in casi.items():
    if b[-1] != "tran 20u %g 0 20u uic" % TF:
        sys.exit("RIFIUTATO: %s non finisce a %g s (%s)" % (nome, TF, b[-1]))


def num(pat):
    v = [ln for ln in corpo if re.match(pat, ln)]
    if len(v) != 1:
        sys.exit("RIFIUTATO: %r: %d righe" % (pat, len(v)))
    return v[0]


# the audio board's currents as the deck has them (no second copy of carico.txt)
I_PIU = float(re.search(r"pwl\(0 0 0\.5 ([\d.e-]+)\)", num(r"IPLUS ")).group(1))
I_MENO = float(re.search(r"pwl\(0 0 0\.5 ([\d.e-]+)\)", num(r"IMINUS ")).group(1))
R1 = float(num(r"RT1_SEC_Aa ").split()[3])
R2 = float(num(r"RT2_SEC_A ").split()[3])
R550 = float(num(r"RR550 raw_p raw_pr ").split()[3])
R551 = float(num(r"RR551 raw_mr raw_m ").split()[3])
num(r"XU501 raw_pr vplus_reg 0 en_u501 REGPSS ")
num(r"XU502 raw_mr vminus_reg 0 en_u502 REGMSS ")
num(r"XU503 raw_v vrelay_reg rly_ret en_u503 REGPSS ")
num(r"XU504 vrelay_reg v5_pre rly_ret ")

DIODI1 = ("dd501a", "dd501b", "dd501c", "dd501d")
DIODI2 = ("dd503a", "dd503b", "dd503c", "dd503d", "dd504")
DSCH = ("dd515", "dd516")
DPROT = ("dd510", "dd513", "dd511", "dd514")
NODI = {"dd501a": ("t1_sec_a", "raw_p"), "dd501b": ("t1_sec_b", "raw_p"),
        "dd501c": ("raw_m", "t1_sec_a"), "dd501d": ("raw_m", "t1_sec_b"),
        "dd503a": ("t2_sec_a", "rect_v"), "dd503b": ("t2_sec_b", "rect_v"),
        "dd503c": ("rly_ret", "t2_sec_a"), "dd503d": ("rly_ret", "t2_sec_b"),
        "dd504": ("rect_v", "raw_v"),
        "dd515": ("vplus_reg", "vplus"), "dd516": ("vminus", "vminus_reg"),
        "dd510": ("vplus_reg", "raw_pr"), "dd513": ("vplus_reg", "raw_pr"),
        "dd511": ("raw_mr", "vminus_reg"), "dd514": ("raw_mr", "vminus_reg")}
for d, (a, c) in NODI.items():
    num(r"%s %s %s " % (d.upper()[:2] + d[2:], a, c))


def somma(diodi):
    return " + ".join("(v(%s)-v(%s))*@%s[id]" % (NODI[d][0], NODI[d][1], d) for d in diodi)


SAVE = ("save all " + " ".join("@%s[id]" % d for d in DIODI1 + DIODI2 + DSCH + DPROT)
        + " v.xu501.vsns#branch v.xu502.vsns#branch v.xu503.vsns#branch @b.xu503.bo[i]")
LET = [
    "let pt1 = v(t1_sec_aa_e)*i(vt1a_sns) + v(t1_sec_ab_e)*i(vt1b_sns)",
    "let pt2 = (v(t2_sec_a_e)-v(t2_sec_b))*i(vt2_sns)",
    "let cu1 = %g*(i(vt1a_sns)^2 + i(vt1b_sns)^2)" % R1,
    "let cu2 = %g*i(vt2_sns)^2" % R2,
    "let dbr1 = " + somma(DIODI1),
    "let dbr2 = " + somma(DIODI2),
    "let rpre = (v(raw_p)-v(raw_pr))^2/%g + (v(raw_mr)-v(raw_m))^2/%g" % (R550, R551),
    "let reg1 = (v(raw_pr)-v(vplus_reg))*v.xu501.vsns#branch",
    "let reg2 = (v(vminus_reg)-v(raw_mr))*v.xu502.vsns#branch",
    "let dsch = " + somma(DSCH),
    "let dprot = " + somma(DPROT),
    "let reg3 = (v(raw_v)-v(vrelay_reg))*v.xu503.vsns#branch",
    "let paud = v(vplus)*%g - v(vminus)*%g" % (I_PIU, I_MENO),
    "let pvr = (v(vrelay_reg)-v(rly_ret))*@b.xu503.bo[i]",
]
GRANDEZZE = ("pt1", "pt2", "cu1", "cu2", "dbr1", "dbr2", "rpre", "reg1", "reg2", "dsch", "dprot",
             "reg3", "paud", "pvr")

righe = ["* L64b tb_calore - GENERATED by genera_calore.py from ../rete/tb_psu_rete.cir "
         "(the three steady states; averages over %g-%g s)" % (DA, TF)] + corpo[1:] \
    + [".control", "set numdgt=15", SAVE]
for nome in ("regime_m10", "regime_nom", "regime_p10"):
    righe += casi[nome] + LET
    righe += ["meas tran %s avg %s from=%g to=%g" % (g, g, DA, TF) for g in GRANDEZZE]
    righe += ["echo CALORE %s %s" % (nome, " ".join("%s=$&%s" % (g, g) for g in GRANDEZZE)),
              "destroy all"]
righe += [".endc", ".end"]
open(OUT, "w").write("\n".join(righe) + "\n")
print("scritto %s (I_PIU %g A, I_MENO %g A, R1 %g, R2 %g, R550 %g, R551 %g)"
      % (OUT, I_PIU, I_MENO, R1, R2, R550, R551))
