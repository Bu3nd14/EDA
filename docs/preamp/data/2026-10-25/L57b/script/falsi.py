#!/usr/bin/env python3
"""L57b: i falsi del controllo del limitatore (scripts/check_relay_safe_state.py, check_limiter).

Dalla netlist di oggi scrive in falsi/ le varianti sbagliate, corre il controllo su ognuna e vuole che
cada col messaggio del limitatore; la netlist di prima di L57b (falsi/prima_di_adr101.net, da
`git show`) deve cadere anche lei. Esce col numero di falsi che il controllo NON ha preso.

Uso: /usr/bin/python3 falsi.py
"""
import os
import re
import subprocess
import sys

D = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(D)
ROOT = os.path.abspath(os.path.join(LOTTO, "..", "..", "..", "..", ".."))
NET = os.path.join(ROOT, "circuits", "preamp", "preamp_audio.net")
CHK = os.path.join(ROOT, "scripts", "check_relay_safe_state.py")
OUT = os.path.join(LOTTO, "falsi")
os.makedirs(OUT, exist_ok=True)
base = open(NET).read()


def scambia(txt, ref, p1, p2):
    """Scambia i piedini p1 e p2 di ref nella sezione delle reti."""
    pat = r'(\(ref "%s"\)\s*\(pin ")(%s|%s)(")' % (ref, p1, p2)
    n = len(re.findall(pat, txt))
    assert n == 2, (ref, p1, p2, n)
    return re.sub(pat, lambda m: m.group(1) + (p2 if m.group(2) == p1 else p1) + m.group(3), txt)


def valore(txt, ref, vecchio, nuovo):
    pat = r'(\(comp\s*\(ref "%s"\)\s*\(value ")%s(")' % (ref, re.escape(vecchio))
    assert len(re.findall(pat, txt)) == 1, ref
    return re.sub(pat, r"\g<1>%s\g<2>" % nuovo, txt)


FALSI = {
    "d179_rovescio": ("diodo doppio montato al contrario (estremi scambiati)",
                      lambda t: scambia(t, "D179", "1", "2"), "verso giusto"),
    "d379_comune_sbagliato": ("il piedino comune non sull'ingresso",
                              lambda t: scambia(t, "D379", "3", "1"), "piedino comune"),
    "u1_rovescio": ("il riferimento positivo montato al contrario",
                    lambda t: scambia(t, "U1", "1", "2"), "verso giusto"),
    "u2_rovescio": ("il riferimento negativo montato al contrario",
                    lambda t: scambia(t, "U2", "1", "2"), "verso giusto"),
    "r179_10k": ("la resistenza in serie di un altro valore",
                 lambda t: valore(t, "R179", "1k", "10k"), "una sola resistenza"),
}

mancati = 0
casi = [(k, v[0], v[1](base), v[2]) for k, v in FALSI.items()]
prima = os.path.join(OUT, "prima_di_adr101.net")
casi.append(("prima_di_adr101", "la netlist di main prima di L57b, senza limitatore",
             open(prima).read(), "una sola resistenza"))
for nome, cosa, testo, atteso in casi:
    p = os.path.join(OUT, nome + ".net")
    if nome != "prima_di_adr101":
        open(p, "w").write(testo)
    r = subprocess.run(["/usr/bin/python3", CHK, p], capture_output=True, text=True)
    preso = r.returncode != 0 and atteso in r.stdout
    mancati += not preso
    print("%-24s %-6s rc=%d  %s" % (nome, "PRESO" if preso else "MANCATO", r.returncode, cosa))
print("falsi presi: %d su %d" % (len(casi) - mancati, len(casi)))
sys.exit(mancati)
