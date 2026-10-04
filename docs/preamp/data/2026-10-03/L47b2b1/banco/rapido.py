"""rapido.py - L47b2b1: il banco ridotto di L47b1 in Python, per cercare il profilo in fretta.

Non sostituisce ngspice: serve a esplorare (centinaia di profili in secondi), e ogni profilo
scelto si riverifica con la `tran` vera (sfumatura.py qui accanto, e poi il banco V2).

IL MODELLO e' quello di models/optocoupler/nsl32sr3_comportamentale.lib, letto dal file (non
ricopiato): lo stato xs = log10(R) insegue xt = pwl(log10(I_mA)); accensione (xt < xs) del primo
ordine con tau 1,526 ms, spegnimento (xt > xs) dello stesso ordine ma limitato al tasso
pwl(xs) in decadi/s (292 sotto 100 kohm, 0,238 sopra). La cella ha in parallelo CCELL 5 pF;
CIO (0,5 pF verso l'anodo del LED) e' trascurata.

IL BANCO (comune.py di L47b1): sorgente 1,5 ohm, cella in serie, cella verso massa e R_IN 1 Mohm
sull'ingresso del blocco A. Il livello e' |H| a 1 kHz, mediato su 10 ms (la finestra del fit
di scripts/v2_metodo.py), un valore ogni ms. S come v2_metodo.salto_db: la variazione massima in
100 ms col livello tenuto a -70 dB.

Le correnti dei LED sono generatori ideali (il pilota ideale). Stdlib soltanto.
"""
import cmath
import math
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
NSL_LIB = os.path.join(REPO, "models", "optocoupler", "nsl32sr3_comportamentale.lib")

RSRC, RIN, CCELL, F = 1.5, 1e6, 5e-12, 1000.0
PAVIMENTO, FINESTRA = -70.0, 0.100
DT = 1e-4


def _numeri(s):
    return [float(x) for x in re.findall(r"[-+]?\d+\.\d+|[-+]?\d+", s)]


def leggi_modello(path=NSL_LIB):
    """{curva: tabella xt}, tabella del tasso, tau: dal file del modello."""
    testo = open(path).read()
    curve, tasso, tau = {}, None, None
    for m in re.finditer(r"\.subckt NSL32SR3_(\w)(.*?)\.ends", testo, re.S):
        corpo = m.group(2)
        bxt = re.search(r"BXT .*?pwl\(log10\(max\(abs\(i\(VSEN\)\)\*1000, 1e-9\)\),(.*?)\)\s*$",
                        corpo, re.M).group(1)
        v = _numeri(bxt)
        curve[m.group(1)] = list(zip(v[0::2], v[1::2]))
        bdx = re.search(r"BDX .*?min\(\(V\(xt\) - V\(xs\)\)/([0-9.]+), pow\(10, pwl\(V\(xs\),(.*?)\)\)\)",
                        corpo).group
        tau = float(bdx(1))
        w = _numeri(bdx(2))
        tasso = list(zip(w[0::2], w[1::2]))
    return curve, tasso, tau


CURVE, TASSO, TAU = leggi_modello()


def pwl(x, pts):
    # ngspice estrapola linearmente fuori dai punti (limitations #31): lo si rifa' uguale
    if x <= pts[0][0]:
        (x0, y0), (x1, y1) = pts[0], pts[1]
    elif x >= pts[-1][0]:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
    else:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                break
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


def xt_di(curva, i):
    return pwl(math.log10(max(abs(i) * 1000, 1e-9)), CURVE[curva])


def r_statica(curva, i):
    return 10 ** xt_di(curva, i)


def passo(xs, xt, dt=DT):
    if xt < xs:      # accensione: primo ordine, esatto
        return xt + (xs - xt) * math.exp(-dt / TAU)
    v = min((xt - xs) / TAU, 10 ** pwl(xs, TASSO))
    return min(xs + v * dt, xt)


def h(rs, rp):
    w = 2 * math.pi * F
    zs = 1 / (1 / rs + 1j * w * CCELL)
    zp = 1 / (1 / rp + 1j * w * CCELL + 1 / RIN)
    return abs(zp / (RSRC + zs + zp))


# E3 (|Zin| >= 100 kohm, 20 Hz - 20 kHz, al connettore: tb_e3_e5_ldr.cir). Il minimo e' a 20 kHz.
# Il resto del nodo SRCX (CSEL, trim...) come un'ammettenza Y_RESTO a 20 kHz, ricavata dai due
# stati di tb_e3_e5_ldr di L47b2a: «gioco» 110,7 kohm e «mute» 113,6 kohm (G 1,456 uS, B 8,054 uS,
# ~64 pF); il terzo stato, «meta'» (serie 248 kohm), ridà 113,9 contro 114,4 kohm misurati.
# Il valore esatto lungo la sequenza resta di V2 (post): qui serve a tenere il profilo lontano
# dal bordo. Conseguenza: il ramo della cella deve valere >= ~224 kohm in ogni istante.
F_E3 = 20e3
Y_RESTO = complex(1.456e-6, 8.054e-6)


