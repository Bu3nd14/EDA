"""b2_ideale.py - L47c2b1: B2 con musica dopo un taglio netto e' musica che passa, o la coda del
passa-alto del metodo che digerisce il taglio? Sulla corsa della sonda bser (che corre fino in
fondo), per ogni uscita:
  - B2 del circuito (v2_metodo.b_picco, come analizza: filtrato da t = 0, picco da
    t_ins + t_grad + 20 ms a t_rel);
  - B2 del taglio ideale (il riferimento «mai» fino al contatto, poi il «sempre»: costruito come
    in tabella_clic.py), stessa finestra;
  - B1 (il riferimento «sempre in mute», da 0,5 s): la musica che passa davvero a mute inserito;
  - il picco GREZZO del jack nella finestra di B2, senza filtro;
  - B2 col filtro fatto partire al contatto (stato nullo), invece che da t = 0.

    /usr/bin/python3 b2_ideale.py <cartella> <corsa> <rif_mai> <rif_sempre> <f_hz> <t_fine>
"""
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import v2_metodo as vm  # noqa: E402

d, corsa, rm, rs, f, tf = sys.argv[1:7]
f, tf = float(f), float(tf)
T_INS, TG, T_REL = 1.0, 0.024, 2.0
TC = T_INS + TG
MATRICE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "matrice_interruttore")
dt = 2e-6 if f < 20000 else 1e-7
xe, _ = vm.leggi_wrdata(os.path.join(d, corsa + ".dat"), dt, tf)
xm, _ = vm.leggi_wrdata(os.path.join(MATRICE, rm + ".dat"), dt, tf)
xs, _ = vm.leggi_wrdata(os.path.join(MATRICE, rs + ".dat"), dt, tf)
a, b = T_INS + TG + 0.020, T_REL
ia, ib, ic = int(a * vm.FS), int(b * vm.FS), int(round(TC * vm.FS))
print("# %s, %g Hz: finestra di B2 %.3f..%.3f s; contatto a %.4f s" % (corsa, f, a, b, TC))
for k, u in enumerate(vm.USCITE):
    e, m, s = xe[k], xm[k], xs[k]
    n = min(len(e), len(m), len(s))
    ide = m[:ic] + s[ic:n]
    b2, ib2 = vm.b_picco(e[:n], a, b)
    b2i, _ = vm.b_picco(ide, a, b)
    b1, _ = vm.b_picco(s[:n], 0.5, tf)
    grezzo = max(abs(v) for v in e[ia:ib])
    y = vm.filtra(e[:n], ic)
    b2c = max(abs(v) for v in y[ia:ib])
    print("%-9s B2 %.4g V (a %.4f s) | taglio ideale %.4g V | B1 %.3g V | grezzo %.3g V |"
          " filtro dal contatto %.3g V" % (u, b2, ib2 / vm.FS, b2i, b1, grezzo, b2c))
