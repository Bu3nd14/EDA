#!/usr/bin/env python3
"""verifica_statica.py - il modello VTL5C4 riproduce i punti da cui e' generato? (L29b)

Un processo ngspice per punto: in sequenza (alter + op) il punto di lavoro parte dal
precedente e, col log10 della corrente del LED, fallisce la convergenza e stampa cifre
sbagliate. E' una trappola del banco, non del modello: da punto zero ogni op converge.
Confronta ogni punto di CURVE (genera_modello.py) entro TOL, e l'estrapolazione dichiarata
(400 Mohm al buio). Esce col numero di punti fuori tolleranza. Solo stdlib.
"""
import ast, os, re, subprocess, sys, tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
LIB = os.path.join(REPO, "models", "optocoupler", "vtl5c4_comportamentale.lib")
NGSPICE = "/opt/homebrew/bin/ngspice"
TOL = 0.005   # il modello interpola in log i punti stessi: deve restituirli quasi esatti

src = open(os.path.join(QUI, "genera_modello.py")).read()
CURVE = ast.literal_eval(re.search(r"^CURVE = (\{.*?^\})", src, re.S | re.M).group(1))


def R(curva, i_led):
    cir = ("vtl5c4 op\n.include %s\n.options reltol=1e-6 abstol=1e-15\n"
           "IA 0 AA DC %g\nXA AA 0 CA 0 VTL5C4_%s\nVCA CA 0 DC 1m\n"
           ".control\nop\necho \"RIS $&i(vca)\"\n.endc\n.end\n") % (LIB, i_led, curva)
    with tempfile.NamedTemporaryFile("w", suffix=".cir", delete=False) as f:
        f.write(cir)
    out = subprocess.run([NGSPICE, "-b", f.name], capture_output=True, text=True).stdout
    os.unlink(f.name)
    if "failed" in out:
        return None
    return -1e-3 / float(re.search(r"RIS (\S+)", out).group(1))


fuori = 0
print("curva  I_mA     R_datasheet  R_modello   errore")
for k, pts in CURVE.items():
    for i_ma, r_ds in pts:
        r = R(k, i_ma * 1e-3)
        e = None if r is None else r / r_ds - 1
        ok = e is not None and abs(e) <= TOL
        fuori += not ok
        print("%s   %8.4f  %9.0f  %11s  %s %s" % (k, i_ma, r_ds, "NON CONV." if r is None else "%.0f" % r,
              "" if e is None else "%+.2f %%" % (100 * e), "" if ok else "<-- FUORI"))
print("\nestrapolazione dichiarata (buio 400 Mohm):")
for k in CURVE:
    for i_led in (1e-9, 1e-6, 1e-5):
        r = R(k, i_led)
        print("%s  %g A  R = %s" % (k, i_led, "NON CONV." if r is None else "%.3g ohm" % r))
        fuori += r is None
print("\npunti fuori tolleranza o non convergenti:", fuori)
sys.exit(fuori)
