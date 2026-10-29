#!/usr/bin/env python3
"""L55: le cifre della domanda all'utente, ricontate dai CSV (la regola delle domande, NEXT-SESSION).

Tre opzioni: il MJE com'e' (mje), il candidato col Miller di oggi (mje24x), il candidato con 330 pF
(mje24x_cm330p). Per ciascuna: V1 (il peggiore su pubblicazione e gruppo B, idss.csv; sintesi.csv), la
distorsione e l'intermodulazione a 27 C uniformi (sintesi.csv) e a caldo, aria 57 C, il peggiore delle
spec --sot223--diss e --sot223--diss--molt (sintesi_caldo.csv; il candidato dalle copie di banco «_fz»),
il PSRR+ (sintesi.csv), lo slew in discesa, il riposo a caldo (riposo.csv non c'e': si stampa dai
tj/), i finali nei corti e a riposo con 60 C d'aria (dissipatore.csv). Solo stdlib, /usr/bin/python3 -I.
"""
import csv
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def righe(f):
    return list(csv.DictReader(open(os.path.join(L, f))))


S = {r["variante"]: r for r in righe("sintesi.csv")}
I = {r["variante"]: r for r in righe("idss.csv")}
C = righe("sintesi_caldo.csv")
D = righe("dissipatore.csv")
OPZ = (("Il MJE com'e'", "mje", "mje", "fmje"),
       ("Candidato, Miller di oggi 470 pF", "mje24x", "mje24x_fz", "c243"),
       ("Candidato, Miller 330 pF", "mje24x_cm330p", "mje24x_cm330p_fz", "c243m"))

for nome, v, vc, vg in OPZ:
    s, i = S[v], I[v]
    v1 = min(float(s["v1_min"]), float(i["B_grB_min"]), float(i["A_grB_min"]), float(i["buf_grB_min"]))
    caldi = [r for r in C if r["spec"] in ("%s--sot223--diss" % vc, "%s--sot223--diss--molt" % vc)
             and r["cond"].startswith("t57")]
    fuori = max(int(r["thd_fuori"]) for r in caldi)
    marg = min(float(r["thd_margine_min_dB"]) for r in caldi)
    thd_lo = max(float(r["thd_lo_max_pct"]) for r in caldi)
    thd_hi = max(float(r["thd_hi_max_pct"]) for r in caldi)
    imd = max(float(r["imd_lo_max_dB"]) for r in caldi)
    dd = {r["caso"]: r for r in D if r["variante"] == vg}
    corto = max(float(dd[k]["Tj_con_C"]) for k in dd if "corto" in k and "P7" not in k)
    riposo = max(float(dd[k]["Tj_con_C"]) for k in dd if "riposo" in k)
    p7 = max(float(dd[k]["Tj_con_C"]) for k in dd if k.startswith("P7"))
    rsa = min(float(dd[k]["RthSA_max_a_125C"]) for k in dd if "corto" in k and "P7" not in k)
    print("== %s (%s / %s / %s)" % (nome, v, vc, vg))
    print("  V1 peggiore %.2f gradi (limite 60); a 27 C: THD 20 kHz 0,2 V %s %%, IMD %s dB, 2 V %s %%"
          % (v1, s["thd_lo_20k"], s["imd_lo_db"], s["thd_hi_20k"]))
    print("  a caldo, aria 57 C: fuori %d su 12, margine peggiore %.1f dB, THD 0,2 V %.6f %% (tetto 0,001),"
          " 2 V %.5f %% (tetto 0,01), IMD %.1f dB (tetto -110)" % (fuori, marg, thd_lo, thd_hi, imd))
    print("  PSRR+ 1 / 10 / 20 kHz %s / %s / %s dB; slew in discesa %s V/us; rumore D %s uV"
          % (s["psrrp_1k"], s["psrrp_10k"], s["psrrp_20k"], s["sr_disc"], s["rum_D_uv"]))
    print("  finali con 60 C d'aria: corti %.0f C, riposo %.0f C, P7 %.0f C (limite 125, max 150);"
          " dissipatore massimo per 125 C: %.1f C/W" % (corto, riposo, p7, rsa))
