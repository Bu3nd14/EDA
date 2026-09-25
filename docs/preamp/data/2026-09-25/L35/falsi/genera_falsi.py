#!/usr/bin/env python3
"""L35: i falsi del 2e per ADR-045 (K6 su un comando proprio) e per il pannello (ADR-028).

Dalla netlist generata di oggi scrive varianti sabotate e fa girare su ognuna
scripts/check_relay_safe_state.py. Ogni variante DEVE fallire (rc 1); la netlist
vera deve passare (rc 0). Piu' la netlist di main prima di L35 (K6 su MUTE_CMD, LED
sulla scheda, nessun J4), passata come secondo argomento, che deve fallire anch'essa.

Uso: genera_falsi.py <preamp_audio.net di oggi> <preamp_audio.net di main> <cartella uscita>

I sabotaggi toccano solo la sezione (nets), come in L36: un pin cambia numero, un nodo
sparisce (il pin resta scollegato), o un nodo passa su un'altra rete. Le quattro funzioni
sono quelle di data/2026-09-25/L36/falsi/genera_falsi.py, copiate.
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


def rete_di(testo, ref, pin):
    """Il nome della rete che porta il nodo (ref, pin)."""
    nets = testo.split("(nets", 1)[1]
    for chunk in re.split(r"\(net\s*\(code", nets)[1:]:
        if re.search(NODO % (re.escape(ref), re.escape(pin)), chunk):
            return re.search(r'\(name "([^"]*)"\)', chunk).group(1)
    raise AssertionError((ref, pin))


FALSI = {
    # --- ADR-045: i comandi ------------------------------------------------
    # il residuo di L36 che rientra: K6 di nuovo sul comando dei rele' del jack
    "permesso_su_mute_cmd": lambda t: sposta(t, "K6", "8", "MUTE_CMD"),
    # il comando del permissivo non esce dalla scheda: nessuno lo pilota
    "permit_cmd_fuori_da_J4": lambda t: togli_pin(t, "J4", "2"),
    # il comando dei rele' del jack non esce dalla scheda
    "mute_cmd_fuori_da_J4": lambda t: togli_pin(t, "J4", "1"),
    # i due comandi scambiati sul connettore: il temporizzatore sfaserebbe al contrario
    "comandi_scambiati_su_J4": lambda t: scambia_pin(t, "J4", "1", "2"),
    # --- F10: l'interruttore di mute --------------------------------------
    # l'interruttore non arriva al temporizzatore
    "interruttore_fuori_da_J4": lambda t: togli_pin(t, "J4", "3"),
    # l'interruttore in serie al comando dei jack: perde lo sfasamento
    "interruttore_su_mute_cmd": lambda t: sposta(t, "SW3", "1", "MUTE_CMD"),
    # --- F9: i LED del trim ------------------------------------------------
    # i pin 0 dB e -6 dB scambiati sull'header
    "trim_led_0_6_scambiati": lambda t: scambia_pin(t, "J5", "1", "2"),
    # NC-014 sulla spia: reset e set del polo 1 di SPIA1 scambiati
    "spia1_reset_set_scambiati": lambda t: scambia_pin(t, "K9", "2", "4"),
    # l'header del trim senza ritorno: nessun LED si accende
    "trim_led_senza_ritorno": lambda t: togli_pin(t, "J5", "4"),
    # --- ADR-030 punto 2: i LED del guadagno --------------------------------
    # i pin +3 e +10 scambiati sull'header
    "gain_led_3_10_scambiati": lambda t: scambia_pin(t, "J6", "2", "3"),
    # l'anodo +3 su una rete di segnale (il COM del polo 1 di K1, R_g3 del canale L)
    "gain_led_su_segnale": lambda t: sposta(t, "J6", "2", rete_di(t, "K1", "3")),
    # --- F11: il LED di mute -----------------------------------------------
    # alimentato da VRELAY: sempre acceso, non legge niente
    "led_mute_da_vrelay": lambda t: sposta(t, "R3", "1", "VRELAY"),
    # letto dal NO di K6 (VHOLD): acceso fuori mute, cioe' al contrario
    "led_mute_da_vhold": lambda t: sposta(t, "R3", "1", "VHOLD"),
    # letto dal comando invece che da un contatto
    "led_mute_dal_comando": lambda t: sposta(t, "R3", "1", "MUTE_CMD"),
}


def corri(path):
    r = subprocess.run(["/usr/bin/python3", CHK, path], capture_output=True, text=True)
    return r.returncode, r.stdout


def main(argv):
    vera, main_net, out = argv[1], argv[2], argv[3]
    os.makedirs(out, exist_ok=True)
    righe = ["variante,rc_atteso,rc,esito,prima_riga"]
    testo = open(vera).read()
    casi = [("vera", vera, 0), ("main_prima_di_L35", main_net, 1)]
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
