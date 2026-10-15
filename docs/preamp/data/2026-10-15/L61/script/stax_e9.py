"""L61: il condensatore d'uscita della fissa 2 (Stax) al limite di E9, e P10.

Solo calcolo, nessun circuito toccato. Uso:
    /usr/bin/python3 -I docs/preamp/data/2026-10-15/L61/script/stax_e9.py

La catena della fissa 2 (circuits/preamp/preamp_audio.py) ha due poli bassi:
  - C_IN 1 uF su R_SEL 470k || R_IN 1M (ADR-064), -0.003 dB a 20 Hz;
  - C_out 4.7 uF (ADR-007) sui due bleed da 470k (lato jack e lato
    condensatore, ADR-044) e sul carico: a vuoto 235k, Stax 50k -> 42.7k.
Il blocco A e il buffer F2 sono accoppiati in continua (nessun condensatore
nel ramo di reazione in gain_block.py).
"""
import math

V_STEP = 14.9    # gradino al jack, blocco al rail (L45a, ADR-069)
V_ROOF = 0.87    # tetto di non-danno (PR-23)
E9_DB = 0.2      # +-0.2 dB a 20 Hz (E9, ADR-053)
F = 20.0


def par(*r):
    return 1.0 / sum(1.0 / x for x in r)


def loss_db(fc, f=F):
    """Attenuazione di un passa-alto del primo ordine a f, in dB (positiva)."""
    return 10 * math.log10(1 + (fc / f) ** 2)


def t_above(tau, v0=V_STEP, roof=V_ROOF):
    return tau * math.log(v0 / roof)


R_A_VUOTO = par(470e3, 470e3)
R_STAX = par(470e3, 470e3, 50e3)
R_IN = par(470e3, 1e6)
fc_in = 1 / (2 * math.pi * R_IN * 1e-6)

# --- 1. i numeri noti, prima dei nuovi ---------------------------------
chk = [
    ("C_IN 1u, perdita a 20 Hz [dB]", loss_db(fc_in), 0.003, 0.0005),
    ("4.7u a vuoto, tau [s]", 4.7e-6 * R_A_VUOTO, 1.1, 0.02),
    ("4.7u a vuoto, sopra 0.87 V [s]", t_above(4.7e-6 * R_A_VUOTO), 3.1, 0.05),
    ("4.7u su Stax 50k, tau [s] (ADR-069: 0.20)", 4.7e-6 * par(R_A_VUOTO, 50e3), 0.20, 0.01),
    ("tau 37 ms, sopra 0.87 V [ms]", 1e3 * t_above(0.037), 105, 1),
]
for name, got, want, tol in chk:
    ok = abs(got - want) <= tol
    print(f"[{'ok' if ok else 'FALLITO'}] {name}: {got:.4g} (atteso {want})")
    assert ok, name

# --- 2. il condensatore d'uscita al limite di E9 ------------------------
budget = E9_DB - loss_db(fc_in)
fc_max = F * math.sqrt(10 ** (budget / 10) - 1)
tau_min = 1 / (2 * math.pi * fc_max)
c_min = tau_min / R_STAX
print(f"\nBudget al condensatore d'uscita: {budget:.4f} dB -> fc <= {fc_max:.3f} Hz, "
      f"tau >= {1e3 * tau_min:.1f} ms, C >= {1e9 * c_min:.0f} nF sul carico Stax "
      f"({R_STAX / 1e3:.1f} kOhm)")

# Per P10 servirebbe tau <= 100 ms / ln(14.9/0.87)
tau_p10 = 0.100 / math.log(V_STEP / V_ROOF)
print(f"P10 (100 ms) chiede tau <= {1e3 * tau_p10:.1f} ms: fc >= "
      f"{1 / (2 * math.pi * tau_p10):.2f} Hz, a 20 Hz "
      f"{loss_db(1 / (2 * math.pi * tau_p10)) + loss_db(fc_in):.3f} dB sulla catena")

print("\nValori commerciali (film), con +-5 % di tolleranza:")
print(f"{'C':>7} {'tol':>5} {'E9 20 Hz Stax':>14} {'sopra 0.87 V Stax':>18} {'a vuoto':>9}")
for c in (0.82e-6, 1.0e-6):
    for k in (0.95, 1.0, 1.05):
        cc = c * k
        e9 = loss_db(1 / (2 * math.pi * cc * R_STAX)) + loss_db(fc_in)
        ts = t_above(cc * R_STAX)
        tv = t_above(cc * R_A_VUOTO)
        print(f"{c * 1e6:>5.2f}u {k:>5.2f} {e9:>11.3f} dB {1e3 * ts:>15.0f} ms {tv:>7.2f} s")
