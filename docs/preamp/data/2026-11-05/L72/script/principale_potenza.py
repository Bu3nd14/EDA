"""L72: che cosa protegge le Heresy da un guasto della scheda audio sull'uscita principale (NC-084).

Solo calcolo. Uso: /usr/bin/python3 -I .../L72/script/principale_potenza.py

La catena di oggi (REQUIREMENTS.md, contesto d'uso): conrad-johnson Evolution 250 (MV50 in triodo, 30 W),
Klipsch Heresy I 96 dB / 1 W / 1 m, 8 ohm. La convenzione dei dB SPL della FMEA e' quella di NC-028:
96 + 20 log10(V_picco_al_diffusore / 2,83 V), col finale x21,1.
Il trasformatore d'uscita non blocca un gradino di 14-21 V con costante ~0,3 s: lo passa come transitorio
di bassa frequenza (L65, rilievo R7). Quello che limita e' la potenza: il finale satura.
"""
import math

P_FINALE, R_ALTOP, SENS, G_FINALE = 30.0, 8.0, 96.0, 21.1
V_CLIP = math.sqrt(2 * P_FINALE * R_ALTOP)            # picco al diffusore in clipping, seno


def spl(v_picco_diffusore):
    return SENS + 20 * math.log10(v_picco_diffusore / 2.83)


tetto = spl(V_CLIP)
print(f"Il finale satura a {V_CLIP:.1f} V di picco su 8 ohm: {tetto:.1f} dB SPL di picco a 1 m")
print(f"  ingresso del finale al clipping: {V_CLIP / G_FINALE:.2f} V di picco "
      f"(il gradino del guasto, 14-21 V, e' {14 / (V_CLIP / G_FINALE):.0f}-{21 / (V_CLIP / G_FINALE):.0f} volte tanto)")
for v_jack, nome in ((14.4, "Q132 corto B-E (FMEA)"), (21.4, "Q132 corto C-E (FMEA)")):
    print(f"  {nome}: lineare {spl(v_jack * G_FINALE):.1f} dB SPL; il finale ne da' al piu' {tetto:.1f}")
# il caso peggiore di potenza: il finale in clipping duro, onda quadra = il doppio della potenza del seno
print(f"Potenza nel diffusore: {P_FINALE:.0f} W col seno al clipping, al piu' {2 * P_FINALE:.0f} W in onda "
      f"quadra; contro i 100 W continui / 400 W di picco che Klipsch pubblica per Heresy III e IV")
print(f"  margine sul continuo: {10 * math.log10(100 / (2 * P_FINALE)):.1f} dB col caso quadro, "
      f"{10 * math.log10(100 / P_FINALE):.1f} dB col seno")
