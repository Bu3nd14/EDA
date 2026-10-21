#!/usr/bin/env python3
"""L45d2b2c: le tensioni e il calore delle parti del blocco col rail alto, contro i loro limiti.
Solo stdlib, /usr/bin/python3 -I.

Uso: analizza_massimi.py    legge run/<rail>_B/<modo>/ e run/tb_<rail>/tb_mute_corto/, scrive
                            tensioni.csv, calore.csv, p7.csv e massimi_blocco.csv

LE TENSIONI (<modo>_tensioni.csv di genera_massimi.py: massimo e minimo su tutta la corsa di ogni
differenza fra due terminali). Ogni parte contro i limiti di limiti_blocco.csv (DS salvo dove detto),
con la polarita' della parte:
  NPN (MMBT/DZT5551, MJE15032)   V_CE = max(c-e), V_CB = max(c-b), V_EB inversa = max(e-b)
  PNP (MMBT/DZT5401, LS352, MJE15033)  V_EC = -min(c-e), V_BC = -min(c-b), V_BE inversa = -min(e-b)
  JFET N (LSK489)                V_GS inversa = -min(g-s), V_GD inversa = -min(g-d) (V_GSO, V_GDO
                                 60 V); V_DS = max(d-s): nessun limite nel DS (Rev A30), solo letto
  diodo (1N4148)                 inversa = -min(a-k), V_R 75 V
  condensatore                   |V| massima; la tensione nominale dove il sorgente la scrive (C145
                                 >= 25 V), altrimenti quella che la parte deve avere (riga «serve»)
LE R_thJA e il calore: Tj = 60 C + P * R_thJA (P7, ADR-021), le R_thJA di analizza_L62b.py (q127
125 C/W, LS352 233 e LSK489 250 sulla somma), P dai <modo>_fine.csv (ultimi 10 ms). Resistenze:
0,25 W (0207 a 60 C, Yageo MFR-25 nominali a 70 C), R134 / R135 0,34 W (ADR-021).
P7: tb_mute_corto_regime.csv, tb_mute_corto_l56.csv e tb_mute_corto_vbe.csv (una riga per cella e
per blocco), il massimo su tutte le righe.
"""
import csv
import glob
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(LOTTO, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-13", "L45a", "script"))
import analizza_tr as at  # noqa: E402

RAIL = ("nom", "p", "m", "pm")
# P7 only: the rail of the IN-OUT short at mains -10 / 0 / +10 % (genera_massimi.py, RAIL_P7)
RAIL_P7 = ("p_m10", "p_0", "p_p10", "m_m10", "m_0", "m_p10")
TA, TJ_P7 = 60.0, 125.0
# the 47 ohm of the main output: >= 1.3 W at 60 C (ADR-087, NONCOMPLIANCE.md); the MJE's V_EB 5 V
R47_LIM, VBE_MJE = 1.3, 5.0
RTH = dict(at.RTH)
RTH.update({"q127": 125})
R_LIM, R22_LIM = 0.25, 0.34
NPN = {"q106": "MMBT5551", "q117": "MMBT5551", "q118": "MMBT5551", "q125": "DZT5551",
       "q127": "DZT5551", "q132": "MJE15032"}
PNP = {"q122": "DZT5401", "q146": "MMBT5401", "q148": "MMBT5401", "q121a": "LS352",
       "q121b": "LS352", "q133": "MJE15033"}
# (V_CE / V_EC, V_CB / V_BC, base-emettitore inversa), limiti_blocco.csv
LIM_Q = {"MMBT5551": (160, 180, 6.0), "DZT5551": (160, 180, 6.0), "MJE15032": (250, 250, 5.0),
         "MMBT5401": (150, 160, 5.0), "DZT5401": (150, 160, 6.0), "LS352": (60, 60, 6.0),
         "MJE15033": (250, 250, 5.0)}
# i condensatori: (parte, nominale o None, nota)
CAP = {"c104": ("100u elettrolitico", None), "c116": ("47u elettrolitico", None),
       "c141": ("100u elettrolitico", None), "c142": ("100u elettrolitico", None),
       "c145": ("1000u elettrolitico", 25.0), "c105": ("100n ceramico", 50.0),
       "c139": ("100n ceramico", 50.0), "c140": ("100n ceramico", 50.0),
       "c124": ("470p C0G", 100.0), "c137": ("330p C0G", None)}


def leggi(p):
    if not os.path.isfile(p):
        return None
    out = {}
    for r in csv.reader(open(p)):
        if len(r) == 2 and r[0] != "grandezza":
            try:
                out[r[0]] = float(r[1])
            except ValueError:
                out[r[0]] = float("nan")
    return out


def voci_tensioni(t):
    """(parte, grandezza, valore, limite) dalle misure di un deck."""
    v = []
    for q, tipo in sorted(NPN.items()):
        lce, lcb, leb = LIM_Q[tipo]
        v += [(q, tipo, "V_CE", t["t_%s_ce_max" % q], lce), (q, tipo, "V_CB", t["t_%s_cb_max" % q], lcb),
              (q, tipo, "V_EB inversa", t["t_%s_eb_max" % q], leb)]
    for q, tipo in sorted(PNP.items()):
        lce, lcb, leb = LIM_Q[tipo]
        v += [(q, tipo, "V_EC", -t["t_%s_ce_min" % q], lce), (q, tipo, "V_BC", -t["t_%s_cb_min" % q], lcb),
              (q, tipo, "V_BE inversa", -t["t_%s_eb_min" % q], leb)]
    for j in ("jq110a", "jq110b"):
        v += [(j, "LSK489", "V_GS inversa", -t["t_%s_gs_min" % j], 60.0),
              (j, "LSK489", "V_GD inversa", -t["t_%s_gd_min" % j], 60.0),
              (j, "LSK489", "V_DS", t["t_%s_ds_max" % j], None)]
    for d in ("d102", "d103", "d154", "d155", "d156", "d157"):
        v.append((d, "1N4148", "inversa", -t["t_%s_ak_min" % d], 75.0))
    for c, (tipo, lim) in sorted(CAP.items()):
        v.append((c, tipo, "|V|", max(abs(t["t_%s_12_max" % c]), abs(t["t_%s_12_min" % c])), lim))
        v.append((c, tipo, "segno", 1.0 if t["t_%s_12_min" % c] * t["t_%s_12_max" % c] < 0 else 0.0, None))
    return v


def main():
    global R22_LIM, R47_LIM
    # analizza_massimi.py cbe: only P7 of the variant with D158 / D159 (run/tb_cbe_<rail>/), against
    # the constraints the user chose (2026-10-21, «Resistenze piu' robuste»): the 22 ohm >= 0.45 W and
    # the 47 ohm of the main output >= 1.6 W at 60 C -> p7_cbe.csv; with the diodes' current and power
    cbe = sys.argv[1:] == ["cbe"]
    pref = "tb_cbe_" if cbe else "tb_"
    if cbe:
        R22_LIM, R47_LIM = 0.45, 1.6
    tens, calore, p7 = [], [], []
    peggio = {}
    for r in (() if cbe else RAIL):
        for d in sorted(glob.glob(os.path.join(LOTTO, "run", "%s_B" % r, "*"))):
            if not os.path.isdir(d):
                continue
            modo = os.path.basename(d)
            t = leggi(os.path.join(d, modo + "_tensioni.csv"))
            f = leggi(os.path.join(d, modo + "_fine.csv"))
            if not t or not f:
                sys.exit("RIFIUTATO: %s senza tensioni o fine" % d)
            for parte, tipo, g, val, lim in voci_tensioni(t):
                riga = {"rail": r, "modo": modo, "parte": parte, "tipo": tipo, "grandezza": g,
                        "valore": "%.3f" % val, "limite": "" if lim is None else "%g" % lim,
                        "margine": "" if lim is None else "%.2f" % (lim - val)}
                tens.append(riga)
                k = (r, parte, g)
                if k not in peggio or val > float(peggio[k]["valore"]):
                    peggio[k] = riga
            c = {"rail": r, "modo": modo, "I_rail_piu_mA": "%.1f" % (-f["ipp_avg"] * 1e3),
                 "I_rail_meno_mA": "%.1f" % (f["imm_avg"] * 1e3)}
            tj = {k: TA + abs(f["p_" + k]) * rt for k, rt in RTH.items() if "p_" + k in f}
            tj["q121"] = TA + (abs(f["p_q121a"]) + abs(f["p_q121b"])) * 233
            tj["jq110"] = TA + (abs(f["p_jq110a"]) + abs(f["p_jq110b"])) * 250
            for k in ("q132", "q133", "q122", "q125", "q127", "q146", "q148", "q121", "jq110"):
                if k in tj:
                    c["Tj_%s" % k] = "%.1f" % tj[k]
            for k in ("q132", "q133"):
                c["P_%s_W" % k] = "%.3f" % abs(f["p_" + k])
            pr = {k[2:]: abs(x) for k, x in f.items() if k.startswith("p_r")}
            for k in ("r134", "r135", "r123", "r126", "r144", "r152"):
                c["P_%s_W" % k] = "%.3f" % pr.get(k, float("nan"))
            oltre = ["%s %.0f C" % (k, x) for k, x in sorted(tj.items()) if x > TJ_P7]
            oltre += ["%s %.3f W" % (k, p) for k, p in sorted(pr.items())
                      if p > (R22_LIM if k in ("r134", "r135") else R_LIM)]
            c["oltre_60C"] = "; ".join(oltre)
            calore.append(c)
    for r in RAIL + RAIL_P7:
        reg = os.path.join(LOTTO, "run", pref + r, "tb_mute_corto", "tb_mute_corto_regime.csv")
        l56 = os.path.join(LOTTO, "run", pref + r, "tb_mute_corto", "tb_mute_corto_l56.csv")
        if not os.path.isfile(reg) or not os.path.isfile(l56):
            sys.exit("RIFIUTATO: P7 di %s mancante" % r)
        righe = list(csv.DictReader(open(reg)))
        righe56 = list(csv.DictReader(open(l56)))
        x = {"rail": r, "celle": len(righe)}
        for k in ("p_q132", "p_q133", "p_q122", "p_q125", "p_q127", "p_q117", "p_q118", "p_q106",
                  "p_r134", "p_r135", "p_r123", "p_r126", "p_rsep", "p_rsep2"):
            x[k] = "%.4f" % max(abs(float(z[k])) for z in righe)
        for k in ("p_q146", "p_q148", "p_r153"):
            x[k] = "%.4f" % max(abs(float(z[k])) for z in righe56)
        q121 = max(abs(float(z["p_q121a"])) + abs(float(z["p_q121b"])) for z in righe)
        j110 = max(abs(float(z["p_jq110a"])) + abs(float(z["p_jq110b"])) for z in righe)
        tj = {k: TA + float(x["p_" + k]) * RTH[k] for k in ("q132", "q133", "q122", "q125", "q117",
                                                             "q118", "q106", "q146", "q148")}
        tj["q127"] = TA + float(x["p_q127"]) * 125
        tj["q121"] = TA + q121 * 233
        tj["jq110"] = TA + j110 * 250
        for k in sorted(tj):
            x["Tj_%s" % k] = "%.1f" % tj[k]
        oltre = ["%s %.0f C" % (k, v) for k, v in sorted(tj.items()) if v > TJ_P7]
        oltre += ["%s %.3f W" % (k, float(x["p_" + k])) for k in ("r134", "r135")
                  if float(x["p_" + k]) > R22_LIM]
        oltre += ["%s %.3f W" % (k, float(x["p_" + k])) for k in ("r123", "r126", "r153")
                  if float(x["p_" + k]) > R_LIM]
        if float(x["p_rsep"]) > R47_LIM:
            oltre.append("47 ohm %.3f W" % float(x["p_rsep"]))
        vbe = list(csv.DictReader(open(reg.replace("_regime.csv", "_vbe.csv"))))
        # one row per cell and block in both files (150 cells x 4 blocks)
        if len(vbe) != len(righe) or {z["blk"] for z in vbe} != {"A", "F1", "F2", "B"}:
            sys.exit("RIFIUTATO: %s ha %d righe di vbe per %d celle" % (r, len(vbe), len(righe)))
        x["veb_q132_inv_max"] = "%.3f" % max(float(z["veb_q132_max"]) for z in vbe)
        x["vbe_q133_inv_max"] = "%.3f" % max(float(z["vbe_q133_max"]) for z in vbe)
        oltre += ["%s %s V in inversa" % (k, x[k]) for k in ("veb_q132_inv_max", "vbe_q133_inv_max")
                  if float(x[k]) > VBE_MJE]
        if cbe:
            # 1N4148: I_F 300 mA continuous, I_FRM 500 mA, P_tot 440 mW at 45 C (limiti_blocco.csv)
            for k in ("id_d158_max", "id_d159_max", "p_d158", "p_d159"):
                x[k] = "%.4f" % max(float(z[k]) for z in vbe)
            oltre += ["%s %s A" % (k, x[k]) for k in ("id_d158_max", "id_d159_max") if float(x[k]) > 0.5]
            oltre += ["%s %s W" % (k, x[k]) for k in ("p_d158", "p_d159") if float(x[k]) > 0.44]
        x["oltre_60C"] = "; ".join(oltre)
        p7.append(x)
    if cbe:
        uscite = (("p7_cbe.csv", p7),)
    else:
        uscite = (("tensioni.csv", tens), ("calore.csv", calore), ("p7.csv", p7))
    for nome, righe in uscite:
        campi = []
        for z in righe:
            campi += [k for k in z if k not in campi]
        with open(os.path.join(LOTTO, nome), "w", newline="") as fo:
            w = csv.DictWriter(fo, fieldnames=campi)
            w.writeheader()
            w.writerows(righe)
    if cbe:
        for x in p7:
            print("P7 cbe %-6s q132 %s q133 %s C  r134 %s r135 %s 47ohm %s W  inversa %s / %s V  "
                  "diodi %s / %s A %s / %s W  %s" % (
                      x["rail"], x["Tj_q132"], x["Tj_q133"], x["p_r134"], x["p_r135"], x["p_rsep"],
                      x["veb_q132_inv_max"], x["vbe_q133_inv_max"], x["id_d158_max"], x["id_d159_max"],
                      x["p_d158"], x["p_d159"], x["oltre_60C"]))
        return
    with open(os.path.join(LOTTO, "massimi_blocco.csv"), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(tens[0].keys()))
        w.writeheader()
        for k in sorted(peggio):
            w.writerow(peggio[k])
    fuori = [z for z in peggio.values() if z["margine"] and float(z["margine"]) < 0]
    print("tensioni: %d righe, %d peggiori, %d fuori" % (len(tens), len(peggio), len(fuori)))
    for z in fuori:
        print("  FUORI %s %s %s %s %s (limite %s)" % (z["rail"], z["modo"], z["parte"], z["grandezza"],
                                                   z["valore"], z["limite"]))
    for c in calore:
        print("calore %-4s %-8s q132 %s q133 %s C  %s" % (c["rail"], c["modo"], c.get("Tj_q132"),
                                                         c.get("Tj_q133"), c["oltre_60C"]))
    for x in p7:
        print("P7 %-6s q132 %s q133 %s C  r134 %s r135 %s 47ohm %s W  inversa %s / %s V  %s" % (
            x["rail"], x["Tj_q132"], x["Tj_q133"], x["p_r134"], x["p_r135"], x["p_rsep"],
            x["veb_q132_inv_max"], x["vbe_q133_inv_max"], x["oltre_60C"]))


if __name__ == "__main__":
    main()
