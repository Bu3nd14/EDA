"""sfumatura.py - L47b1: la sfumatura vera nel tempo, e S col metodo di V2.

La profondita' d(t) sale da 0 a 1 in TD secondi a T_INS, resta, e torna a 0 in TD a T_REL. Il
JFET la riceve sui due comandi (comune.comandi, poi il filtro RC della scheda); la NSL-32SR3 sulle
correnti dei LED col profilo v4 di ADR-040 (comune.correnti_ldr, la stessa tabella del banco V2).
Tono di prova 3,818 V di picco a 1 kHz da 1,5 ohm. Si scrive v(ain).

S e' quella di scripts/v2_metodo.py (importata, non riscritta): l'ampiezza del tono dal fit a + b
su max(10 ms, un periodo), il livello in dB sotto il pieno, tenuto a -70 dB; S = la variazione
massima in 100 ms, all'inserzione e al rilascio. Il pieno: l'ampiezza del 95esimo percentile
prima dell'inserzione (la cella in gioco). v(AIN) invece del jack: gli stadi a valle sono lineari.

    /usr/bin/python3 sfumatura.py           # tutte le corse
"""
import csv
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from comune import (A_PIENO, ION, IRIP, QUI, REPO, SERIE_V4, cella_jfet, cella_ldr, corri,
                    guardia, testa)

sys.path.insert(0, os.path.join(REPO, "scripts"))
import v2_metodo as V2  # noqa: E402

T_INS = 0.3
CORSE = [
    # (nome, cella, args, TD)
    ("jfet_TIP_TIP_k030_td1", "jfet", ("TIP", "TIP", "k030"), 1.0),
    ("jfet_TIP_TIP_k030_td6", "jfet", ("TIP", "TIP", "k030"), 6.0),
    ("jfet_VHI_VLO_k030_td6", "jfet", ("VHI", "VLO", "k030"), 6.0),
    ("jfet_VHI_VHI_k030_td6", "jfet", ("VHI", "VHI", "k030"), 6.0),
    ("ldr_B_B_td1", "ldr", ("B", "B"), 1.0),
    ("ldr_B_B_td6", "ldr", ("B", "B"), 6.0),
    ("ldr_D_D_td6", "ldr", ("D", "D"), 6.0),
    ("ldr_E_E_td6", "ldr", ("E", "E"), 6.0),
    ("ldr_A_A_td6", "ldr", ("A", "A"), 6.0),
    ("ldr_C_C_td6", "ldr", ("C", "C"), 6.0),
]
# Per la domanda sul tempo massimo del mute: dove la NSL-32SR3 smette di passare fra 1 e 6 s.
CORSE_TEMPO = [
    ("ldr_B_B_td2", "ldr", ("B", "B"), 2.0),
    ("ldr_B_B_td3", "ldr", ("B", "B"), 3.0),
    ("ldr_D_D_td2", "ldr", ("D", "D"), 2.0),
    ("ldr_D_D_td3", "ldr", ("D", "D"), 3.0),
    # dopo la scelta dell'utente («proviamo target a 3s»): il bersaglio su tutto l'inviluppo A-E
    ("ldr_A_A_td3", "ldr", ("A", "A"), 3.0),
    ("ldr_C_C_td3", "ldr", ("C", "C"), 3.0),
    ("ldr_E_E_td3", "ldr", ("E", "E"), 3.0),
]
# NC-049: lo stesso bersaglio di 3 s con la cima del LED a 12 mA (ADR-050), tutte le curve
CORSE_CIMA12 = [("ldr_%s_%s_td3_cima12" % (c, c), "ldr", (c, c), 3.0) for c in "ABCDE"]
if "--cima12" in sys.argv:
    CORSE = CORSE_CIMA12
elif "--tre" in sys.argv:
    CORSE_TEMPO = CORSE_TEMPO[-3:]
    sys.argv.append("--tempo")
if "--tempo" in sys.argv:
    CORSE = CORSE_TEMPO


def tempi(td):
    t_rel = T_INS + td + 1.0
    return t_rel, t_rel + td + 0.5


