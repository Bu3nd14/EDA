#!/usr/bin/env python3
"""L45d2b1: il dimensionamento del rivelatore di continua (ADR-072). Solo stdlib, /usr/bin/python3.

Uso: dimensiona.py            stampa i numeri e scrive dimensiona.csv accanto a questo file
     dimensiona.py --prova    le formule chiuse contro un'integrazione a passi

IL PRINCIPIO (perche' non un filtro): un passa-basso che vede 0,95 V di continua entro ~95 ms scatta
anche sul primo semiperiodo di un basso a 20 Hz da 14 V (../studio/studio_filtro.py, 1-4 poli). Il
rivelatore misura invece la PERSISTENZA: per ogni uscita una finestra a +-VT e un temporizzatore che
riparte da zero ogni volta che l'uscita rientra nella finestra. Scatta se l'uscita resta fuori, dallo
stesso lato, per T_HOLD di fila. Nella banda di E9 (>= 20 Hz) la musica non ha continua: un segnale
periodico a 20 Hz passa per zero almeno una volta ogni 50 ms. Un guasto tiene l'uscita da una parte.

L'ALIMENTAZIONE (scelta 8 di ADR-072): il filo del rail + aperto fra le schede deve essere visto. Il
rivelatore non vive dei soli rail audio: VDP e' il maggiore fra VPLUS e VRELAY (due 1N4148W), e
tutto il rivelatore sta fra VDP e GND. Ogni uscita arriva ai comparatori spostata a meta' di VDP:
    S = (v + 2 VDP) / 4        (300k da v, 150k da VDP, 300k a GND, 0,1 %)
cosi' S resta dentro [0, VDP] per v fra -15,3 e +15,3 V anche con VDP = VRELAY - 0,65 = 11,35 V. La
finestra, le soglie e il riferimento dello scatto sono frazioni di VDP: ratiometrici.

I VINCOLI
  - P10 (ADR-069): il jack a vuoto sopra 0,87 V per al piu' 100 ms. Il jack e' accoppiato in
    alternata (tau 1,03 s il principale, 1,1 s le fisse): una continua VX all'uscita del blocco lo
    tiene sopra 0,87 V oltre 100 ms per VX > ~0,95 V. Il taglio deve arrivare entro ~95 ms per ogni
    VX >= 0,95 V, e VT sta sotto con margine.
  - La musica: T_HOLD minimo > 50 ms (un periodo a 20 Hz, il caso peggiore di un'onda periodica
    asimmetrica: una forma a impulsi resta da una parte quasi tutto il periodo).
"""
import csv
import itertools
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))

VDP_NOM = 15.0 - 0.65       # VPLUS attraverso un 1N4148W a ~1,3 mA
VDP_RELAY = 12.0 - 0.65     # VPLUS assente: VRELAY attraverso l'altro
# ---- lo spostamento d'ingresso, 0,1 %
R_V, R_D, R_G = 300e3, 150e3, 300e3
# ---- la compensazione: dall'uscita a VMINUS, la stessa corrente che lo spostamento mette dentro
R_COMP = 634e3
C_F = 4.7e-9                # su S: tau = (300k || 150k || 300k) 4,7n = 0,35 ms (3,5 ms nella prima
                            # stesura: mediava il clip asimmetrico di B a 1 kHz, ../banco/)
# ---- l'inibizione all'accensione: POR da VDP per 1,43M su 100n, contro VDP / 2
R_POR, C_POR = 1.43e6, 100e-9
# ---- la catena delle soglie, 0,1 %: VDP - R_A - VTHP - R_B - VTHM - R_A - GND
R_A, R_B = 100e3, 4.12e3
# ---- il temporizzatore: C_T a GND, caricato da VDP per R_T; il comparatore lo tiene a V_SAT
R_T, C_T = 976e3, 100e-9
V_SAT = (0.2, 0.6)          # SBOS589D: <= 600 mV a 0 mA; qui ~15 uA
# ---- lo scatto: il massimo dei temporizzatori (diodi 1N4148W) contro REF = VDP / 2
R_REF_TOP, R_REF_BOT = 100e3, 100e3
VF = (0.30, 0.55)
# ---- tolleranze
TOL_R01, TOL_R1, TOL_C = 0.001, 0.01, 0.05
VOS = 5.5e-3                # SBOS589D, -40...+125 C
T_RELE = 3e-3               # G6K, rilascio massimo (en-g6k.pdf p. 3)
T_CATENA = 1e-3             # comparatore, NPN, diodi sui gate, Q501: microsecondi; 1 ms di margine


def s_di(v, vdp, rv=R_V, rd=R_D, rg=R_G):
    gv, gd, gg = 1 / rv, 1 / rd, 1 / rg
    return (v * gv + vdp * gd) / (gv + gd + gg)


