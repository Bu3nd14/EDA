#!/usr/bin/env python3
"""L29b2: le varianti sbagliate che check_relay_safe_state.py deve rifiutare (regola LDR).

Uso:  /usr/bin/python3 genera_falsi.py SCRATCH
      SCRATCH contiene una copia di circuits/preamp/{preamp_audio,gain_block,trim,spice_export}.py;
      scrive SCRATCH/F<n>.py e stampa i comandi per generarne la netlist col venv di SKiDL.

F1  il LED della serie L appeso all'ingresso del blocco A (ADR-022 violata)
F2  la derivazione L sul lato del connettore invece che sul nodo di R_IN
F3  la serie L oltre R_IN: connettore dritto al blocco A, la cella verso un nodo morto
"""
import os
import sys

D = os.path.abspath(sys.argv[1])
src = open(os.path.join(D, "preamp_audio.py")).read()
VAR = {
    "F1": [("        j3[pin_a] += left[2]\n",
            "        j3[pin_a] += left[2]\n        if fn == 'S':\n"
            "            left[2] += chans['L'][0]['IN']   # SABOTAGGIO F1\n")],
    "F2": [("    lp[3] += a[\"IN\"]\n", "    lp[3] += in_src if ch == 'L' else a[\"IN\"]   # SABOTAGGIO F2\n")],
    "F3": [("    ls[3] += in_src\n    ls[4] += a[\"IN\"]\n",
            "    ls[3] += in_src\n    ls[4] += (Net('MORTO') if ch == 'L' else a[\"IN\"])   # F3\n"
            "    if ch == 'L':\n        in_src += a[\"IN\"]\n")],
}
for nome, subs in VAR.items():
    s = src
    for a, b in subs:
        assert a in s, (nome, a)
        s = s.replace(a, b)
    open(os.path.join(D, nome + ".py"), "w").write(s)
    print("PREAMP_AUDIO_NET_OUT=%s/%s.net /Users/roberto/EDA/env/venv/bin/python3 %s/%s.py"
          % (D, nome, D, nome))
