#!/usr/bin/env python3
"""Dopo L57b (copia di L57b): la protezione dell'ingresso come la genera il sorgente, per i banchi di L57a.

Dopo L57b il subckt chiama il diodo DI_BAV199 (il modello di Diodes Incorporated, models/diodes/
bav199.lib); i modelli alternativi sono scritti con quel nome:
  dio="di"      models/diodes/bav199.lib, il modello del costruttore (il default)
  dio="fit"     la stima di L57b (bav199_fit.lib) rinominata: deve ridare le cifre di L57b
  dio="1n4148"  il modello del 1N4148 rinominato: il caso noto di L57a
  dio="di2c"    il modello del costruttore con la capacita' raddoppiata (CJO 4,00 pF)
(le voci dio= qui sotto sono quelle di L57b)

righe(rif, dio) restituisce le righe SPICE della protezione fra il contatto del selettore (NK) e
l'ingresso del blocco (AIN), PRESE dal subckt generato spice/preamp/input_limiter.subckt
(circuits/preamp/input_limiter.py, ADR-101): il corpo di INLIM con SELCOM -> NK, e il corpo di
INREF (i due LM4040 coi loro 10 k dai rail e i 100 n), messi al livello del deck perche' il banco
legga le correnti dei diodi come @d179a[id] / @d179b[id]. Nessuna riga e' scritta a mano:
  rif=None      i riferimenti del sorgente col modello di TI (LM4040_NB5P0): non trova il punto di
                lavoro dietro i 10 k (limitations #76)
  rif="eq"      i riferimenti del sorgente come INREF_EQ (generato): le stesse R / C, ogni LM4040
                come la sua cifra di datasheet, 4,992 V dietro 1,1 ohm. Il circuito dei banchi
  rif=<V>       al posto di INREF due sorgenti ideali a +/-V (il caso noto di L57a: 5 V)
  dio="fit"     il BAV199 di models/diodes/bav199_fit.lib (la stima dichiarata dal datasheet)
  dio="1n4148"  il BAV199 col modello del 1N4148 (D1N914 rinominato): il caso noto di L57a
  dio="fit2c"   il BAV199 con la capacita' raddoppiata (CJO 3,7 pF): la sensibilita' del costo

prova() confronta il subckt con preamp_audio.net parte per parte (valore e reti di ogni piedino, le
reti del canale sinistro e della scheda): esce se differiscono.
"""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
L57B = os.path.dirname(QUI)
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
SUB = os.path.join(REPO, "spice", "preamp", "input_limiter.subckt")
NET = os.path.join(REPO, "circuits", "preamp", "preamp_audio.net")
MOD = os.path.join(L57B, "modelli")


def corpo(nome):
    testo = open(SUB).read()
    m = re.search(r"^\.subckt %s ([^\n]*)\n(.*?)^\.ends %s" % (nome, nome), testo, re.M | re.S)
    assert m, nome
    porte = m.group(1).split()
    righe = [r for r in m.group(2).split("\n") if r.strip() and not r.startswith("*")]
    return porte, righe


def _modelli():
    """I modelli alternativi col nome DI_BAV199, scritti dai file di models/ (mai a mano)."""
    os.makedirs(MOD, exist_ok=True)
    d914 = open(os.path.join(REPO, "models", "diodes", "1n4148.lib")).read()
    assert d914.count(".MODEL D1N914 D") == 1
    open(os.path.join(MOD, "bav199_come_1n4148.lib"), "w").write(
        "* dopo L57b: il modello del 1N4148 (models/diodes/1n4148.lib) col nome DI_BAV199: il caso noto di L57a\n"
        + d914.replace(".MODEL D1N914 D", ".MODEL DI_BAV199 D"))
    fit = open(os.path.join(REPO, "models", "diodes", "bav199_fit.lib")).read()
    assert fit.count(".MODEL BAV199 D") == 1
    open(os.path.join(MOD, "bav199_fit_come_di.lib"), "w").write(
        "* dopo L57b: la stima di L57b (models/diodes/bav199_fit.lib) col nome DI_BAV199\n"
        + fit.replace(".MODEL BAV199 D", ".MODEL DI_BAV199 D"))
    di = open(os.path.join(REPO, "models", "diodes", "bav199.lib")).read()
    # il PARAMETRO, nella riga del modello (non un commento: L57b ci era cascato una volta)
    pat = r"^(\+\s*CJO=)2\.00p(\s+M=0\.333)"
    n = len(re.findall(pat, di, re.M))
    assert n == 1, n
    open(os.path.join(MOD, "bav199_di_2c.lib"), "w").write(
        "* dopo L57b: bav199.lib (Diodes Inc.) con CJO raddoppiata (4,00 pF): la sensibilita' del costo\n"
        + re.sub(pat, r"\g<1>4.00p\g<2>", di, flags=re.M))


