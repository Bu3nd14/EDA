#!/usr/bin/env python3
"""Scratch L29b: il mute graduale a monte con due LDR VTL5C4 sulla catena intera,
col metodo di V2 (ADR-038). Non e' il deck versionato.

Uso:  /usr/bin/python3 build.py OUTDIR [TD=3] [v2|v1]   ->  OUTDIR/ldr1k.cir, poi  ngspice -b ldr1k.cir
      (i .dat e il manifesto si scrivono in OUTDIR; le forme d'onda non si versionano)

IL CANALE e' il blocco "* >>> CANALE" ... "* <<< CANALE" di
spice/preamp/tb/tb_v2_mute_graduale.cir, COPIATO SENZA TOCCARLO (tolleranze
comprese: reltol=1e-6 vntol=1e-6 abstol=1e-12). Fuori dal blocco:
- RSRC portata a 1 T con alter, e al suo posto 1,5 ohm + la LDR IN SERIE (XLS) fra
  la sorgente e il selettore: il selettore resta chiuso (0,1 ohm), l'ordine non conta;
- la LDR VERSO MASSA (XLP) sull'ingresso del blocco A (INA), accanto a R_IN = 1 M;
- il comando dei LED: generatori di corrente ideali (B), catodo a massa, e 10 M
  dall'anodo a massa (trappola di L29b: un LED col solo generatore a 0 A non ha
  percorso DC e l'op fallisce senza errore);
- la profondita' d: una sola variabile 0 -> 1 in TD secondi dall'inserzione, e al
  rilascio indietro con la stessa velocita' da dove si trova (inversione a meta'
  compresa). PROFILO v2 (L29b, dopo la prima corsa):
    serie        20 mA a d = 0  ->  10 nA a d = 0,45, log-lineare;
    derivazione  10 nA a d = 0,5 ->  20 mA a d = 1, log-lineare.
  10 nA e' la corrente di riposo di ENTRAMBI i LED: sta sotto il ginocchio del buio
  della curva B (0,19 uA), la cella resta a 400 M, ma l'anodo non salta mai da 0 V.
  PROFILO v1 (la prima corsa): serie lineare 20 mA -> 0 per d in [0, 0.1];
  derivazione 0 fino a d = 0,35, poi 0,2 uA -> 20 mA. Due difetti, entrambi del
  profilo: al rilascio la serie tornava in 0,1 s (C2 1,25 V); il gradino 0 -> 0,2 uA
  faceva saltare di ~1,4 V l'anodo del LED della derivazione, che tramite CIO 0,5 pF
  colpisce un nodo a 1 M (A senza segnale 0,12-4,8 mV a d = 0,35);
- il rele' al jack: e' il contatto netto BJK* del blocco (col rimbalzo), chiuso a
  TI + TD + RITARDO_RELE (profondita' completa, con isteresi) e aperto a TR, prima
  che la derivazione si spenga. RITARDO_RELE = 0,5 s (v1: 50 ms): la serie si fa
  buia lentamente, e a 50 ms valeva solo 576 k (C2 di chiusura 1,05 mV a 1 kHz). Nella corsa "norele" non si chiude mai: la differenza con
  l'evento e' il solo rele'.
Curva B (nominale) per entrambe le LDR; le altre curve e la dispersione sono di L29c.
Modello comportamentale dal datasheet, con estrapolazione dichiarata.
"""
import os
import sys

R = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
OUT = os.path.abspath(sys.argv[1])
TD = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0     # la corsa della profondita'
PROFILO = sys.argv[3] if len(sys.argv) > 3 else "v2"
TB = os.path.join(R, "spice", "preamp", "tb", "tb_v2_mute_graduale.cir")
righe = open(TB).read().splitlines()
fine = next(i for i, r in enumerate(righe) if r.startswith("* <<< CANALE"))
L = [r.replace("@REPO@", R) for r in righe[:fine + 1]]
L[0] = "ldr1k.cir - L29b scratch: mute graduale a monte con due LDR VTL5C4, catena intera, 1 kHz"
L.insert(1, ".include %s/models/optocoupler/vtl5c4_comportamentale.lib" % R)

