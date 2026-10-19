#!/usr/bin/env python3
"""L62a: il «A» della principale per i modi di NC-062 coi due metodi di v2_metodo, la media (di oggi,
ADR-087 / ADR-088) e il puntuale col diradamento (quello di L45a). Prova che il gradino nuovo viene
dal metodo che legge per area l'impulso di ~2 us dell'interruttore ideale, non dal blocco.
Uso: metodo_scatto.py run/<cart>/<modo> ...   -> stampa"""
import os
import sys

L62A = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(L62A, "..", "..", "2026-10-13", "L45a", "script"))
import analizza_tr as at  # noqa: E402

vm = at.vm
i0 = int(round(at.T_GUASTO * vm.FS))
print("cartella/modo                 media: A mV  dB SPL   puntuale: A mV  dB SPL")
for d in sys.argv[1:]:
    m = os.path.basename(d.rstrip("/"))
    riga = "%-28s" % "/".join(d.rstrip("/").split(os.sep)[-2:])
    for metodo in ("media", "puntuale"):
        serie, t_fine = vm.leggi_wrdata(os.path.join(d, m + ".dat"), at.DTMIN, 10.0, metodo)
        x = serie[0]
        a_v, _, _ = vm.a_picco(x, [x[i0 - 10]] * len(x), at.T_GUASTO, t_fine)
        riga += "   %10.3f  %6.1f" % (a_v * 1e3, at.db_main(a_v))
    print(riga)
