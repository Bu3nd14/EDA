#!/usr/bin/env python3
"""stati.py : le dieci righe `Stato:` di L51c, scelte dall'utente il 2026-10-10 una per una.

    /usr/bin/python3 docs/preamp/data/2026-10-10/L51c/script/stati.py

Scrive la stessa frase nella riga «Data: ... · Stato: ...» del file della decisione e
nell'ultima cella della sua riga in decisions/README.md (il punto 14 del generatore le
vuole uguali). Tocca solo quelle due righe per ADR; rifiuta se una riga non si trova.
Rieseguirlo non cambia niente.

Le frasi: tre sono state riscritte su richiesta dell'utente («troppe referenze e acronimi
[...] rendila piú parlante» per il trim; «anche questa rendila piú chiara» per il mute
graduale; «non si capisce, rendila comprensibile» per il mute coi rele'), e la soglia del
gradino si dice in dB («le soglie devono sempre essere in dB non in V»: 100 µV sono
33,4 dB SPL di picco a 1 m con la catena di NC-028).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
DEC = os.path.join(REPO, "docs", "preamp", "decisions")

STATI = {
    "009": "accettata — la clausola «nessun microcontrollore in tutto il progetto» è superata da "
           "ADR-022; l'attenuatore a scatti è superato da ADR-065 (un potenziometro col "
           "bilanciamento); gli ingressi a relè sono realizzati da ADR-064; niente telecomando resta",
    "027": "accettata — i LED del trim leggono lo stato dei relè stessi (ADR-033); il relè del trim "
           "si muove solo dopo che i relè del jack hanno staccato l'uscita (ADR-045); dopo il trim "
           "ora c'è un condensatore, poi il volume e il bilanciamento (ADR-065)",
    "032": "accettata — la soglia vale circa 33 dB SPL di picco a 1 m, sotto il rumore di una "
           "stanza silenziosa. Da allora: con la musica che suona un gradino non si giudica "
           "(ADR-036); a mute inserito con la musica conta quello che passa davvero al jack "
           "(ADR-063); il taglio della musica non ha più una soglia: il mute taglia, e il clic si "
           "misura e si dichiara (ADR-062)",
    "038": "superata da ADR-062: il mute non abbassa più la musica piano con le fotoresistenze, la "
           "taglia di colpo coi relè al jack; i relè al jack, decisi qui, restano",
    "039": "superata da ADR-062: le fotoresistenze, il loro connettore fra le schede e la sfumatura "
           "di 6 s non ci sono più; il mute taglia coi relè",
    "040": "superata da ADR-062: senza sfumatura non c'è più da giudicare quanto in fretta scende la "
           "musica; il mute taglia di colpo, e il clic si misura e si dichiara",
    "049": "accettata — il pilota delle fotoresistenze e il convertitore che lo comandava sono tolti "
           "da ADR-062; restano il micro, i ritardi fatti in hardware e l'interruttore che in "
           "standby toglie l'alimentazione ai relè della scheda audio",
    "050": "superata da ADR-062: senza fotoresistenze non c'è più una corrente massima da fissare",
    "061": "superata da ADR-062: senza sfumatura non ci sono più il profilo di 3 s, il suo pilota né "
           "l'impronta propria della fotoresistenza",
    "062": "accettata — ADR-063 precisa solo come si misura: lo strascico a bassa frequenza che "
           "resta subito dopo il taglio fa parte del clic, e si dichiara con lui; a mute inserito si "
           "misura quello che arriva davvero all'uscita",
}


def main():
    names = {re.match(r"ADR-(\d{3})-", n).group(1): n for n in os.listdir(DEC)
             if re.match(r"ADR-\d{3}-.*\.md$", n)}
    idx_path = os.path.join(DEC, "README.md")
    with open(idx_path, encoding="utf-8") as f:
        idx = f.read().split("\n")
    for n, stato in STATI.items():
        p = os.path.join(DEC, names[n])
        with open(p, encoding="utf-8") as f:
            text = f.read()
        new, k = re.subn(r"^(Data: \S+ · Stato:) ?.*$", lambda m: f"{m.group(1)} {stato}",
                         text, count=1, flags=re.M)
        if k != 1:
            sys.exit(f"RIFIUTATO: ADR-{n}: riga Stato non trovata")
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
        rows = [i for i, ln in enumerate(idx) if ln.startswith(f"| [{n}](")]
        if len(rows) != 1:
            sys.exit(f"RIFIUTATO: ADR-{n}: {len(rows)} righe nell'indice")
        ln = idx[rows[0]]
        if not ln.endswith(" |"):
            sys.exit(f"RIFIUTATO: ADR-{n}: riga dell'indice senza la cella finale")
        head = ln[:-2]
        cut = head.rfind(" | ")
        idx[rows[0]] = head[:cut] + " | " + stato + " |"
        print(f"ADR-{n}: scritta")
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write("\n".join(idx))


if __name__ == "__main__":
    main()
