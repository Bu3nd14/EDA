#!/usr/bin/env python3
"""e4.py - il verdetto su E4 dall'output di tb_e4_uscite.cir (L13).

Uso: /usr/bin/python3 e4.py <cartella di output di run_simulation.sh>

REQUIREMENTS E4: "< 100 ohm in banda passante (misurata escludendo la
reattanza del condensatore d'accoppiamento), costante con la posizione del
volume".

Legge tb_e4_uscite_tab.csv, tb_e4_uscite_guadagno.csv e l'unico .log della
cartella. Esce 0 solo se TUTTI i controlli passano, 1 altrimenti, 2 se mancano
i file. Controlli, nell'ordine:

  A  completezza: 135 righe di Zout (3 uscite x 45 celle), 45 di guadagno,
     nessuna cella vuota, nessuna riga "Error" nel log (#26: rc 0 non basta)
  B  tabella = log: ogni cella della tabella echo coincide con la print
     del log per la stessa cella
  C  controllo positivo: il guadagno a 1 kHz segue trim, attenuatore e modo.
     Senza, "costante col volume" uscirebbe anche da un attenuatore scollegato
  D  la sonda e' al jack: Re(Z) a 1 kHz >= 47 ohm (la resistenza in serie),
     |Z| a 20 Hz > 1 k (il 4,7 uF e' nel percorso), nodo del blocco < 1 ohm
  E  E4, soglia: Re(Z) massima su 20 Hz - 20 kHz < 100 ohm, in ogni cella
  F  E4, costanza: per uscita e modo, la dispersione (max - min) su trim e
     attenuatore di Re(Z) max, Re(Z) a 1 kHz e |Z| a 1 kHz < 1 ohm. Le fisse
     anche fra i modi. LA SOGLIA E' UNA LETTURA DEL LOTTO: E4 non da'
     tolleranza. Il termine di confronto e' il passivo di ADR-002, R/4 =
     2,5 k a meta' corsa su un 10 k
  G  numeri noti: FIX1 contro L17 (data/2026-09-14/L17/tb_uscite_fisse_e4.csv,
     Re(Z) max 53,1318, nodo 0,0386 ohm); MAIN contro tb_zout_psrr_noise.cir
     corretto in L13 (data/2026-09-15/L13/dopo/, |Z| 1 kHz)
"""
import csv
import glob
import math
import os
import re
import sys

MODES = {"0db": 0.0, "3db": 3.05, "10db": 9.97}       # E2, ADR-026
TRIMS = {"0": 0.0, "6": -6.003, "12": -11.939}        # tb_trim.cir, L16, cand 2
ATTS = {"0": None, "25": 2.5e3, "50": 5e3, "75": 7.5e3, "100": 10e3}  # RATTL
OUTS = ("main", "fix1", "fix2")
COLS = ("zrmax", "zr20", "zr1k", "zr20k", "zm20", "zm1k", "zn1k", "zn20k")
TOL_DB = 0.15
SOGLIA_E4 = 100.0
SOGLIA_COSTANZA = 1.0
NOTI_FIX = {"zrmax": 53.1318, "zn1k": 0.03864}                  # L17
NOTI_MAIN_ZM1K = {"0db": 57.94488, "3db": 57.95394, "10db": 57.99139}  # L13 dopo


class Esito:
    def __init__(self):
        self.falliti = []

    def check(self, sigla, ok, msg):
        if not ok:
            self.falliti.append(f"{sigla}: {msg}")
        return ok


