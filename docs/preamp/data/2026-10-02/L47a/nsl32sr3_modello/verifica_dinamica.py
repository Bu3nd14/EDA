#!/usr/bin/env python3
"""verifica_dinamica.py - il modello NSL-32SR3 rispetta i tempi pubblicati? (L47a)

Curva B, con le definizioni del costruttore (Silonex Rev 07, Luna Rev 01-04-16):
- salita: dal buio a 5 mA, la conduttanza al 63 % della finale in 5 ms;
- discesa: dal regime a 5 mA, 100 kohm 10 ms dopo lo spegnimento;
- buio: almeno 25 Mohm 10 s dopo lo spegnimento (il modello ci arriva per costruzione, col
  tasso piu' lento compatibile: si confronta entro TOL).
TOL 3 %. method=gear, come in L29b: col trapezio il gradino del LED lascia un'oscillazione non
smorzata nelle correnti dei condensatori (CIO 0,5 pF). Le opzioni dei banchi veri e 1 V sulla
cella (verifica_statica.py). Una corsa con «Transient op» o bloccata conta come fuori.
Uso: verifica_dinamica.py [lib]. Esce col numero di punti fuori tolleranza.
"""
import os, re, subprocess, sys, tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import genera_modello as G

LIB = sys.argv[1] if len(sys.argv) > 1 else G.OUT
NGSPICE = "/opt/homebrew/bin/ngspice"
TOL = 0.03


def corsa(pwl_led, tstop, tmax, istanti):
    righe = "\n".join("meas tran m%d find rdy at=%.9g" % (k, t) for k, t in enumerate(istanti))
    cir = ("nsl32sr3 tran\n.include %s\n.options reltol=1e-6 vntol=1e-6 abstol=1e-12 method=gear\n"
           "IDYN 0 ADY PWL(%s)\nRPD ADY 0 1G\nXDY ADY 0 CDY 0 NSL32SR3_B\nVCDY CDY 0 DC 1\n"
           ".control\ntran %g %g 0 %g\nlet rdy = -1/i(vcdy)\n%s\n.endc\n.end\n"
           % (LIB, pwl_led, tmax, tstop, tmax, righe))
    with tempfile.NamedTemporaryFile("w", suffix=".cir", delete=False) as f:
        f.write(cir)
    try:
        p = subprocess.run([NGSPICE, "-b", f.name], capture_output=True, text=True, timeout=300)
        out = p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        out = ""
    os.unlink(f.name)
    if "Transient op" in out:
        return [float("nan")] * len(istanti)
    trovati = [re.search(r"^m%d\s*=\s*(\S+)" % k, out, re.M) for k in range(len(istanti))]
    return [float(m.group(1)) if m else float("nan") for m in trovati]


fuori = 0


def giudica(titolo, rif, val):
    global fuori
    ok = abs(val / rif - 1) <= TOL            # NaN -> False
    fuori += not ok
    print("%-52s %12.5g  %12.5g  %+.2f %% %s" % (titolo, rif, val, 100 * (val / rif - 1), "" if ok else "<-- FUORI"))


I5 = G.I_TEMPI * 1e-3
RF5 = 10 ** G.XF5
print("%-52s %12s  %12s" % ("", "riferimento", "modello"))

# salita: buio (LED a zero all'op), poi 5 mA a t = 1 ms
T0 = 1e-3
r = corsa("0 0 %g 0 %g %g 20m %g" % (T0, T0 + 1e-6, I5, I5), T0 + 12e-3, 10e-6, [T0 + G.TR_S, T0 + 11e-3])
giudica("salita: R a 5 ms = R finale / 0,63", RF5 / 0.63, r[0])
giudica("salita: R finale a 5 mA (11 ms)", RF5, r[1])

# discesa: regime a 5 mA, spento a t = 0,1 s
T0 = 0.1
r = corsa("0 %g %g %g %g 0 20 0" % (I5, T0, I5, T0 + 1e-6), T0 + 10.05, 0.2e-3,
          [T0 - 1e-3, T0 + G.TD_S, T0 + G.T_BUIO])
giudica("discesa: regime a 5 mA prima dello spegnimento", RF5, r[0])
giudica("discesa: 100 kohm 10 ms dopo lo spegnimento", G.RD_TD, r[1])
giudica("buio: 25 Mohm 10 s dopo lo spegnimento", G.RDARK, r[2])

print("\npunti fuori tolleranza:", fuori)
sys.exit(fuori)
