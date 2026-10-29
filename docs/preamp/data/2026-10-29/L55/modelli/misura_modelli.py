#!/usr/bin/env python3
"""L55 (NC-056) - il dispositivo d'uscita del blocco: CJE, CJC, hFE, fT e
capacita' dei modelli del costruttore, TUTTI sullo stesso script e alle
stesse condizioni, MJE15032/33 (il caso noto) compreso.

Condizioni (quelle del follower in classe A del blocco di guadagno):
  IC = 20 mA, VCE = 15 V, 25 C ("set temp = 25", come ogni ricetta di
  scripts/validate_models.py; TNOM resta il default di ngspice, 27 C).
  Il polarizzatore trova IB per bisezione sull'op: IC = 20,0000 mA +-1e-6.

Per ogni modello:
  CJE, CJC            parametri di ZERO POLARIZZAZIONE letti dal testo del file
  Vbe, hFE, gm        all'op di sopra
  Cpi, Cmu            le capacita' di piccolo segnale che ngspice calcola
                      all'op (Cpi = CJE a Vbe + diffusione TF*gm; Cmu = la
                      parte XCJC di CJC a Vcb)
  fT (incrocio)       frequenza a cui |ic/ib| = 1, collettore in corto in AC
  GBW@10MHz           |ic/ib| * 10 MHz  (la definizione dei datasheet onsemi
                      dei MJE243/253 e' hfe*ftest a 10 MHz, IC = 100 mA)
  fT = gm/2pi(Cpi+Cmu)  controllo analitico
  Cobo                a VCB = 10 V, IE = 0, f = 0,1 MHz (condizione del
                      datasheet onsemi MJE243/253 e MJE170/172)

Uso:  /usr/bin/python3 misura_modelli.py   (scrive misure.txt e misure.json)
Solo libreria standard. ngspice 47.
"""
import json
import math
import os
import re
import subprocess

NGSPICE = "/opt/homebrew/bin/ngspice"
ROOT = "/Users/roberto/EDA/.claude/worktrees/L55"
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "ngspice")
os.makedirs(WORK, exist_ok=True)

IC_TARGET = 20e-3
VCE = 15.0

V = ROOT + "/vendor"
# (etichetta, file del costruttore, nome del modello, segno)
DEVICES = [
    ("MJE15032 NPN (caso noto)", V + "/bjt_npn/onsemi/MJE15032/mje15032.lib", "Qmje15032", +1),
    ("MJE15033 PNP (caso noto)", V + "/bjt_pnp/onsemi/MJE15033/mje15033.lib", "Qmje15033", -1),
    ("MJE243 NPN", V + "/bjt_npn/onsemi/MJE243/mje243.lib", "Qmje243", +1),
    ("MJE253 PNP", V + "/bjt_pnp/onsemi/MJE253/mje253.lib", "Qmje253", -1),
    ("MJE182 NPN", HERE + "/scartati/mje182.lib", "Qmje182", +1),
    ("MJE172 PNP", HERE + "/scartati/mje172.lib", "Qmje172", -1),
    ("ZXTN25040DZ NPN (gia' in models/)", V + "/bjt_npn/diodes_inc/ZXTN25040DZ/ZXTN25040DZ.spice.txt", "ZXTN25040DZ", +1),
    ("ZXTP25040DZ PNP (gia' in models/)", V + "/bjt_pnp/diodes_inc/ZXTP25040DZ/ZXTP25040DZ.spice.txt", "ZXTP25040DZ", -1),
    # vagliati e scartati: i file stanno in scartati/ (byte per byte, sha256 in SHA256SUMS)
    ("ZXTN19060CG NPN (Diodes, SOT-223)", HERE + "/scartati/ZXTN19060CG.spice.txt", "ZXTN19060CG", +1),
    ("ZXTP19060CG PNP (Diodes, SOT-223)", HERE + "/scartati/ZXTP19060CG.spice.txt", "ZXTP19060CG", -1),
    ("FZT651 NPN (Diodes, SOT-223)", HERE + "/scartati/FZT651.spice.txt", "FZT651", +1),
    ("FZT751 PNP (Diodes, SOT-223)", HERE + "/scartati/FZT751.spice.txt", "FZT751", -1),
    ("MJD243 NPN (onsemi, DPAK)", HERE + "/scartati/mjd243.lib", "Qmjd243", +1),
    ("MJE340 NPN (onsemi, 300 V)", HERE + "/scartati/mje340.lib", "Qmje340", +1),
    ("MJE350 PNP (onsemi, 300 V)", HERE + "/scartati/mje350.lib", "Qmje350", -1),
    ("D44H11 NPN (onsemi, TO-220)", HERE + "/scartati/d44h11.lib", "Qd44h11", +1),
    ("D45H11 PNP (onsemi, TO-220)", HERE + "/scartati/d45h11.lib", "Qd45h11", -1),
    ("MJD44H11 NPN (onsemi, DPAK)", HERE + "/scartati/mjd44h11.lib", "Qmjd44h11", +1),
    ("MJD45H11 PNP (onsemi, DPAK)", HERE + "/scartati/mjd45h11.lib", "Qmjd45h11", -1),
]


