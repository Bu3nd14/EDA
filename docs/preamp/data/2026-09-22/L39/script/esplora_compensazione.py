#!/usr/bin/env python3
"""L39, ESPLORAZIONE - nessun valore del sorgente cambia. Coi modelli del
costruttore V1 cade a 0 dB (blocco B 55,55 gradi, buffer 54,92, blocco A 57,93).
Quanto dovrebbero valere C_f (C137, OUT-FB, 330 p da ADR-025) o il Miller
(C124, NX-NHI, 470 p) per tornare sopra 60? E' una misura per l'utente, che
decide: non e' una proposta applicata.

Scrive esplorazione/tb_loop_comp.cir: il circuito di spice/preamp/tb/tb_loop.cir
fino a .control, byte per byte (quindi gli include del costruttore di L39), e un
.control che per ogni (C137, C124) spazza 0 e +10 dB, 100 k e 10 k, sorgente
1 mohm e 2,611 k, sonda al jack (pos 1, ADR-024), cavo 1 fF - 4,7 nF. Tabella
tb_loop_comp.csv. La prima riga (330p, 470p) deve ridare le celle di dopo/tb_loop:
e' il controllo che l'alter non ha sbagliato bersaglio (limitations #22, #29).

Uso: /usr/bin/python3 esplora_compensazione.py   poi run_simulation.sh sul deck
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(QUI, *[".."] * 6))
SRC = os.path.join(ROOT, "spice", "preamp", "tb", "tb_loop.cir")
OUT = os.path.join(os.path.dirname(QUI), "esplorazione", "tb_loop_comp.cir")

righe = open(SRC).read().split("\n")
c0 = righe.index(".control")
testa = righe[:c0]
testa[0] = ("tb_loop_comp.cir - L39 ESPLORAZIONE: V1 coi modelli del costruttore "
            "al variare di C_f (C137) e del Miller (C124). Generato da "
            "esplora_compensazione.py dal circuito di tb_loop.cir")
COPPIE = [("330p", "470p"), ("390p", "470p"), ("470p", "470p"), ("560p", "470p"),
          ("680p", "470p"), ("820p", "470p"), ("1n", "470p"),
          ("330p", "560p"), ("330p", "680p"), ("330p", "820p"), ("330p", "1n")]
ctl = [".control", "alter r109 = 1G", "set units = degrees",
       'echo "cf,cm,mode,rload,rsrc,cprobe,fcross_hz,pm_deg,tdb_10hz" > tb_loop_comp.csv',
       "alter cnode = 1f"]
for cf, cm in COPPIE:
    ctl += ["alter c137 = %s" % cf, "alter c124 = %s" % cm,
            "foreach mode 0 10",
            "  if $mode = 0", "    alter rrg = 1G", "    alter rrg10 = 1G", "  end",
            "  if $mode = 10", "    alter rrg = 0.1", "    alter rrg10 = 0.1", "  end",
            "  foreach rl 100k 10k", "    alter rload = $rl",
            "    foreach rs 1m 2.611k", "      alter rsrcb = $rs",
            "      foreach cab 1f 470p 1n 1.5n 2.2n 2.7n 3.3n 4.7n",
            "        alter ccable = $cab",
            "        ac dec 100 1 100meg",
            "        let T = v(fb)/v(g2)", "        let Tdb = db(T)", "        let Tph = ph(T)",
            "        meas ac fcross when Tdb=0", "        meas ac pmarg find Tph when Tdb=0",
            "        meas ac tdc find Tdb at=10",
            '        echo "%s,%s,$mode,$rl,$rs,$cab,$&fcross,$&pmarg,$&tdc" >> tb_loop_comp.csv'
            % (cf, cm),
            "        destroy all", "      end", "    end", "  end", "end"]
ctl += ["print @c137[capacitance] @c124[capacitance]", ".endc", ".end", ""]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write("\n".join(testa + ctl))
print("scritto", OUT, "-", len(COPPIE), "coppie")