def soglie(vdp, ra1=R_A, rb=R_B, ra2=R_A):
    i = vdp / (ra1 + rb + ra2)
    return vdp - i * ra1, i * ra2          # VTHP, VTHM


def vt(vdp=VDP_NOM, k=None):
    """La soglia riportata all'uscita del blocco: il v per cui S = VTHP (e -VT per VTHM).
    k: fattori di tolleranza (rv, rd, rg, ra1, rb, ra2) e offset (vos_p, vos_m)."""
    k = k or (1, 1, 1, 1, 1, 1, 0, 0)
    rv, rd, rg = R_V * k[0], R_D * k[1], R_G * k[2]
    vthp, vthm = soglie(vdp, R_A * k[3], R_B * k[4], R_A * k[5])
    vthp += k[6]
    vthm += k[7]
    gv, gd, gg = 1 / rv, 1 / rd, 1 / rg
    vp = (vthp * (gv + gd + gg) - vdp * gd) / gv
    vm = (vthm * (gv + gd + gg) - vdp * gd) / gv
    return vp, vm


def t_hold(r, c, vsat, vf, vdp=VDP_NOM, kref=1.0):
    ref = vdp * R_REF_BOT / (R_REF_TOP * kref + R_REF_BOT)
    return r * c * math.log((vdp - vsat) / (vdp - ref - vf))


def t_filtro(vx, v_t, vdp=VDP_NOM):
    """Il ritardo del filtro su S: il gradino VX all'uscita sposta S di VX / 4 con
    tau = (R_V || R_D || R_G) C_F; S passa la soglia dopo tau ln(VX / (VX - VT))."""
    tau = C_F / (1 / R_V + 1 / R_D + 1 / R_G)
    return tau * math.log(vx / (vx - v_t)) if vx > v_t else float("inf")


def angoli_vt():
    vps, vms = [], []
    for f in itertools.product((1 - TOL_R01, 1 + TOL_R01), repeat=6):
        for o in itertools.product((-VOS, VOS), repeat=2):
            for vdp in (VDP_NOM, VDP_RELAY):
                p, m = vt(vdp, f + o)
                vps.append(p)
                vms.append(m)
    return min(vps), max(vps), min(vms), max(vms)


def angoli_t():
    out = []
    for kr in (1 - TOL_R1, 1 + TOL_R1):
        for kc in (1 - TOL_C, 1 + TOL_C):
            for vs in V_SAT:
                for vf in VF:
                    for vdp in (VDP_NOM * 0.99, VDP_NOM * 1.01, VDP_RELAY):
                        for kref in (0.98, 1.02):
                            out.append(t_hold(R_T * kr, C_T * kc, vs, vf, vdp, kref))
    return min(out), max(out)


def prova():
    vs, vf = 0.35, 0.45
    att = t_hold(R_T, C_T, vs, vf)
    v, t, dt = vs, 0.0, 1e-6
    soglia = VDP_NOM / 2 + vf
    while v < soglia:
        v += (VDP_NOM - v) / (R_T * C_T) * dt
        t += dt
    ok = abs(t - att) < 2e-5
    print("t_hold: forma chiusa %.3f ms, a passi %.3f ms -> %s" % (att * 1e3, t * 1e3, "OK" if ok else "SBAGLIATO"))
    # lo spostamento: S a v = 0 deve essere VDP / 2, e la soglia riportata deve dare S = VTHP
    vp, vm = vt()
    vthp, vthm = soglie(VDP_NOM)
    ok2 = abs(s_di(0, VDP_NOM) - VDP_NOM / 2) < 1e-9 and abs(s_di(vp, VDP_NOM) - vthp) < 1e-9 \
        and abs(s_di(vm, VDP_NOM) - vthm) < 1e-9
    print("spostamento: S(0) = %.4f V, S(VT) = %.4f V = VTHP %.4f -> %s" % (
        s_di(0, VDP_NOM), s_di(vp, VDP_NOM), vthp, "OK" if ok2 else "SBAGLIATO"))
    # il filtro, a passi sul nodo S
    tau = C_F / (1 / R_V + 1 / R_D + 1 / R_G)
    s0, s, t = s_di(0, VDP_NOM), s_di(0, VDP_NOM), 0.0
    sf = s_di(0.95, VDP_NOM)
    while s < vthp:
        s += (sf - s) / tau * dt
        t += dt
    ok3 = abs(t - t_filtro(0.95, vp)) < 2e-5
    print("filtro, 0,95 V: forma chiusa %.3f ms, a passi %.3f ms -> %s" % (
        t_filtro(0.95, vp) * 1e3, t * 1e3, "OK" if ok3 else "SBAGLIATO"))
    return 0 if ok and ok2 and ok3 else 1


