#!/usr/bin/env python3
"""L36: i falsi del 2e per l'interblocco del guadagno (ADR-041, strada B di ADR-030).

Dalla netlist generata di oggi scrive varianti sabotate e fa girare su ognuna
scripts/check_relay_safe_state.py. Ogni variante DEVE fallire (rc 1); la netlist
vera deve passare (rc 0). Piu' la netlist di main prima di L36 (nessun ausiliario),
passata come secondo argomento, che deve fallire anch'essa.

Uso: genera_falsi.py <preamp_audio.net di oggi> <preamp_audio.net di main> <cartella uscita>

I sabotaggi toccano solo la sezione (nets): un pin cambia numero, un nodo sparisce
(il pin resta scollegato), o un nodo passa su un'altra rete.
"""
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
CHK = os.path.join(REPO, "scripts", "check_relay_safe_state.py")

NODO = r'\(node\s*\(ref "%s"\)\s*\(pin "%s"\)\s*\(pintype "[^"]*"\)\)'


def scambia_pin(testo, ref, a, b):
    """Scambia i numeri di pin a e b del componente ref nella sezione (nets)."""
    testa, nets = testo.split("(nets", 1)
    pat = re.compile(r'(\(ref "%s"\)\s*\(pin ")(%s|%s)(")' % (re.escape(ref), a, b))
    nets, n = pat.subn(lambda m: m.group(1) + (b if m.group(2) == a else a) + m.group(3), nets)
    assert n == 2, (ref, a, b, n)
    return testa + "(nets" + nets


def rinumera(testo, ref, a, b):
    """Il nodo (ref, a) diventa (ref, b): il pin b era scollegato."""
    testa, nets = testo.split("(nets", 1)
    pat = re.compile(r'(\(ref "%s"\)\s*\(pin ")%s(")' % (re.escape(ref), a))
    nets, n = pat.subn(lambda m: m.group(1) + b + m.group(2), nets)
    assert n == 1, (ref, a, b, n)
    return testa + "(nets" + nets


def togli_pin(testo, ref, pin):
    """Toglie dalle reti il nodo (ref, pin): il pin resta scollegato."""
    testa, nets = testo.split("(nets", 1)
    nets, n = re.subn(NODO % (re.escape(ref), re.escape(pin)), "", nets)
    assert n == 1, (ref, pin, n)
    return testa + "(nets" + nets


def sposta(testo, ref, pin, rete):
    """Porta il nodo (ref, pin) sulla rete di nome `rete` (anche se era scollegato)."""
    testa, nets = testo.split("(nets", 1)
    pat = re.compile(NODO % (re.escape(ref), re.escape(pin)))
    m = pat.search(nets)
    nodo = m.group(0) if m else '(node (ref "%s") (pin "%s") (pintype "passive"))' % (ref, pin)
    if m:
        nets = nets[:m.start()] + nets[m.end():]
    k = nets.find('(name "%s")' % rete)
    assert k >= 0, rete
    k += len('(name "%s")' % rete)
    nets = nets[:k] + "\n\t\t\t" + nodo + nets[k:]
    return testa + "(nets" + nets


FALSI = {
    # senza il polo ponte di K1: la corsa di ADR-030 si riapre
    "senza_ponte_K1": lambda t: togli_pin(t, "SW2", "14"),
    # il ponte direttamente alla bobina, senza il contatto dell'ausiliario:
    # la manopola accende K1 fuori mute
    "ponte_senza_ausiliario": lambda t: sposta(sposta(t, "SW2", "5", "G3_HI"), "SW2", "6", "G3_HI"),
    # la tenuta da VRELAY invece che da VHOLD: in mute K1 non si spegne piu'
    "tenuta_da_vrelay": lambda t: sposta(t, "D12", "2", "VRELAY"),
    # il diodo di comando in corto: G3_HI rientra su VTRIM e il trim si
    # comanda fuori mute
    "diodo_comando_in_corto": lambda t: sposta(sposta(t, "SW2", "2", "G3_HI"), "SW2", "3", "G3_HI"),
    # il diodo della tenuta montato al contrario
    "diodo_tenuta_invertito": lambda t: scambia_pin(t, "D12", "1", "2"),
    # senza il diodo della tenuta di K1 (VHOLD e H3 una rete sola): in mute il
    # ponte di K1 tiene K5 a +3 dB
    "senza_diodo_tenuta": lambda t: sposta(sposta(sposta(togli_pin(t, "D12", "1"),
                                                      "SW2", "5", "VHOLD"),
                                               "SW2", "6", "VHOLD"), "K11", "3", "VHOLD"),
    # l'ausiliario di K1 con la bobina sulla rete di K5
    "hold3_bobina_su_g10": lambda t: sposta(t, "K11", "1", "G10_HI"),
    # la posizione +3 comanda K5 invece di K1 (ADR-026)
    "k5_senza_k1": lambda t: sposta(sposta(togli_pin(togli_pin(t, "SW2", "2"), "SW2", "5"),
                                           "SW2", "8", "C10"), "SW2", "11", "H10"),
    # i LED +3 e +10 scambiati
    "led_scambiati": lambda t: sposta(sposta(t, "D8", "2", "D9_A"), "D9", "2", "D8_A"),
    # NC-014 sul polo dei LED di K11: NC e NO del polo 2 scambiati
    "nc_no_polo2_K11": lambda t: scambia_pin(t, "K11", "7", "5"),
    # NC-014 sul polo della tenuta di K11: la tenuta cablata sul NC (pin 2)
    # invece che sul NO (pin 4)
    "nc_no_polo1_K11": lambda t: rinumera(t, "K11", "4", "2"),
}


def corri(path):
    r = subprocess.run(["/usr/bin/python3", CHK, path], capture_output=True, text=True)
    return r.returncode, r.stdout


def main(argv):
    vera, main_net, out = argv[1], argv[2], argv[3]
    os.makedirs(out, exist_ok=True)
    righe = ["variante,rc_atteso,rc,esito,prima_riga"]
    testo = open(vera).read()
    casi = [("vera", vera, 0), ("main_prima_di_L36", main_net, 1)]
    for nome, f in FALSI.items():
        p = os.path.join(out, nome + ".net")
        with open(p, "w") as fh:
            fh.write(f(testo))
        casi.append((nome, p, 1))
    fallite = 0
    for nome, p, atteso in casi:
        rc, so = corri(p)
        ok = rc == atteso
        fallite += not ok
        coda = so.split("FALLITO", 1)[1] if "FALLITO" in so else ""
        trovati = [l.strip() for l in coda.splitlines() if l.startswith("  ")]
        prima = (trovati[0] if trovati else "").replace(",", ";")[:220]
        righe.append(f"{nome},{atteso},{rc},{'ok' if ok else 'SBAGLIATO'},{prima}")
        if nome != "vera":
            with open(os.path.join(out, nome + ".txt"), "w") as fh:
                fh.write(so)
        if p.startswith(out):
            os.remove(p)
        print(f"{nome:28s} atteso {atteso} rc {rc} {'ok' if ok else 'SBAGLIATO'}  {prima[:110]}")
    with open(os.path.join(out, "esito.csv"), "w") as fh:
        fh.write("\n".join(righe) + "\n")
    return 1 if fallite else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
