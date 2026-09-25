#!/usr/bin/env python3
"""L35: i falsi di L16 (trim) rifatti sul sorgente di L35 col 2e esteso.

falsi.py di L16 genera la netlist da copie sabotate di trim.py e scrive nella propria
cartella dati: come in L36 lo si fa girare su una COPIA della radice (circuits/preamp,
library, scripts), cosi' i dati di L16 non si toccano.

Una variante non si applica piu': "bobina_K6_altra_net" metteva la bobina di K6 su
Net("PERMIT_CMD") invece che su MUTE_CMD. Da ADR-045 (L35) e' il PROGETTO. La sua
versione di oggi e' "permesso_su_mute_cmd" (K6 di nuovo su MUTE_CMD) e
"permit_cmd_fuori_da_J4" (un PERMIT_CMD che nessuno pilota), in genera_falsi.py.

Uso: regressione_L16.py <radice del repo> <cartella scratch>
"""
import re
import shutil
import sys
from pathlib import Path

root, scratch = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
if scratch.exists():
    shutil.rmtree(scratch)
for sub in ("circuits/preamp", "library", "scripts"):
    shutil.copytree(root / sub, scratch / sub,
                    ignore=shutil.ignore_patterns("__pycache__", "*.net"))
src = (root / "docs/preamp/data/2026-09-14/L16/esplorazione/script/falsi.py").read_text()
src, n = re.subn(r'    "bobina_K6_altra_net": \[\n.*?\n    \],\n', "", src, flags=re.S)
assert n == 1, n
print("bobina_K6_altra_net: non applicabile (da ADR-045 e' il progetto)")
sys.argv = ["falsi.py", str(scratch)]
exec(compile(src, "falsi.py (L16)", "exec"), {"__name__": "__main__"})
