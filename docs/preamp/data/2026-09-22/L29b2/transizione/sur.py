#!/usr/bin/env python3
"""L29b2: il simulatore VELOCE della transizione del mute LDR. Scratch, per progettare il
profilo; il verdetto resta di ngspice e di v2_metodo.py analizza.

Catena: profilo delle correnti dei LED in funzione della profondita' d(t)
        -> corrente nel LED (col 10 M del banco, o senza)
        -> stato log10(R) delle due celle, con le STESSE equazioni del modello
           (models/optocoupler/vtl5c4_comportamentale.lib, curva B, tabelle lette da li')
        -> livello g(t) all'ingresso del blocco A
        -> tono al jack principale A*g(t)*sin(...) -> C2 con residuo_c, filtra, picco di
           scripts/v2_metodo.py, contro il riferimento (tono pieno, o zero).

Le ipotesi del simulatore, da tarare contro ngspice (tara.py):
- la catena dopo INA e' lineare e piatta a 1 kHz: il jack vale A_MAIN * g(t);
- la distorsione di regime non c'e' (nel C2 vero contro "mai" vale fino a 0,96 mV sul tratto
  ancora silenziato: qui manca, ed e' detto accanto a ogni cifra);
- pwl() ESTRAPOLA linearmente fuori dai punti, come ngspice 47 (provato in L29b2).
"""
import math
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import v2_metodo as vm  # noqa: E402

FS = vm.FS
LIB = os.path.join(REPO, "models", "optocoupler", "vtl5c4_comportamentale.lib")


def _coppie(s):
    v = [float(x) for x in s.split(",")]
    return list(zip(v[0::2], v[1::2]))


def _leggi(curva="B"):
    t = open(LIB).read()
    blocco = t.split(".subckt VTL5C4_%s " % curva, 1)[1].split(".ends", 1)[0]
    xt = re.search(r"BXT xt 0 V = pwl\(log10\(max\(abs\(i\(VSEN\)\)\*1000, 1e-9\)\), ([^)]*)\)", blocco).group(1)
    tau = re.search(r"BTAU tau 0 V = pwl\(V\(xt\), ([^)]*)\)", blocco).group(1)
    d0 = re.search(r"BD0 d0 0 V = pwl\(V\(xt\), ([^)]*)\)", blocco).group(1)
    rate = re.search(r"pow\(10, pwl\(V\(xs\), ([^)]*)\)\)\)", blocco).group(1)
    tf = re.search(r"max\(V\(xs\) - V\(xt\) - V\(d0\), 0\)/([0-9.e+-]+)", blocco).group(1)
    return _coppie(xt), _coppie(tau), _coppie(d0), _coppie(rate), float(tf)


XT, TAU, D0, RATE, TFAST = _leggi()


def pwl(x, pts):
    """come pwl() di una sorgente B di ngspice 47: lineare a tratti, ESTRAPOLA ai due capi."""
    if x <= pts[0][0]:
        (x0, y0), (x1, y1) = pts[0], pts[1]
    elif x >= pts[-1][0]:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
    else:
        lo, hi = 0, len(pts) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if pts[m][0] <= x:
                lo = m
            else:
                hi = m
        (x0, y0), (x1, y1) = pts[lo], pts[hi]
    if x1 == x0:
        return y1
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


# ---- il LED: 2,8e-16 A, N = 2 (DLED_VTL5C4), e il 10 M del banco in parallelo ----
IS, NVT = 2.8e-16, 2 * 0.025852


def i_led(i_src, r_shunt):
    """corrente nel LED quando il generatore i_src alimenta LED || r_shunt (None = niente)."""
    if r_shunt is None or i_src <= 0:
        return max(i_src, 0.0)
    lo, hi = 0.0, 3.0
    for _ in range(60):
        v = 0.5 * (lo + hi)
        if IS * (math.exp(v / NVT) - 1) + v / r_shunt > i_src:
            hi = v
        else:
            lo = v
    return IS * (math.exp(lo / NVT) - 1)


