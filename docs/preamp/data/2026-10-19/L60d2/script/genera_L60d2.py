#!/usr/bin/env python3
"""L60d2: i guasti sulla Stax rifatti col blocco a ridondanza (ADR-086: R150 4,7 kOhm in parallelo a
R109, R112 / R151 due da 200 Ohm, R144 / R152 due da 20 Ohm; ADR-087: R153 4,7 kOhm sul collettore
dell'inseguitore). Solo stdlib, /usr/bin/python3 -I.

Uso:
  genera_L60d2.py        scrive deck/<gruppo>/<caso>.cir e deck/lista.txt

IL BANCO e' quello di L60c2, importato e non copiato: verifica_netlist() (il condensatore della
Stax a 1 uF prima di K3, K3 un IM06, la geometria iii), la geometria G0 di L60c1, i deck di
guasto di L45a (genera_canale: i modi si leggono da gain_block.subckt di oggi, quindi quelli delle
parti nuove esistono per nome). MA la copia guasta che il deck include (inc/<modo>.subckt) e'
riscritta qui dal blocco di oggi: quella di L45a/inc/ e' il blocco senza ridondanza (vedi INC_L45A).

I GRUPPI
  g0       i riferimenti di L60c2 (il blocco al rail, il pin di un rail aperto, V2 A, il caldo,
           E9): il controllo CTRL_OUT_VP deve ancora superare il tetto.
  guasti   P10 sulla Stax: i 107 modi di L60c2 (modi_guasti(): ogni guasto di A / F2 che a vuoto
           portava la Stax sopra 0,87 V in L45b, con le impostazioni della sua corsa buona) piu'
           i modi delle parti di ADR-086 e ADR-087, aperta e corto: R150, R151, R152, R153 e
           R112 / R144 col valore nuovo, se non gia' fra i 107. Posizioni A e F2, condensatore
           nominale e +5 %.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L60D2 = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L60D2, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-15", "L60c2", "script"))
import genera_L60c2 as g2                # noqa: E402

g1 = g2.g1
gc = g2.gc
NUOVE = ("R150", "R151", "R152", "R153", "R112", "R144")
# LE COPIE GUASTE DEL BLOCCO. Un deck di guasto non include gain_block.subckt guasto al volo: include
# inc/<modo>.subckt, la copia con la riga cambiata, che `genera_canale.py modi` ha scritto UNA volta
# in L45a (2026-10-13) - cioe' il blocco di L45a, senza R150..R153 e con R112 / R144 a 100 / 10 ohm.
# Qui le copie si riscrivono dal gain_block.subckt di oggi in L60d2/inc/, con la stessa
# subckt_guasto() di L45a, e i deck le includono da li'. (In L60c2 era giusto cosi': il blocco era
# ancora quello di L45a.)
INC_L45A = "@REPO@/%s/inc/" % gc.REL
INC = os.path.join(L60D2, "inc")
INC_REL = "@REPO@/%s/" % os.path.relpath(INC, gc.ROOT)
OGGI = ("R150", "R151", "R152", "R153")


def modi():
    """(pos, modo, gear, tfine): i 107 di L60c2 piu' i modi delle parti nuove o sdoppiate."""
    out = list(g2.modi_guasti())
    gia = {(p, m) for p, m, _, _ in out}
    nomi = {m for m, _, _, _, _ in gc.modi()}
    for parte in NUOVE:
        for sigla in ("ap", "cc"):
            m = "%s_%s" % (parte, sigla)
            if m not in nomi:
                sys.exit("RIFIUTATO: %s non e' un modo di gain_block.subckt di oggi" % m)
            for pos in ("A", "F2"):
                if (pos, m) not in gia:
                    out.append((pos, m, False, g2.T_FINE))
    return sorted(out)


def casi():
    c = [(g, n, t) for g, n, t in g2.casi() if g == "g0"]
    for pos, modo, gear, tfine in modi():
        for k in (1.0, 1.05):
            sk = "" if k == 1.0 else "_k105"
            t = gc.deck_tr(pos, 0, modo, False, False, tfine=tfine, gear=gear)
            c.append(("guasti", "G0_%s_%s%s" % (pos, modo, sk), g1.applica(t, "G0", k)))
    return c


def copia_guasta(modo):
    """inc/<modo>.subckt dal blocco di oggi; rifiuta se non e' il blocco a ridondanza."""
    t = gc.subckt_guasto(modo)
    righe = {r.split()[0] for r in t.splitlines() if r.split()}
    if not set(OGGI) <= righe:
        sys.exit("RIFIUTATO: la copia di %s non ha %s: non e' il blocco di oggi" % (modo, OGGI))
    gc.scrivi(os.path.join(INC, modo + ".subckt"), t)


def reindirizza(testo, nome):
    """L'include della copia guasta da L45a/inc/ a L60d2/inc/, scrivendo la copia."""
    n = testo.count(INC_L45A)
    if n == 0:
        return testo
    if n != 1:
        sys.exit("RIFIUTATO: %s include %d copie guaste" % (nome, n))
    i = testo.index(INC_L45A) + len(INC_L45A)
    modo = testo[i:testo.index(".subckt", i)]
    copia_guasta(modo)
    return testo.replace(INC_L45A, INC_REL)


def main():
    print(g2.verifica_netlist())
    lista = []
    for gruppo, nome, testo in casi():
        testo = reindirizza(g1.rinomina(testo, nome), nome)
        if gruppo == "guasti" and INC_REL not in testo:
            sys.exit("RIFIUTATO: %s non include una copia guasta" % nome)
        p = os.path.join(L60D2, "deck", gruppo, nome + ".cir")
        if testo.startswith("L60c1 "):
            testo = "L60d2" + testo[len("L60c1"):]
            gc.scrivi(p, testo)
        else:
            gc.scrivi(p, "L60d2 %s %s - " % (gruppo, nome) + testo)
        if p not in lista:          # G0_CTRL_F2 viene da due gruppi di L60c1: una corsa sola
            lista.append(p)
    gc.scrivi(os.path.join(L60D2, "deck", "lista.txt"), "\n".join(lista) + "\n")
    n107 = len(g2.modi_guasti())
    print("L60d2: %d deck (%d modi di guasto: %d di L60c2, %d nuovi)"
          % (len(lista), len(modi()), n107, len(modi()) - n107))


if __name__ == "__main__":
    main()
