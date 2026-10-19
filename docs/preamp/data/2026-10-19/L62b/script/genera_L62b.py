#!/usr/bin/env python3
"""L62b (NC-062, ADR-090): copiato da L62a/script/genera_L62a.py. Il blocco del SORGENTE, coi quattro
diodi D154-D157 fra NX e NY, sul banco di L62a: una sola variante, `base`, che e' il blocco generato
(il controllo byte per byte contro spice/preamp/ resta); i modi delle parti nuove sono quelli dei
diodi del sorgente (PROPRIE), non piu' righe aggiunte. Il resto uguale. Da confrontare con la
variante `diodi` di L62a (D160-D163): confronta_L62a.py.

L62a (NC-062): i quattro guasti del moltiplicatore di Vbe sul blocco di oggi, e i rimedi sul banco.
Solo stdlib, /usr/bin/python3 -I. Il circuito NON cambia: i rimedi sono varianti testuali del
gain_block.subckt e del gain_block_flat.inc generati, scritte in varianti/<v>/ (come
L60d1/script/varianti_follower.py).

Uso:
  genera_L62b.py      scrive varianti/, inc/<v>/, deck/<v>_<pos>/<modo>.cir, deck/lista.txt,
                      deck/lista_tb.txt, modi.csv

IL BANCO e' il canale di L45a (genera_canale.py, importato come gc: C_IN, trim, C_T, volume, le
tre uscite con la geometria iii, il guasto a 0,3 s, 2,3 s di corsa, le potenze medie degli ultimi
10 ms in <modo>_fine.csv). Ma (limitations #62) la copia guasta che il deck include NON e' quella
di L45a/inc/: si riscrive qui dal subckt della variante, con la stessa subckt_guasto() (gc.SUBCKT
puntato alla variante), in inc/<v>/, e si rifiuta se non contiene R150..R153 (il blocco di oggi) e
le parti nuove della variante. Anche i blocchi sani del canale includono il subckt della variante.

LE VARIANTI (le parti nuove con sigle 160+, che nel blocco non esistono)
  base     il blocco di oggi
  guardia  un secondo moltiplicatore di Vbe in parallelo a NX-NY, tarato sopra il nominale
           (Self 1995, «the lowest voltage wins»): Q160 MMBT5551, R161 2,7k collettore-base,
           R162 1k base-emettitore. Spento a blocco sano (8 uA a 27 C, 27 a 60, prototipo)
  diodi    quattro 1N4148 in serie in parallelo a NX-NY (Elliott, Project 03, «fail-safe»)
  limite   un limitatore per finale sulla 22 ohm: Q160 (NPN) toglie base a Q132 quando
           22 * I * 1k / 2,2k supera la sua Vbe (~72 mA), Q163 (PNP) lo stesso per Q133

I MODI: i quattro di NC-062 (Q127_ae, Q127_be, R129_cc, R128_ap) e quelli delle parti nuove, nelle
posizioni A, F1, F2, B e B a +10 dB; piu' il riferimento sano (rif); e il controllo CTRL_OUT_VP
(sulla base, posizione B), che deve superare 0,87 V al jack.

I DECK A BLOCCO SANO di ogni variante (lista_tb.txt): tb_op, tb_loop, tb_loop_blockA,
tb_loop_bufferfissa, tb_idss_loop (V1) e tb_mute_corto (P7, con le misure di Q146/Q148 di
L60d1/script/p7_l56.py), con gli include del blocco rediretti alla variante.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L62A = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L62A, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-13", "L45a", "script"))
sys.path.insert(0, os.path.join(DATA, "2026-10-18", "L60d1", "script"))
import genera_canale as gc   # noqa: E402
import p7_l56                # noqa: E402

ROOT = gc.ROOT
SP = os.path.join(ROOT, "spice", "preamp")
REL = os.path.relpath(L62A, ROOT)
NC062 = ("Q127_ae", "Q127_be", "R129_cc", "R128_ap")
OGGI = ("R150", "R151", "R152", "R153")
POSIZIONI = (("A", 0), ("F1", 0), ("F2", 0), ("B", 0), ("B", 10))
VARIANTI = {"base": []}
# L62b: i quattro diodi di ADR-090 sono nel sorgente; i loro modi si generano come parti nuove
PROPRIE = {"base": ["D154", "D155", "D156", "D157"]}
TB = ("tb_op", "tb_loop", "tb_loop_blockA", "tb_loop_bufferfissa", "tb_idss_loop", "tb_mute_corto")
INC_L45A = "@REPO@/%s/inc/" % gc.REL
SANO = "@REPO@/spice/preamp/gain_block.subckt"
PIATTO = "@REPO@/spice/preamp/gain_block_flat.inc"


def scrivi(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(t)
    return p


def subckt_variante(v):
    t = open(os.path.join(SP, "gain_block.subckt")).read()
    if not VARIANTI[v]:
        return t
    a = "\n.ends GAINBLOCK"
    if t.count(a) != 1:
        sys.exit("RIFIUTATO: .ends GAINBLOCK trovato %d volte" % t.count(a))
    extra = "\n* L62a, variante %s (NC-062): parti aggiunte\n%s" % (v, "\n".join(VARIANTI[v]))
    return t.replace(a, extra + a)


def piatto_variante(v):
    t = open(os.path.join(SP, "gain_block_flat.inc")).read()
    if not VARIANTI[v]:
        return t
    return t.rstrip("\n") + "\n* L62a, variante %s (NC-062): parti aggiunte\n%s\n" % (v, "\n".join(VARIANTI[v]))


def nuove(v):
    return [r.split()[0] for r in VARIANTI[v]] + PROPRIE.get(v, [])


def modi_variante(v):
    """I modi della variante: NC-062 e quelli delle parti nuove (da gc.modi() sul suo subckt)."""
    tutti = {m: (nome, tipo, a, b) for m, nome, tipo, a, b in gc.modi()}
    for m in NC062:
        if m not in tutti:
            sys.exit("RIFIUTATO: %s non e' un modo del subckt di %s" % (m, v))
    propri = [m for m, (nome, _, _, _) in tutti.items() if nome in nuove(v)]
    if len(propri) < 2 * len(nuove(v)):
        sys.exit("RIFIUTATO: %s ha %d modi per %d parti nuove" % (v, len(propri), len(nuove(v))))
    return list(NC062) + sorted(propri), tutti


def copia_guasta(v, modo):
    t = gc.subckt_guasto(modo)
    righe = {r.split()[0] for r in t.splitlines() if r.split()}
    manca = (set(OGGI) | set(nuove(v))) - righe
    if manca:
        sys.exit("RIFIUTATO: la copia %s/%s non ha %s" % (v, modo, sorted(manca)))
    scrivi(os.path.join(L62A, "inc", v, modo + ".subckt"), t)


def deck_guasto(v, pos, gain, modo):
    t = gc.deck_tr(pos, gain, modo, False, False)
    if modo != "rif":
        if t.count(INC_L45A) != 1:
            sys.exit("RIFIUTATO: %s/%s include %d copie guaste" % (v, modo, t.count(INC_L45A)))
        copia_guasta(v, modo)
        t = t.replace(INC_L45A, "@REPO@/%s/inc/%s/" % (REL, v))
    if t.count(SANO) != 1:
        sys.exit("RIFIUTATO: %s/%s include il blocco sano %d volte" % (v, modo, t.count(SANO)))
    t = t.replace(SANO, "@REPO@/%s/varianti/%s/gain_block.subckt" % (REL, v))
    if INC_L45A in t or "L45a/inc" in t:
        sys.exit("RIFIUTATO: %s/%s include ancora L45a/inc" % (v, modo))
    return "L62b %s " % v + t


def includi(t, v):
    n = 0
    for vecchio, f in ((SANO, "gain_block.subckt"), (PIATTO, "gain_block_flat.inc")):
        n += t.count(vecchio)
        t = t.replace(vecchio, "@REPO@/%s/varianti/%s/%s" % (REL, v, f))
    if n < 1:
        sys.exit("RIFIUTATO: nessun include del blocco")
    return t


def main():
    lista, lista_tb = [], []
    with open(os.path.join(L62A, "modi.csv"), "w", newline="") as fm:
        w = csv.writer(fm)
        w.writerow(["variante", "modo", "parte", "tipo", "terminali"])
        for v in VARIANTI:
            d = os.path.join(L62A, "varianti", v)
            scrivi(os.path.join(d, "gain_block.subckt"), subckt_variante(v))
            scrivi(os.path.join(d, "gain_block_flat.inc"), piatto_variante(v))
            gc.SUBCKT = os.path.join(d, "gain_block.subckt")
            modi, tutti = modi_variante(v)
            for m in modi:
                nome, tipo, a, b = tutti[m]
                w.writerow([v, m, nome, tipo, "%s-%s" % (a, b) if b is not None else str(a)])
            for pos, gain in POSIZIONI:
                cart = "%s_%s%s" % (v, pos, "_g10" if gain else "")
                casi = ["rif"] + modi + (["CTRL_OUT_VP"] if v == "base" and pos == "B" and not gain else [])
                for m in casi:
                    lista.append(scrivi(os.path.join(L62A, "deck", cart, m + ".cir"),
                                        deck_guasto(v, pos, gain, m)))
            for k in TB:
                t = includi(open(os.path.join(SP, "tb", k + ".cir")).read(), v)
                if k == "tb_mute_corto":
                    t = p7_l56.aggiungi(t, r153=True)
                lista_tb.append(scrivi(os.path.join(L62A, "deck", "tb_" + v, k + ".cir"), t))
    gc.SUBCKT = os.path.join(SP, "gain_block.subckt")
    # il controllo: la variante base deve essere il blocco di oggi, byte per byte
    for f in ("gain_block.subckt", "gain_block_flat.inc"):
        if open(os.path.join(L62A, "varianti", "base", f)).read() != open(os.path.join(SP, f)).read():
            sys.exit("RIFIUTATO: varianti/base/%s non e' il blocco di oggi" % f)
    scrivi(os.path.join(L62A, "deck", "lista.txt"), "\n".join(lista) + "\n")
    scrivi(os.path.join(L62A, "deck", "lista_tb.txt"), "\n".join(lista_tb) + "\n")
    print("L62b: %d deck di guasto, %d deck a blocco sano" % (len(lista), len(lista_tb)))


if __name__ == "__main__":
    main()
