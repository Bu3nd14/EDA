#!/usr/bin/env python3
"""L30 (NC-029): stima termica del telaio con otto blocchi, alimentatore compreso.

Solo stdlib. Lanciare con /usr/bin/python3; scrive la tabella su stdout.

CALCOLATA, non misurata. La conferma e' la temperatura nel telaio del prototipo (NC-029,
punto 4; ADR-021, «Da riaprire se»).

Il modello ha due salti in serie, come l'ipotesi di ADR-021 / ADR-010 (i 60 C sono «la stanza
a 35 C piu' ~25 C di aumento in un telaio chiuso dentro una libreria»):
  1. l'aria dentro il telaio sopra l'aria del vano: P / (h_telaio * A_telaio);
  2. l'aria del vano sopra la stanza: P / (U_vano * A_vano).
Il telaio si prende SIGILLATO (nessuna feritoia): e' il caso peggiore, le feritoie di P5
abbassano il primo salto. Il vano si prende CHIUSO su sei lati, di truciolare da 18 mm.
"""

# ---- la dissipazione, W: (nominale, minimo, massimo) ----
P = {
    # ADR-042, tb_op: 15 V x (32,6 + 33,6) mA = 0,993 W per blocco, otto blocchi
    "scheda audio (8 blocchi)": (7.94, 7.94, 7.94),
    # regolatori +-15 V: (Vin_media - 15) x 0,265 A per rail. Vin la sceglie il lotto
    # dell'alimentatore: 18,5 / 20 / 22 V
    "regolatori +-15 V": (2 * 5.0 * 0.265, 2 * 3.5 * 0.265, 2 * 7.0 * 0.265),
    # raddrizzatore: un diodo per rail conduce per semionda, V_F ~0,9 V
    "raddrizzatore": (2 * 0.9 * 0.265, 2 * 0.8 * 0.265, 2 * 1.0 * 0.265),
    # bobine e LED: 175 mA a 5 V nel caso peggiore (L35); la potenza per bobina del G6K e'
    # ~0,1 W a qualunque tensione nominale
    "bobine dei rele' e LED": (0.875, 0.875, 0.875),
    # regolatore di VRELAY: da ~8-10 V a 5 V, 175 mA
    "regolatore di VRELAY": (0.175 * 4.0, 0.175 * 3.0, 0.175 * 5.0),
    # LDR (2 stringhe x 20 mA x ~3,4 V), sorvegliante, temporizzatore
    "LDR, sorvegliante, temporizzatore": (0.25, 0.15, 0.35),
    # toroidale da 30-50 VA a ~15 W di carico: ferro ~1 W, rame con la corrente di picco
    # dei condensatori d'ingresso
    "trasformatore": (2.5, 1.5, 3.5),
}

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
    print("L30 - stima termica del telaio (CALCOLATA)")
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
