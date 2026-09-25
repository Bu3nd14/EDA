#!/usr/bin/env python3
"""L36: la corsa al rilascio del mute (ADR-030), simulata con ngspice.

Il circuito delle bobine di K1 + K11 (gain_interlock.py), a +3 dB, con i contatti di
K6 comandati nel tempo e il buco di trasferimento spazzato. Tre varianti:

  ingenua  - la strada B come ADR-030 la descrive e basta: comando da VTRIM (NC di
             K6) e tenuta da VHOLD (NO di K6) attraverso il NO di K11. E' il
             controfattuale: senza il polo ponte di SW2.
  progetto - con il polo ponte: VRELAY -> SW2 polo b -> H3 -> NO di K11 -> G3_HI.
  residuo  - il progetto, con la manopola girata a 0 dB FUORI mute (t = 15 ms) e il
             mute inserito dopo (t = 30 ms): quando cade K1, dopo l'apertura del NO
             di K6? E' il caso che L36 dichiara ordinato ma non chiuso dal datasheet.

IL MODELLO DEL RELE', DICHIARATO. Il datasheet del G6K (en-g6k.pdf p. 3) da' solo:
237 ohm +/-10 % a 5 V, must operate 80 % max, must release 10 % min, operate e
release 3 ms max. NON da' l'induttanza, ne' un tempo minimo, ne' il trasferimento.
  - bobina: R (213 / 237 / 261 ohm) in serie a L IPOTETICA, spazzata 5-200 mH;
  - ancora: interruttore a isteresi sulla corrente di bobina. Si chiude a
    4 V / R (must operate, 80 % di 5 V), si apre a FRAZ * 5 V / R con FRAZ spazzata
    0,1-0,7 (il 10 % e' il minimo garantito; di piu' e' il caso peggiore per chi
    deve tenere). Nessun ritardo meccanico accreditato: l'ancora si apre appena la
    corrente scende sotto soglia. E' il verso peggiore per la tenuta;
  - K6: NC e NO comandati nel tempo (VPWL), con il buco fra l'apertura dell'uno e
    la chiusura dell'altro spazzato 0,1-3 ms (3 ms = il release massimo intero);
  - diodi: modelli generici, NON del costruttore (la parte si sceglie al giro BOM):
    Schottky IS=31.7u N=1.373 RS=0.051; 1N4148 IS=2.52n N=1.752 RS=0.568.
Le cifre di corrente dipendono da questo modello. Quello che la simulazione prova
e' la forma: nella variante ingenua la tenuta dipende da L, FRAZ e buco; nel
progetto la bobina non perde mai l'alimentazione, qualunque siano.

Limitazioni del repo rispettate: niente wrdata (le misure sono .meas, #30 non si
applica); le PWL sono sorgenti V indipendenti, che tengono l'ultimo valore (#31
riguarda pwl() nelle sorgenti B); nessun if in .control (#32); ogni log e' letto
per "Transient op started" e la corsa che lo contiene non vale (#33).

Uso: corsa.py <cartella di lavoro per i deck e i log> <csv di uscita> [processi]
"""
import csv
import itertools
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

NGSPICE = "/opt/homebrew/bin/ngspice"

LS = (5e-3, 20e-3, 50e-3, 100e-3, 200e-3)
GAPS = (0.1e-3, 0.3e-3, 1e-3, 3e-3)
RS = (213.0, 237.0, 261.0)
FRAZ = (0.1, 0.3, 0.5, 0.7)
VRS = (4.75, 5.0)

T_REL = 5e-3     # il mute si rilascia: NC di K6 si apre
T_KNOB = 15e-3   # residuo: la manopola va a 0 dB fuori mute
T_INS = 30e-3    # il mute si inserisce: NO di K6 si apre
T_END = 50e-3


def pwl(points):
    return "pwl(" + " ".join(f"{t:.9g} {v:g}" for t, v in points) + ")"