def zin_e3(rs, rp, f=F_E3):
    """|Zin| al connettore alla frequenza f: la parte resistiva di Y_RESTO uguale, la capacitiva
    scalata con f (Y_RESTO e' a 20 kHz)."""
    w = 2 * math.pi * f
    y_resto = complex(Y_RESTO.real, Y_RESTO.imag * f / F_E3)
    zs = 1 / (1 / rs + 1j * w * CCELL)
    zp = 1 / (1 / rp + 1j * w * CCELL + 1 / RIN)
    return 1 / abs(y_resto + 1 / (zs + zp))


# La scelta dell'utente in L47b2b1 («3 s e 3 s, impedenza ai bassi»): durante la sfumatura E3 si
# giudica ai bassi, dove ha la sua ragione (il condensatore d'uscita del phono): a 20 Hz.
F_BASSI = 20.0


def carico(rs, rp):
    """L29b/ldr_catena/post.py: R_s + (R_p || 1 M), contro 100 kohm."""
    return rs + rp * RIN / (rp + RIN)


def corsa(i_serie, i_deriv, t_fine, curve=("B", "B"), t0_stato=None):
    """i_serie(t), i_deriv(t) in A. Lo stato parte dal regime a t = 0 (l'op di ngspice).
    Ritorna (tempi ogni ms, livello lineare mediato su 10 ms, xs serie, xs derivazione)."""
    cs, cp = curve
    xs = xt_di(cs, i_serie(0.0))
    xp = xt_di(cp, i_deriv(0.0))
    n = int(round(t_fine / DT))
    amp, xss, xps = [], [], []
    for k in range(n + 1):
        t = k * DT
        amp.append(h(10 ** xs, 10 ** xp))
        xss.append(xs)
        xps.append(xp)
        xs = passo(xs, xt_di(cs, i_serie(t)))
        xp = passo(xp, xt_di(cp, i_deriv(t)))
    # media mobile centrata su 10 ms, un valore ogni ms
    m = int(round(0.010 / DT))
    pref = [0.0]
    for a in amp:
        pref.append(pref[-1] + a)
    tt, ll, s1, p1 = [], [], [], []
    passo_ms = int(round(1e-3 / DT))
    for k in range(m // 2, n + 1 - m // 2, passo_ms):
        tt.append(k * DT)
        ll.append((pref[k + m // 2] - pref[k - m // 2]) / m)
        s1.append(xss[k])
        p1.append(xps[k])
    return tt, ll, s1, p1


def salto(tt, ll, a_pieno, t_da, t_a):
    """v2_metodo.salto_db sulla finestra [t_da, t_a]: (dB, istante d'inizio)."""
    idx = [k for k, t in enumerate(tt) if t_da <= t <= t_a]
    lv = [max(20 * math.log10(max(ll[k], 1e-30) / a_pieno), PAVIMENTO) for k in idx]
    kk = int(round(FINESTRA / 1e-3))
    best, tb = 0.0, None
    for j in range(len(lv) - kk):
        d = abs(lv[j + kk] - lv[j])
        if d > best:
            best, tb = d, tt[idx[j]]
    return best, tb


# ------------------------------------------------------------------ i profili in funzione di d
def tabella_log(pts):
    """[(d, I)] -> f(d) interpolata in log10(I), tenuta agli estremi."""
    lp = [(d, math.log10(i)) for d, i in pts]

    def f(d):
        d = min(max(d, lp[0][0]), lp[-1][0])
        return 10 ** pwl(d, lp)
    return f


def profilo_v4(ion, irip=10e-9):
    serie = [(0, ion), (0.1, 0.2e-3), (0.45, 4.5e-6), (0.75, 0.19e-6), (0.8, irip), (1, irip)]
    deriv = [(0, irip), (0.5, irip), (1, ion)]
    return tabella_log(serie), tabella_log(deriv)


# IL PROFILO v5 (L47b2b1): simmetrico, 3 s per verso, cima 7 mA (ADR-060). Dalla famiglia
# (famiglia.py, a 0,6 b 0,3 i0 0,1 uA g 1): la serie log-lineare fino al riposo a d = 0,6; la
# derivazione log-lineare dalla cima indietro fino al riposo, che raggiunge a d = 0,155 (i 0,1 uA
# a d = 0,3 della famiglia stanno sulla stessa retta, nella zona buia della cella).
SERIE_V5_D, DERIV_V5_D = 0.6, 0.155


def profilo_v5(ion, irip=10e-9):
    serie = [(0, ion), (SERIE_V5_D, irip), (1, irip)]
    deriv = [(0, irip), (DERIV_V5_D, irip), (1, ion)]
    return tabella_log(serie), tabella_log(deriv)


T_INS = 0.3


def sfumatura(fs, fp, td, curve, t_ins=T_INS):
    """La sfumatura di sfumatura.py di L47b1: d sale in td a t_ins, resta 1 s, scende in td."""
    t_rel = t_ins + td + 1.0
    t_fine = t_rel + td + 0.5

    def d(t):
        if t < t_rel:
            return min(max((t - t_ins) / td, 0.0), 1.0)
        return min(max(1 - (t - t_rel) / td, 0.0), 1.0)
    return sequenza(lambda t: fs(d(t)), lambda t: fp(d(t)), td, curve, t_ins)


def sequenza(i_s, i_p, td, curve, t_ins=T_INS):
    """Le metriche di sfumatura() per correnti date nel tempo: comando di mute a t_ins, di
    rilascio a t_rel = t_ins + td + 1; S misurato su [t - 20 ms, t + td + 200 ms]."""
    t_rel = t_ins + td + 1.0
    t_fine = t_rel + td + 0.5
    tt, ll, xs, xp = corsa(i_s, i_p, t_fine, curve)
    pre = [l for t, l in zip(tt, ll) if 0.05 <= t <= t_ins - 0.02]
    a_pieno = sorted(pre)[int(0.95 * (len(pre) - 1))]
    s_ins = salto(tt, ll, a_pieno, t_ins - 0.020, t_ins + td + 0.200)
    s_rel = salto(tt, ll, a_pieno, t_rel - 0.020, min(t_rel + td + 0.200, t_fine))
    mute = [l for t, l in zip(tt, ll) if t_rel - 0.15 <= t <= t_rel - 0.05]
    liv = 20 * math.log10(max(mute) / a_pieno)
    e3 = [(zin_e3(10 ** a, 10 ** b), t) for t, a, b in zip(tt, xs, xp)]
    e3_min, e3_t = min(e3)
    # per verso: l'inserimento fino al comando di rilascio, il rilascio dopo
    e3_ins = min(z for z, t in e3 if t < t_rel)
    e3_rel = min(z for z, t in e3 if t >= t_rel)
    car_ins = min(carico(10 ** a, 10 ** b) for t, a, b in zip(tt, xs, xp) if t < t_rel)
    car_rel = min(carico(10 ** a, 10 ** b) for t, a, b in zip(tt, xs, xp) if t >= t_rel)
    e3_bassi = min(zin_e3(10 ** a, 10 ** b, F_BASSI) for a, b in zip(xs, xp))
    # il criterio storico di L29b (ldr_catena/post.py): il solo ramo della cella, resistivo
    car = min((carico(10 ** a, 10 ** b), t) for t, a, b in zip(tt, xs, xp))
    return {"S_ins_dB": s_ins[0], "S_ins_t": s_ins[1], "S_rel_dB": s_rel[0], "S_rel_t": s_rel[1],
            "liv_mute_dB": liv, "e3_min": e3_min, "e3_t": e3_t, "carico_min": car[0],
            "carico_t": car[1], "e3_ins": e3_ins, "e3_rel": e3_rel, "carico_ins": car_ins,
            "carico_rel": car_rel, "e3_bassi": e3_bassi,
            "tt": tt, "ll": ll, "a_pieno": a_pieno, "xs": xs, "xp": xp}


if __name__ == "__main__":
    import sys
    ion = float(sys.argv[1]) if len(sys.argv) > 1 else 12e-3
    fs, fp = (profilo_v5 if "v5" in sys.argv else profilo_v4)(ion)
    for c in "ABCDE":
        r = sfumatura(fs, fp, 3.0, (c, c))
        print("%s  S ins %5.2f dB @%.3f  S rel %5.2f dB @%.3f  mute %6.1f dB  E3 20 kHz %6.1f k @%.2f"
              "  20 Hz %6.1f k  carico %6.1f k" % (
                  c, r["S_ins_dB"], r["S_ins_t"], r["S_rel_dB"], r["S_rel_t"], r["liv_mute_dB"],
                  r["e3_min"] / 1e3, r["e3_t"], r["e3_bassi"] / 1e3, r["carico_min"] / 1e3))