def rel(a, b):
    return abs(a - b) / max(abs(a), abs(b), 1e-30)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    d = sys.argv[1]
    ptab = os.path.join(d, "tb_e4_uscite_tab.csv")
    pgain = os.path.join(d, "tb_e4_uscite_guadagno.csv")
    logs = glob.glob(os.path.join(d, "*.log"))
    if not (os.path.exists(ptab) and os.path.exists(pgain) and len(logs) == 1):
        print(f"MANCANO I FILE in {d}: tabella {os.path.exists(ptab)}, "
              f"guadagno {os.path.exists(pgain)}, log {len(logs)}")
        return 2
    e = Esito()
    log = open(logs[0]).read().splitlines()

    # ---------------- A: completezza ----------------
    nerr = sum(1 for x in log if "Error" in x)
    e.check("A", nerr == 0, f"{nerr} righe 'Error' nel log")
    tab, gain = {}, {}
    with open(ptab) as f:
        for r in csv.DictReader(f):
            key = (r["out"], r["trim"], r["att"], r["mode"])
            vals = {}
            for c in COLS:
                try:
                    vals[c] = float(r[c])
                except (ValueError, TypeError):
                    vals[c] = None
            e.check("A", None not in vals.values(), f"cella vuota in {key}")
            e.check("A", key not in tab, f"riga ripetuta {key}")
            tab[key] = vals
    with open(pgain) as f:
        for r in csv.DictReader(f):
            key = (r["trim"], r["att"], r["mode"])
            try:
                gain[key] = float(r["g1k_db"])
            except (ValueError, TypeError):
                gain[key] = None
                e.check("A", False, f"guadagno vuoto in {key}")
    celle = [(t, a, m) for t in TRIMS for a in ATTS for m in MODES]
    for t, a, m in celle:
        e.check("A", (t, a, m) in gain, f"manca il guadagno {t},{a},{m}")
        for o in OUTS:
            e.check("A", (o, t, a, m) in tab, f"manca la riga {o},{t},{a},{m}")
    e.check("A", len(tab) == 135, f"{len(tab)} righe di Zout, attese 135")
    e.check("A", len(gain) == 45, f"{len(gain)} righe di guadagno, attese 45")
    if e.falliti:
        return fine(e, {}, tab)

    # ---------------- B: tabella = log ----------------
    val = re.compile(r"^(\w+) = ([-+0-9.eE]+)$")
    nb = 0
    for i, x in enumerate(log):
        mc = re.match(r"^CELL out=(\w+) trim=(\d+) att=(\d+) mode=(\w+)$", x)
        mg = re.match(r"^GAIN trim=(\d+) att=(\d+) mode=(\w+)$", x)
        if mc:
            key = mc.groups()
            got = {}
            for y in log[i + 1:i + 1 + len(COLS)]:
                mv = val.match(y)
                if mv:
                    got[mv.group(1)] = float(mv.group(2))
            for c in COLS:
                ok = c in got and key in tab and rel(got[c], tab[key][c]) < 1e-5
                e.check("B", ok, f"{key} {c}: log {got.get(c)} tabella "
                        f"{tab.get(key, {}).get(c)}")
                nb += 1
        elif mg:
            key = mg.groups()
            mv = val.match(log[i + 1]) if i + 1 < len(log) else None
            ok = mv is not None and key in gain and \
                abs(float(mv.group(2)) - gain[key]) < 1e-4 * max(1, abs(gain[key]))
            e.check("B", ok, f"guadagno {key}: log {mv and mv.group(2)} tabella {gain.get(key)}")
            nb += 1
    e.check("B", nb == 135 * len(COLS) + 45, f"{nb} valori confrontati col log, "
            f"attesi {135 * len(COLS) + 45}")

    # ---------------- C: controllo positivo ----------------
    for t, a, m in celle:
        g = gain[(t, a, m)]
        if ATTS[a] is None:
            e.check("C", g < -100, f"trim {t} att {a} {m}: {g:.3f} dB, "
                    "atteso < -100 (cursore a massa)")
            continue
        att = 20 * math.log10(ATTS[a] / 10e3)
        atteso = MODES[m] + TRIMS[t] + att
        e.check("C", abs(g - atteso) < TOL_DB,
                f"trim {t} att {a} {m}: {g:.3f} dB, atteso {atteso:.3f} +/- {TOL_DB}")

    # ---------------- D: la sonda e' al jack ----------------
    for key, v in tab.items():
        e.check("D", v["zr1k"] >= 46.9, f"{key} Re(Z) 1 kHz {v['zr1k']:.4g} < 47 ohm: "
                "la sonda non e' al jack")
        e.check("D", v["zm20"] > 1e3, f"{key} |Z| 20 Hz {v['zm20']:.4g}: il 4,7 uF "
                "non e' nel percorso misurato")
        e.check("D", v["zn1k"] < 1.0, f"{key} nodo del blocco {v['zn1k']:.4g} ohm")

    # ---------------- E, F: il verdetto ----------------
    riass = {}
    for o in OUTS:
        gruppi = [[m] for m in MODES] if o == "main" else [list(MODES)]
        for ms in gruppi:
            righe = [tab[(o, t, a, m)] for t in TRIMS for a in ATTS for m in ms]
            r = {"n": len(righe), "zrmax": max(x["zrmax"] for x in righe)}
            for c in ("zrmax", "zr1k", "zm1k", "zn1k"):
                vs = [x[c] for x in righe]
                r[c + "_min"], r[c + "_max"] = min(vs), max(vs)
                r[c + "_disp"] = max(vs) - min(vs)
            etich = f"{o} {'+'.join(ms)}"
            riass[etich] = r
            e.check("E", r["zrmax"] < SOGLIA_E4,
                    f"{etich}: Re(Z) max {r['zrmax']:.4f} >= {SOGLIA_E4} ohm")
            for c in ("zrmax", "zr1k", "zm1k"):
                e.check("F", r[c + "_disp"] < SOGLIA_COSTANZA,
                        f"{etich}: {c} varia di {r[c + '_disp']:.4g} ohm "
                        f"({r[c + '_min']:.4g} .. {r[c + '_max']:.4g}) - non costante")

    # ---------------- G: numeri noti ----------------
    for o in ("fix1", "fix2"):
        for key, v in tab.items():
            if key[0] != o:
                continue
            for c, ref in NOTI_FIX.items():
                tol = 1e-3 if c == "zrmax" else 1e-2
                e.check("G", rel(v[c], ref) < tol, f"{key} {c} {v[c]:.6g} contro "
                        f"L17 {ref}")
    for m, ref in NOTI_MAIN_ZM1K.items():
        for t in TRIMS:
            for a in ATTS:
                v = tab[("main", t, a, m)]["zm1k"]
                e.check("G", rel(v, ref) < 1e-3, f"main {t},{a},{m} |Z| 1 kHz "
                        f"{v:.6g} contro tb_zout_psrr_noise corretto {ref}")
    return fine(e, riass, tab)