ION = 20e-3       # corrente del LED acceso
IMIN = 0.2e-6     # v1: sotto, buio per la curva B (genera_modello.py: buio da 0,19 uA)
IRIP = 10e-9      # v2: riposo dei LED, sotto il ginocchio del buio
RITARDO_RELE = 0.5 if PROFILO == "v2" else 0.05
if PROFILO == "v2":
    COMANDO = [
        "BILS 0 ALS I = %g * pow(%g, min(max(1 - V(DEP)/0.45, 0), 1))" % (IRIP, ION / IRIP),
        "BILP 0 ALP I = %g * pow(%g, min(max((V(DEP) - 0.5)/0.5, 0), 1))" % (IRIP, ION / IRIP),
    ]
else:
    COMANDO = [
        "BILS 0 ALS I = %g * max(1 - V(DEP)/0.1, 0)" % ION,
        "BILP 0 ALP I = V(DEP) < 0.35 ? 0 : %g * pow(%g, (V(DEP) - 0.35)/0.65)" % (IMIN, ION / IMIN),
    ]
L += [
    "* ---- L29b: le due LDR e il loro comando, fuori dal blocco CANALE ----",
    "VTI NTI 0 DC 1000",
    "VTR NTR 0 DC 2000",
    "VTD NTD 0 DC %g" % TD,
    "BDIN DIN 0 V = min(max((time - V(NTI))/V(NTD), 0), 1)",
    "BDEP DEP 0 V = time < V(NTR) ? V(DIN) : max(min(max((V(NTR) - V(NTI))/V(NTD), 0), 1)"
    " - (time - V(NTR))/V(NTD), 0)",
] + COMANDO + [
    "RALS ALS 0 10MEG",
    "RALP ALP 0 10MEG",
    "RSRC2 SRC SRCX 1.5",
    "XLS ALS 0 SRCX SELA VTL5C4_B",
    "XLP ALP 0 INA 0 VTL5C4_B",
]

MAN = os.path.join(OUT, "manifest.csv")
L += [
    ".control",
    "set d = .dat",
    "save v(mainjack) v(fixjack1) v(fixjack2) v(xls.xs) v(xlp.xs) v(dep) v(ina)",
    'echo "cella,file,variante,f_hz,amp,gm,rl,t_ins,t_rel,t_fine,tmax,tipo,rif_ins,rif_rel,t_grad" > %s' % MAN,
    "alter rsrc = 1e12",
    "alter rrgb = 0.1",
    "alter rrg10b = 0.1",
    "alter vphs dc = 1.5707963267948966",
    "alter vmhjk dc = 1",
]

TI = 1.0
T_RELE = TI + TD + RITARDO_RELE
TR = T_RELE + 1.0 if PROFILO == "v2" else 5.0        # 1 s di rele' chiuso: B2
TF = TR + TD + 3.0 if PROFILO == "v2" else 12.0      # 3 s dopo il rilascio: la ripresa


def corsa(nome, amp, ti, tr, rele_on, rele_off, tf, tmax=10e-6, stati=False):
    out = [
        "alter vamp dc = %s" % amp,
        "alter vti dc = %s" % ti, "alter vtr dc = %s" % tr,
        "alter vtijk dc = %s" % rele_on, "alter vtrjk dc = %s" % rele_off,
        "tran %g %s 0 %g" % (tmax, tf, tmax),
        "wrdata %s/%s$d v(mainjack) v(fixjack1) v(fixjack2)" % (OUT, nome),
    ]
    if stati:
        out.append("wrdata %s/%s_stati$d v(xls.xs) v(xlp.xs) v(dep) v(ina)" % (OUT, nome))
    return out + ["destroy all"]


