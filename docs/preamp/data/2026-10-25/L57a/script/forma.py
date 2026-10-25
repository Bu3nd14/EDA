#!/usr/bin/env python3
"""L57a: la corrente di gate dell'RCA a caldo sulla forma d'onda (genera.py --forma).

L53 aveva letto i 29-39 mA di picco come lo spostamento capacitivo del fronte del contatto. Qui si
guarda quando cadono e quale giunzione e' in conduzione: gate-source (g1 - s1) o gate-drain
(g1 - d1n) in avanti oltre 0,5 V, e per quanto tempo la corrente sta sopra IG(F) = 10 mA.

wrdata scrive per ogni vettore la coppia (tempo, valore): le colonne pari sono il tempo.
Uso: /usr/bin/python3 forma.py <forma_caso.txt>...
"""
import sys

NOMI = ["jin", "ain", "g1", "g2", "s1", "d1n", "ncasc", "aout", "main", "ig"]
for f in sys.argv[1:]:
    t, c = [], {n: [] for n in NOMI}
    for riga in open(f):
        x = riga.split()
        if len(x) < 2 * len(NOMI):
            continue
        try:
            v = [float(y) for y in x]
        except ValueError:
            continue
        t.append(v[0])
        for i, n in enumerate(NOMI):
            c[n].append(v[2 * i + 1])
    ig = c["ig"]
    k = max(range(len(t)), key=lambda i: abs(ig[i]))
    sopra = [i for i in range(len(t)) if abs(ig[i]) > 10.0]
    durata = 0.0
    for i in sopra:
        if i + 1 < len(t):
            durata += t[i + 1] - t[i]
    gd = [c["g1"][i] - c["d1n"][i] for i in range(len(t))]
    gs = [c["g1"][i] - c["s1"][i] for i in range(len(t))]
    veb = [c["d1n"][i] - c["ncasc"][i] for i in range(len(t))]
    fwd_gd = sum(1 for i in sopra if gd[i] > 0.5)
    fwd_gs = sum(1 for i in sopra if gs[i] > 0.5)
    print("== %s" % f)
    print("  picco ig %.2f mA a t = %.4f ms: ain %.2f g1 %.2f s1 %.2f d1n %.2f ncasc %.2f aout %.2f V"
          % (ig[k], t[k] * 1e3, c["ain"][k], c["g1"][k], c["s1"][k], c["d1n"][k], c["ncasc"][k], c["aout"][k]))
    print("  gd al picco %.2f V, gs al picco %.2f V" % (gd[k], gs[k]))
    print("  |ig| > 10 mA: %d campioni, %.3f ms in tutto, primo a %.4f ms, ultimo a %.4f ms"
          % (len(sopra), durata * 1e3, t[sopra[0]] * 1e3 if sopra else 0, t[sopra[-1]] * 1e3 if sopra else 0))
    print("  di questi con gate-drain in avanti (>0,5 V): %d; con gate-source in avanti: %d" % (fwd_gd, fwd_gs))
    print("  gate-drain massimo %.2f V, minimo %.2f V; Q117 emettitore-base in inversa massimo %.2f V"
          % (max(gd), min(gd), max(veb)))
    tm = [i for i in range(len(t)) if t[i] >= 0.05]
    print("  ain massimo %.2f V minimo %.2f V; jin massimo %.2f minimo %.2f V"
          % (max(c["ain"][i] for i in tm), min(c["ain"][i] for i in tm),
             max(c["jin"][i] for i in tm), min(c["jin"][i] for i in tm)))