def fine(e, riass, tab):
    if riass:
        print("uscita / modi         celle  Re(Z)max  Re(Z)1k min..max      "
              "|Z|1k min..max        nodo 1k min..max       disp Re(Z)max")
        for k, r in riass.items():
            print(f"{k:<21} {r['n']:>5}  {r['zrmax']:8.4f}  "
                  f"{r['zr1k_min']:8.4f}..{r['zr1k_max']:8.4f}  "
                  f"{r['zm1k_min']:8.4f}..{r['zm1k_max']:8.4f}  "
                  f"{r['zn1k_min']:.5f}..{r['zn1k_max']:.5f}  "
                  f"{r['zrmax_disp']:.3e}")
    if e.falliti:
        sig = sorted({x[0] for x in e.falliti})
        print(f"\nRIFIUTATO: {len(e.falliti)} controlli falliti, sigle {''.join(sig)}")
        for x in e.falliti[:25]:
            print("  " + x)
        if len(e.falliti) > 25:
            print(f"  ... e altri {len(e.falliti) - 25}")
        return 1
    print("\nVERDETTO E4: CONFORME su MAIN, FIX1, FIX2 - Re(Z) < 100 ohm in banda in "
          "ogni cella, costante con trim e attenuatore (dispersione < 1 ohm), "
          "controlli A-G tutti passati")
    return 0


if __name__ == "__main__":
    sys.exit(main())