def main():
    if "--prova" in sys.argv:
        sys.exit(prova())
    righe = []

    def r(nome, valore, nota):
        righe.append((nome, valore, nota))
        print("%-44s %16s  %s" % (nome, valore, nota))

    vp, vm = vt()
    vp_lo, vp_hi, vm_lo, vm_hi = angoli_vt()
    r("VDP (V)", "%.1f / %.1f" % (VDP_NOM, VDP_RELAY), "da VPLUS / da VRELAY (rail + assente)")
    r("S a v = -15,3 / +15,3 V (V)", "%.2f / %.2f" % (s_di(-15.3, VDP_RELAY), s_di(15.3, VDP_NOM)),
      "dentro [0, VDP] ai due estremi (SBOS589D: VCM da V- a V+)")
    r("VT nominale, + / - (V)", "%.3f / %.3f" % (vp, vm), "300k/150k/300k, 100k/4,12k/100k")
    r("VT +: min / max (V)", "%.3f / %.3f" % (vp_lo, vp_hi), "R 0,1 %, offset 5,5 mV, VDP dai due lati")
    r("VT -: min / max (V)", "%.3f / %.3f" % (vm_lo, vm_hi), "idem")
    tn = t_hold(R_T, C_T, 0.35, 0.45)
    tmin, tmax = angoli_t()
    r("T_HOLD nominale (ms)", "%.1f" % (tn * 1e3), "R_T 976k, C_T 100n C0G, REF = VDP / 2")
    r("T_HOLD min / max (ms)", "%.1f / %.1f" % (tmin * 1e3, tmax * 1e3), "R 1 %, C 5 %, V_SAT, VF, VDP, REF 2 %")
    r("musica: margine sul periodo a 20 Hz (ms)", "%.1f" % ((tmin - 0.050) * 1e3), "T_HOLD min - 50 ms; > 0 = nessuno scatto")
    r("musica: frequenza periodica piu' bassa (Hz)", "%.1f" % (1 / tmin), "1 / T_HOLD min")
    vtw = max(vp_hi, -vm_lo)
    for vx in (0.81, 0.95, 1.5, 5.0, 14.9):
        tf = t_filtro(vx, vtw)
        tot = tf + tmax + T_CATENA + T_RELE
        r("taglio peggiore, VX = %.2f V (ms)" % vx, "%.1f" % (tot * 1e3),
          "filtro %.1f + T_HOLD max + catena + rele' 3 ms; P10: <= 100" % (tf * 1e3))
    vbe = 0.65
    for vdp in (VDP_NOM, VDP_RELAY):
        ib = (vdp - vbe) / 94e3 - vbe / 10e3
        r("NPN: corrente di base, VDP %.1f V (uA)" % vdp, "%.0f" % (ib * 1e6), "MMBT5551, hFE >= 80: >= %.0f mA" % (ib * 80e3))
    r("NPN: soglia di TRIP (V)", "%.2f" % (vbe * 57e3 / 10e3), "VDP sotto i 2,2 V del comparatore non lo accende")
    r("linea: corrente da assorbire (mA)", "%.1f" % ((5 - 0.3) / 10e3 * 4 * 1e3),
      "pull-up 10k + R513, R520, R537 (10k) dai 5 V attraverso i BAT54")
    # la corrente che il rivelatore mette nell'uscita a 0 V: lo spostamento la spinge dentro da S0,
    # R_COMP la toglie verso VMINUS (ADR-079)
    for vdp, vm, nome in ((VDP_NOM, 15.05, "VDP da VPLUS"), (VDP_RELAY, 15.05, "VDP da VRELAY"),
                          (VDP_NOM, 0.0, "VMINUS assente")):
        i_in = s_di(0, vdp) / R_V
        i_out = vm / R_COMP
        r("corrente nell'uscita a 0 V, %s (uA)" % nome, "%+.2f" % ((i_in - i_out) * 1e6),
          "%.1f uA dallo spostamento, %.1f verso VMINUS per 634k" % (i_in * 1e6, i_out * 1e6))
    t_por = R_POR * C_POR * math.log(2)
    r("inibizione all'accensione (ms)", "%.0f / %.0f / %.0f" % (
        t_por * 1e3, t_por * (1 - TOL_R1) * (1 - TOL_C) * 1e3, t_por * (1 + TOL_R1) * (1 + TOL_C) * 1e3),
      "1,43M x 100n x ln 2, nominale / min / max; i jack si chiudono >= 150 ms dopo i rail buoni")
    i_vdp = 14 * 55e-6 + 6 * VDP_NOM / 2 / R_D + 12 * VDP_NOM / 2 / R_T + VDP_NOM / (2 * R_A + R_B) \
        + VDP_NOM / (R_REF_TOP + R_REF_BOT)
    r("VDP: corrente a riposo (mA)", "%.2f" % (i_vdp * 1e3), "14 canali da 55 uA, spostamenti, temporizzatori, partitori")
    with open(os.path.join(QUI, "dimensiona.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["grandezza", "valore", "nota"])
        w.writerows(righe)


if __name__ == "__main__":
    main()