def xt_di(i):
    return pwl(math.log10(max(abs(i) * 1000, 1e-9)), XT)


def passo(xs, xt, dt):
    """un passo dello stato log10(R): le equazioni di BDX, integrate in modo esatto a tratti."""
    tau = max(pwl(xt, TAU), 1e-4)
    if xt >= xs:                                   # si spegne: esponenziale, col tetto del tasso
        tetto = 10 ** pwl(xs, RATE) * dt
        return xs + min((xt - xs) * (1 - math.exp(-dt / tau)), tetto)
    d0 = pwl(xt, D0)                               # si accende: oltre d0 il salto (TFAST ~ us)
    if xs - xt > d0:
        xs = xt + d0 + (xs - xt - d0) * math.exp(-dt / TFAST)
    return xt + (xs - xt) * math.exp(-dt / tau)


def evolvi(correnti, n, dt, xs0, r_shunt):
    """correnti: funzione k -> corrente del generatore; ritorna la lista di xs."""
    out = [0.0] * n
    xs = xs0
    cache = {}
    for k in range(n):
        i = correnti(k)
        key = round(math.log10(max(i, 1e-15)), 5)
        if key not in cache:
            cache[key] = xt_di(i_led(i, r_shunt))
        xs = passo(xs, cache[key], dt)
        out[k] = xs
    return out


# ---- la profondita' d(t) ----
def profondita(n, dt, t_ins, t_rel, td, acc=None):
    """d(t): 0 -> 1 in td dall'inserzione, e indietro dal rilascio da dove si trova.
    acc = None: la velocita' cambia di colpo (v3). acc = tempo per passare da +v a -v con
    accelerazione costante (la velocita' segue una rampa), cosi' l'inversione non ha spigoli."""
    v = 1.0 / td
    out = [0.0] * n
    d, vel = 0.0, 0.0
    for k in range(n):
        t = k * dt
        vt = 0.0 if t < t_ins else (v if t < t_rel else -v)
        if acc is None:
            vel = vt
        else:
            a = 2 * v / acc
            vel += max(min(vt - vel, a * dt), -a * dt)
        d = min(max(d + vel * dt, 0.0), 1.0)
        if d in (0.0, 1.0):
            vel = 0.0 if acc is not None and ((d == 1.0 and vel > 0) or (d == 0.0 and vel < 0)) else vel
        out[k] = d
    return out


def livello(xs_s, xs_p, r_src=1.5, r_in=1e6):
    g = []
    for a, b in zip(xs_s, xs_p):
        rs, rp = 10 ** a, 10 ** b
        par = rp * r_in / (rp + r_in)
        g.append(par / (rs + r_src + par))
    return g


A_MAIN = 3.818 * 3.1523     # tono di V2 al jack principale, +10 dB


def c2(g, t_ev, finestra, f=1000.0, rif=1.0, amp=A_MAIN):
    """C2 (picco, V) della corsa col livello g contro il riferimento a livello costante rif,
    nella finestra [t_ev - 20 ms, t_ev + finestra + 0,2 s], come c2_da_residui di v2_metodo."""
    n = len(g)
    w = 2 * math.pi * f / FS
    x = [amp * g[k] * math.sin(w * k + math.pi / 2) for k in range(n)]
    y = [amp * rif * math.sin(w * k + math.pi / 2) for k in range(n)]
    re_, i0, i1, _ = vm.residuo_c(x, f)
    rr, _, _, _ = vm.residuo_c(y, f)
    d = [re_[k] - rr[k] for k in range(n)]
    z = vm.filtra(d, i0)
    a = max(int(round((t_ev - 0.020) * FS)), i0)
    b = min(int(round((t_ev + finestra + 0.200) * FS)), i1)
    return vm.picco(z, a, b)
