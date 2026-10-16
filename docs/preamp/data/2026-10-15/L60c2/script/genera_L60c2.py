#!/usr/bin/env python3
"""L60c2: le prove sulla fissa 2 col circuito nuovo - il condensatore da 1 uF prima di K3 (ADR-081,
ADR-084) e K3 un TE Axicom IM06TS (ADR-085). Solo stdlib, /usr/bin/python3 -I.

Uso:
  genera_L60c2.py        scrive deck/<gruppo>/<caso>.cir e deck/lista.txt

IL BANCO e' quello di L60c1, importato e non copiato: la geometria G0 di L60c1 (47 -> 1 uF -> COM,
NO al jack, NC a massa, bleed 470k sui due lati, carico 50k della Stax) E' il circuito di L60c2.
Prima di scrivere un deck il generatore lo verifica sulla netlist (circuits/preamp/preamp_audio.net):
il condensatore della fissa 2 (C165 / C365) a 1u, i bleed a 470k, la 47 ohm, K3 un IM06 e la
geometria iii di ADR-044 (check_relay_safe_state.check, lo stesso controllo del 2e). Se il circuito
cambia, il banco rifiuta invece di provare la cosa sbagliata.

I GRUPPI
  g0       i casi G0 di L60c1, rifatti: il blocco A / F2 al rail (C nominale e +5 %), il pin di un
           rail aperto, V2 A senza segnale (inserimento e rilascio, VOSF2 0 / +-20 mV), il caldo,
           E9 (C nominale e -5 %). Devono ridare i numeri di L60c1. Fuori: l'isolamento di K3 (le
           corse I_K3), che ADR-085 toglie da P10 col rele' a isolamento supplementare.
  e9       E9 col condensatore a +5 % (L60c1 non l'aveva), per avere la banda intera.
  guasti   P10: OGNI guasto del blocco di L45a, sulle posizioni A e F2, che a vuoto portava la Stax
           sopra 0,87 V (p10_blocco.csv di L45b, colonna fix2_sopra_ms > 0: 107 modi), ora col
           condensatore da 1 uF e il carico della Stax, C nominale e +5 %. Le impostazioni di
           ciascun modo sono quelle della sua corsa buona in L45b (gear, accorciata).
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L60C2 = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L60C2, "..", ".."))
ROOT = os.path.abspath(os.path.join(DATA, "..", "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-15", "L60c1", "script"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import genera_L60c1 as g1                # noqa: E402
import check_relay_safe_state as crs     # noqa: E402
from pathlib import Path                 # noqa: E402

gc = g1.gc
T_FINE = g1.T_FINE
P10_L45B = os.path.join(DATA, "2026-10-13", "L45b", "p10_blocco.csv")


def verifica_netlist():
    """Il banco G0 e' il circuito: si legge dalla netlist, non si suppone."""
    comps, pin_net = crs.parse_netlist(Path(ROOT, "circuits", "preamp", "preamp_audio.net"))
    findings, relays, _ = crs.check(comps, pin_net)
    if findings:
        sys.exit("RIFIUTATO: la netlist non passa il 2e:\n  " + "\n  ".join(findings))
    k3 = comps["K3"]
    if (k3["part"], crs.role_of(k3["value"])) != ("IM06", "MUTE"):
        sys.exit("RIFIUTATO: K3 non e' l'IM06 di mute (ADR-085): %s" % k3)
    attesi = {"C165": "1u", "C365": "1u", "R164": "47", "R364": "47",
              "R166": "470k", "R366": "470k", "R168": "470k", "R368": "470k"}
    for ref, v in attesi.items():
        if comps[ref]["value"] != v:
            sys.exit("RIFIUTATO: %s = %s nella netlist, il banco G0 ha %s" % (ref, comps[ref]["value"], v))
    # la geometria: la 47 ohm sul condensatore, il condensatore sul COM di K3, i bleed ai loro nodi
    for ch, (c, r47, rbl, rbc, com, no) in {"L": ("C165", "R164", "R166", "R168", "3", "4"),
                                            "R": ("C365", "R364", "R366", "R368", "6", "5")}.items():
        lato_c = pin_net[("K3", com)]
        jack = pin_net[("K3", no)]
        if lato_c not in (pin_net[(c, "1")], pin_net[(c, "2")]):
            sys.exit("RIFIUTATO: %s non sta sul COM di K3 (%s)" % (c, lato_c))
        if {pin_net[(r47, "1")], pin_net[(r47, "2")]} & {pin_net[(c, "1")], pin_net[(c, "2")]} == set():
            sys.exit("RIFIUTATO: %s non tocca %s" % (r47, c))
        if {pin_net[(rbc, "1")], pin_net[(rbc, "2")]} != {lato_c, "GND"}:
            sys.exit("RIFIUTATO: %s non e' il bleed lato C" % rbc)
        if {pin_net[(rbl, "1")], pin_net[(rbl, "2")]} != {jack, "GND"}:
            sys.exit("RIFIUTATO: %s non e' il bleed del jack" % rbl)
    return "netlist: K3 %s, C165/C365 1u, R164/R364 47, bleed 470k sui due lati, geometria iii" % k3["value"]


def modi_guasti():
    """(pos, modo, gear, tfine) per ogni guasto di A / F2 che a vuoto portava la Stax sopra 0,87 V.
    Di un modo corso in piu' varianti si prende la corsa buona: la normale, poi gear, poi corta."""
    righe = [r for r in csv.DictReader(open(P10_L45B))
             if r["posizione"] in ("A", "F2") and float(r["fix2_sopra_ms"] or 0) > 0]

    def pref(r):
        v = r["variante"]
        return (r["stato"] != "ok", "gear" in v, "corta" in v)
    scelti = {}
    for r in sorted(righe, key=pref):
        scelti.setdefault((r["posizione"], r["modo"]), r)
    out = []
    for (pos, modo), r in sorted(scelti.items()):
        out.append((pos, modo, "gear" in r["variante"], 0.6 if "corta" in r["variante"] else T_FINE))
    return out


def casi():
    c = []
    for gruppo, nome, testo in g1.casi():
        if nome.startswith("G0_") and "_I_K3_" not in nome:
            c.append(("g0", nome, testo))
    nome, t = g1.deck_e9("G0", 1.05)
    c.append(("e9", nome, t))
    for pos, modo, gear, tfine in modi_guasti():
        for k in (1.0, 1.05):
            sk = "" if k == 1.0 else "_k105"
            t = gc.deck_tr(pos, 0, modo, False, False, tfine=tfine, gear=gear)
            c.append(("guasti", "G0_%s_%s%s" % (pos, modo, sk), g1.applica(t, "G0", k)))
    return c


def main():
    print(verifica_netlist())
    lista = []
    for gruppo, nome, testo in casi():
        testo = g1.rinomina(testo, nome)
        p = os.path.join(L60C2, "deck", gruppo, nome + ".cir")
        if testo.startswith("L60c1 "):
            testo = "L60c2" + testo[len("L60c1"):]
            gc.scrivi(p, testo)
        else:
            gc.scrivi(p, "L60c2 %s %s - " % (gruppo, nome) + testo)
        lista.append(p)
    gc.scrivi(os.path.join(L60C2, "deck", "lista.txt"), "\n".join(lista) + "\n")
    print("L60c2: %d deck (%d modi di guasto)" % (len(lista), len(modi_guasti())))


if __name__ == "__main__":
    main()
