#!/usr/bin/env python3
"""L45d2b3b1: il calore e il jack di OGNI modo del blocco di oggi, nelle cinque posizioni del canale.
Solo stdlib, /usr/bin/python3 -I.

Uso:
  genera_calore.py              scrive varianti/, inc/<v>/, deck/<v>_<pos>/<modo>.cir,
                                deck/lista_calore.txt (oggi), deck/lista_controllo.txt (l62b), modi.csv

IL BANCO e' quello di L62b (genera_L62b.py, importato come g62, e attraverso lui il canale di L45a:
rail ideali a +-15 V, le tre uscite con la geometria iii, il guasto a 0,3 s, 2,3 s di corsa, le
potenze medie degli ultimi 10 ms). Qui cambiano tre cose:
  - i modi: TUTTI quelli del blocco di oggi (gc.modi()), con le stesse esclusioni di L45a
    (RAIL_A_MASSA, e le parti che in una posizione non ci sono, SOLO), non solo quelli di NC-062;
  - le copie guaste (limitations #62) si rifiutano se non hanno R150..R153 e D154..D159 (ADR-090,
    ADR-095): sono il blocco di oggi;
  - la potenza dei diodi (D154..D159, D102, D103): `@d...[p]` media degli ultimi 10 ms in
    <modo>_fine.csv. Il canale di L45a misura solo Q e R; D158 / D159 portano il limite di corrente
    di ADR-095 e possono scaldare.

LE VARIANTI
  oggi   spice/preamp/gain_block.subckt, uguale byte per byte (controllato)
  l62b   il blocco di L62b (L62b/varianti/base/gain_block.subckt, prima di ADR-095): IL CASO NOTO.
         Coi modi e le posizioni di L62b deve ridare calore.csv di L62b (confronta_l62b.py).
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-19", "L62b", "script"))
import genera_L62b as g62   # noqa: E402

gc = g62.gc
L62B = os.path.join(DATA, "2026-10-19", "L62b")
SP = g62.SP
DIODI = ("D102", "D103", "D154", "D155", "D156", "D157", "D158", "D159")
OGGI = ("R150", "R151", "R152", "R153") + DIODI
SORGENTE = {"oggi": os.path.join(SP, "gain_block.subckt"),
            "l62b": os.path.join(L62B, "varianti", "base", "gain_block.subckt")}
PIATTO = {"oggi": os.path.join(SP, "gain_block_flat.inc"),
          "l62b": os.path.join(L62B, "varianti", "base", "gain_block_flat.inc")}
# il banco di L62b punta i suoi percorsi a questa cartella
g62.L62A = L
g62.REL = os.path.relpath(L, g62.ROOT)
g62.OGGI = ("R150", "R151", "R152", "R153")
g62.VARIANTI = {"oggi": [], "l62b": []}
g62.PROPRIE = {"oggi": list(DIODI[2:]), "l62b": ["D154", "D155", "D156", "D157"]}


def diodi_presenti():
    return [p[0] for p in gc.dispositivi() if p[0][0] == "D"]


def con_diodi(t, pos, modo):
    """Aggiunge al deck di L45a la potenza media dei diodi del blocco guasto in <modo>_fine.csv."""
    x = {"A": "xa", "F1": "xf1", "F2": "xf2", "B": "xb"}[pos]
    vett = ["@d.%s.%s[p]" % (x, d.lower()) for d in diodi_presenti()]
    righe = t.split("\n")
    i_save = [i for i, r in enumerate(righe) if r.startswith("save v(mainjack)")]
    i_quit = [i for i, r in enumerate(righe) if r == "quit"]
    i_tran = [i for i, r in enumerate(righe) if r.startswith("tran ")]
    if len(i_save) != 1 or len(i_quit) != 1 or len(i_tran) != 1:
        sys.exit("RIFIUTATO: %s/%s non ha una sola riga save / tran / quit" % (pos, modo))
    t_fine = float(righe[i_tran[0]].split()[2])
    da = t_fine - 10e-3
    righe[i_save[0]] += " " + " ".join(vett)
    agg = []
    for d, v in zip(diodi_presenti(), vett):
        n = "p_" + d.lower()
        agg.append("meas tran %s AVG %s from=%g to=%g" % (n, v, da, t_fine))
        agg.append("echo \"%s,$&%s\" >> %s_fine.csv" % (n, n, modo))
    righe[i_quit[0]:i_quit[0]] = agg
    return "\n".join(righe)


def modi_tutti():
    out = []
    for m, nome, tipo, a, b in gc.modi():
        if m in gc.RAIL_A_MASSA:
            continue
        out.append((m, nome))
    return out


def main():
    lista = {"oggi": [], "l62b": []}
    with open(os.path.join(L, "modi.csv"), "w", newline="") as fm:
        w = csv.writer(fm)
        w.writerow(["variante", "modo", "parte", "tipo", "terminali"])
        for v in ("oggi", "l62b"):
            d = os.path.join(L, "varianti", v)
            g62.scrivi(os.path.join(d, "gain_block.subckt"), open(SORGENTE[v]).read())
            g62.scrivi(os.path.join(d, "gain_block_flat.inc"), open(PIATTO[v]).read())
            gc.SUBCKT = os.path.join(d, "gain_block.subckt")
            tutti = {m: (nome, tipo, a, b) for m, nome, tipo, a, b in gc.modi()}
            if v == "oggi":
                modi = [m for m, _ in modi_tutti()]
                posizioni = g62.POSIZIONI
            else:
                modi, _ = g62.modi_variante(v)
                posizioni = (("A", 0),)
            for m in modi:
                nome, tipo, a, b = tutti[m]
                w.writerow([v, m, nome, tipo, "%s-%s" % (a, b) if b is not None else str(a)])
            for pos, gain in posizioni:
                cart = "%s_%s%s" % (v, pos, "_g10" if gain else "")
                casi = ["rif"] + [m for m in modi
                                  if not (tutti[m][0] in gc.SOLO and pos not in gc.SOLO[tutti[m][0]])]
                if pos == "B" and not gain:
                    casi.append("CTRL_OUT_VP")
                for m in casi:
                    t = g62.deck_guasto(v, pos, gain, m)
                    if m != "rif" and m != "CTRL_OUT_VP":
                        copia = open(os.path.join(L, "inc", v, m + ".subckt")).read()
                        righe = {r.split()[0] for r in copia.splitlines() if r.split()}
                        manca = set(OGGI if v == "oggi" else g62.OGGI) - righe
                        if manca:
                            sys.exit("RIFIUTATO: la copia %s/%s non ha %s" % (v, m, sorted(manca)))
                    if v == "oggi":
                        t = con_diodi(t, pos, m)
                    lista[v].append(g62.scrivi(os.path.join(L, "deck", cart, m + ".cir"), t))
    gc.SUBCKT = os.path.join(SP, "gain_block.subckt")
    for f in ("gain_block.subckt", "gain_block_flat.inc"):
        if open(os.path.join(L, "varianti", "oggi", f)).read() != open(os.path.join(SP, f)).read():
            sys.exit("RIFIUTATO: varianti/oggi/%s non e' il blocco di oggi" % f)
    if "D158" in open(os.path.join(L, "varianti", "l62b", "gain_block.subckt")).read():
        sys.exit("RIFIUTATO: la variante l62b ha D158: non e' il blocco di L62b")
    g62.scrivi(os.path.join(L, "deck", "lista_calore.txt"), "\n".join(lista["oggi"]) + "\n")
    g62.scrivi(os.path.join(L, "deck", "lista_controllo.txt"), "\n".join(lista["l62b"]) + "\n")
    print("calore: %d deck (oggi, %d modi), controllo: %d deck (l62b)"
          % (len(lista["oggi"]), len(modi_tutti()), len(lista["l62b"])))


if __name__ == "__main__":
    main()
