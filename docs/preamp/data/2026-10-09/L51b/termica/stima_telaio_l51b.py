#!/usr/bin/env python3
"""L51b: la stima termica del telaio con le cifre di oggi (l'utente, 2026-10-09: «Rifare e
mostrarmela»).

Copia di data/2026-09-26/L41a/scelte/stima_telaio_l41a.py: il modello termico del telaio e del
vano e' IDENTICO (righe da T_STANZA in giu', copiate); cambia il dizionario P, che non e' piu'
fatto di ipotesi ma letto:

  - la scheda audio da tb_op di oggi (L51a/dopo/tb_op/tb_op.log): 8 x 15 V x (|i(vpp)| + |i(vmm)|);
  - tutto l'alimentatore dal banco di oggi, termica/tb_calore.log (genera_calore.py: il banco
    della rete col carico di carico.txt, i rail di oggi e la bobina del selettore, a regime con
    la musica e ogni bobina dello stato accesa; medie su 1,5-2,0 s). Le tre colonne sono rete
    nominale / -10 % / +10 %, come in L41a (regolatori simulati a 1,0 / 0,9 / 1,1);
  - le LDR non ci sono piu' (ADR-062): la voce e' tolta; il sorvegliante, il temporizzatore e
    il micro stanno nella linea a 12 V (il banco li carica da li').

Restano IPOTESI, dichiarate: il ferro dei due trasformatori (il banco ha una sorgente ideale con
R e L in serie, senza ferro). T1: ~1 W, la parte «ferro» della voce di L30/L41a (2,5 W =
ferro ~1 W + rame), con lo stesso scarto di +-1 W che L41a dava alla voce intera. T2: meta' della
voce di L41a (0,6 W per trasformatore e raddrizzatore; il raddrizzatore e il rame ora sono
misurati), 0,3 W, con lo stesso scarto relativo.

Solo stdlib. /usr/bin/python3 stima_telaio_l51b.py  -> la tabella su stdout.
CALCOLATA (il calore), con le potenze SIMULATE: la conferma resta la temperatura nel telaio del
prototipo (NC-029, ADR-021).
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(os.path.dirname(os.path.dirname(QUI)))
TB_OP = os.path.join(DATA, "2026-10-09", "L51a", "dopo", "tb_op", "tb_op.log")
CALORE = os.path.join(QUI, "tb_calore.log")


def leggi_calore():
    out = {}
    for r in open(CALORE):
        m = re.match(r"CALORE (regime_\w+) (.*)$", r.strip())
        if m:
            out[m.group(1)] = {k: float(v) for k, v in (x.split("=") for x in m.group(2).split())}
    if sorted(out) != ["regime_m10", "regime_nom", "regime_p10"]:
        sys.exit("RIFIUTATO: %s non ha i tre casi a regime" % CALORE)
    for r in open(CALORE):
        if re.search(r"error|singular|timestep too small", r, re.I):
            sys.exit("RIFIUTATO: %s ha un errore: %s" % (CALORE, r.strip()))
    return out


def leggi_op():
    t = open(TB_OP).read()
    ip = abs(float(re.search(r"^i\(vpp\) = (\S+)", t, re.M).group(1)))
    im = abs(float(re.search(r"^i\(vmm\) = (\S+)", t, re.M).group(1)))
    return ip, im


C = leggi_calore()
IP, IM = leggi_op()
P_BLK = 15 * (IP + IM)


def col(k):
    """(nominale, minimo, massimo) = rete nominale, -10 %, +10 %."""
    return tuple(C[c][k] for c in ("regime_nom", "regime_m10", "regime_p10"))


def resto(c):
    """Quello che i secondari danno e nessuna voce nomina: i partitori del sorvegliante,
    le resistenze serie dei condensatori, le correnti di riposo. Dal bilancio, non stimato."""
    x = C[c]
    return (x["pt1"] - x["cu1"] - x["dbr1"] - x["reg1"] - x["reg2"] - x["paud"]
            + x["pt2"] - x["cu2"] - x["dbr2"] - x["reg3"] - x["pvr"])


# ---- la dissipazione, W: (nominale, minimo, massimo) ----
P = {
    # L51b: tb_op di oggi (ADR-054), 8 blocchi
    "scheda audio (8 blocchi)": (8 * P_BLK,) * 3,
    # L51b: dal banco, ingresso x (ingresso - uscita), U501 + U502
    "regolatori +-15 V": tuple(a + b for a, b in zip(col("reg1"), col("reg2"))),
    # L51b: dal banco, i quattro diodi del ponte dei rail
    "raddrizzatore dei rail": col("dbr1"),
    # L51b: dal banco, il rame dei secondari di T1 (0,72 ohm per meta')
    "rame di T1": col("cu1"),
    # IPOTESI (vedi l'intestazione): il ferro del toroidale da 50 VA
    "ferro di T1 (ipotesi)": (1.0, 0.5, 1.5),
    # L51b: dal banco, quello che U503 consegna: bobine (mute, PERMIT, selettore, il resto della
    # scheda), bobina del rele' di rete, micro e linea a 5 V
    "linea a 12 V: bobine, selettore, micro": col("pvr"),
    # L51b: dal banco, U503
    "regolatore di VRELAY": col("reg3"),
    # L51b: dal banco, il ponte di T2 e lo Schottky
    "raddrizzatore di VRELAY": col("dbr2"),
    # L51b: dal banco, il rame del secondario di T2 (5,76 ohm)
    "rame di T2": col("cu2"),
    # IPOTESI (vedi l'intestazione): il ferro del piccolo trasformatore
    "ferro di T2 (ipotesi)": (0.3, 0.2, 0.45),
    # L51b: il bilancio dei secondari meno le voci sopra
    "il resto (partitori, ESR, riposo)": tuple(resto(c) for c in ("regime_nom", "regime_m10", "regime_p10")),
}

# --- da qui in giu' IDENTICO a stima_telaio_l41a.py (a meno del titolo stampato) ---
T_STANZA = 35.0     # ADR-021
T_LIMITE = 60.0     # ADR-021

# ---- il telaio: Modushop Pesante 03PN, 3U (P8, ADR-029), esterni 435 x 305 x 122 mm ----
L, W, H = 0.435, 0.305, 0.122
# il fondo sui piedini scambia meno: conta a meta'
A_TELAIO = L * W + 0.5 * L * W + 2 * L * H + 2 * W * H
# coefficiente globale di un involucro metallico sigillato, convezione naturale piu'
# irraggiamento (ordine dei metodi di quadri elettrici, IEC/TR 60890): 4,5 / 5,5 / 6,5
H_TELAIO = (5.5, 6.5, 4.5)   # nominale, favorevole, sfavorevole

# ---- il vano della libreria: truciolare 18 mm, k ~0,15 W/mK, film interno ed esterno ~8 W/m2K
U_VANO = 1.0 / (1 / 8.0 + 0.018 / 0.15 + 1 / 8.0)     # ~2,7 W/m2K


def area_vano(gioco):
    """Area interna del vano che lascia `gioco` metri attorno al telaio su ogni lato."""
    a, b, c = L + 2 * gioco, W + 2 * gioco, H + 2 * gioco
    return 2 * (a * b + a * c + b * c)


def main():
    pn = sum(v[0] for v in P.values())
    pmin = sum(v[1] for v in P.values())
    pmax = sum(v[2] for v in P.values())
    print("L51b - stima termica del telaio (CALCOLATA, potenze dal banco di oggi)")
    print()
    print("%-36s %6s %6s %6s" % ("dissipazione, W", "nom", "min", "max"))
    for k, (n, lo, hi) in P.items():
        print("%-36s %6.2f %6.2f %6.2f" % (k, n, lo, hi))
    print("%-36s %6.2f %6.2f %6.2f" % ("TOTALE", pn, pmin, pmax))
    print()
    print("telaio: A efficace %.3f m2, h %s W/m2K; vano: U %.2f W/m2K" % (A_TELAIO, H_TELAIO, U_VANO))
    print()
    print("%-10s %-9s %8s %8s %8s %8s" % ("gioco vano", "caso", "P, W", "dT tel", "dT vano", "T dentro"))
    for gioco in (0.03, 0.05, 0.10, 0.20, None):
        for caso, p, h in (("nominale", pn, H_TELAIO[0]), ("peggiore", pmax, H_TELAIO[2])):
            dt_t = p / (h * A_TELAIO)
            dt_v = 0.0 if gioco is None else p / (U_VANO * area_vano(gioco))
            t = T_STANZA + dt_t + dt_v
            g = "all'aria" if gioco is None else "%g cm" % (gioco * 100)
            print("%-10s %-9s %8.1f %8.1f %8.1f %8.1f%s" % (g, caso, p, dt_t, dt_v, t,
                                                          "  SOPRA 60" if t > T_LIMITE else ""))
    # il gioco minimo che tiene 60 C nel caso peggiore
    g = 0.0
    while g < 1.0:
        t = T_STANZA + pmax / (H_TELAIO[2] * A_TELAIO) + pmax / (U_VANO * area_vano(g))
        if t <= T_LIMITE:
            break
        g += 0.005
    print()
    print("gioco minimo del vano chiuso per 60 C nel caso peggiore: %.1f cm per lato" % (g * 100))


if __name__ == "__main__":
    main()
