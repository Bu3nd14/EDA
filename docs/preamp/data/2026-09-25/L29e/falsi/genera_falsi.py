#!/usr/bin/env python3
"""L29e: i falsi del 2e per la geometria iii (ADR-044).

Dalla netlist generata di oggi scrive varianti sabotate e fa girare su ognuna
scripts/check_relay_safe_state.py. Ogni variante DEVE fallire (rc 1); la netlist
vera deve passare (rc 0). Piu' la netlist di main prima di L29e (la derivazione
al jack), passata come secondo argomento, che deve fallire anch'essa.

Uso: genera_falsi.py <preamp_audio.net di oggi> <preamp_audio.net di main> <cartella uscita>

I sabotaggi toccano solo i nodi della sezione (nets): un pin cambia numero, o un
resistore perde i suoi nodi (sparisce dalle reti, come se non fosse montato).
"""
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
CHK = os.path.join(REPO, "scripts", "check_relay_safe_state.py")


def scambia_pin(testo, ref, a, b):
    """Scambia i numeri di pin a e b del componente ref nella sezione (nets)."""
    testa, nets = testo.split("(nets", 1)
    pat = re.compile(r'(\(ref "%s"\)\s*\(pin ")(%s|%s)(")' % (re.escape(ref), a, b))
    nets, n = pat.subn(lambda m: m.group(1) + (b if m.group(2) == a else a) + m.group(3), nets)
    assert n == 2, (ref, a, b, n)
    return testa + "(nets" + nets


def togli(testo, ref):
    """Toglie dalle reti ogni nodo del componente ref."""
    testa, nets = testo.split("(nets", 1)
    pat = re.compile(r'\(node\s*\(ref "%s"\)\s*\(pin "[^"]+"\)\s*\(pintype "[^"]*"\)\)' % re.escape(ref))
    nets, n = pat.subn("", nets)
    assert n == 2, (ref, n)
    return testa + "(nets" + nets


FALSI = {
    # NC-014: l'NC e l'NO del polo 2 scambiati - il canale destro esce a riposo
    "nc_no_polo2_K2": lambda t: scambia_pin(t, "K2", "7", "5"),
    # il lato condensatore sul NO e il jack sul COM: la iii rovesciata
    "com_no_polo1_K4": lambda t: scambia_pin(t, "K4", "3", "4"),
    # il bleed lato condensatore non montato (fissa 1, L)
    "senza_bleed_c_R167": lambda t: togli(t, "R167"),
    # il bleed del jack non montato (principale, L): a riposo il jack e' sospeso
    "senza_bleed_jack_R263": lambda t: togli(t, "R263"),
}


def corri(path):
    r = subprocess.run(["/usr/bin/python3", CHK, path], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main(argv):
    oggi, vecchia, out = argv[1:4]
    os.makedirs(out, exist_ok=True)
    righe = []
    rc, txt = corri(oggi)
    righe.append(("vera (oggi)", 0, rc))
    rc, txt = corri(vecchia)
    open(os.path.join(out, "main_derivazione_al_jack.txt"), "w").write(txt)
    righe.append(("main prima di L29e", 1, rc))
    base = open(oggi).read()
    for nome, f in FALSI.items():
        p = os.path.join(out, nome + ".net")
        open(p, "w").write(f(base))
        rc, txt = corri(p)
        open(os.path.join(out, nome + ".txt"), "w").write(txt)
        os.remove(p)   # la netlist sabotata si rifa' correndo; si tiene l'esito
        righe.append((nome, 1, rc))
    ok = all(atteso == rc for _, atteso, rc in righe)
    with open(os.path.join(out, "esito.csv"), "w") as fh:
        fh.write("variante,rc_atteso,rc\n")
        for r in righe:
            fh.write("%s,%d,%d\n" % r)
    for r in righe:
        print("%-28s atteso %d  rc %d  %s" % (r[0], r[1], r[2], "ok" if r[1] == r[2] else "SBAGLIATO"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
