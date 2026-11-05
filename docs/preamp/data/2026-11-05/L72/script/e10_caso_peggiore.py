"""L72: E10, l'equilibrio fra i canali, nel caso peggiore delle tolleranze (NC-081).

Solo calcolo. Uso: /usr/bin/python3 -I .../L72/script/e10_caso_peggiore.py  -> e10_caso_peggiore.csv

Le sei posizioni per canale che fissano il guadagno fra i canali col volume al massimo:
  blocco B (il solo che commuta il guadagno, gain_block.py switchable=True):
    R_F 1,50k (R235 / R435), R_G3 3,57k (R237 / R437), R_G10 866 (R242 / R442)
    0 dB: nessun ramo, guadagno 1 esatto; +3 dB: 1 + R_F/R_G3; +10 dB: 1 + R_F/(R_G3 || R_G10)
  la scala del trim (trim.py): R1 845, R2 464, R3 464 (R901-R903 / R911-R913), caricata alla presa
    0 dB: l'uscita del blocco A, esatto; -6 dB: presa fra R1 e R2; -12 dB: presa fra R2 e R3.
Il blocco A e i buffer delle fisse sono inseguitori a guadagno 1 (switchable=False): il loro R_F non
entra. Il carico della presa (bilanciamento + volume, fuori scheda) e' lo STESSO nei due canali: lo
scarto fra le sezioni dei potenziometri e' la clausola da 1 dB di E10, corretta dal bilanciamento
(ADR-065). Il calcolo si fa a 8 kOhm (il minimo, preamp_audio.py), a 10 kOhm (il carico
per cui la scala e' tarata, trim.py) e a vuoto, e prende il peggiore.

Il caso peggiore fra i canali: ogni canale ha 2^6 angoli (ogni resistenza al +tol o al -tol); un
canale all'angolo piu' alto, l'altro al piu' basso. Lo scarto e' max - min sugli angoli.
"""
import csv
import itertools
import math
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
NOM = {"RF": 1500.0, "RG3": 3570.0, "RG10": 866.0, "R1": 845.0, "R2": 464.0, "R3": 464.0}
CARICHI = (8e3, 10e3, 1e12)


def par(*r):
    return 1.0 / sum(1.0 / x for x in r)


def guadagno(r, g):
    if g == 0:
        return 1.0
    if g == 3:
        return 1 + r["RF"] / r["RG3"]
    return 1 + r["RF"] / par(r["RG3"], r["RG10"])


def trim(r, t, rl):
    if t == 0:
        return 1.0
    if t == -6:      # presa fra R1 e R2: sotto la presa (R2 + R3) || carico
        low = par(r["R2"] + r["R3"], rl)
        return low / (r["R1"] + low)
    # -12: presa fra R2 e R3; sotto R3 || carico, sopra R1 + R2
    low = par(r["R3"], rl)
    return low / (r["R1"] + r["R2"] + low)


def db(x):
    return 20 * math.log10(x)


def scarto(tol, g, t, rl):
    vals = []
    for segni in itertools.product((-1, 1), repeat=6):
        r = {k: NOM[k] * (1 + s * tol) for k, s in zip(NOM, segni)}
        vals.append(db(guadagno(r, g) * trim(r, t, rl)))
    return max(vals) - min(vals)


def peggiore(tol, g, t):
    return max(scarto(tol, g, t, rl) for rl in CARICHI)


# --- 1. i numeri noti --------------------------------------------------------
r0 = dict(NOM)
chk = [
    ("+3 dB nominale (gain_block.py: +3,05)", db(guadagno(r0, 3)), 3.05, 0.01),
    ("+10 dB nominale (gain_block.py: +9,97)", db(guadagno(r0, 10)), 9.97, 0.01),
    ("trim -6 dB su 10k (trim.py: -6,003)", db(trim(r0, -6, 10e3)), -6.003, 0.01),
    ("trim -12 dB su 10k (trim.py: -11,939)", db(trim(r0, -12, 10e3)), -11.939, 0.01),
    ("architetto, 1 %, +10 dB fra i canali: 0,24", peggiore(0.01, 10, 0), 0.24, 0.015),
    ("architetto, 1 %, trim -12 fra i canali: 0,26", peggiore(0.01, 0, -12), 0.26, 0.015),
    ("architetto, 1 %, insieme: 0,49", peggiore(0.01, 10, -12), 0.49, 0.02),
]
for name, got, want, tol in chk:
    ok = abs(got - want) <= tol
    print(f"[{'ok' if ok else 'FALLITO'}] {name}: {got:.3f}")
    assert ok, name

# --- 2. tutte le combinazioni, all'1 % e allo 0,1 % ---------------------------
righe = []
for tol in (0.01, 0.001):
    for g in (0, 3, 10):
        for t in (0, -6, -12):
            righe.append({"tolleranza_pct": 100 * tol, "guadagno_dB": g, "trim_dB": t,
                          "scarto_LR_dB": round(peggiore(tol, g, t), 4)})
with open(os.path.join(L, "e10_caso_peggiore.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(righe[0]))
    w.writeheader()
    w.writerows(righe)
for tol in (1.0, 0.1):
    sel = [r for r in righe if r["tolleranza_pct"] == tol]
    m = max(sel, key=lambda r: r["scarto_LR_dB"])
    print(f"\n{tol} %: il peggiore {m['scarto_LR_dB']:.3f} dB (guadagno {m['guadagno_dB']:+d}, "
          f"trim {m['trim_dB']}), contro 0,2 dB")
    for r in sel:
        print(f"   guadagno {r['guadagno_dB']:+3d} dB, trim {r['trim_dB']:4d} dB: {r['scarto_LR_dB']:.4f} dB")