def deck(var, L, gap, R, fraz, vr):
    iop = 4.0 / R                   # must operate, 80 % di 5 V
    irel = fraz * 5.0 / R
    vt, vh = (iop + irel) / 2 * 1e3, (iop - irel) / 2 * 1e3   # 1 V per mA
    e = 1e-6
    # K6: NC chiuso in mute; si apre a T_REL, si richiude a T_INS + gap.
    nc = pwl([(0, 1), (T_REL, 1), (T_REL + e, 0), (T_INS + gap, 0), (T_INS + gap + e, 1)])
    # NO: si chiude a T_REL + gap, si apre a T_INS.
    no = pwl([(0, 0), (T_REL + gap, 0), (T_REL + gap + e, 1), (T_INS, 1), (T_INS + e, 0)])
    if var == "residuo":
        knob = pwl([(0, 1), (T_KNOB, 1), (T_KNOB + e, 0)])
    else:
        knob = pwl([(0, 1)])
    ponte = "" if var == "ingenua" else "SPB vrelay h3 knob 0 swc\n"
    return f"""L36 corsa {var} L={L} gap={gap} R={R} fraz={fraz} vr={vr}
* titolo: la prima riga e' sempre il titolo (CLAUDE.md)
VR vrelay 0 {vr}
VNC cnc 0 {nc}
VNO cno 0 {no}
VKN knob 0 {knob}
* K6: i due NC in serie come un contatto solo; il NO del polo 1 da' VHOLD
SNC vrelay vtrim cnc 0 swc
SNO vrelay vhold cno 0 swc
D3 0 vtrim d4148
* SW2: polo a (comando) e, nel progetto, polo b (ponte)
SPA vtrim c3 knob 0 swc
{ponte}D10 c3 g3hi dsch
D12 vhold h3 d4148
* NO di K11, comandato dalla corrente della sua bobina
SK11 h3 g3hi a11 0 swk
D14 0 g3hi d4148
* K1 e K11: bobine in parallelo, R + L ipotetica
VS1 g3hi n1 0
L1 n1 m1 {L:g}
R1 m1 0 {R:g}
VS11 g3hi n11 0
L11 n11 m11 {L:g}
R11 m11 0 {R:g}
H1 a1 0 VS1 1000
H11 a11 0 VS11 1000
* l'ancora di K1 e' solo osservata: la sua corrente di bobina e' quella di K11
RA1 a1 0 1meg
RF1 vtrim 0 100meg
RF2 c3 0 100meg
RF3 h3 0 100meg
RF4 vhold 0 100meg
.model swc sw vt=0.5 vh=0.1 ron=0.1 roff=1e9
.model swk sw vt={vt:.6g} vh={vh:.6g} ron=0.1 roff=1e9
.model dsch d is=31.7u n=1.373 rs=0.051
.model d4148 d is=2.52n n=1.752 rs=0.568
.control
tran 1u {T_END:g} 0 1u
meas tran imin_rel min i(VS1) from={T_REL:g} to={T_INS - 1e-4:g}
meas tran ifin_out find i(VS1) at={T_INS - 5e-4:g}
meas tran imin_ins min i(VS1) from={T_INS:g} to={T_END - 1e-4:g}
meas tran ifin find i(VS1) at={T_END - 5e-4:g}
meas tran i0 find i(VS1) at={T_REL - 5e-4:g}
meas tran tdrop when i(VS1)={irel:.6g} fall=1 from={T_INS:g}
echo "RISULTATO" $&imin_rel $&ifin_out $&imin_ins $&ifin $&i0 $&tdrop
quit
.endc
.end
"""


def corri(args):
    var, L, gap, R, fraz, vr, work = args
    nome = f"{var}_L{L * 1e3:g}m_g{gap * 1e3:g}m_R{R:g}_f{fraz:g}_v{vr:g}"
    cir = os.path.join(work, nome + ".cir")
    with open(cir, "w") as fh:
        fh.write(deck(var, L, gap, R, fraz, vr))
    r = subprocess.run([NGSPICE, "-b", cir], capture_output=True, text=True)
    log = r.stdout + r.stderr
    with open(os.path.join(work, nome + ".log"), "w") as fh:
        fh.write(log)
    m = re.search(r"RISULTATO\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(\S*)", log)
    top = "Transient op started" in log
    vals = [float(x) for x in m.groups()[:5]] if m else [float("nan")] * 5
    td = m.group(6) if m else ""
    try:
        tdrop = float(td) - T_INS
    except ValueError:
        tdrop = float("nan")      # la corrente non scende sotto soglia
    irel = fraz * 5.0 / R
    esito = "OPT" if top else ("ERR" if not m or r.returncode else "ok")
    tiene_rel = vals[0] > irel
    tiene_ins = vals[2] > irel
    return dict(variante=var, L_mH=L * 1e3, gap_ms=gap * 1e3, R=R, fraz=fraz, vrelay=vr,
                irel_mA=irel * 1e3, i0_mA=vals[4] * 1e3, imin_rilascio_mA=vals[0] * 1e3,
                ifuori_mA=vals[1] * 1e3, imin_inserimento_mA=vals[2] * 1e3,
                ifine_mA=vals[3] * 1e3, tiene_al_rilascio=tiene_rel,
                tiene_all_inserimento=tiene_ins, tcaduta_dopo_NO_K6_us=tdrop * 1e6,
                rc=r.returncode, corsa=esito)


def main(argv):
    work, out = argv[1], argv[2]
    nproc = int(argv[3]) if len(argv) > 3 else 8
    os.makedirs(work, exist_ok=True)
    jobs = [(v, L, g, R, f, vr, work)
            for v in ("ingenua", "progetto", "residuo")
            for L, g, R, f, vr in itertools.product(LS, GAPS, RS, FRAZ, VRS)]
    with ThreadPoolExecutor(nproc) as ex:
        rows = list(ex.map(corri, jobs))
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} corse -> {out}")
    print("esiti corsa:", {e: sum(r['corsa'] == e for r in rows) for e in ("ok", "OPT", "ERR")})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
