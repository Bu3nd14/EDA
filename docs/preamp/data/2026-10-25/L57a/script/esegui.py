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
                ("r2k2_lim5", "R=2.2k,D=5"), ("r4k7_lim5", "R=4.7k,D=5"),
                # le due da 1 k aggiunte dopo il costo: 4,7 k esce da V4 (costo/costo.csv)
                ("r1k_rail", "R=1k,D=rail"), ("r1k_lim5", "R=1k,D=5")):
    for rete in ("0.9", "1.1"):
        RETI["%s_rete%s" % (v, rete.replace(".", ""))] = ["--prot", prot, "--rete", rete, "--casi", "classeII"]
GRUPPI["reti"] = RETI
# il mute inserito durante il gesto, senza rimedio e con le due protezioni da 1 k, alle tre reti
MUTE = {}
for v, prot in (("senza", "nessuna"), ("r1k_rail", "R=1k,D=rail"), ("r1k_lim5", "R=1k,D=5")):
    for rete in ("0.9", "1.0", "1.1"):
        MUTE["mute_%s_rete%s" % (v, rete.replace(".", ""))] = ["--prot", prot, "--rete", rete,
                                                               "--casi", "classeII", "--mute"]
GRUPPI["mute"] = MUTE
# il costo al segnale (dist.py): thd e rumore per ciascuna protezione
COSTO = {}
for v, prot in (("senza", "nessuna"), ("r1k_rail", "R=1k,D=rail"), ("r2k2_rail", "R=2.2k,D=rail"),
                ("r4k7_rail", "R=4.7k,D=rail"), ("r10k_rail", "R=10k,D=rail"), ("r1k_lim5", "R=1k,D=5"),
                ("r2k2_lim5", "R=2.2k,D=5"), ("r4k7_lim5", "R=4.7k,D=5")):
    for fam in ("thd", "rumore"):
        COSTO["%s_%s" % (fam, v)] = ["--prot", prot]
GRUPPI["costo"] = COSTO
# la variante di Elliott Sound Products, AN-015 fig. 4 (chiesta dall'utente dopo la ricerca): la
# resistenza in serie (>= 1 k, meglio 1,5 k) e diodi a bassa capacita' in serie a zener da 12 V verso
# massa, cioe' un limitatore a ~+/-12,6 V; lo zener e' una sorgente ideale da 12 V (nessun modello di
# zener nel repo: ginocchio netto, la sua capacita' e' isolata dal diodo in serie come in AN-015)
AN015, COSTO_AN015 = {}, {}
for v, prot in (("r1k_z12", "R=1k,D=12"), ("r1k5_z12", "R=1.5k,D=12")):
    for rete in ("0.9", "1.0", "1.1"):
        AN015["%s_rete%s" % (v, rete.replace(".", ""))] = ["--prot", prot, "--rete", rete]
    for fam in ("thd", "rumore"):
        COSTO_AN015["%s_%s" % (fam, v)] = ["--prot", prot]
GRUPPI["an015"] = AN015
GRUPPI["costo_an015"] = COSTO_AN015


def corri(gruppo, nome, argomenti):
    costo = gruppo.startswith("costo")
    d = os.path.join(L57A, "costo") if costo else os.path.join(L57A, "rca", gruppo)
    os.makedirs(d, exist_ok=True)
    deck = os.path.join(d, nome + ".cir")
    out = os.path.join(d, "out_" + nome)
    if costo:
        subprocess.run([PY, os.path.join(QUI, "dist.py"), nome.split("_")[0], deck] + argomenti, check=True)
        r = subprocess.run(["/bin/zsh", SIM, deck, out], capture_output=True, text=True)
        return "%s: ngspice rc=%d" % (nome, r.returncode)
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
