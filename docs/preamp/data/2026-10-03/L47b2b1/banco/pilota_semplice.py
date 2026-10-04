"""pilota_semplice.py - L47b2b1, NC-045: i numeri del pilota semplificato, prima della domanda.

Il pilota di oggi (psu.py, ADR-049/050): DAC doppio a 12 bit, due convertitori esponenziali a
coppia appaiata con anello d'op-amp e specchio PNP, compensazione di Vt col sensore del micro,
calibrazione a due punti. Realizza qualunque tabella log10(I) contro d: il profilo v5 di questo
lotto. Il pilota semplificato toglie DAC, convertitori e calibrazione; il micro resta (trim e
permissivo, R4 respinto dall'utente) e da' solo i fronti: un pin per stringa, alto o basso.

Due realizzazioni, ciascuna per stringa (serie, derivazione):
  P1  «un RC piu' un generatore di corrente» (NC-045, alla lettera): il pin carica o scarica un RC
      (tau_su e tau_giu distinti: un diodo e due resistenze), un generatore lineare (op-amp,
      transistore, resistenza) da' I = I_TOP * v. Nessuna dipendenza dalla temperatura; il
      pavimento lo fanno gli offset (I_PAV).
  P2  un RC che comanda la base di un NPN con resistenza d'emettitore RE: esponenziale in basso,
      lineare (RE) in alto. Vb = VB_TOP * v; I da Vb = n Vt ln(1 + I/Is) + I RE. Senza
      compensazione ne' calibrazione: agli angoli di temperatura (Vbe -2 mV/C attraverso Is(T)) e
      di dispersione di Is (+-18 mV, un fattore 2), e la tolleranza dell'RC.

Le correnti entrano nel banco ridotto di rapido.py (il modello della NSL-32SR3, le metriche di V2,
E3 a 20 kHz al connettore e il carico della cella). Stdlib.
"""
import math

import rapido as R

ION = 7e-3
VT0, T0 = 0.025693, 298.15        # kT/q a 25 C
K_Q = VT0 / T0


class RC:
    """v(t) di un RC comandato da un pin: eventi [(t, 0|1)], tau_su in salita, tau_giu in discesa.
    Parte dal valore del primo evento (a regime)."""

    def __init__(self, eventi, tau_su, tau_giu):
        self.ev = sorted(eventi)
        self.su, self.giu = tau_su, tau_giu
        # il valore all'inizio di ogni evento
        self.v0 = []
        v = float(self.ev[0][1])
        for k, (t, liv) in enumerate(self.ev):
            if k:
                tp, lp = self.ev[k - 1]
                v = self._evolvi(v, lp, t - tp)
            self.v0.append(v)

    def _evolvi(self, v, liv, dt):
        tau = self.su if liv > v else self.giu
        return liv + (v - liv) * math.exp(-dt / tau)

    def __call__(self, t):
        k = 0
        while k + 1 < len(self.ev) and self.ev[k + 1][0] <= t:
            k += 1
        tk, liv = self.ev[k]
        return self._evolvi(self.v0[k], liv, max(t - tk, 0.0))


def p1(rc, i_top=ION, i_pav=0.0):
    return lambda t: max(i_top * rc(t), 0.0) + i_pav


class Esponenziale:
    """P2: I(Vb) di un NPN con RE, a temperatura tc e con lo scarto di Vbe dv_is (V, a pari I).
    Is(T) da Vbe(T) = Vbe(25 C) - 2 mV/C a corrente costante."""

    def __init__(self, vb_top, re, tc=25.0, dv_is=0.0, n=1.0, is25=1e-14):
        self.vb_top, self.re, self.n = vb_top, re, n
        tk = tc + 273.15
        self.vt = K_Q * tk
        # Vbe a 1 mA a 25 C, poi spostata di -2 mV/C e di dv_is
        vbe1 = n * VT0 * math.log(1e-3 / is25) - 2e-3 * (tc - 25.0) + dv_is
        self.is_ = 1e-3 / math.exp(vbe1 / (n * self.vt))

    def i(self, vb):
        if vb <= 0:
            return 0.0
        lo, hi = 0.0, vb / self.re      # I tale che n Vt ln(1 + I/Is) + I RE = vb, per bisezione in log
        if hi <= 0:
            return 0.0
        a, b = -30.0, math.log10(hi)
        for _ in range(60):
            m = 0.5 * (a + b)
            im = 10 ** m
            if self.n * self.vt * math.log1p(im / self.is_) + im * self.re > vb:
                b = m
            else:
                a = m
        return 10 ** a

    def corrente(self, rc):
        cache = {}

        def f(t):
            v = round(rc(t), 7)
            if v not in cache:
                cache[v] = self.i(self.vb_top * v)
            return cache[v]
        return f


def vb_top_per(i_top, re, tc=60.0, dv_is=-18e-3):
    """La Vb di cima che da' i_top all'angolo caldo e a Vbe bassa (la corrente piu' alta)."""
    e = Esponenziale(1.0, re, tc, dv_is)
    return e.n * e.vt * math.log1p(i_top / e.is_) + i_top * re
