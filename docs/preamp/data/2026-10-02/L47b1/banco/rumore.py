"""rumore.py - L47b1: E5 della cella in gioco, e il rumore del comando ammesso.

In gioco (d = 0), sorgente 1,5 ohm:
  - `noise v(ain) vsrc dec 50 20 20k`: il rumore totale su AIN, 20 Hz-20 kHz, e lo stesso banco
    senza cella (SRCX e AIN uniti da 1 uohm, nessun'altra parte): la differenza in quadratura e'
    il contributo della cella. Al jack principale x3,15 (+10 dB, caso peggiore);
  - il comando: |H| dal comando ad AIN (ac, per V di comando o per A di LED) sulla banda; la
    densita' bianca di rumore del comando che da' da sola 1 uV RMS al jack (la quota ausiliaria di
    ADR-022 punto 4, che il comando dovrebbe dividere con il resto del digitale).
Riferimento di E5: 9,90 uV RMS al circuito del segnale; il caso peggiore di oggi 5,531 uV
(tb_e3_e5_ldr, curva D, +10 dB, 430 ohm), con la LDR in serie come 118 ohm.

    /usr/bin/python3 rumore.py
"""
import math
import os
import sys

from comune import G_JACK, QUI, cella_jfet, cella_ldr, corri, guardia, testa, valori

CASI = [("jfet", ("TIP", "TIP", "k030")), ("jfet", ("TIP", "TIP", "k048")),
        ("jfet", ("VHI", "VHI", "k030")), ("jfet", ("TIP", "TIP", "nessuno")),
        ("ldr", ("B", "B")), ("ldr", ("D", "D")), ("ldr", ("E", "E")), ("nessuna", ())]


def deck(cella, args):
    r = testa("rumore %s %s" % (cella, args))
    if cella == "jfet":
        r += cella_jfet(*args)
        cmd = ["vcs", "vcp"]
    elif cella == "ldr":
        r += cella_ldr(*args)
        cmd = ["ils", "ilp"]
    else:
        r += ["RCORTO SRCX AIN 1u"]
        cmd = []
    r += [".control", "option itl1=1000", "set numdgt=10",
          "noise v(ain) vsrc dec 50 20 20k", "setplot noise2",
          "let vn = sqrt(onoise_total^2)", "print vn", "setplot noise1", "destroy all"]
    for c in cmd:
        r += ["alter vsrc ac = 0", "alter %s ac = 1" % c,
              "ac dec 50 20 20k", "let h2 = mag(v(ain))^2",
              "let hrms_%s = sqrt(mean(h2))" % c, "let hmax_%s = vecmax(mag(v(ain)))" % c,
              "print hrms_%s hmax_%s" % (c, c), "destroy all", "alter %s ac = 0" % c]
    return r + [".endc", ".end"], cmd


def main():
    cartella = os.path.join(QUI, "run", "rumore")
    os.makedirs(cartella, exist_ok=True)
    ris, ok = {}, True
    for cella, args in CASI:
        nome = "_".join([cella] + list(args))
        r, cmd = deck(cella, args)
        p = os.path.join(cartella, nome + ".cir")
        open(p, "w").write("\n".join(r) + "\n")
        rc, log = corri(p)
        cattive = guardia(log)
        nomi = {"vn"} | {"%s_%s" % (g, c) for g in ("hrms", "hmax") for c in cmd}
        v = valori(log, nomi)
        if rc != 0 or cattive or len(v) != len(nomi):
            print("RIFIUTATA %s rc=%d %s letti %d/%d" % (nome, rc, cattive[:3], len(v), len(nomi)))
            ok = False
            continue
        ris[nome] = (v, cmd)
    rif = ris["nessuna"][0]["vn"]
    print("Banco senza cella: %.4g uV RMS su AIN (la sorgente 1,5 ohm e R_IN)" % (rif * 1e6))
    for nome, (v, cmd) in ris.items():
        if nome == "nessuna":
            continue
        cella_uv = math.sqrt(max(v["vn"] ** 2 - rif ** 2, 0)) * 1e6
        al_jack = cella_uv * G_JACK
        e5 = math.sqrt(5.531 ** 2 + al_jack ** 2)
        riga = "%-20s cella %.3g uV su AIN, %.3g uV al jack; E5 caso peggiore %.3f -> %.3f uV (limite 9,90)" % (
            nome, cella_uv, al_jack, 5.531, e5)
        for c in cmd:
            # densita' bianca e del comando: e * hrms * sqrt(B) * G = 1 uV
            amm = 1e-6 / (v["hrms_" + c] * math.sqrt(20000 - 20) * G_JACK)
            unita = "V/rtHz" if c.startswith("v") else "A/rtHz"
            riga += " | %s: |H|max %.3g, ammesso %.3g %s" % (c, v["hmax_" + c], amm, unita)
        print(riga)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
