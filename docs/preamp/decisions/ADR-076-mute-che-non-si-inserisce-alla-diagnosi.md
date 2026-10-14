# ADR-076 — Il mute che non si inserisce: lo rivela il firmware, e la realizzazione va al lotto della diagnosi

Data: 2026-10-14 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- È la **scelta 5** di `data/2026-10-14/L45d1/scelte_L45d2.pdf` (8 righe alte, 2 medie, L45c1 e
  L45c2).
- Il rimedio è una diagnosi, e la sua realizzazione va a **L58** (test point e autodiagnosi dei
  guasti latenti). Qui si sceglie soltanto.

## Contesto

Q501 in corto fra drain e source, Q501 con gate e drain in corto, o il contatto NO di un relè di
mute (K2–K4) saldato: al guasto non succede niente, e la musica continua. Allo spegnimento o alla
perdita di rete, però, il jack resta collegato: 0,27 V (~102 dB SPL a 1 m), e fino a **3,6 V**
(~125 dB SPL, sopra il tetto per 549 ms) se poi si spegne un regolatore. Il LED rosso guarda il
comando, non il jack, e quindi non lo vede (ADR-028). Sono guasti latenti: per sentirli serve un
secondo evento.

## Decisione

Parole dell'utente (2026-10-14): «Rivelarlo, alla diagnosi».

**Il firmware rivela il mute che non si inserisce**: legge `MUTE_CMD` (o il jack), e se il mute non
segue il comando stacca la linea dei relè alla scheda audio con Q505, e lo segnala. Come leggere
(quale nodo, quando, con quale soglia) e come segnalarlo lo decide **L58**. Il circuito del mute non
cambia.

## Perché

- **Sono guasti latenti, quindi il punto è vederli.** Una volta visto, il guasto si ripara prima
  che arrivi il secondo evento.
- **PR-24 regge**: il guasto singolo del mute non dà colpi, quindi la sicurezza contro di esso non
  dipende dal firmware. Il firmware interviene sul doppio evento.
- **Costa poco nel circuito**: un ingresso del micro e una lettura, e il firmware fa già da
  riserva per i rail (ADR-073).

## Alternative scartate

- **La ridondanza nel circuito** (relè di mute con un contatto in serie che il guasto non salda,
  due interruttori in serie sul comando del jack): toglie il guasto invece di vederlo, ma raddoppia
  relè e transistor del mute sulla scheda audio. L'utente non l'ha scelta.
- **Accettarlo**: avrebbe lasciato un colpo fino a ~125 dB SPL in attesa del secondo evento,
  invisibile.

## Da riaprire se

- L58 trova che il firmware non può leggere il mute in modo affidabile (un nodo che non si raggiunge,
  un falso positivo con la musica): si torna all'utente con la ridondanza nel circuito.
- Il riesame del micro (L54) toglie a Q505 la possibilità di staccare la linea dei relè.
