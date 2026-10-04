"""genera_e3_sequenza.py - L47b2b1: E3 lungo la sfumatura, con l'AC vera del deck E3.

Lo stato delle due celle in ogni istante dipende solo dalla corrente dei LED (il pilota e' ideale,
le celle non vedono il circuito): gli stati della `tran` del banco ridotto (../banco/run/v5/, v5,
curve A-E) sono quelli del preamp intero. Per ogni curva si prendono gli istanti in cui |Zin|
stimata (rapido.zin_e3) e' minima a 20 Hz e a 20 kHz; lo stato (log10 R di serie e derivazione)
si porta nel deck E3 come una corrente STATICA del LED che lo da' a regime (la tabella xt della
curva, invertita). Poi l'AC di spice/preamp/tb/tb_e3_e5_ldr.cir (il circuito, il trim, il
selettore), per ogni posizione del trim e capacita' del selettore.

    /usr/bin/python3 genera_e3_sequenza.py <uscita.cir>
Poi:  /bin/zsh scripts/run_simulation.sh <uscita.cir> <cartella>
"""
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.join(QUI, "..", "banco")
sys.path.insert(0, BANCO)
import rapido as R  # noqa: E402
import sfumatura as SF  # noqa: E402

REPO = R.REPO
TB = os.path.join(REPO, "spice", "preamp", "tb", "tb_e3_e5_ldr.cir")
IRIP = 10e-9


def corrente_per(curva, x):
    """La corrente del LED che da' log10(R) = x a regime sulla curva (xt e' decrescente in I)."""
    if x >= R.xt_di(curva, IRIP) - 1e-9:
        return IRIP
    a, b = math.log10(IRIP), math.log10(0.1)
    for _ in range(80):
        m = 0.5 * (a + b)
        if R.xt_di(curva, 10 ** m) > x:
            a = m
        else:
            b = m
    return 10 ** (0.5 * (a + b))


def istanti(curva):
    p = os.path.join(BANCO, "run", "v5", "v5_%s.dat" % curva)
    t, xs, xp = SF.leggi_stati(p)
    out = []
    for f, nome in ((R.F_BASSI, "20Hz"), (R.F_E3, "20kHz")):
        z = [(R.zin_e3(10 ** a, 10 ** b, f), k) for k, (a, b) in enumerate(zip(xs, xp))]
        zmin, k = min(z)
        out.append((nome, t[k], xs[k], xp[k], zmin))
    return out


def main():
    righe = open(TB).read().splitlines()
    i_ctrl = next(i for i, r in enumerate(righe) if r.strip() == ".control")
    testa = righe[:i_ctrl]
    testa[0] = ("tb_e3_sequenza.cir - L47b2b1: E3 negli istanti peggiori della sfumatura v5, "
                "curve A-E (GENERATO da genera_e3_sequenza.py)")
    # le celle della curva giusta: una coppia di sottocircuiti per curva, si sceglie con alter? No:
    # il nome del sottocircuito non si altera. Una coppia di celle per curva, tutte collegate e
    # tutte al buio (10 nA, 25 Mohm) tranne quella della corsa: il buio e' 25 Mohm in parallelo,
    # che si somma al resto. Per non sporcare, si scrive un deck per curva.
    stati = {c: istanti(c) for c in "ABCDE"}
    decks = []
    for c in "ABCDE":
        d = list(testa)
        d = [r.replace("NSL32SR3_B", "NSL32SR3_%s" % c) for r in d]
        d += [".control",
              'echo "curva,quando,t_s,rs_ohm,rp_ohm,stima_kohm,pos,csel,zmin_ohm,z20_ohm,z1k_ohm,z20k_ohm"'
              " > tb_e3_seq_%s.csv" % c,
              "alter rsrc = 1m"]
        for nome, tk, a, b, zst in stati[c]:
            i_s, i_p = corrente_per(c, a), corrente_per(c, b)
            for pos, (r1r, r1s, r2r, r2s) in ((0, ("0.1", "1G", "0.1", "1G")),
                                             (6, ("1G", "0.1", "0.1", "1G")),
                                             (12, ("1G", "0.1", "1G", "0.1"))):
                for cs in ("1f", "22p", "68p"):
                    d += ["alter ils dc = %.6g" % i_s, "alter ilp dc = %.6g" % i_p,
                          "alter rt1r = %s" % r1r, "alter rt1s = %s" % r1s,
                          "alter rt2r = %s" % r2r, "alter rt2s = %s" % r2s,
                          "alter csel = %s" % cs,
                          "op",
                          "let rsv = 10^v(xls.xs)", "let rpv = 10^v(xlp.xs)",
                          'set rsvs = "$&rsv"', 'set rpvs = "$&rpv"',
                          "ac dec 50 20 20k",
                          "let zmag = mag(v(srcx)/(-i(vsrc)))",
                          "meas ac zmin min zmag from=20 to=20000",
                          "meas ac z20 find zmag at=20",
                          "meas ac z1k find zmag at=1000",
                          "meas ac z20k find zmag at=20000",
                          'echo "%s,%s,%.4f,$rsvs,$rpvs,%.2f,%d,%s,$&zmin,$&z20,$&z1k,$&z20k" >> tb_e3_seq_%s.csv'
                          % (c, nome, tk, zst / 1e3, pos, cs, c),
                          "destroy all"]
        d += [".endc", ".end"]
        decks.append((c, d))
    base = sys.argv[1]
    for c, d in decks:
        p = base.replace(".cir", "_%s.cir" % c)
        open(p, "w").write("\n".join(d) + "\n")
        print("scritto", p)
    for c in "ABCDE":
        for nome, tk, a, b, zst in stati[c]:
            print("%s %-5s t=%.3f s  serie %.3f dec (I %.3g A)  deriv %.3f dec (I %.3g A)  stima %.1f k" % (
                c, nome, tk, a, corrente_per(c, a), b, corrente_per(c, b), zst / 1e3))


if __name__ == "__main__":
    main()