def ngspice(deck_text, name):
    path = os.path.join(WORK, name + ".cir")
    with open(path, "w") as f:
        f.write(deck_text)
    p = subprocess.run([NGSPICE, "-b", path], capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise RuntimeError(f"ngspice exit {p.returncode} on {name}: {p.stdout[-300:]} {p.stderr[-300:]}")
    return p.stdout + p.stderr


def ib_nodes(sign):
    return "0 b" if sign > 0 else "b 0"


def op_deck(lib, model, sign, ib):
    return f"""* L55 op {model}
.include {lib}
Q1 c b 0 {model}
Vc c 0 DC {VCE * sign}
Ib {ib_nodes(sign)} DC {ib:.12g}
.control
set temp = 25
op
print @q1[ic] @q1[ib] @q1[cpi] @q1[cmu] @q1[gm] @q1[vbe]
.endc
.end
"""


def parse_op(text):
    out = {}
    for m in re.finditer(r"^@q1\[(\w+)\]\s*=\s*(\S+)", text, re.M):
        out[m.group(1)] = float(m.group(2))
    return out


def find_ib(lib, model, sign, tag):
    lo, hi = 1e-8, 5e-2
    for _ in range(60):
        mid = math.sqrt(lo * hi)
        o = parse_op(ngspice(op_deck(lib, model, sign, mid), f"{tag}_bis"))
        ic = abs(o["ic"])
        if ic < IC_TARGET:
            lo = mid
        else:
            hi = mid
        if abs(ic - IC_TARGET) / IC_TARGET < 1e-7:
            break
    return mid, o


def ac_ft(lib, model, sign, ib, tag):
    csv = os.path.join(WORK, f"{tag}_ac.csv")
    if os.path.exists(csv):
        os.remove(csv)
    deck = f"""* L55 fT {model}
.include {lib}
Q1 c b 0 {model}
Vc c 0 DC {VCE * sign}
Ib {ib_nodes(sign)} DC {ib:.12g} AC 1
.control
set temp = 25
ac dec 50 100k 5g
let hfe = mag(i(Vc))
wrdata {csv} hfe
.endc
.end
"""
    ngspice(deck, f"{tag}_ac")
    rows = []
    for line in open(csv):
        v = line.split()
        if len(v) >= 2:
            rows.append((float(v[0]), float(v[1])))
    # incrocio |hfe| = 1, interpolazione log-log fra i due campioni
    ft = None
    for (f0, h0), (f1, h1) in zip(rows, rows[1:]):
        if h0 >= 1.0 > h1:
            a = (math.log(1.0) - math.log(h0)) / (math.log(h1) - math.log(h0))
            ft = math.exp(math.log(f0) + a * (math.log(f1) - math.log(f0)))
            break
    # |hfe| * f a 10 MHz (interpolazione log-log)
    gbw10 = None
    for (f0, h0), (f1, h1) in zip(rows, rows[1:]):
        if f0 <= 10e6 <= f1:
            a = (math.log(10e6) - math.log(f0)) / (math.log(f1) - math.log(f0))
            gbw10 = math.exp(math.log(h0) + a * (math.log(h1) - math.log(h0))) * 10e6
            break
    hfe_lf = rows[0][1]
    return ft, gbw10, hfe_lf


def cobo(lib, model, sign, tag):
    csv = os.path.join(WORK, f"{tag}_cobo.csv")
    if os.path.exists(csv):
        os.remove(csv)
    deck = f"""* L55 Cobo {model}
.include {lib}
Q3 c3 0 e3 {model}
Re3 e3 0 1G
Vc3 c3 0 DC {10.0 * sign} AC 1
.control
set temp = 25
ac lin 1 100k 100k
let cre = real(i(Vc3))
let cim = imag(i(Vc3))
wrdata {csv} cre cim
.endc
.end
"""
    ngspice(deck, f"{tag}_cobo")
    v = open(csv).read().split()
    f, re_, im_ = float(v[0]), float(v[1]), float(v[3])
    return abs(im_) / (2 * math.pi * f), abs(re_ / im_)


def par(text, name):
    m = re.search(r"\b" + name + r"\s*=\s*([-+0-9.eE]+)", text)
    return float(m.group(1)) if m else None


def main():
    results = []
    for label, lib, model, sign in DEVICES:
        tag = re.sub(r"[^A-Za-z0-9]", "_", model)
        if not os.path.isfile(lib):
            print(f"MANCA {lib}")
            continue
        text = open(lib, errors="replace").read()
        # i parametri del modello di QUESTO dispositivo (un file puo' averne piu' di uno)
        m = re.search(r"\.MODEL\s+" + re.escape(model) + r"\s+\w+(.*?)(?=\n\s*\.MODEL|\Z)", text, re.S | re.I)
        body = m.group(1) if m else text
        cje, cjc = par(body, "CJE"), par(body, "CJC")
        ib, o = find_ib(lib, model, sign, tag)
        ft, gbw10, hfe_lf = ac_ft(lib, model, sign, ib, tag)
        cp, cm, gm = o["cpi"], o["cmu"], o["gm"]
        co, ratio = cobo(lib, model, sign, tag)
        r = {
            "dispositivo": label, "modello": model, "file": os.path.relpath(lib, ROOT),
            "CJE_zero_bias_F": cje, "CJC_zero_bias_F": cjc,
            "IC_A": abs(o["ic"]), "IB_A": abs(o["ib"]), "hFE": abs(o["ic"] / o["ib"]),
            "Vbe_V": abs(o["vbe"]), "gm_S": gm,
            "Cpi_F": cp, "Cmu_F": cm,
            "fT_incrocio_Hz": ft, "GBW_10MHz_Hz": gbw10, "fT_gm_Hz": gm / (2 * math.pi * (cp + cm)),
            "hfe_ac_bassa": hfe_lf, "Cobo_10V_100kHz_F": co, "Cobo_re_su_im": ratio,
        }
        results.append(r)
        print(f"{label}: ok")
    with open(os.path.join(HERE, "misure.json"), "w") as f:
        json.dump(results, f, indent=1)

    lines = []
    w = lines.append
    w("L55 - modelli del costruttore a IC = 20 mA, VCE = 15 V, 25 C (ngspice 47)")
    w("")
    hdr = f"{'dispositivo':36s} {'CJE0 pF':>8s} {'CJC0 pF':>8s} {'hFE':>6s} {'Vbe V':>6s} {'gm mS':>7s} {'Cpi pF':>8s} {'Cmu pF':>7s} {'fT inc MHz':>10s} {'GBW10 MHz':>9s} {'fT gm MHz':>9s} {'Cobo pF':>8s}"
    w(hdr)
    w("-" * len(hdr))
    for r in results:
        w(f"{r['dispositivo']:36s} {r['CJE_zero_bias_F'] * 1e12:8.1f} {r['CJC_zero_bias_F'] * 1e12:8.1f} "
          f"{r['hFE']:6.1f} {r['Vbe_V']:6.3f} {r['gm_S'] * 1e3:7.1f} {r['Cpi_F'] * 1e12:8.1f} {r['Cmu_F'] * 1e12:7.2f} "
          f"{r['fT_incrocio_Hz'] / 1e6:10.1f} {r['GBW_10MHz_Hz'] / 1e6:9.1f} {r['fT_gm_Hz'] / 1e6:9.1f} {r['Cobo_10V_100kHz_F'] * 1e12:8.2f}")
    w("")
    w("CJE0 / CJC0: parametri di zero polarizzazione del modello. Cpi, Cmu: capacita' di piccolo segnale")
    w("all'op (Cpi comprende la diffusione TF*gm). fT inc: |ic/ib| = 1. GBW10: |ic/ib| a 10 MHz per 10 MHz.")
    w("Cobo: VCB = 10 V, IE = 0, 0,1 MHz.")
    txt = "\n".join(lines)
    with open(os.path.join(HERE, "misure.txt"), "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
