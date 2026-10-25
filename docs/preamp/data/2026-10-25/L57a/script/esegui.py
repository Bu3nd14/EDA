#!/usr/bin/env python3
"""L57a: genera e corre le varianti del banco dell'RCA a caldo (genera.py modo oggi).

Ogni variante: rca/<gruppo>/<nome>.cir -> rca/<gruppo>/out_<nome>/ (run_simulation.sh), poi spl.py.
Tre corse alla volta (limitations #75: il circuito e' un canale senza guasti, ~0,4 s di corsa;
le memorie si guardano con ps durante la prima lista).

Uso: /usr/bin/python3 esegui.py <gruppo>      gruppi: oggi | strade | reti | forma
"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

QUI = os.path.dirname(os.path.abspath(__file__))
L57A = os.path.dirname(QUI)
REPO = os.path.abspath(os.path.join(L57A, "..", "..", "..", "..", ".."))
PY = "/usr/bin/python3"
SIM = os.path.join(REPO, "scripts", "run_simulation.sh")

# nome: (argomenti di genera.py)
GRUPPI = {
    "oggi": {"senza": []},
    "forma": {"forma_senza": ["--casi", "classeII", "--forma", "--tstop", "0.12"]},
    "strade": {
        "r2k2": ["--prot", "R=2.2k"],
        "r1k_rail": ["--prot", "R=1k,D=rail"],
        "r2k2_rail": ["--prot", "R=2.2k,D=rail"],
        "r4k7_rail": ["--prot", "R=4.7k,D=rail"],
        "r10k_rail": ["--prot", "R=10k,D=rail"],
        "r1k_lim5": ["--prot", "R=1k,D=5"],
        "r2k2_lim5": ["--prot", "R=2.2k,D=5"],
        "r4k7_lim5": ["--prot", "R=4.7k,D=5"],
    },
}
# le tre reti, solo i casi in classe II (la tensione dei condensatori Y scala con la rete)
RETI = {}
for v, prot in (("senza", "nessuna"), ("r2k2_rail", "R=2.2k,D=rail"), ("r4k7_rail", "R=4.7k,D=rail"),
                ("r2k2_lim5", "R=2.2k,D=5"), ("r4k7_lim5", "R=4.7k,D=5")):
    for rete in ("0.9", "1.1"):
        RETI["%s_rete%s" % (v, rete.replace(".", ""))] = ["--prot", prot, "--rete", rete, "--casi", "classeII"]
GRUPPI["reti"] = RETI


def corri(gruppo, nome, argomenti):
    d = os.path.join(L57A, "rca", gruppo)
    os.makedirs(d, exist_ok=True)
    deck = os.path.join(d, nome + ".cir")
    out = os.path.join(d, "out_" + nome)
    subprocess.run([PY, os.path.join(QUI, "genera.py"), "oggi", deck] + argomenti, check=True)
    r = subprocess.run(["/bin/zsh", SIM, deck, out], capture_output=True, text=True)
    if r.returncode != 0:
        return "%s: ngspice rc=%d" % (nome, r.returncode)
    if "--forma" not in argomenti:
        subprocess.run([PY, os.path.join(QUI, "spl.py"), out], check=True, capture_output=True)
    return "%s: ok" % nome


gruppo = sys.argv[1]
with ThreadPoolExecutor(max_workers=3) as ex:
    for esito in ex.map(lambda kv: corri(gruppo, kv[0], kv[1]), GRUPPI[gruppo].items()):
        print(esito, flush=True)
