#!/usr/bin/env python3
"""L35: i falsi di L36 rifatti sulla netlist di L35 col 2e esteso.

Importa FALSI da data/2026-09-25/L36/falsi/genera_falsi.py e li applica alla netlist di
oggi. Una variante che sabota una parte che non esiste piu' (D7-D9: i LED del guadagno
sono usciti dalla scheda in L35, ADR-028) solleva AssertionError nel sabotaggio stesso e
si segna "non applicabile": la sostituisce la sua versione sull'header in
L35/falsi/genera_falsi.py (gain_led_3_10_scambiati).

Uso: regressione_L36.py <preamp_audio.net di oggi> <preamp_audio.net prima di L36>
"""
import importlib.util
import os
import subprocess
import sys
import tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
L36 = os.path.join(QUI, "..", "..", "L36", "falsi", "genera_falsi.py")
spec = importlib.util.spec_from_file_location("falsi_l36", L36)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main(argv):
    oggi, prima = argv[1], argv[2]
    testo = open(oggi).read()
    casi = [("vera (L35)", oggi, 0), ("main prima di L36", prima, 1)]
    tmp = tempfile.mkdtemp()
    na = []
    for nome, f in mod.FALSI.items():
        try:
            t = f(testo)
        except AssertionError as e:
            na.append(nome)
            print(f"{nome:28s} non applicabile: {e}")
            continue
        p = os.path.join(tmp, nome + ".net")
        open(p, "w").write(t)
        casi.append((nome, p, 1))
    sbagliate = 0
    for nome, p, atteso in casi:
        r = subprocess.run(["/usr/bin/python3", mod.CHK, p], capture_output=True, text=True)
        coda = r.stdout.split("FALLITO", 1)[1] if "FALLITO" in r.stdout else ""
        trovati = [l.strip() for l in coda.splitlines() if l.startswith("  ")]
        ok = r.returncode == atteso
        sbagliate += not ok
        print(f"{nome:28s} atteso {atteso} rc {r.returncode} {'ok' if ok else 'SBAGLIATO'}  "
              f"{(trovati[0] if trovati else '')[:100]}")
    return 1 if sbagliate else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
