"""L72: la finestra ammessa del condensatore della Stax (C165 / C365), NC-080.

Solo calcolo; i limiti si controllano poi sulle corse di stax/ (genera_stax.py).
Uso: /usr/bin/python3 -I docs/preamp/data/2026-11-05/L72/script/stax_finestra.py

Da L61 (data/2026-10-15/L61/script/stax_e9.py, copiato nella parte 1): la catena della fissa 2 ha due
poli bassi, C_IN 1 uF su 470k || 1M (ADR-064) e il condensatore d'uscita sui due bleed da 470k e sulla
Stax (50k): 41,2 kOhm. Il blocco A e il buffer F2 sono accoppiati in continua.

- Limite BASSO: E9, +-0,2 dB a 20 Hz su ogni uscita (ADR-053), col carico della Stax.
- Limite ALTO: P10 / PR-30, al piu' 150 ms sopra 0,87 V col carico della Stax (ADR-086, ADR-117). Il
  caso peggiore sul banco e' 124,5 ms col condensatore a 1,05 uF (L45d2b3b2b2, il JFET d'ingresso; il
  dossier, sezione 20). La durata sopra soglia di una scarica RC con lo stesso gradino e' tau * ln(V0/Vt):
  lineare in C. La linearita' si controlla con le corse, non si assume.
"""
import math

E9_DB = 0.2
F = 20.0
P10_MS = 150.0
WORST_MS, WORST_C = 124.5, 1.05e-6     # L45d2b3b2b2, G0_A_JQ110A_ds_k105
V_STEP, V_ROOF = 14.0, 0.87            # gradino dell'architetto (L65, R3)


def par(*r):
    return 1.0 / sum(1.0 / x for x in r)


def loss_db(fc, f=F):
    return 10 * math.log10(1 + (fc / f) ** 2)


R_STAX = par(470e3, 470e3, 50e3)
R_IN = par(470e3, 1e6)
fc_in = 1 / (2 * math.pi * R_IN * 1e-6)


def e9_db(c):
    """Perdita a 20 Hz della catena della fissa 2 (due poli del primo ordine)."""
    return loss_db(fc_in) + loss_db(1 / (2 * math.pi * R_STAX * c))


# --- 1. i numeri noti --------------------------------------------------------
chk = [
    ("carico Stax [kOhm] (architetto: 41,2)", R_STAX / 1e3, 41.2, 0.05),
    ("C_IN a 20 Hz [dB] (L61: 0,003)", loss_db(fc_in), 0.003, 0.0005),
    # L60c2, e9.csv: 0,147 / 0,161 / 0,178 dB simulati sul netlist a C +5 % / nominale / -5 %
    ("E9 a 1,05 uF [dB] (L60c2 simulato 0,147)", e9_db(1.05e-6), 0.147, 0.002),
    ("E9 a 1,00 uF [dB] (L60c2 simulato 0,161)", e9_db(1.00e-6), 0.161, 0.002),
    ("E9 a 0,95 uF [dB] (L60c2 simulato 0,178)", e9_db(0.95e-6), 0.178, 0.002),
    ("sopra 0,87 V a 1 uF, 14 V [ms] (architetto: 115)",
     1e3 * R_STAX * 1e-6 * math.log(V_STEP / V_ROOF), 115, 1.5),
]
for name, got, want, tol in chk:
    ok = abs(got - want) <= tol
    print(f"[{'ok' if ok else 'FALLITO'}] {name}: {got:.4g}")
    assert ok, name

# --- 2. i limiti sulla capacita' REALE ---------------------------------------
budget = E9_DB - loss_db(fc_in)
fc_max = F * math.sqrt(10 ** (budget / 10) - 1)
c_lo = 1 / (2 * math.pi * fc_max * R_STAX)
c_hi = WORST_C * P10_MS / WORST_MS
print(f"\nCapacita' reale ammessa: {1e6 * c_lo:.3f} uF (E9: {e9_db(c_lo):.4f} dB a 20 Hz) "
      f"... {1e6 * c_hi:.3f} uF (P10: {WORST_MS} ms x {1e6 * c_hi:.3f}/{1e6 * WORST_C:.2f} = "
      f"{WORST_MS * c_hi / WORST_C:.1f} ms)")

# --- 3. sul valore NOMINALE, con la tolleranza della parte --------------------
print("\nValore nominale ammesso, per tolleranza:")
for tol in (0.01, 0.02, 0.025, 0.05, 0.10):
    lo, hi = c_lo / (1 - tol), c_hi / (1 + tol)
    print(f"  +-{100 * tol:4.1f} %: {1e6 * lo:.3f} ... {1e6 * hi:.3f} uF")

print("\nValori commerciali ±5 %: perdita a 20 Hz al -5 %, durata del peggiore al +5 % (lineare)")
for cn in (0.82e-6, 0.91e-6, 1.0e-6, 1.1e-6, 1.2e-6, 1.5e-6):
    e9 = e9_db(0.95 * cn)
    ms = WORST_MS * 1.05 * cn / WORST_C
    ok = e9 <= E9_DB and ms <= P10_MS
    print(f"  {1e6 * cn:4.2f} uF: E9 {e9:.3f} dB, P10 {ms:5.1f} ms -> {'dentro' if ok else 'FUORI'}")
