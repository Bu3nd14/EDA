"""L72: le finestre di valore della lista ammessa (NC-082, P6), e E12 per ogni tipo.

Solo calcolo. Uso: /usr/bin/python3 -I .../L72/script/finestre.py  -> finestre.csv

Le catene a 20 Hz (poli del primo ordine; L61 / L60c2 mostrano che il modello a poli ridà la
simulazione entro 0,001 dB sulla Stax, stax_finestra.py):
  principale: C_IN su 470k || 1M; C_T su >= 8 kOhm (bilanciamento + volume, preamp_audio.py);
              C_out su 220k || 220k || 100k (i due bleed e il cj EV250, il carico del contesto d'uso)
  fissa 1:    C_IN; C_out su 470k || 470k || Singxer (impedenza ignota: 10 kOhm, il caso di ADR-007)
  fissa 2:    C_IN; C_out su 470k || 470k || 50k (Stax)
Il blocco A, i buffer e il blocco B sono accoppiati in continua (R_G 1M al cursore).
Ogni finestra si controlla con TUTTI i condensatori della catena al limite basso della finestra, a -5 %.

E10 a 20 Hz: lo scarto fra i canali dovuto alla tolleranza dei condensatori (un canale a +5 %,
l'altro a -5 %, sulla stessa catena), da sommare allo 0,049 dB delle resistenze (e10_caso_peggiore.py).

E12: la continua al jack viene dalla perdita del film. Ai capi del condensatore d'uscita c'e' la
continua dell'uscita del blocco: a regime al piu' +-30 mV con la dispersione delle parti (NC-041,
preamp_audio.py); si prende 0,1 V, tre volte tanto. Un guasto non e' «a regime» (E12). La
corrente di perdita e' V * C / tau_IR e chiude sul carico al jack: V_jack = V * C * R_jack / tau_IR.
Se ne ricava la tau_IR minima perche' V_jack <= 1 mV; il tipo della lista la deve superare.
"""
import csv
import math
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
F = 20.0
TOL = 0.05


def par(*r):
    return 1.0 / sum(1.0 / x for x in r)


def loss(c, r, f=F):
    fc = 1 / (2 * math.pi * r * c)
    return 10 * math.log10(1 + (fc / f) ** 2)


R_IN = par(470e3, 1e6)
R_CT = 8e3
R_MAIN = par(220e3, 220e3, 100e3)
R_F1 = par(470e3, 470e3, 10e3)
R_F2 = par(470e3, 470e3, 50e3)

# finestre nominali (uF): basso, alto, oggi; e il perche'
FIN = {
    "ingresso C171-C174 / C371-C374": (1.0, 2.2, 1.0, R_IN,
        "basso: il budget di E9 delle altre finestre e' calcolato con 1 uF; alto: PR-14 (F1 regge "
        "~0,65 V di continua della sorgente con C/tau_IR = 1 uF / 10 000 s, ADR-064): tau_IR >= 10 000 s x C[uF]"),
    "C_T C265 / C465": (6.8, 10.0, 10.0, R_CT,
        "basso: E9 sulla principale con C_IN e C_out al loro basso; alto: 10 uF, il valore verificato "
        "(il gradino del trim si scarica in C_T con tau ~0,1 s sotto il mute, PR-17)"),
    "principale C262 / C462": (2.2, 10.0, 4.7, R_MAIN,
        "basso: E9 col cj EV250 da 100 kOhm (architetto L65); alto: nessun requisito, le durate di P10 "
        "sulla principale e il clic al rilascio a 20 Hz si dichiarano (non hanno soglia)"),
    "fissa 1 C162 / C362": (4.7, 10.0, 4.7, R_F1,
        "basso: 4,7 uF, l'impedenza d'ingresso del Singxer non e' pubblicata (ADR-007); alto: nessun requisito"),
    "fissa 2 C165 / C365": (1.0, 1.1, 1.0, R_F2,
        "reale 0,895-1,265 uF (stax_finestra.py e le corse di stax/): 1,0 o 1,1 uF a +-5 %"),
}

chk = [("Stax 1 uF a 20 Hz con C_IN (L60c2 simulato 0,161)",
        loss(1e-6, R_IN) + loss(1e-6, R_F2), 0.161, 0.002)]
for name, got, want, tol in chk:
    ok = abs(got - want) <= tol
    print(f"[{'ok' if ok else 'FALLITO'}] {name}: {got:.4f}")
    assert ok, name

cin = FIN["ingresso C171-C174 / C371-C374"]
catene = {
    "principale": [("ingresso C171-C174 / C371-C374", R_IN), ("C_T C265 / C465", R_CT),
                   ("principale C262 / C462", R_MAIN)],
    "fissa 1": [("ingresso C171-C174 / C371-C374", R_IN), ("fissa 1 C162 / C362", R_F1)],
    "fissa 2": [("ingresso C171-C174 / C371-C374", R_IN), ("fissa 2 C165 / C365", R_F2)],
}
print("\nE9 a 20 Hz, ogni condensatore al basso della finestra a -5 % (limite 0,2 dB):")
e9 = {}
for cat, el in catene.items():
    tot = sum(loss(FIN[k][0] * 1e-6 * (1 - TOL), r) for k, r in el)
    oggi = sum(loss(FIN[k][2] * 1e-6, r) for k, r in el)
    hi = sum(loss(FIN[k][0] * 1e-6 * (1 + TOL), r) for k, r in el)
    e9[cat] = (tot, oggi, tot - hi)
    print(f"  {cat:10s}: {tot:.3f} dB ({'entro' if tot <= 0.2 else 'FUORI'}); oggi {oggi:.3f} dB; "
          f"scarto fra i canali al basso (+-5 %) {tot - hi:.3f} dB")
    assert tot <= 0.2, cat

V_DC = 0.1
print("\nE12: tau_IR minima per <= 1 mV al jack con 0,1 V ai capi (3 x i 30 mV del blocco):")
righe = []
for k, (lo, hi_, oggi, r, perche) in FIN.items():
    if k.startswith("ingresso") or k.startswith("C_T"):
        tau_min = None   # non danno continua al jack: a valle c'e' un condensatore d'uscita
        r_jack = None
    else:
        r_jack = {"principale C262 / C462": R_MAIN, "fissa 1 C162 / C362": par(470e3, 470e3),
                  "fissa 2 C165 / C365": par(470e3, 470e3)}[k]   # a vuoto: il carico piu' alto
        tau_min = V_DC * hi_ * 1e-6 * r_jack / 1e-3
    righe.append({"posizione": k, "finestra_nominale_uF": f"{lo:g}-{hi_:g}", "oggi_uF": oggi,
                  "tau_IR_min_s_per_E12": "" if tau_min is None else round(tau_min, 1),
                  "perche": perche})
    print(f"  {k:32s}: {lo:g}-{hi_:g} uF; tau_IR >= "
          f"{'(nessun limite: c e un condensatore d uscita a valle)' if tau_min is None else f'{tau_min:.0f} s'}")
for cat, (tot, oggi, sc) in e9.items():
    righe.append({"posizione": f"E9 catena {cat}", "finestra_nominale_uF": "",
                  "oggi_uF": "", "tau_IR_min_s_per_E12": "",
                  "perche": f"20 Hz al basso -5 %: {tot:.3f} dB; oggi {oggi:.3f} dB; scarto L-R {sc:.3f} dB"})
with open(os.path.join(L, "finestre.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(righe[0]))
    w.writeheader()
    w.writerows(righe)
