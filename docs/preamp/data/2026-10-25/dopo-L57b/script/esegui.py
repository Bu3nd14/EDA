#!/usr/bin/env python3
"""Dopo L57b (copia di L57b): genera e corre le varianti del banco dell'RCA a caldo e del costo, con la
protezione presa dal subckt generato (genera.py / dist.py --prot S..., limitatore.py).

Varianti (--prot):
  S,rif=5,dio=1n4148  caso noto 1: la topologia generata coi modelli del banco di L57a (1N4148 e
                      riferimenti ideali a 5 V) deve ridare r1k_lim5 di L57a
  S,rif=eq,dio=fit    caso noto 2: la stima di L57b deve ridare le cifre «lim» di L57b
  S,rif=eq            il circuito: il BAV199 col modello di Diodes Inc. (models/diodes/bav199.lib),
                      i due LM4040 come INREF_EQ (limitations #76)
  S,rif=eq,dio=di2c   il modello del costruttore con la capacita' raddoppiata: la sensibilita' del costo

Tre corse alla volta (limitations #75: ~65 MB l'una in L57a).

Uso: /usr/bin/python3 esegui.py <gruppo>    gruppi: noto | reti | mute | costo
"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

QUI = os.path.dirname(os.path.abspath(__file__))
L57B = os.path.dirname(QUI)
REPO = os.path.abspath(os.path.join(L57B, "..", "..", "..", "..", ".."))
PY = "/usr/bin/python3"
SIM = os.path.join(REPO, "scripts", "run_simulation.sh")

VARIANTI = {"noto": "S,rif=5,dio=1n4148", "lim_fit": "S,rif=eq,dio=fit", "lim": "S,rif=eq",
            "lim_2c": "S,rif=eq,dio=di2c"}
GRUPPI = {"noto": {"noto_r1k_lim5": ["--prot", VARIANTI["noto"]],
                   "lim_fit_rete10": ["--prot", VARIANTI["lim_fit"], "--rete", "1.0"]}}
RETI = {}
for v in ("lim", "lim_2c"):
    for rete in ("0.9", "1.0", "1.1"):
        casi = [] if rete == "1.0" else ["--casi", "classeII"]
        RETI["%s_rete%s" % (v, rete.replace(".", ""))] = ["--prot", VARIANTI[v], "--rete", rete] + casi
GRUPPI["reti"] = RETI
GRUPPI["mute"] = {"mute_lim_rete%s" % r.replace(".", ""): ["--prot", VARIANTI["lim"], "--rete", r, "--casi",
                                                         "classeII", "--mute"] for r in ("0.9", "1.0", "1.1")}
COSTO = {}
for v, prot in (("senza", "nessuna"), ("noto", VARIANTI["noto"]), ("limfit", VARIANTI["lim_fit"]),
                ("lim", VARIANTI["lim"]), ("lim_2c", VARIANTI["lim_2c"])):
    for fam in ("thd", "rumore", "imd"):
        COSTO["%s_%s" % (fam, v)] = ["--prot", prot]
GRUPPI["costo"] = COSTO


def corri(gruppo, nome, argomenti):
    costo = gruppo == "costo"
    d = os.path.join(L57B, "costo") if costo else os.path.join(L57B, "rca", gruppo)
    os.makedirs(d, exist_ok=True)
    deck = os.path.join(d, nome + ".cir")
    out = os.path.join(d, "out_" + nome)
    if costo:
        subprocess.run([PY, os.path.join(QUI, "dist.py"), nome.split("_")[0], deck] + argomenti, check=True)
    else:
        subprocess.run([PY, os.path.join(QUI, "genera.py"), "oggi", deck] + argomenti, check=True)
    r = subprocess.run(["/bin/zsh", SIM, deck, out], capture_output=True, text=True)
    if r.returncode != 0:
        return "%s: ngspice rc=%d" % (nome, r.returncode)
    if not costo:
        subprocess.run([PY, os.path.join(QUI, "spl.py"), out], check=True, capture_output=True)
    return "%s: ok" % nome


gruppo = sys.argv[1]
with ThreadPoolExecutor(max_workers=3) as ex:
    for esito in ex.map(lambda kv: corri(gruppo, kv[0], kv[1]), GRUPPI[gruppo].items()):
        print(esito, flush=True)