def include(rif, dio):
    _modelli()
    rel = lambda f: "@REPO@/" + os.path.relpath(os.path.join(MOD, f), REPO)  # noqa: E731
    s = {"di": "@REPO@/models/diodes/bav199.lib",
         "fit": rel("bav199_fit_come_di.lib"),
         "1n4148": rel("bav199_come_1n4148.lib"),
         "di2c": rel("bav199_di_2c.lib")}[dio]
    inc = ".include %s\n" % s
    if rif is None:
        inc += ".include @REPO@/models/voltage_reference/lm4040_5v0_ngspice.lib\n"
    return inc


def righe(rif=None, dio="di"):
    porte, lim = corpo("INLIM")
    assert porte == ["SELCOM", "AIN", "VLIM_P", "VLIM_M"], porte
    out = ["* la protezione dell'ingresso, dal subckt generato (L57b, limitatore.py: rif=%s dio=%s)"
           % (rif, dio)]
    for r in lim:
        out.append(" ".join("NK" if t == "SELCOM" else t for t in r.split()))
    if rif is None or rif == "eq":
        porte, ref = corpo("INREF" if rif is None else "INREF_EQ")
        assert porte == ["VLIM_P", "VLIM_M", "VPLUS", "VMINUS"], porte
        out += ref
        # dove partire (il modello di TI, da solo, ha un punto di lavoro difficile): solo un nodeset
        out.append(".nodeset v(VLIM_P)=4.992 v(VLIM_M)=-4.992")
    else:
        out += ["VCLP VLIM_P 0 DC %s" % rif, "VCLN VLIM_M 0 DC -%s" % rif]
    out.append(".save all @d179a[id] @d179b[id]")
    return "\n".join(out) + "\n"


def prova():
    """Il subckt contro la netlist: ogni dispositivo, il valore e la rete di ogni piedino."""
    net = open(NET).read()
    comp = {m.group(1): m.group(2) for m in
            re.finditer(r'\(comp\s*\(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', net)}
    pin = {}
    for blk in re.split(r"\(net\s*\(code", net.split("(nets", 1)[1])[1:]:
        nome = re.search(r'\(name "([^"]*)"\)', blk).group(1)
        for m in re.finditer(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk):
            pin[(m.group(1), m.group(2))] = nome
    mappa = {"L_SELCOM": "SELCOM", "AL_IN": "AIN", "GND": "0"}
    piedini = {"R": ["1", "2"], "C": ["1", "2"], "X": ["1", "2"]}
    viste = 0
    for nome in ("INLIM", "INREF"):
        for r in corpo(nome)[1]:
            t = r.split()
            dev = t[0]
            if dev[0] == "D":
                ref, pp = dev[:-1], {"A": ["1", "3"], "B": ["3", "2"]}[dev[-1]]
                val = t[3]
            elif dev[0] == "X":
                ref, pp, val = dev[1:], piedini["X"], t[3]
            else:
                ref, pp, val = dev, piedini[dev[0]], t[3]
            reti = [mappa.get(pin[(ref, p)], pin[(ref, p)]) for p in pp]
            assert reti == t[1:3], (dev, reti, t[1:3])
            v = comp[ref]
            ok = {"D": {"BAV199": "DI_BAV199"}.get(v) == val, "X": v.replace("LM4040B-5.0", "LM4040_NB5P0") == val,
                  "R": v == val, "C": v == val}[dev[0]]
            assert ok, (dev, v, val)
            viste += 1
    return viste


if __name__ == "__main__":
    _modelli()
    print("prova contro preamp_audio.net: %d dispositivi uguali" % prova())
    print(righe())
