#!/usr/bin/env python3
"""L45d2b3b2a (NC-042, ADR-097 punto 4): il calore dei quindici guasti del blocco. Solo stdlib,
/usr/bin/python3 -I. Il circuito NON cambia: i rimedi sono varianti testuali del blocco generato.

Uso:
  genera.py noto              il caso noto: la variante `oggi` (il blocco di oggi, byte per byte),
                              i 15 modi + rif nelle cinque posizioni -> deck/lista_noto.txt
  genera.py dopo              lo stato dopo la parte bruciata: copie DOPPIAMENTE guaste
                              -> deck/lista_dopo.txt
  genera.py dopo2             il secondo giro dello stato dopo (BRUCIA2) -> deck/lista_dopo2.txt
  genera.py rimedi [v ...]    le varianti dei rimedi (tutte, o quelle nominate), i 15 modi + rif
                              + i modi delle parti nuove -> deck/lista_rimedi.txt

IL BANCO e' quello del calore di L45d2b3b1 (genera_calore.py, importato come gk; e attraverso lui
L62b e il canale di L45a: rail ideali a +-15 V, le tre uscite con la geometria iii, il guasto a
0,3 s, 2,3 s di corsa, le potenze medie degli ultimi 10 ms, piu' la potenza dei diodi). I percorsi
di L62b (inc/, varianti/) puntano a QUESTA cartella. Le copie guaste si riscrivono dal subckt della
variante (limitations #62) e si rifiutano se non hanno R150..R153, R160 e le parti della variante.

LO STATO DOPO: la parte che il guasto porta oltre i limiti si rompe dopo. Non si sa come: si corrono
tutte e due le forme. «ap» = tutti i terminali aperti (la riga tolta, 1 Gohm a massa su ogni suo
nodo perche' nessuno resti appeso, limitations #27); «cc» = corto collettore-emettitore (1 mohm).
La rottura e' presente da t = 0 nella copia guasta, e il guasto di partenza entra a 0,3 s come
sempre: a fine corsa i due guasti ci sono tutti e due. I blocchi sani del canale restano quelli di oggi.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b1", "script"))
import genera_calore as gk   # noqa: E402

g62 = gk.g62
gc = gk.gc
g62.L62A = L
g62.REL = os.path.relpath(L, g62.ROOT)
SP = g62.SP
OGGI = ("R150", "R151", "R152", "R153", "R160")

# I quindici di ADR-097 punto 4 (righe_b1.csv, «FUORI (calore)»; C145 in corto e' NC-075)
QUINDICI = ("Q132_ce", "Q133_ce", "Q125_ce", "Q106_ce", "Q121A_be", "Q148_ce", "Q121A_ae",
            "R119_ap", "D102_ap", "D103_ap", "R101_cc", "R107_cc", "R126_cc", "R149_cc", "Q121B_be")

# Lo stato dopo: la parte che brucia (la piu' calda, sintesi_calore.csv di b1) -> i modi.
# Q121B_be e Q132_ce restano a 149 C, sotto i 150 C assoluti: non bruciano, e non sono qui.
# R101 in corto porta D102 / D103 a ~99 W ciascuno: il primo che si apre ferma la corrente. Il
# corto di tutti e due mette il rail - a massa (un guasto dell'alimentatore, RAIL_A_MASSA di L45a).
BRUCIA = {
    "Q148": ("R149_cc", "Q121A_be", "Q121A_ae", "R119_ap", "R107_cc", "Q106_ce", "D102_ap", "D103_ap"),
    "Q121": ("Q148_ce",),
    "Q122": ("Q133_ce", "Q125_ce"),
    "Q125": ("R126_cc",),
    "D102": ("R101_cc",),
}
PARTI = {"Q121": ("Q121A", "Q121B")}
FORME = {"D102": ("ap",)}
# il secondo giro, dopo aver letto il primo: (nome, parte gia' bruciata, sua forma, parte nuova, forme, modi)
BRUCIA2 = []


def scrivi(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(t)
    return p


def righe_oggi(f):
    return open(os.path.join(SP, f)).read()


def sostituisci(testo, cambi, aggiunte, tag):
    """cambi: {sigla: [righe nuove]} (la riga della sigla sostituita); aggiunte: righe in fondo al
    corpo. Vale per il subckt (prima di .ends) e per il piatto (in fondo)."""
    out, visti = [], set()
    for r in testo.splitlines():
        p = r.split()
        if p and p[0] in cambi:
            visti.add(p[0])
            out += cambi[p[0]]
        else:
            out.append(r)
    manca = set(cambi) - visti
    if manca:
        sys.exit("RIFIUTATO: %s non trova %s" % (tag, sorted(manca)))
    extra = ["* L45d2b3b2a, variante %s" % tag] + list(aggiunte)
    if any(r.startswith(".ends GAINBLOCK") for r in out):
        i = [k for k, r in enumerate(out) if r.startswith(".ends GAINBLOCK")]
        if len(i) != 1:
            sys.exit("RIFIUTATO: .ends GAINBLOCK %d volte" % len(i))
        out[i[0]:i[0]] = extra
    else:
        out += extra
    return "\n".join(out) + "\n"


# LE VARIANTI DEI RIMEDI: (cambi, aggiunte, parti nuove). Sigle nuove da 161 (il blocco arriva a R160).
RC148 = ({"Q148": ["Q148 NHC NMIRC NMIRI MMBT5401"]}, ["R161 NHC VMINUS 10k"], ["R161"])
SDOPP = ({"R101": ["R101 0 NREFH 3.40k"], "R107": ["R107 NTE NTEH 68.1"],
          "R126": ["R126 NVLE NVLEH 28.0"]},
         ["R162 NREFH NREF 3.40k", "R163 NTEH VMINUS 68.1", "R164 NVLEH VMINUS 28.0",
          "D165 NREF NREFM D1N914", "D166 NREFM VMINUS D1N914"],
         ["R162", "R163", "R164", "D165", "D166"])
VASLIM = ({"R123": ["R123 VPF NVS 33"]}, ["R167 NVS NVE 22", "Q168 NVB NVS VPF MMBT5401"],
          ["R167", "Q168"])


def unisci(*vv):
    c, a, n = {}, [], []
    for x in vv:
        c.update(x[0])
        a += x[1]
        n += x[2]
    return c, a, n


RIMEDI = {
    "rc148": RC148,
    "sdopp": SDOPP,
    "vaslim": VASLIM,
    "tutti": unisci(RC148, SDOPP, VASLIM),
}


B1 = os.path.join(DATA, "2026-10-22", "L45d2b3b1", "varianti", "oggi")


def richieste(v):
    """Le parti che ogni copia della variante deve avere: il blocco di b1 non ha R160 (ADR-097)."""
    return ("R150", "R151", "R152", "R153") if v == "b1" else OGGI


def prepara(v, cambi=None, aggiunte=(), nuove=()):
    d = os.path.join(L, "varianti", v)
    for f in ("gain_block.subckt", "gain_block_flat.inc"):
        t = open(os.path.join(B1, f)).read() if v == "b1" else righe_oggi(f)
        if cambi is not None:
            t = sostituisci(t, cambi, aggiunte, v)
        scrivi(os.path.join(d, f), t)
    gc.SUBCKT = os.path.join(d, "gain_block.subckt")
    g62.VARIANTI[v] = []
    g62.PROPRIE[v] = []
    corpo = {r.split()[0] for r in gc.righe_subckt() if r.split()}
    manca = (set(richieste(v)) | set(nuove)) - corpo
    if manca:
        sys.exit("RIFIUTATO: la variante %s non ha %s" % (v, sorted(manca)))


def un_deck(v, pos, gain, m, nuove=()):
    t = g62.deck_guasto(v, pos, gain, m)
    if m not in ("rif", "CTRL_OUT_VP"):
        copia = open(os.path.join(L, "inc", v, m + ".subckt")).read()
        righe = {r.split()[0] for r in copia.splitlines() if r.split()}
        manca = (set(richieste(v)) | set(nuove)) - righe
        if manca:
            sys.exit("RIFIUTATO: la copia %s/%s non ha %s" % (v, m, sorted(manca)))
    t = gk.con_diodi(t, pos, m)
    cart = "%s_%s%s" % (v, pos, "_g10" if gain else "")
    return scrivi(os.path.join(L, "deck", cart, m + ".cir"), t)


def esistono(modi):
    tutti = {m for m, _, _, _, _ in gc.modi()}
    for m in modi:
        if m not in tutti:
            sys.exit("RIFIUTATO: %s non e' un modo del blocco %s" % (m, gc.SUBCKT))


def posizioni_di(m):
    nome = m.rsplit("_", 1)[0]
    return [(p, g) for p, g in g62.POSIZIONI if not (nome in gc.SOLO and p not in gc.SOLO[nome])]


def noto():
    """b1: il blocco su cui b1 ha corso i quindici (prima di ADR-097), deve ridare calore_oggi.csv
    di b1 cella per cella. oggi: il blocco di oggi (R153 + R160), la base dei rimedi."""
    for v, sorgente, nome_lista in (("b1", B1, "lista_noto.txt"), ("oggi", SP, "lista_oggi.txt")):
        prepara(v)
        for f in ("gain_block.subckt", "gain_block_flat.inc"):
            if open(os.path.join(L, "varianti", v, f)).read() != open(os.path.join(sorgente, f)).read():
                sys.exit("RIFIUTATO: varianti/%s/%s non e' il blocco atteso" % (v, f))
        esistono(QUINDICI)
        lista = []
        for pos, gain in g62.POSIZIONI:
            for m in ("rif",) + QUINDICI:
                if m == "rif" or (pos, gain) in posizioni_di(m):
                    lista.append(un_deck(v, pos, gain, m))
        scrivi(os.path.join(L, "deck", nome_lista), "\n".join(lista) + "\n")
        print("%s: %d deck" % (v, len(lista)))
    if "R160" in open(os.path.join(L, "varianti", "b1", "gain_block.subckt")).read():
        sys.exit("RIFIUTATO: la variante b1 ha R160: non e' il blocco di b1")
    gc.SUBCKT = os.path.join(SP, "gain_block.subckt")


def brucia(testo, parti, forma):
    out, agg = [], []
    trovate = set()
    for r in testo.splitlines():
        p = r.split()
        if p and p[0] in parti:
            trovate.add(p[0])
            if forma == "ap":
                agg += ["RBRN_%s_%d %s 0 1G" % (p[0], k, n) for k, n in enumerate(p[1:-1]) if n != "0"]
                continue
            if p[0][0] == "Q":
                agg.append("RBRN_%s %s %s 1m" % (p[0], p[1], p[3]))
            elif p[0][0] == "D":
                agg.append("RBRN_%s %s %s 1m" % (p[0], p[1], p[2]))
            else:
                sys.exit("RIFIUTATO: forma %s per %s" % (forma, p[0]))
        out.append(r)
    if trovate != set(parti):
        sys.exit("RIFIUTATO: brucia non trova %s" % sorted(set(parti) - trovate))
    i = [k for k, r in enumerate(out) if r.startswith(".ends GAINBLOCKG")]
    if len(i) != 1:
        sys.exit("RIFIUTATO: .ends GAINBLOCKG %d volte" % len(i))
    out[i[0]:i[0]] = ["* L45d2b3b2a: %s bruciat%s (%s) da t = 0" % ("/".join(parti), "o", forma)] + agg
    return "\n".join(out) + "\n"


def giro(casi, nome_lista):
    lista = []
    for v, bruciate, modi in casi:
        prepara(v)
        esistono(modi)
        for pos, gain in g62.POSIZIONI:
            for m in modi:
                if (pos, gain) not in posizioni_di(m):
                    continue
                lista.append(un_deck(v, pos, gain, m))
                p = os.path.join(L, "inc", v, m + ".subckt")
                t = open(p).read()
                for parti, forma in bruciate:
                    t = brucia(t, parti, forma)
                scrivi(p, t)
    scrivi(os.path.join(L, "deck", nome_lista), "\n".join(lista) + "\n")
    print("%s: %d deck, %d casi" % (nome_lista, len(lista), len(casi)))


def dopo():
    casi = []
    for parte, modi in BRUCIA.items():
        for forma in FORME.get(parte, ("ap", "cc")):
            casi.append(("d_%s%s" % (parte, forma), [(PARTI.get(parte, (parte,)), forma)], list(modi)))
    giro(casi, "lista_dopo.txt")


def dopo2():
    casi = []
    for nome, p1, f1, p2, forme, modi in BRUCIA2:
        for forma in forme:
            casi.append(("d2_%s_%s%s" % (nome, p2, forma),
                         [(PARTI.get(p1, (p1,)), f1), (PARTI.get(p2, (p2,)), forma)], list(modi)))
    giro(casi, "lista_dopo2.txt")


def rimedi(scelte):
    lista = []
    for v in (scelte or list(RIMEDI)):
        cambi, aggiunte, nuove = RIMEDI[v]
        prepara(v, cambi, aggiunte, nuove)
        propri = [m for m, nome, _, _, _ in gc.modi() if nome in nuove and m not in gc.RAIL_A_MASSA]
        if len(propri) < 2 * len(nuove):
            sys.exit("RIFIUTATO: %s ha %d modi per %d parti nuove" % (v, len(propri), len(nuove)))
        modi = [m for m in QUINDICI if m.rsplit("_", 1)[0] in {r.split()[0] for r in gc.righe_subckt() if r.split()}]
        esistono(modi)
        for pos, gain in g62.POSIZIONI:
            for m in ["rif"] + modi + propri:
                if m == "rif" or (pos, gain) in posizioni_di(m):
                    lista.append(un_deck(v, pos, gain, m, nuove))
    gc.SUBCKT = os.path.join(SP, "gain_block.subckt")
    scrivi(os.path.join(L, "deck", "lista_rimedi.txt"), "\n".join(lista) + "\n")
    print("rimedi: %d deck" % len(lista))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "noto":
        noto()
    elif cmd == "dopo":
        dopo()
    elif cmd == "dopo2":
        dopo2()
    elif cmd == "rimedi":
        rimedi(sys.argv[2:])
    else:
        sys.exit(__doc__)
