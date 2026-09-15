#!/usr/bin/env python3
"""genera.py - le copie sabotate di spice/preamp/tb/tb_e4_uscite.cir (L13).

Uso: /usr/bin/python3 genera.py <repo-root>

Scrive accanto a se' c<lettera>.cir. Ogni sabotaggio e' una sostituzione di
testo esatta: se il testo da sostituire non compare esattamente il numero di
volte atteso, rifiuta (exit 1) e non scrive niente, cosi' un sabotaggio non
diventa in silenzio una copia identica del deck.

  a  VSRC lasciata accesa durante l'iniezione (il difetto di
     tb_zout_psrr_noise.cir fino a L13)
  b  sonda del MAIN sul nodo sbagliato: BOUT, prima dei 47 ohm, invece del jack
  c0 attenuatore scollegato dal blocco B: il gate vede 2,5 k fissi a massa.
     PRIMA FORMA DI c, tenuta perche' non ha dato l'esito atteso: il segnale
     al jack e' zero esatto, vdb(0) da' "Error" e il guadagno esce vuoto, quindi
     cade la completezza (A) e il controllo positivo (C) non viene esercitato
  c  la manopola che non cambia niente: il gate del blocco B sull'uscita del
     trim, l'attenuatore appeso a un nodo che nessuno legge. Il segnale arriva,
     ma non dipende dalla posizione: deve cadere C
  d  iniezione e sonda sul cursore dell'attenuatore: il passivo di ADR-002
  e  iniezione in FIXJACK2, lettura su FIXJACK1
  f  RG10 del blocco B non terminato (#27): deve cadere il 2g
  g  un modo che non cambia niente: il contatto di K1 resta aperto a +3 e +10 dB
"""
import os
import sys

DECK = "spice/preamp/tb/tb_e4_uscite.cir"

SABOTAGGI = {
    "a": [("      alter @vsrc[acmag] = 0\n", "      alter @vsrc[acmag] = 1\n", 1)],
    "b": [("let ZR = real(v(mainjack))", "let ZR = real(v(bout))", 1),
          ("let ZM = mag(v(mainjack))", "let ZM = mag(v(bout))", 1)],
    "c0": [("RATTH ATOP BIN 1m", "RATTH ATOP BINOFF 1m", 1),
           ("RATTL BIN 0 10k", "RATTL BINOFF 0 10k\nRSAB BIN 0 2.5k", 1)],
    "c": [("RATTH ATOP BIN 1m", "RATTH ATOP BINOFF 1m", 1),
          ("RATTL BIN 0 10k", "RATTL BINOFF 0 10k\nRSAB ATOP BIN 1m", 1)],
    "d": [("IMAIN  0 MAINJACK DC 0 AC 0", "IMAIN  0 BIN DC 0 AC 0", 1),
          ("let ZR = real(v(mainjack))", "let ZR = real(v(bin))", 1),
          ("let ZM = mag(v(mainjack))", "let ZM = mag(v(bin))", 1)],
    "e": [("let ZR = real(v(fixjack2))", "let ZR = real(v(fixjack1))", 1),
          ("let ZM = mag(v(fixjack2))", "let ZM = mag(v(fixjack1))", 1)],
    "f": [("CSTB10 BRG10 0 15p\n", "", 1),
          ("RRG10B BRG10 0 1G\n", "", 1)],
    "g": [("        alter rrgb = 0.1\n", "        alter rrgb = 1G\n", 2)],
}


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    src = open(os.path.join(sys.argv[1], DECK)).read()
    out = {}
    for k, subs in SABOTAGGI.items():
        txt = src
        for old, new, n in subs:
            c = txt.count(old)
            if c != n:
                print(f"RIFIUTATO {k}: {old!r} compare {c} volte, attese {n}")
                return 1
            txt = txt.replace(old, new)
        if txt == src:
            print(f"RIFIUTATO {k}: copia identica al deck")
            return 1
        out[k] = txt.replace(
            "tb_e4_uscite.cir - L13:",
            f"tb_e4_uscite.cir SABOTATO ({k}) - L13:", 1)
    here = os.path.dirname(os.path.abspath(__file__))
    for k, txt in out.items():
        p = os.path.join(here, f"c{k}.cir")
        open(p, "w").write(txt)
        print(f"scritto {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
