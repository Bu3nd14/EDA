#!/usr/bin/env python3
"""L46b, ESPLORAZIONE - nessun valore del sorgente cambia.

Copiato da L46a/script/varianti.py (stesso meccanismo, dizionario nuovo). La base
e' spice/preamp/gain_block_flat.inc com'e' su main dopo L46a: il blocco di ADR-054
(VAS ~10,7 mA, C124 470p). La variante `ctrl` non cambia niente e deve ridare
`vas56_cm470p` di L46a.

Scrive in ../inc/<variante>.inc una copia del blocco con le modifiche:
  ("set", "R123", "R123 NVPF NVE 56")  sostituisce la riga del dispositivo
  ("del", "R130")                      toglie la riga
  ("add", "RF1 VPLUS NVPF 10")         aggiunge una riga in coda
I nomi nuovi non collidono con quelli del blocco ne' dei deck (#24): RF*, CF*,
RCF*, QF*, nodi NVPF, NCFE, NVPB, NVPBE (controllato con grep su spice/).

Il meccanismo (gain_block.py): sul rail + stanno gli emettitori dello specchio
d'ingresso (R119, R120, 220 Ohm), del VAS (R123, 56 Ohm), il riferimento del
cascode (R114, 4,99k, gia' filtrato a ~1 Hz da C 47u), il collettore del MJE15032
(Q132) e il disaccoppiamento (C139, C141). La base del VAS segue il rail, e il
Miller C124 lo porta in uscita: per questo il PSRR+ dipende dal Miller (L46a).
Le varianti alimentano specchio e/o VAS da un nodo filtrato NVPF.

Il condensatore della cella porta la sua ESR in serie (RCF1): **0,05 Ohm**,
ipotesi dichiarata, non letta da un datasheet: ~2-3 volte l'impedenza a 100 kHz
di un elettrolitico low-ESR da 1000-2200 uF 25 V a 20 C, per coprire il freddo e
l'invecchiamento. `esr02` la porta a 0,2 Ohm (un elettrolitico generico). In
banda audio, sopra pochi kHz, la reattanza di 1000 uF (16 mOhm a 10 kHz) e' gia'
sotto l'ESR: l'attenuazione della cella tende a R / ESR.

La prima riga di ogni .inc dice da dove viene e cosa cambia (#29).

Uso: /usr/bin/python3 varianti.py [variante...]   (nessun argomento: tutte)
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L46A = os.path.dirname(QUI)       # la cartella del lotto (nome tenuto da L46a)
ROOT = os.path.abspath(os.path.join(L46A, *[".."] * 5))
# la base congelata: gain_block_flat.inc di main prima di L46b (c9078f65, ADR-054). Il
# sorgente ora contiene la cella di ADR-056: le varianti non devono partire da li'.
SRC = os.path.join(L46A, "base", "gain_block_flat_adr054.inc")

SPECCHIO = [("set", "R119", "R119 NVPF NME1 220"),
            ("set", "R120", "R120 NVPF NME2 220")]
VAS = [("set", "R123", "R123 NVPF NVE 56")]
CASCODE = [("set", "R114", "R114 NVPF NCASC 4.99k")]


def cella(r, c, esr="0.05"):
    """La cella RC: RF1 dal rail al nodo filtrato, CF1 + la sua ESR a massa."""
    return [("add", "RF1 VPLUS NVPF %s" % r),
            ("add", "CF1 NVPF NCFE %s" % c),
            ("add", "RCF1 NCFE 0 %s" % esr)]


def moltiplicatore(r, c, esr="0.05"):
    """Moltiplicatore di capacita': RC sulla base di un MJE15032 (lo stesso
    dispositivo d'uscita, gia' in distinta), emettitore su NVPF. Caduta ~0,7 V +
    la caduta di RF2 per la corrente di base. RF2 a 1k: con h_FE ~50 e ~15 mA,
    ~0,3 mA di base, ~0,3 V."""
    return [("add", "QF1 VPLUS NVPB NVPF Qmje15032"),
            ("add", "RF2 VPLUS NVPB %s" % r),
            ("add", "CF2 NVPB NVPBE %s" % c),
            ("add", "RCF2 NVPBE 0 %s" % esr),
            ("add", "CF1 NVPF NCFE 100u"),
            ("add", "RCF1 NCFE 0 0.1")]


VARIANTI = {"ctrl": []}

# specchio + VAS dalla cella: R x C
for r in ("4.7", "10", "22"):
    for c in ("1000u", "2200u"):
        VARIANTI["sv_r%s_c%s" % (r.replace(".", "p"), c)] = SPECCHIO + VAS + cella(r, c)
VARIANTI["sv_r10_c1000u_esr02"] = SPECCHIO + VAS + cella("10", "1000u", "0.2")
# la scelta dell'utente (ADR-056) com'e' nel sorgente, condensatore ideale: deve ridare
# la regressione rigenerata da gain_block.py (la seconda strada)
VARIANTI["sv_r10_c1000u_esr0"] = SPECCHIO + VAS + cella("10", "1000u", "1u")
# dopo la scelta: il guasto di U502 e il corto della linea a 12 V crescono col condensatore
# (l41c/): celle piu' piccole, con un'ESR piu' alta (dichiarata, sfavorevole)
# Il guasto di U502 e il corto della linea a 12 V NON dipendono dalla cella (R 4,7 / 10,
# C 220-1000: stesse cifre; il blocco di ADR-054 senza cella anche): li ha peggiorati
# ADR-054. Meccanismo: col jack collegato il guadagno cade +10 -> 0 dB e al jack arriva il
# salto della continua d'uscita del blocco (-26 mV x 3,15 -> -26 mV). La continua viene
# dalla corrente di base del VAS (83 uA, beta ~129) che entra in NHI e sbilancia la coppia.
# Rimedio: R120 (degenerazione del lato d'uscita dello specchio) piu' grande, Q121B da
# ~83 uA in meno: 220 / 0,962 = ~229 Ohm. Sopra la cella scelta, condensatore ideale.
for r120 in ("226", "232", "237"):
    VARIANTI["sv_r10_esr0_r120_%s" % r120] = (
        [("set", "R119", "R119 NVPF NME1 220"), ("set", "R120", "R120 NVPF NME2 %s" % r120)]
        + VAS + cella("10", "1000u", "1u"))
# il blocco di ADR-056 (cella + R120 226) con l'ESR prudente: la fonte della tabella per
# tono di ADR-020 in REQUIREMENTS.md
VARIANTI["adr056_esr005"] = (
    [("set", "R119", "R119 NVPF NME1 220"), ("set", "R120", "R120 NVPF NME2 226")]
    + VAS + cella("10", "1000u", "0.05"))
VARIANTI["sv_r10_c470u"] = SPECCHIO + VAS + cella("10", "470u", "0.1")
VARIANTI["sv_r10_c220u"] = SPECCHIO + VAS + cella("10", "220u", "0.2")
# per separare i contributi
VARIANTI["s_r47_c470u"] = SPECCHIO + cella("47", "470u")
VARIANTI["v_r10_c1000u"] = VAS + cella("10", "1000u")
# anche il riferimento del cascode
VARIANTI["svc_r10_c1000u"] = SPECCHIO + VAS + CASCODE + cella("10", "1000u")
# moltiplicatore di capacita' (se le celle non bastano)
VARIANTI["sv_molt_r1k_c100u"] = SPECCHIO + VAS + moltiplicatore("1k", "100u")


def applica(nome, mods):
    righe = open(SRC).read().rstrip("\n").split("\n")
    for op, *arg in mods:
        if op == "add":
            righe.append(arg[0])
            continue
        dev = arg[0]
        idx = [i for i, r in enumerate(righe) if r.split()[:1] == [dev]]
        if len(idx) != 1:
            sys.exit("%s: %s %s trovato %d volte" % (nome, op, dev, len(idx)))
        if op == "set":
            righe[idx[0]] = arg[1]
        else:
            del righe[idx[0]]
    desc = "; ".join("%s %s" % (op, " | ".join(a)) for op, *a in mods) or "nessuna modifica"
    testa = ["* L46b ESPLORAZIONE, variante %s, da base/gain_block_flat_adr054.inc: %s"
             % (nome, desc)]
    d = os.path.join(L46A, "inc")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, nome + ".inc")
    open(p, "w").write("\n".join(testa + righe) + "\n")
    return p


nomi = sys.argv[1:] or sorted(VARIANTI)
for n in nomi:
    print(applica(n, VARIANTI[n]))