def deck(nome, cella, args, td):
    t_rel, t_fine = tempi(td)
    dep = ("BDEP DEP 0 V = time < %g ? min(max((time - %g)/%g, 0), 1)"
           " : min(max(1 - (time - %g)/%g, 0), 1)" % (t_rel, T_INS, td, t_rel, td))
    r = testa("sfumatura %s" % nome)
    if cella == "jfet":
        c = cella_jfet(*args)
        c = [x for x in c if not x.startswith(("VCS ", "VCP "))]
        c += ["* i comandi dalla profondita' (comune.comandi, ordine serie_prima)",
              "BCS CS 0 V = -15 * min(max(V(DEP)/0.5, 0), 1)",
              "BCP CP 0 V = -15 * (1 - min(max((V(DEP) - 0.5)/0.5, 0), 1))"]
        salva = "v(ain)"
    else:
        c = cella_ldr(*args)
        c = [x for x in c if not x.startswith(("ILS ", "ILP "))]
        c += ["* il profilo v4 (ADR-040), come genera_tb_v2_casopeggiore.py",
              "BILS 0 ALS I = pow(10, pwl(V(DEP), %s))" % ", ".join(
                  "%g,%.4f" % (d, __import__("math").log10(i)) for d, i in SERIE_V4),
              "BILP 0 ALP I = %g * pow(%g, min(max((V(DEP) - 0.5)/0.5, 0), 1))" % (IRIP, ION / IRIP)]
        salva = "v(ain) v(xls.xs) v(xlp.xs)"
    r += c + [dep, ".control", "option itl1=1000", "set numdgt=15",
              "* il pieno di partenza: lo stato in gioco (d = 0) e' l'op",
              "tran 10u %g 0 10u" % t_fine,
              "wrdata %s.dat %s" % (nome, salva), ".endc", ".end"]
    return r


def analizza(nome, td):
    t_rel, t_fine = tempi(td)
    cols, tend = V2.leggi_wrdata(os.path.join(QUI, "run", "sfumatura", nome + ".dat"), 2e-6, t_fine)
    x = cols[0]
    _, ap = V2.ampiezza(x, 1000.0, 0.05, T_INS - 0.02)
    a_pieno = sorted(ap)[int(0.95 * (len(ap) - 1))]
    out = {"corsa": nome, "td_s": td, "a_pieno_V": a_pieno, "t_fine_letto": tend}
    for nm, te in (("S_ins", T_INS), ("S_rel", t_rel)):
        ii, aa = V2.ampiezza(x, 1000.0, te - 0.020, min(te + td + 0.200, t_fine))
        vs, js = V2.salto_db(ii, aa, a_pieno)
        out[nm + "_dB"] = vs
        out[nm + "_t"] = None if js is None else js / V2.FS
    # il livello a fine inserzione e appena prima del rilascio: la profondita' raggiunta
    ii, aa = V2.ampiezza(x, 1000.0, t_rel - 0.15, t_rel - 0.05)
    out["liv_mute_dB"] = 20 * __import__("math").log10(max(max(aa), 1e-30) / a_pieno)
    return out


def main():
    cartella = os.path.join(QUI, "run", "sfumatura")
    os.makedirs(cartella, exist_ok=True)
    for nome, cella, args, td in CORSE:
        open(os.path.join(cartella, nome + ".cir"), "w").write("\n".join(deck(nome, cella, args, td)) + "\n")
    with ThreadPoolExecutor(5) as ex:
        esiti = list(ex.map(lambda c: (c, corri(os.path.join(cartella, c[0] + ".cir"), 7200)), CORSE))
    righe, ok = [], True
    for (nome, cella, args, td), (rc, log) in esiti:
        cattive = guardia(log)
        if rc != 0 or cattive:
            print("RIFIUTATA %s rc=%d %s" % (nome, rc, cattive[:3]))
            ok = False
            continue
        r = analizza(nome, td)
        righe.append(r)
        print("%-24s S ins %5.1f dB  S rel %5.1f dB  mute %6.1f dB  (pieno %.4f V)" % (
            nome, r["S_ins_dB"], r["S_rel_dB"], r["liv_mute_dB"], r["a_pieno_V"]))
    if righe:
        out = ("sfumatura_cima12.csv" if "--cima12" in sys.argv else
               "sfumatura_tre.csv" if "--tre" in sys.argv else
               "sfumatura_tempo.csv" if "--tempo" in sys.argv else "sfumatura.csv")
        with open(os.path.join(QUI, "tabelle", out), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(righe[0]))
            w.writeheader()
            for r in righe:
                w.writerow({k: ("%.6g" % v if isinstance(v, float) else v) for k, v in r.items()})
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
