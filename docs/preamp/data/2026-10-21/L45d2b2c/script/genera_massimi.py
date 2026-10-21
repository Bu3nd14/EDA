#!/usr/bin/env python3
"""L45d2b2c (ADR-078, punto 1): il blocco di guadagno col rail alto. Solo stdlib, /usr/bin/python3 -I.

Uso: genera_massimi.py   scrive varianti/base/, inc/base/, deck/<rail>_B/<modo>.cir,
                         deck/tb_<rail>/tb_mute_corto.cir, deck/lista.txt, deck/lista_tb.txt

IL BANCO e' quello di L62b (genera_L62b.py, importato come g62, che importa il canale di L45a): il
blocco del sorgente coi quattro diodi di ADR-090, le copie guaste rifatte dal blocco di oggi
(limitations #62), il guasto a 0,3 s, 2,3 s di corsa, le potenze medie degli ultimi 10 ms in
<modo>_fine.csv. Le cartelle di g62 (L62A, REL) sono spostate qui: niente si scrive in L62b/.

I RAIL. Nel canale di L45a e nel deck di P7 sono due sorgenti ideali, `VPP VPLUS 0 DC 15` e
`VMM VMINUS 0 DC -15`; qui si sostituiscono (ognuna deve comparire una volta sola):
  nom  +15 / -15        il banco di L62b (il controllo: le potenze uguali a L62b, calore.csv)
  p    +20,3 / -15      il rail + alto: U501 ingresso-uscita in corto, 20,05 V a rete +10 %
                        (rail_alto.csv), arrotondato per eccesso al 20,3 di ADR-078 / L45c1
  m    +15 / -20,3      il rail - alto: U502 ingresso-uscita in corto, -19,97 V
  pm   +20,3 / -20,3    tutti e due: NON e' un guasto singolo, e' il limite superiore dichiarato
Il ripple (al piu' 86 mV picco-picco, rail_alto.csv) sta dentro i 0,25 V d'arrotondamento.

I MODI, nella posizione B (la principale): il riferimento sano (rif) e i quattro di NC-062
(Q127_ae, Q127_be, R129_cc, R128_ap: i diodi di ADR-090 portano la corrente del VAS). Col rail
alto, rif e' il guasto singolo; i quattro di NC-062 sono un DOPPIO guasto (il rail e il
moltiplicatore), letto per informazione e dichiarato come tale.

LE TENSIONI. Per ogni parte del blocco in B, dalle righe di spice/preamp/gain_block.subckt: per
ogni coppia di terminali (Q: c-e, c-b, e-b; J: d-s, g-s, g-d; D: a-k; C e R: i due nodi) il
massimo e il minimo su TUTTA la corsa (da 0, il punto di lavoro, al guasto e dopo), in
<modo>_tensioni.csv. I nodi del blocco sono v(xb.<nodo>); le porte (IN, OUT, ..., VPLUS, VMINUS)
si leggono sui nodi esterni della riga XB del deck.

P7 (tb_mute_corto, ogni caso di corto e di carico, con le misure di Q146 / Q148 / R153 di L60d1)
coi quattro rail, nelle cartelle tb_<rail>.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(LOTTO, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-19", "L62b", "script"))
import genera_L62b as g62   # noqa: E402

gc = g62.gc
ROOT = gc.ROOT
SP = os.path.join(ROOT, "spice", "preamp")
g62.L62A = LOTTO
g62.REL = os.path.relpath(LOTTO, ROOT)
RAIL = {"nom": (15.0, -15.0), "p": (20.3, -15.0), "m": (15.0, -20.3), "pm": (20.3, -20.3)}
# P7 only, at the three mains levels: the rail of the IN-OUT short (rail_alto.csv, vp_max / vm_min)
# rounded up to 0.1 V, the other rail at 15 V
RAIL_P7 = {"p_m10": (16.3, -15.0), "p_0": (18.2, -15.0), "p_p10": (20.1, -15.0),
           "m_m10": (15.0, -16.2), "m_0": (15.0, -18.1), "m_p10": (15.0, -20.0)}
MODI = ("rif",) + g62.NC062
POS = "B"
X = "xb"
VPP0, VMM0 = "VPP VPLUS 0 DC 15\n", "VMM VMINUS 0 DC -15\n"
COPPIE = {"Q": (("ce", 0, 2), ("cb", 0, 1), ("eb", 2, 1)),
          "J": (("ds", 0, 2), ("gs", 1, 2), ("gd", 1, 0)),
          "D": (("ak", 0, 1),), "C": (("12", 0, 1),), "R": (("12", 0, 1),)}


def rail(t, r):
    vp, vm = RAIL[r] if r in RAIL else RAIL_P7[r]
    if t.count(VPP0) != 1 or t.count(VMM0) != 1:
        sys.exit("RIFIUTATO: i rail del deck non sono una riga ciascuno (%d, %d)"
                 % (t.count(VPP0), t.count(VMM0)))
    return t.replace(VPP0, "VPP VPLUS 0 DC %g\n" % vp).replace(VMM0, "VMM VMINUS 0 DC %g\n" % vm)


def parti():
    """(nome, tipo, nodi) di ogni riga del blocco; le porte dalla riga .subckt."""
    porte, out = None, []
    for r in open(os.path.join(SP, "gain_block.subckt")):
        p = r.split()
        if not p or p[0].startswith("*"):
            continue
        if p[0] == ".subckt":
            porte = p[2:]
        elif p[0][0] in COPPIE:
            n = 4 if p[0][0] in "QJ" else 3
            out.append((p[0], p[0][0], p[1:n]))
    # 57 parts, 59 lines: the two halves of the LSK489 (JQ110A / B) and of the LS352 (Q121A / B)
    assert porte and len(out) == 59, (porte, len(out))
    return porte, out


def tensioni(t, modo):
    """Le misure delle tensioni ai terminali delle parti di XB, aggiunte al deck di g62."""
    porte, ps = parti()
    xb = [r for r in t.splitlines() if r.split() and r.split()[0] == "XB"]
    assert len(xb) == 1, xb
    est = xb[0].split()[1:1 + len(porte)]
    mappa = dict(zip(porte, est))

    def nodo(n):
        e = mappa.get(n.upper(), None) if n.upper() in mappa else None
        if e is not None:
            return None if e == "0" else "v(%s)" % e.lower()
        return None if n == "0" else "v(%s.%s)" % (X, n.lower())

    salva, lets, nomi = set(), [], []
    for nome, tipo, nodi in ps:
        for suf, a, b in COPPIE[tipo]:
            va, vb = nodo(nodi[a]), nodo(nodi[b])
            salva |= {v for v in (va, vb) if v}
            espr = "%s - %s" % (va or "0", vb or "0")
            k = "t_%s_%s" % (nome.lower(), suf)
            lets.append("let %s = %s" % (k, espr))
            nomi.append(k)
    a = "save v(mainjack)"
    if t.count(a) != 1:
        sys.exit("RIFIUTATO: la riga save del deck non c'e' una volta sola")
    t = t.replace(a, "save %s v(mainjack)" % " ".join(sorted(salva)))
    m = "\n".join(lets) + "\n"
    for k in nomi:
        m += "meas tran %s_max MAX %s\nmeas tran %s_min MIN %s\n" % (k, k, k, k)
    m += "echo \"grandezza,valore\" > %s_tensioni.csv\n" % modo
    for k in nomi:
        m += "echo \"%s_max,$&%s_max\" >> %s_tensioni.csv\n" % (k, k, modo)
        m += "echo \"%s_min,$&%s_min\" >> %s_tensioni.csv\n" % (k, k, modo)
    q = "quit\n.endc"
    if t.count(q) != 1:
        sys.exit("RIFIUTATO: la fine del .control non c'e' una volta sola")
    return t.replace(q, m + q)


# The remedy of the finals' reverse base-emitter (the user, 2026-10-21: «Rimedio in questo lotto»):
# a 1N4148 across each final's base-emitter, conducting only in reverse - D158 from NEN to NBN
# (Q132, NPN), D159 from NBP to NEP (Q133, PNP). A VARIANT of the generated block (L62a's method),
# genera_massimi.py cbe: P7 at every rail, in deck/tb_cbe_<rail>/.
CBE = ["D158 NEN NBN D1N914", "D159 NBP NEP D1N914"]


def vbe_p7(t, diodi=False):
    """P7: the finals' base-emitter junctions in REVERSE, in every block and every case - the base of
    the finals' off side rises above its emitter by ~22 ohm x I - (the bias spread) with the other
    side carrying the short's current; the MJE15032 / 15033 allow 5 V (limiti_blocco.csv). The
    maximum over the run of v(nen) - v(nbn) (Q132, NPN) and v(nbp) - v(nep) (Q133, PNP), in
    tb_mute_corto_vbe.csv, one row per cell and block; the same anchors as p7_l56.aggiungi."""
    blk = ("a", "f1", "f2", "b")
    save = "\n".join("save v(x%s.nbn) v(x%s.nen) v(x%s.nbp) v(x%s.nep)" % ((b,) * 4) for b in blk)
    testa = 'echo "blk,modo_db,f_hz,vin_pk,k_att,caso,veb_q132_max,vbe_q133_max%s" > tb_mute_corto_vbe.csv' % (
        ",id_d158_max,id_d159_max,p_d158,p_d159" if diodi else "")
    if diodi:
        save += "\n" + "\n".join("save @d.x%s.d158[id] @d.x%s.d159[id]" % (b, b) for b in blk)
    mis = []
    for b in blk:
        mis += ["  let l2c132 = v(x%s.nen) - v(x%s.nbn)" % (b, b),
                "  let l2c133 = v(x%s.nbp) - v(x%s.nep)" % (b, b),
                "  meas tran l2c132x MAX l2c132",
                "  meas tran l2c133x MAX l2c133"]
        if diodi:
            mis += ["  let l2p158 = @d.x%s.d158[id] * l2c132" % b,
                    "  let l2p159 = @d.x%s.d159[id] * l2c133" % b,
                    "  meas tran l2i158 MAX @d.x%s.d158[id]" % b,
                    "  meas tran l2i159 MAX @d.x%s.d159[id]" % b,
                    "  meas tran l2p158a AVG l2p158",
                    "  meas tran l2p159a AVG l2p159"]
        mis.append('  echo "%s,$gm,$f,$a,$k,$c,$&l2c132x,$&l2c133x%s" >> tb_mute_corto_vbe.csv' % (
            b.upper(), ",$&l2i158,$&l2i159,$&l2p158a,$&l2p159a" if diodi else ""))
    ancora = "  * --- blocco A ---"
    a2 = "\nforeach sweep 1 2 3\n"
    if t.count(ancora) != 1 or t.count(a2) != 1:
        sys.exit("RIFIUTATO: gli ancoraggi di P7 non ci sono una volta sola")
    t = t.replace(ancora, "\n".join(mis) + "\n" + ancora)
    return t.replace(a2, "\n" + save + "\n" + testa + "\n" + a2.lstrip("\n"))


def main_cbe():
    """The variant with D158 / D159: P7 at every rail (RAIL and RAIL_P7), deck/tb_cbe_<rail>/."""
    g62.VARIANTI["cbe"] = CBE
    d = os.path.join(LOTTO, "varianti", "cbe")
    g62.scrivi(os.path.join(d, "gain_block.subckt"), g62.subckt_variante("cbe"))
    g62.scrivi(os.path.join(d, "gain_block_flat.inc"), g62.piatto_variante("cbe"))
    lista = []
    for r in list(RAIL) + list(RAIL_P7):
        t = g62.includi(open(os.path.join(SP, "tb", "tb_mute_corto.cir")).read(), "cbe")
        t = vbe_p7(g62.p7_l56.aggiungi(t, r153=True), diodi=True)
        lista.append(g62.scrivi(os.path.join(LOTTO, "deck", "tb_cbe_" + r, "tb_mute_corto.cir"),
                                "L45d2b2c cbe rail=%s %s" % (r, rail(t, r))))
    g62.scrivi(os.path.join(LOTTO, "deck", "lista_tb_cbe.txt"), "\n".join(lista) + "\n")
    print("L45d2b2c cbe: %d deck di P7" % len(lista))


def main():
    if sys.argv[1:] == ["cbe"]:
        return main_cbe()
    d = os.path.join(LOTTO, "varianti", "base")
    g62.scrivi(os.path.join(d, "gain_block.subckt"), g62.subckt_variante("base"))
    g62.scrivi(os.path.join(d, "gain_block_flat.inc"), g62.piatto_variante("base"))
    gc.SUBCKT = os.path.join(d, "gain_block.subckt")
    g62.modi_variante("base")
    lista, lista_tb = [], []
    for r in list(RAIL) + list(RAIL_P7):
        for m in (MODI if r in RAIL else ()):
            t = g62.deck_guasto("base", POS, 0, m)
            t = "L45d2b2c rail=%s %s" % (r, tensioni(rail(t, r), m))
            lista.append(g62.scrivi(os.path.join(LOTTO, "deck", "%s_%s" % (r, POS), m + ".cir"), t))
        t = g62.includi(open(os.path.join(SP, "tb", "tb_mute_corto.cir")).read(), "base")
        t = vbe_p7(g62.p7_l56.aggiungi(t, r153=True))
        lista_tb.append(g62.scrivi(os.path.join(LOTTO, "deck", "tb_" + r, "tb_mute_corto.cir"),
                                   "L45d2b2c rail=%s %s" % (r, rail(t, r))))
    gc.SUBCKT = os.path.join(SP, "gain_block.subckt")
    for f in ("gain_block.subckt", "gain_block_flat.inc"):
        if open(os.path.join(d, f)).read() != open(os.path.join(SP, f)).read():
            sys.exit("RIFIUTATO: varianti/base/%s non e' il blocco di oggi" % f)
    g62.scrivi(os.path.join(LOTTO, "deck", "lista.txt"), "\n".join(lista) + "\n")
    g62.scrivi(os.path.join(LOTTO, "deck", "lista_tb.txt"), "\n".join(lista_tb[:len(RAIL)]) + "\n")
    g62.scrivi(os.path.join(LOTTO, "deck", "lista_tb_reti.txt"), "\n".join(lista_tb[len(RAIL):]) + "\n")
    print("L45d2b2c: %d deck del blocco, %d deck di P7" % (len(lista), len(lista_tb)))


if __name__ == "__main__":
    main()
