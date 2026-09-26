#!/usr/bin/env python3
"""L41a, Fase 0: i numeri per scegliere il trasformatore (CALCOLATI in ngspice, modello ipotetico).

Solo stdlib. Lanciare con /usr/bin/python3; scrive i deck e la tabella in questa cartella.

Il modello, tutto IPOTESI dichiarate (nessun modello del costruttore):
- il toroidale e' un Thevenin per semi-avvolgimento: V a vuoto = Vn (1 + reg), R serie tale che al
  carico resistivo nominale (VA / 2 / Vn per avvolgimento) l'uscita valga Vn. reg = 12 % per 30 VA,
  8 % per 50 VA (ordine dei cataloghi dei toroidali piccoli; da confermare sul pezzo scelto).
  Dispersione 100 uH per semi-avvolgimento;
- raddrizzatore a ponte sul secondario a presa centrale: ogni rail e' una doppia semionda, un diodo
  in conduzione per semionda. Diodo: Is 1e-9, N 1.8, Rs 0.03 (~0.9 V a 1 A di picco);
- serbatoio 4700 uF per rail, ESR 30 mOhm;
- il regolatore e' un carico a corrente costante: 265 mA sul rail - ; sul rail + 265 mA, piu' 80 mA
  se VRELAY a 12 V si ricava da li' (colonna "+VRELAY");
- la rete a 230 V x 0.9 / 1.0 / 1.1, 50 Hz. Si legge dopo 3 s, sulle ultime 10 semionde.
"""
import os
import subprocess

QUI = os.path.dirname(os.path.abspath(__file__))
NGSPICE = "/opt/homebrew/bin/ngspice"
I_RAIL = 0.265
I_VRELAY12 = 0.080
V_REG = 15.0
DROPOUT = 0.6   # margine richiesto sopra 15 V all'ingresso del regolatore (dropout + tolleranza)


def deck(vn, va, reg, rete, i_plus):
    i_nom = va / 2.0 / vn
    voc = vn * (1 + reg)
    rs = (voc - vn) / i_nom
    vpk = voc * rete * 2 ** 0.5
    return f"""* raddrizzatore L41a vn={vn} va={va} rete={rete}
VA a 0 sin(0 {vpk:.4f} 50)
VB 0 b sin(0 {vpk:.4f} 50)
RA a a1 {rs:.4f}
LA a1 a2 100u
RB b b1 {rs:.4f}
LB b1 b2 100u
.model DR D(Is=1e-9 N=1.8 Rs=0.03)
D1 a2 p DR
D2 b2 p DR
D3 m a2 DR
D4 m b2 DR
CP p pe 4700u
RPE pe 0 0.03
CM me m 4700u
RME me 0 0.03
IP p 0 {i_plus}
IM 0 m {I_RAIL}
.control
tran 20u 3.2 0 20u uic
meas tran pmin min v(p) from=3.0 to=3.2
meas tran pavg avg v(p) from=3.0 to=3.2
meas tran pmax max v(p) from=3.0 to=3.2
meas tran mmin max v(m) from=3.0 to=3.2
meas tran mavg avg v(m) from=3.0 to=3.2
meas tran iarms rms i(VA) from=3.0 to=3.2
echo "RIS $&pmin $&pavg $&pmax $&mmin $&mavg $&iarms"
.endc
.end
"""


def corri(vn, va, reg, rete, i_plus):
    nome = os.path.join(QUI, "deck_%g_%d_%g_%d.cir" % (vn, va, rete, round(i_plus * 1000)))
    open(nome, "w").write(deck(vn, va, reg, rete, i_plus))
    out = subprocess.run([NGSPICE, "-b", nome], capture_output=True, text=True).stdout
    riga = [r for r in out.splitlines() if r.startswith("RIS ")]
    if not riga or "Error" in out:
        raise SystemExit("corsa fallita: " + nome + "\n" + out[-2000:])
    return [float(x) for x in riga[0].split()[1:]]


def main():
    righe = ["vn_ac,va,rete,carico_plus_mA,v_plus_min,v_plus_avg,v_plus_max,v_minus_min,v_minus_avg,"
             "i_avv_rms,p_reg_pm_W,p_vrelay12_W,margine_valle_V"]
    for vn in (12.0, 13.0, 14.0, 15.0):
        for va, reg in ((30, 0.12), (50, 0.08)):
            for rete in (0.9, 1.0, 1.1):
                for i_plus in (I_RAIL, I_RAIL + I_VRELAY12):
                    pmin, pavg, pmax, mmin, mavg, irms = corri(vn, va, reg, rete, i_plus)
                    p_reg = (pavg - V_REG) * I_RAIL + (-mavg - V_REG) * I_RAIL
                    p_vr = (pavg - 12.0) * I_VRELAY12 if i_plus > I_RAIL else 0.0
                    marg = min(pmin, -mmin) - V_REG - DROPOUT
                    righe.append("%g,%d,%g,%d,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f" % (
                        vn, va, rete, round(i_plus * 1000), pmin, pavg, pmax, mmin, mavg, irms, p_reg,
                        p_vr, marg))
    open(os.path.join(QUI, "raddrizzatore.csv"), "w").write("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
