#!/usr/bin/env python3
"""L56 (NC-060), ESPLORAZIONE - nessun valore del sorgente cambia.

Da L46b/script/varianti.py (stesso meccanismo, dizionario nuovo). La base e'
spice/preamp/gain_block_flat.inc di main dopo L53 (96bacb07): il blocco di ADR-056, copiato in
base/gain_block_flat_adr056.inc. La variante `ctrl` non cambia niente e deve ridare L53.

Il meccanismo (L53, NC-060): lo specchio d'ingresso Q121B (LS350, RC 231 Ohm nel modello) ha ai
morsetti
    Vce(Q121B) = I*R123 + Vbe(Q122) - I*R120 - Vbe(Q121B)  ~  0,55 + 0,65 - 0,49 - 0,6
e ~0,5 V se li mangia RC: la giunzione base-collettore interna e' sull'orlo. Il calore abbassa
Vbe(Q122) (il VAS a 0,14 W) e alza la coda (Q106 piu' caldo dei suoi diodi): il gradino.

Le strade, una per famiglia:
  ef_*        un inseguitore di emettitore PNP (QE1, MMBT5401) fra lo specchio e la base del VAS:
              base su NHI, emettitore sulla base del VAS (nodo nuovo NVB), collettore a massa,
              RE1 da VPF a NVB (~1,2 V ai capi: 1,2k ~1 mA, 2,2k ~0,55 mA). Allo specchio una
              Vbe in piu' (~+0,65 V), e la corrente di base del VAS (~83 uA) non entra piu' in
              NHI: R120 226 (ADR-056) compensava proprio quella, quindi `_r220` la riporta a 220.
              Il Miller C124 resta da NX a NHI (attorno a inseguitore e VAS).
  re*         R123 (emettitore del VAS) 56 -> 82 / 100 Ohm: la corrente del VAS la fissa il suo
              carico (Q125), quindi la caduta cresce di 0,28 / 0,47 V e va allo specchio. Costa
              lo stesso al clip positivo, e il clip diventa asimmetrico.
  rm*         R119/R120 220/226 -> 150/154, 100/103 (stesso rapporto): ~+0,15 / +0,26 V allo
              specchio; la degenerazione e' quella che teneva basso il rumore (L22).
  diodo       un 1N4148 (DE1) in serie alla base del VAS, anodo sulla base: ~0,5 V alla corrente
              di base (~83 uA), nessuna polarizzazione aggiunta.
  coda_bassa  R107 137 -> 150 Ohm (coda ~4,1 mA): lontano dal gradino, meno gm.
Le strade termiche (diodi della coda accoppiati a Q106, un VAS che scalda meno) non cambiano il
circuito: sono opzioni di caldo.py su qualunque variante.

Nomi nuovi QE1, RE1, DE1, NVB: nessuna collisione con spice/ ne' coi deck (grep, L56).
La prima riga di ogni .inc dice da dove viene e cosa cambia (#29).

Uso: /usr/bin/python3 varianti.py [variante...]   (nessun argomento: tutte)
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
SRC = os.path.join(LOTTO, "base", "gain_block_flat_adr056.inc")

VAS_DA_NVB = [("set", "Q122", "Q122 NX NVB NVE MMBT5401")]


def ef(re1):
    return VAS_DA_NVB + [("add", "QE1 0 NHI NVB MMBT5401"), ("add", "RE1 VPF NVB %s" % re1)]


R120_220 = [("set", "R120", "R120 VPF NME2 220")]

VARIANTI = {
    "ctrl": [],
    "ef_1k2": ef("1.2k"),
    "ef_2k2": ef("2.2k"),
    "ef_1k2_r220": ef("1.2k") + R120_220,
    "ef_2k2_r220": ef("2.2k") + R120_220,
    "re82": [("set", "R123", "R123 VPF NVE 82")],
    "re100": [("set", "R123", "R123 VPF NVE 100")],
    "rm150": [("set", "R119", "R119 VPF NME1 150"), ("set", "R120", "R120 VPF NME2 154")],
    "rm100": [("set", "R119", "R119 VPF NME1 100"), ("set", "R120", "R120 VPF NME2 103")],
    "diodo": VAS_DA_NVB + [("add", "DE1 NVB NHI D1N914")],
    "coda_bassa": [("set", "R107", "R107 NTE VMINUS 150")],
}
# prove.py: con l'inseguitore il gradino sparisce ma resta un secondo ordine (CCIF -105 dB a +10
# dB) che viene ancora da RC dell'LS350 (con RC a zero -134,5) e non dall'Early (VAF 1000: uguale).
# Ipotesi: la giunzione base-collettore interna a soli -0,18 V e' nella zona piu' non lineare della
# sua capacita'. Piu' polarizzazione inversa: inseguitore + R123 piu' grande, due diodi, R123 150.
VARIANTI["ef_re82"] = ef("1.2k") + R120_220 + [("set", "R123", "R123 VPF NVE 82")]
VARIANTI["ef_re100"] = ef("1.2k") + R120_220 + [("set", "R123", "R123 VPF NVE 100")]
VARIANTI["diodo2"] = VAS_DA_NVB + [("add", "DE1 NVB NVD D1N914"), ("add", "DE2 NVD NHI D1N914")]
VARIANTI["re150"] = [("set", "R123", "R123 VPF NVE 150")]
# Falsificata: con piu' polarizzazione inversa su Q121B il secondo ordine e' identico. La causa
# e' l'ALTRO lato: Q121A ha collettore e base uniti ai morsetti, e RC gli tiene la giunzione
# base-collettore interna diretta di Ic*RC ~ 0,5 V, sempre. Nel controllo i due lati erano tutti e
# due vicini alla saturazione e si compensavano; alzando solo Q121B la simmetria si rompe.
# Il transistor di aiuto (beta helper): QH1 PNP, base sul collettore di Q121A (nodo nuovo NMIRC,
# dove arriva anche il cascode Q118), emettitore sulle basi dello specchio (NMIRI), collettore a
# massa; RH1 da VPF a NMIRI lo polarizza (~1,1 V ai capi: 10k ~110 uA). Il collettore di Q121A
# scende di una Vbe sotto le basi; con l'inseguitore anche NHI e' una Vbe piu' giu': le due meta'
# dello specchio, e i due cascode, alla stessa tensione.
AIUTO = [("set", "Q121A", "Q121A NMIRC NMIRI NME1 LS350"),
         ("set", "Q118", "Q118 NMIRC NCASC D2N MMBT5551"),
         ("add", "QH1 0 NMIRC NMIRI MMBT5401")]


def aiuto(rh1="10k"):
    return AIUTO + [("add", "RH1 VPF NMIRI %s" % rh1)]


VARIANTI["aiuto"] = aiuto()
VARIANTI["ef_aiuto"] = ef("1.2k") + R120_220 + aiuto()
VARIANTI["ef_aiuto_r226"] = ef("1.2k") + aiuto()
VARIANTI["ef_aiuto_rh4k7"] = ef("1.2k") + R120_220 + aiuto("4.7k")
VARIANTI["ef_aiuto_rh22k"] = ef("1.2k") + R120_220 + aiuto("22k")
# Dopo la scelta dell'utente (ef_aiuto): i collettori di QE1 e QH1 al rail negativo invece che a
# massa, perche' la corrente di base del VAS (segnale) non passi nel ritorno di massa.
def al_rail_negativo(mods):
    out = []
    for m in mods:
        if m[0] == "add" and m[1].startswith(("QE1 0 ", "QH1 0 ")):
            m = ("add", m[1].replace(" 0 ", " VMINUS ", 1))
        out.append(m)
    return out


VARIANTI["ef_aiuto_vm"] = al_rail_negativo(VARIANTI["ef_aiuto"])
# il secondo ordine dell'inseguitore contro il bilanciamento dello specchio (prove.py): R120
for _r in ("205", "212", "232", "240"):
    VARIANTI["ef_1k2_r120_%s" % _r] = ef("1.2k") + [("set", "R120", "R120 VPF NME2 %s" % _r)]


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
    testa = ["* L56 ESPLORAZIONE, variante %s, da base/gain_block_flat_adr056.inc: %s"
             % (nome, desc)]
    d = os.path.join(LOTTO, "inc")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, nome + ".inc")
    open(p, "w").write("\n".join(testa + righe) + "\n")
    return p


if __name__ == "__main__":
    for n in sys.argv[1:] or sorted(VARIANTI):
        print(applica(n, VARIANTI[n]))
