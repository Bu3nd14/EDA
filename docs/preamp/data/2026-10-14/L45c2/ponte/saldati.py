#!/usr/bin/env python3
"""L45c1: the welded NO of the mute relays K2-K4 (L45b's latent fault). The supply does exactly
what it does without the fault - the weld is on the audio board, and the coil still releases -
so the bridge of the base case is kept, point for point, with ONE change: the jack contact never
opens (t_jack = null: the audio generator then leaves it closed to the end). The gain relays
still drop when they would. Solo stdlib.

    saldati.py <ponte>       writes nosald_<base>.json for the four bases of modi.SALDATI
"""
import json
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, "..", "psu"))
import modi  # noqa: E402

ponte = sys.argv[1]
for nome, base, ref, cosa in modi.SALDATI:
    j = json.load(open(os.path.join(ponte, base + ".json")))
    assert j["t_jack"] is not None, (base, "il caso di base non apre il jack: niente da saldare")
    j["caso"], j["base"], j["t_jack_base"], j["t_jack"] = nome, base, j["t_jack"], None
    j["nota"] = "L45c1: %s - %s; il ponte di %s col contatto del jack sempre chiuso" % (ref, cosa, base)
    json.dump(j, open(os.path.join(ponte, nome + ".json"), "w"), indent=1)
    print("%-22s da %-14s jack %.5f -> mai" % (nome, base, j["t_jack_base"]))
