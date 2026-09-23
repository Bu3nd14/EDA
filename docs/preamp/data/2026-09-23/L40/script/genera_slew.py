#!/usr/bin/env python3
"""L40, ESPLORAZIONE - slew rate e 20 kHz a fondo scala, blocco B a +10 dB.

Lo stesso metodo di L12 (data/2026-09-14/L12/esplorazione/deck/slew3_B.cir, che
ADR-025 ha usato per scartare C124 = 1 nF: slew in discesa 1,79 V/us, e a 20 kHz
fondo scala la sinusoide in slew con +0,38 V di continua), portato al blocco di
oggi: due contatti R_g (L27, +10 dB = rrg e rrg10 chiusi, x3,152) e i modelli
del costruttore (le stesse righe .include di tb_loop.cir).

Per ogni (C124, R128) e per ogni riga extra di alter passata come variante:
  - 20 kHz, 3,818 V di picco all'ingresso (12,03 V di picco in uscita, pendenza
    ideale 1,512 V/us) e meta' ampiezza: massimo, minimo, media (la continua
    indotta dallo slew), pendenze massime;
  - gradino +-1,9 V all'ingresso: SR in salita e in discesa.
Nodi del deck: VSRCN, NMIDS, OUTA, JACK (limitations #24).

Uso: /usr/bin/python3 genera_slew.py <fase> <etichetta> "<alter>"...
  genera <fase>/slew__<etichetta>.cir; le alter valgono per tutta la corsa.
  C124 e R128 si spazzano dentro: CM e RR qui sotto.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L40 = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L40, *[".."] * 5))
SRC = os.path.join(ROOT, "spice", "preamp", "tb", "tb_loop.cir")
CM = ["470p", "560p", "680p", "820p", "1n", "1.2n"]
RR = ["1.69k", "1.33k"]

fase, etich = sys.argv[1:3]
alters = sys.argv[3:]
inc = [r for r in open(SRC).read().split("\n") if r.startswith(".include")]
testa = ["slew__%s.cir - L40 ESPLORAZIONE: slew rate e 20 kHz a fondo scala, blocco B +10 dB; %s"
         % (etich, "; ".join(alters) or "nessuna alter"),
         "* generato da genera_slew.py; metodo di L12 slew3_B.cir, blocco di oggi"] + inc + [
    "", "VPP VPLUS 0 DC 15", "VMM VMINUS 0 DC -15",
    "VSIN  VSRCN NMIDS SIN(0 3.818 20k)",
    "VSTEP NMIDS 0 PULSE(0 0 1m 1u 1u 1m 10m)",
    "RSRCB VSRCN IN 1.5",
    "* +10 dB: i due contatti chiusi (L27, ADR-026)",
    "CSTRAY   RG   0 15p", "RRG      RG   0 0.1",
    "CSTRAY10 RG10 0 15p", "RRG10    RG10 0 0.1",
    "RISO   OUT OUTA 47", "COUT   OUTA JACK 4.7u", "RBLEED JACK 0 220k", "RLOAD  JACK 0 100k", ""]
ctl = [".control"] + alters + [
    'echo "cm,r128,amp_in,vo_max,vo_min,vo_mean_dc,slope_pos_vus,slope_neg_vus,ideal_slope_vus,gain" > slew_tab.csv',
    'echo "cm,r128,sr_rise_vus,sr_fall_vus" > slew_step.csv',
    "foreach r %s" % " ".join(RR), "  alter r128 = $r",
    "  foreach cm %s" % " ".join(CM), "    alter c124 = $cm",
    "    show c124 : capacitance", "    show r128 : resistance",
    "    foreach amp 3.818 1.909",
    "      alter @vsin[sin] = [ 0 $amp 20k ]",
    "      alter @vstep[pulse] = [ 0 0 1m 1u 1u 1m 10m ]",
    "      tran 10n 1m",
    "      let dvo = deriv(v(out))",
    "      meas tran vomax max v(out) from=0.7m to=0.95m",
    "      meas tran vomin min v(out) from=0.7m to=0.95m",
    "      meas tran vodc avg v(out) from=0.7m to=0.95m",
    "      meas tran vimax max v(in) from=0.7m to=0.95m",
    "      meas tran sp max dvo from=0.7m to=0.95m",
    "      meas tran sn min dvo from=0.7m to=0.95m",
    "      let spv = sp/1e6", "      let snv = sn/1e6",
    "      let gg = (vomax-vomin)/(2*vimax)",
    "      let ideal = 2*3.14159265*20e3*gg*vimax/1e6",
    '      echo "$cm,$r,$amp,$&vomax,$&vomin,$&vodc,$&spv,$&snv,$&ideal,$&gg" >> slew_tab.csv',
    "      destroy all", "    end",
    "    alter @vsin[sin] = [ 0 0 20k ]",
    "    alter @vstep[pulse] = [ -1.9 1.9 1m 1u 1u 1m 10m ]",
    "    tran 10n 3m",
    "    let dvo = deriv(v(out))",
    "    meas tran srr max dvo from=0.95m to=1.5m",
    "    meas tran srf min dvo from=1.95m to=2.5m",
    "    let srrv = srr/1e6", "    let srfv = srf/1e6",
    '    echo "$cm,$r,$&srrv,$&srfv" >> slew_step.csv',
    "    destroy all", "  end", "end", ".endc", ".end", ""]
d = os.path.join(L40, fase)
os.makedirs(d, exist_ok=True)
p = os.path.join(d, "slew__%s.cir" % etich)
open(p, "w").write("\n".join(testa + ctl))
print(p)