def riga(cella, file, var, amp, t_ins, t_rel, tf, tmax, tipo, rins="-", rrel="-", tg=0.0):
    return 'echo "%s,%s.dat,%s,1000,%s,10,100k,%s,%s,%s,%g,%s,%s,%s,%s" >> %s' % (
        cella, file, var, amp, t_ins, t_rel, tf, tmax, tipo, rins, rrel, tg, MAN)


A = 3.818
# riferimenti: mai in mute (d = 0 sempre), sempre in mute (d = 1 e rele' chiuso da t = 0)
L += corsa("mai", A, 1000, 2000, 1000, 2000, TF)
L += [riga("mai", "mai", "rif", A, TI, TR, TF, 10e-6, "rif_mai")]
L += corsa("sempre", A, -10, 1000, -10, 1000, TF)
L += [riga("sempre", "sempre", "rif", A, TI, TR, TF, 10e-6, "rif_sempre")]
# l'evento: inserzione a TI, rele' a TI+TD+50 ms, rilascio a TR (rele' aperto a TR)
L += corsa("ev", A, TI, TR, T_RELE, TR, TF, stati=True)
TG = TD + RITARDO_RELE if PROFILO == "v2" else TD + 0.1   # C2 e B2 coprono tutta la sequenza
L += [riga("ev", "ev", "ldr_%s_td%g" % (PROFILO, TD) if PROFILO == "v2" else "ldr_td3", A, TI, TR, TF, 10e-6, "evento", "sempre", "mai", TG)]
# lo stesso evento senza rele': la differenza e' il rele' soltanto
L += corsa("norele", A, TI, TR, 1000, 2000, TF, stati=True)
L += [riga("norele", "norele", "rif", A, TI, TR, TF, 10e-6, "rif_seq")]
L += [riga("rele", "ev", "rele_contro_norele", A, T_RELE, TR, TF, 10e-6, "evento", "norele", "norele", 0.0)]
# inversione a meta': il rilascio comincia a meta' della rampa della derivazione
DINV = 0.75 if PROFILO == "v2" else 0.6
TINV = TI + DINV * TD
TFI = TINV + DINV * TD + 3.0 if PROFILO == "v2" else 8.6
L += corsa("inv", A, TI, TINV, 1000, 2000, TFI, stati=True)
L += [riga("inv", "inv", "inversione_d%02d" % round(100 * DINV) if PROFILO == "v2" else "inversione_d06", A, TI, TINV, TFI, 10e-6, "evento", "sempre", "mai", DINV * TD)]
# pavimento di C2: la corsa mai in mute con un altro TMAX, letta come C2 contro "mai"
L += corsa("mai7u", A, 1000, 2000, 1000, 2000, TF, tmax=7e-6)
for k, t in enumerate((TI, T_RELE, TR, TINV)):
    L += [riga("pav%d" % k, "mai7u", "pavimento", A, t, 1000, TF, 7e-6, "pav_num", "mai")]
# A senza segnale
L += corsa("lzmai", 0, 1000, 2000, 1000, 2000, TF)
L += [riga("lzmai", "lzmai", "rif", 0, TI, TR, TF, 10e-6, "rif_mai")]
L += corsa("lzsempre", 0, -10, 1000, -10, 1000, TF)
L += [riga("lzsempre", "lzsempre", "rif", 0, TI, TR, TF, 10e-6, "rif_sempre")]
L += corsa("lzev", 0, TI, TR, T_RELE, TR, TF, stati=True)
L += [riga("lzev", "lzev", "ldr_%s_td%g" % (PROFILO, TD) if PROFILO == "v2" else "ldr_td3", 0, TI, TR, TF, 10e-6, "evento", "lzsempre", "lzmai", TG)]
L += [riga("lzrele", "lzev", "rele_contro_norele", 0, T_RELE, TR, TF, 10e-6, "evento", "lzsempre", "lzmai", 0.0)]
L += [".endc", ".end"]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "ldr1k.cir"), "w").write("\n".join(L) + "\n")
print("scritto", os.path.join(OUT, "ldr1k.cir"))
