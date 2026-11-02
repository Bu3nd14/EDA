#!/usr/bin/env python3
"""L64a: le righe `Stato:` scelte dall'utente il 2026-11-02 («Yes, use these sentences»).

    /usr/bin/python3 -I stati.py

Scrive la stessa frase nel file della ADR (la riga «Data: ... · Stato: ...») e nella terza cella
della sua riga in decisions/README.md (regola 2 dell'indice: della ADR vecchia si aggiorna solo
lo Stato). Aggiunge all'indice ADR-087, 088 e 089, che il controllo del contratto trovava
senza riga, col titolo del file. Rifiuta, senza scrivere, se una riga non e' trovata una volta.
"""
import glob
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
D = os.path.join(REPO, "docs", "preamp", "decisions")

STATI = {
    "048": "accettata — il punto 6, il temporizzatore col micro, è sostituito da un temporizzatore "
           "a comparatori (ADR-102); il resto vale",
    "049": "superata da ADR-102 (il temporizzatore a comparatori): il micro e il firmware non ci "
           "sono più, e il pilota delle fotoresistenze era già stato tolto (ADR-062); restano i "
           "ritardi fatti in hardware e l'interruttore che in standby toglie l'alimentazione ai "
           "relè della scheda audio",
    "072": "superata da ADR-081 (il rivelatore di continua esce dal progetto); le scelte 6, 8, 9 e "
           "10, che si appoggiavano a lui, sono rifatte senza (ADR-082)",
    "073": "superata da ADR-102 (il firmware esce): se il sorvegliante di un rail diventa cieco, il "
           "mute lo apre il temporizzatore a comparatori, in meno di mezzo millisecondo",
    "079": "superata da ADR-081 (il rivelatore di continua esce dal progetto); già prima, dove "
           "guardava e «la musica non lo fa scattare» erano cambiati (ADR-080)",
    "080": "superata da ADR-081 (il rivelatore di continua esce dal progetto)",
    "082": "accettata — il condensatore della Stax non va dopo il relè: resta prima, come prevedeva "
           "la riserva di questa decisione (ADR-084); il resto vale",
    "084": "accettata — il relè di mute della Stax non è a isolamento rinforzato ma supplementare "
           "(ADR-085); il resto vale",
    "087": "accettata — la media di V2 si corregge per quanto la media stessa attenua (ADR-088)",
    "088": "accettata",
    "089": "accettata — confermata dopo il cambio di R153 (ADR-098)",
    "099": "accettata — il limitatore del VAS passa a 36,5 + 18,7 Ω (ADR-111); il resto vale",
    "102": "accettata — completata dalle decisioni sul temporizzatore che seguono: la taratura dei "
           "comparatori e R585 (ADR-103), i diodi a bassa perdita e R571 (ADR-104, ADR-105), i "
           "condensatori dei ritardi (ADR-105, ADR-108)",
    "104": "accettata — completata da ADR-105: anche D534 a bassa perdita, e R571 da 1,1 MΩ",
    "105": "accettata — C548 e C552, i due condensatori da 1 µF dei ritardi, sono in film di "
           "polipropilene e non C0G (ADR-108): un C0G da 1 µF a montaggio superficiale non si "
           "trova; il resto vale",
}
NUOVE = ("087", "088", "089")

errori, file_nuovi = [], {}
idx_path = os.path.join(D, "README.md")
idx = open(idx_path, encoding="utf-8").read().split("\n")
for n, stato in STATI.items():
    assert "|" not in stato
    p = glob.glob(os.path.join(D, f"ADR-{n}-*.md"))
    if len(p) != 1:
        errori.append(f"ADR-{n}: {len(p)} file")
        continue
    t = open(p[0], encoding="utf-8").read()
    t2, k = re.subn(r"^(Data: \S+ · Stato: ).*$", lambda m: m.group(1) + stato, t, count=0,
                    flags=re.M)
    if k != 1:
        errori.append(f"ADR-{n}: riga Stato trovata {k} volte")
    file_nuovi[p[0]] = t2
    name = os.path.basename(p[0])
    righe = [i for i, l in enumerate(idx) if l.startswith(f"| [{n}](")]
    if n in NUOVE:
        if righe:
            errori.append(f"ADR-{n}: e' gia' nell'indice")
            continue
        titolo = re.match(r"# ADR-\d{3} — (.+)\n", t).group(1).strip()
        prima = [i for i, l in enumerate(idx) if re.match(r"^\| \[(\d{3})\]\(", l)
                 and int(re.match(r"^\| \[(\d{3})\]", l).group(1)) < int(n)]
        idx.insert(prima[-1] + 1, f"| [{n}]({name}) | {titolo} | {stato} |")
        continue
    if len(righe) != 1:
        errori.append(f"ADR-{n}: riga dell'indice trovata {len(righe)} volte")
        continue
    celle = idx[righe[0]].split(" | ")
    celle[-1] = stato + " |"
    idx[righe[0]] = " | ".join(celle)
if errori:
    print("RIFIUTATO:", *errori, sep="\n  - ", file=sys.stderr)
    sys.exit(1)
for p, t in file_nuovi.items():
    open(p, "w", encoding="utf-8").write(t)
open(idx_path, "w", encoding="utf-8").write("\n".join(idx))
print(f"{len(file_nuovi)} file e l'indice aggiornati; aggiunte all'indice: {', '.join(NUOVE)}")
