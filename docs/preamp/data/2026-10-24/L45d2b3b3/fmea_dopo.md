# NC-042 — la FMEA della scheda audio dopo i rimedi (L45d2b3b3)

Generata da `script/sintesi_dopo.py` da `fmea_dopo.csv` (`script/dopo.py`; le regole in `script/regole.py`, provate da `script/verifica.py` sulle colonne pubblicate di L45d1 e L45d2a). Le colonne «dopo» sono quelle di ADR-070 sul circuito di oggi; la fonte di ogni cifra e' in `fonte_dopo` nel CSV. Il picco e' al jack peggiore fra principale e fissa 1 (V e dB SPL di picco a 1 m); la Stax e' il tempo sopra 0,87 V col suo carico (P10, al piu' 150 ms: ADR-086 / ADR-089 / ADR-098).

## Quante righe, per priorita', prima e dopo il rimedio

| Lotto | righe | alta prima | media prima | bassa prima | **alta dopo** | **media dopo** | bassa dopo | esclusa |
|---|---|---|---|---|---|---|---|---|
| L45a | 112 | 57 | 34 | 21 | 1 | 44 | 67 | 0 |
| L45c1 | 78 | 16 | 7 | 55 | 9 | 4 | 65 | 0 |
| L45c2 | 215 | 20 | 11 | 184 | 13 | 11 | 191 | 0 |
| L45b | 64 | 7 | 4 | 53 | 0 | 4 | 59 | 1 |
| nuove: blocco | 33 | 0 | 0 | 0 | 0 | 8 | 25 | 0 |
| nuove: alimentatore | 37 | 0 | 0 | 0 | 3 | 0 | 34 | 0 |
| **tutte** | 539 | 100 | 56 | 313 | 26 | 71 | 441 | 1 |

Le righe nuove non hanno un «prima»: sono le parti aggiunte dopo L45 (il blocco: ADR-086, 087, 090, 095, 097, 099; l'alimentatore: ADR-091…094), misurate, e i modi che nessun banco ha corso, a calcolo.

## Dove va ogni riga

| Destinazione | righe | alta | media | bassa |
|---|---|---|---|---|
| accettata | 27 | 11 | 16 | 0 |
| alla diagnosi (L58) | 46 | 8 | 30 | 8 |
| NC-073 | 3 | 3 | 0 | 0 |
| NC-072 | 2 | 2 | 0 | 0 |
| NC-075 | 1 | 1 | 0 | 0 |
| a G2 | 3 | 1 | 1 | 1 |
| nel circuito (rimedio costruito, misurata) | 172 | 0 | 24 | 148 |
| esclusa (ADR-085) | 1 | 0 | 0 | 0 |
| invariata (riga di L45) | 275 | 0 | 0 | 275 |
| nel circuito (calcolo) | 9 | 0 | 0 | 9 |

## Priorita' alta dopo il rimedio (26)

| Lotto | Parte | Funzione | Modo | G prima | priorita' prima | G | P | R | dB SPL | Stax ms | Tj C | Stato | Effetto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| alimentatore | R550 | 4,7 Ohm davanti al regolatore + (ADR-092) | corto |  |  | 5 | 1 | 3 |  |  |  | NC-072 (il rame al layout anche senza la resistenza, ADR-100) | CALCOLO, non simulato: torna il caso prima di ADR-092: il regolatore + a 91,6 / 113,7 / 135,9 C a rete -10 / 0 / +10 %, 60 C d'aria (L45d2b2a/rpre.csv, 0 ohm), senza un segno |
| alimentatore | R551 | 4,7 Ohm davanti al regolatore - (ADR-092) | corto |  |  | 5 | 1 | 3 |  |  |  | NC-072 (il rame al layout anche senza la resistenza, ADR-100) | CALCOLO, non simulato: torna il caso prima di ADR-092: il regolatore - a 91,6 / 114,4 / 137,2 C a rete -10 / 0 / +10 %, 60 C d'aria (L45d2b2a/rpre.csv, 0 ohm), senza un segno |
| L45c1 | C509 | il secondario, il ponte e i serbatoi | corto | 4 | media | 5 | 1 | 1 |  |  |  | NC-073 (alla scelta della parte) | il sorvegliante muta, il jack prima del crollo (~32 dB SPL, ADR-093); R550 / R551 al piu' 83.1 W, 7.21 J: l'impulso di NC-073 |
| L45c1 | C510 | il secondario, il ponte e i serbatoi | corto | 5 | alta | 5 | 1 | 1 |  |  |  | NC-073 (alla scelta della parte) | il sorvegliante muta, il jack prima del crollo (~32 dB SPL, ADR-093); R550 / R551 al piu' 82.9 W, 5.73 J: l'impulso di NC-073 |
| L45c2 | K501 | il rele' di rete | bobina in corto | 5 | alta | 5 | 2 | 1 |  |  |  | NC-073 (alla scelta della parte) | le parti del comando e dei 5 V al piu' 176.1 C a 100 ms; oltre: RK (47 ohm, 2 W) (176.1 C): NC-073 |
| L45a | C145 | condensatore della cella RC (1000 uF) | corto | 5 | alta | 5 | 3 | 2 | 137.0 | 123.6 | 68 | NC-075 (alla scelta della parte) | Tj max a 60 C 68 C; principale 15 V (137.0 dB SPL), fissa 1 14.8 V; Stax 123.6 ms sopra 0,87 V; oltre: R144 / R152 ~1,3 J in ~0,25 s (NC-075, alla scelta della parte); principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45c2 | F501 | la linea dei rele' (VRELAY_REG) | in corto (o sovradimensionato) | 5 | alta | 5 | 2 | 3 |  |  |  | a G2 (L45d2a) | come prima: il rimedio non e' nel circuito |
| alimentatore | C536 | fra i due regolatori dei 5 V (ADR-094) | corto |  |  | 5 | 1 | 2 |  |  |  | accettata (ADR-097, 2): lo spegnimento termico del regolatore | i 5 V persi (V5 al piu' basso 0.00479 V): il micro si spegne, i rele' cadono; le parti al piu' 246 C a 100 ms; oltre: U504 (MCP1703A) |
| L45c2 | C516 | il sorvegliante dei rail | corto | 4 | alta | 4 | 1 | 3 |  |  |  | accettata (ADR-073) | come prima: accettato |
| L45c2 | R504 | il riferimento | corto | 4 | alta | 4 | 1 | 3 |  |  |  | accettata (ADR-073) | come prima: accettato |
| L45c2 | R505 | il riferimento | aperto | 4 | alta | 4 | 1 | 3 |  |  |  | accettata (ADR-073) | come prima: accettato |
| L45c2 | R506 | il sorvegliante dei rail | corto | 4 | alta | 4 | 1 | 3 |  |  |  | accettata (ADR-073) | come prima: accettato |
| L45c2 | R507 | il sorvegliante dei rail | aperto | 4 | alta | 4 | 1 | 3 |  |  |  | accettata (ADR-073) | come prima: accettato |
| L45c2 | R508 | il sorvegliante dei rail | aperto | 4 | alta | 4 | 1 | 3 |  |  |  | accettata (ADR-073) | come prima: accettato |
| L45c2 | R509 | il sorvegliante dei rail | corto | 4 | alta | 4 | 1 | 3 |  |  |  | accettata (ADR-073) | come prima: accettato |
| L45c2 | U505 | il sorvegliante dei rail | canale A cieco (uscita aperta), poi U501 spento | 4 | alta | 4 | 2 | 3 |  |  |  | accettata (ADR-073) | come prima: accettato |
| L45c2 | U505 | il sorvegliante dei rail | canale B cieco (uscita aperta), poi U502 spento | 4 | alta | 4 | 2 | 3 |  |  |  | accettata (ADR-073) | come prima: accettato |
| L45c2 | U505 | il sorvegliante dei rail | alimentazione (pin 8) aperta | 4 | alta | 4 | 1 | 3 |  |  |  | accettata (ADR-073) | come prima: accettato |
| L45c1 | K2-K4 | il mute che non si inserisce | NO saldato, poi lo spegnimento | 4 | alta | 4 | 2 | 3 |  |  |  | alla diagnosi, L58 (ADR-076) | come prima: il rimedio non e' nel circuito |
| L45c1 | K2-K4 | il mute che non si inserisce | NO saldato, poi la perdita di rete | 4 | alta | 4 | 2 | 3 |  |  |  | alla diagnosi, L58 (ADR-076) | come prima: il rimedio non e' nel circuito |
| L45c1 | K2-K4 | il mute che non si inserisce | NO saldato, poi U502 spento | 4 | alta | 4 | 2 | 3 |  |  |  | alla diagnosi, L58 (ADR-076) | come prima: il rimedio non e' nel circuito |
| L45c1 | K2-K4 | il mute che non si inserisce | NO saldato, poi U501 spento | 4 | alta | 4 | 2 | 3 |  |  |  | alla diagnosi, L58 (ADR-076) | come prima: il rimedio non e' nel circuito |
| L45c1 | Q501 | il mute che non si inserisce | corto D-S, poi la perdita di rete | 4 | alta | 4 | 2 | 3 |  |  |  | alla diagnosi, L58 (ADR-076) | come prima: il rimedio non e' nel circuito |
| L45c1 | Q501 | il mute che non si inserisce | corto D-S, poi U502 spento | 4 | alta | 4 | 2 | 3 |  |  |  | alla diagnosi, L58 (ADR-076) | come prima: il rimedio non e' nel circuito |
| L45c1 | Q501 | il mute che non si inserisce | corto D-S, poi U501 spento | 4 | alta | 4 | 2 | 3 |  |  |  | alla diagnosi, L58 (ADR-076) | come prima: il rimedio non e' nel circuito |
| L45c2 | Q501 | il comando del jack (MUTE_CMD) | corto G-D, poi la perdita di rete | 4 | alta | 4 | 1 | 3 |  |  |  | alla diagnosi, L58 (ADR-076) | come prima: il rimedio non e' nel circuito |

## Priorita' media dopo il rimedio (71)

| Lotto | Parte | Funzione | Modo | G prima | priorita' prima | G | P | R | dB SPL | Stax ms | Tj C | Stato | Effetto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L45c1 | J1 | il cablaggio dei rail fra le due schede | pin 2 (GND) aperto | 4 | media | 4 | 1 | 2 |  |  |  | a G2 (L45d2a) | come prima: il rimedio non e' nel circuito |
| L45b | C_OUT 4,7 µF (fisse) | il percorso del segnale (condensatori, bleed, resistenze) | corto | 3 | media | 3 | 2 | 3 | 68.8 |  |  | accettata (ADR-082): col blocco al rail dopo e' un doppio guasto | da solo -0.005824 V alla Stax; col blocco al rail poi e' un doppio guasto accettato (ADR-082) (68.8 dB SPL) |
| L45b | C_OUT 4,7 µF (principale) | il percorso del segnale (condensatori, bleed, resistenze) | corto | 3 | media | 3 | 1 | 3 | 68.8 |  |  | accettata (ADR-082): col blocco al rail dopo e' un doppio guasto | da solo -0.005824 V alla Stax; col blocco al rail poi e' un doppio guasto accettato (ADR-082) (68.8 dB SPL) |
| L45b | K1 (o K11), K5 (o K12) | il guadagno e la sua tenuta | bobina aperta durante l'ascolto, o l'ausiliario che cade (la tenuta si perde) | 3 | media | 3 | 3 | 2 |  |  |  | accettata (L45d2a: invariato) | come prima: accettato |
| L45b | R_SEL 470 kΩ | il percorso del segnale (condensatori, bleed, resistenze) | aperto | 3 | media | 3 | 2 | 3 |  |  |  | accettata (L45d2a: invariato) | come prima: accettato |
| L45c1 | C141 | il disaccoppiamento dei blocchi | corto | 3 | media | 3 | 3 | 1 |  |  |  | accettata (L45d2a: invariato) | come prima: accettato |
| L45c1 | C142 | il disaccoppiamento dei blocchi | corto | 3 | media | 3 | 3 | 1 |  |  |  | accettata (L45d2a: invariato) | come prima: accettato |
| L45c2 | C523 | la linea dei rele' (VRELAY_REG) | aperto, poi U503 spento | 3 | media | 3 | 2 | 3 |  |  |  | accettata (ADR-077) | come prima: accettato |
| L45c2 | C528 | il ritardo Delta in hardware | aperto, poi U503 spento | 3 | media | 3 | 1 | 3 |  |  |  | accettata (ADR-077) | come prima: accettato |
| L45c2 | C528 | il ritardo Delta in hardware | aperto, poi la perdita di rete | 3 | media | 3 | 1 | 3 |  |  |  | accettata (ADR-077) | come prima: accettato |
| L45c2 | C528 | il ritardo Delta in hardware | aperto (durante la musica) | 3 | media | 3 | 1 | 3 |  |  |  | accettata (ADR-077) | come prima: accettato |
| L45c2 | D520 | il ritardo Delta in hardware | corto, poi il mute dal tasto | 3 | media | 3 | 1 | 3 |  |  |  | accettata (ADR-077) | come prima: accettato |
| L45c2 | D520 | il ritardo Delta in hardware | corto, poi lo spegnimento | 3 | media | 3 | 1 | 3 |  |  |  | accettata (ADR-077) | come prima: accettato |
| L45c2 | D522 | il permesso (PERMIT_CMD) | corto, poi la perdita di rete | 3 | media | 3 | 1 | 3 |  |  |  | accettata (ADR-077) | come prima: accettato |
| L45c2 | D522 | il permesso (PERMIT_CMD) | corto, poi il mute dal tasto | 3 | media | 3 | 1 | 3 |  |  |  | accettata (ADR-077) | come prima: accettato |
| L45c2 | R524 | il ritardo Delta in hardware | aperto, poi il mute dal tasto | 3 | media | 3 | 1 | 3 |  |  |  | accettata (ADR-077) | come prima: accettato |
| L45c2 | U504 | la logica (V5) | spento (V5 persa) | 3 | media | 3 | 3 | 1 |  |  |  | accettata (ADR-077) | come prima: accettato |
| L45a | C104 | condensatore del riferimento (100 uF) | corto | 3 | media | 3 | 3 | 3 | 112.3 |  | 60 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 60 C; principale 0.875 V (112.3 dB SPL), fissa 1 0.678 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv); principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | C105 | condensatore del riferimento (100 nF) | corto | 3 | media | 3 | 2 | 3 | 112.3 |  | 60 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 60 C; principale 0.875 V (112.3 dB SPL), fissa 1 0.678 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv); principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | C137 | condensatore di retroazione | corto | 3 | media | 3 | 2 | 3 | 70.0 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.00671 V (70.0 dB SPL), fissa 1 3.38e-08 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | D102 | diodo del riferimento (alto) | corto | 3 | media | 3 | 2 | 3 | 64.2 |  | 66 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 66 C; principale 0.00347 V (64.2 dB SPL), fissa 1 0.00111 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | D103 | diodo del riferimento (basso) | corto | 3 | media | 3 | 2 | 3 | 64.2 |  | 66 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 66 C; principale 0.00347 V (64.2 dB SPL), fissa 1 0.00111 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | Q117 | cascode, lato segnale | corto C-E | 3 | media | 3 | 2 | 3 | 88.3 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0554 V (88.3 dB SPL), fissa 1 0.0178 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | Q118 | cascode, lato retroazione | corto C-E | 3 | media | 3 | 2 | 3 | 88.5 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0564 V (88.5 dB SPL), fissa 1 0.0182 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | Q125 | carico del VAS (DZT5551) | corto B-E | 3 | media | 3 | 3 | 3 | 113.1 | 0.0 | 60 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 60 C; principale 0.964 V (113.1 dB SPL), fissa 1 0.417 V; Stax 0.0 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | Q127 | moltiplicatore di Vbe | corto C-E | 3 | media | 3 | 2 | 3 | 81.7 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0259 V (81.7 dB SPL), fissa 1 0.00834 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | Q132 | finale NPN (MJE15032) | corto B-E | 3 | media | 3 | 3 | 3 | 87.9 |  | 115 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 115 C; principale 0.0531 V (87.9 dB SPL), fissa 1 0.0169 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | Q132 | finale NPN (MJE15032) | aperto | 3 | media | 3 | 3 | 3 | 78.7 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0184 V (78.7 dB SPL), fissa 1 0.00586 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | Q133 | finale PNP (MJE15033) | corto B-E | 3 | media | 3 | 3 | 3 | 89.5 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0636 V (89.5 dB SPL), fissa 1 0.0396 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | Q133 | finale PNP (MJE15033) | aperto | 3 | media | 3 | 3 | 2 | 79.1 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0191 V (79.1 dB SPL), fissa 1 0.00602 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | Q148 | transistor di aiuto dello specchio | corto B-E | 3 | media | 3 | 2 | 3 | 96.9 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.148 V (96.9 dB SPL), fissa 1 0.0469 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R111 | degenerazione, lato segnale | corto | 3 | media | 3 | 1 | 3 | 111.1 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.762 V (111.1 dB SPL), fissa 1 0.241 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R112 | degenerazione, lato retroazione | corto | 3 | media | 3 | 1 | 3 | 111.1 | 0.0 | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.759 V (111.1 dB SPL), fissa 1 0.24 V; Stax 0.0 ms sopra 0,87 V |
| L45a | R115 | riferimento dei cascode (basso) | aperto | 3 | media | 3 | 2 | 3 | 78.1 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0171 V (78.1 dB SPL), fissa 1 0.00577 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R123 | emettitore del VAS (56) | corto | 3 | media | 3 | 1 | 3 | 80.4 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0222 V (80.4 dB SPL), fissa 1 0.00713 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R128 | moltiplicatore di Vbe (alto) | corto | 3 | media | 3 | 1 | 3 | 78.2 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0173 V (78.2 dB SPL), fissa 1 0.00544 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R130 | stopper di base del finale NPN | aperto | 3 | media | 3 | 2 | 3 | 76.0 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0134 V (76.0 dB SPL), fissa 1 0.00427 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R131 | stopper di base del finale PNP | aperto | 3 | media | 3 | 2 | 3 | 75.0 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.012 V (75.0 dB SPL), fissa 1 0.00383 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R134 | emettitore del finale NPN (22) | aperto | 3 | media | 3 | 2 | 3 | 78.7 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0184 V (78.7 dB SPL), fissa 1 0.00588 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R134 | emettitore del finale NPN (22) | corto | 3 | media | 3 | 1 | 3 | 74.4 |  | 96 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 96 C; principale 0.0112 V (74.4 dB SPL), fissa 1 0.0035 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R135 | emettitore del finale PNP (22) | corto | 3 | media | 3 | 1 | 3 | 74.7 |  | 96 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 96 C; principale 0.0116 V (74.7 dB SPL), fissa 1 0.00365 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R136 | resistenza di retroazione | corto | 3 | media | 3 | 1 | 3 | 70.0 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.00671 V (70.0 dB SPL), fissa 1 3.38e-08 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R143 | ramo di guadagno +10 dB | aperto | 3 | media | 3 | 1 | 3 | 68.1 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0054 V (68.1 dB SPL), fissa 1 1.27e-09 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R144 | resistenza della cella RC (10) | corto | 3 | media | 3 | 1 | 3 | 63.3 | 0.0 | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.00311 V (63.3 dB SPL), fissa 1 0.00102 V; Stax 0.0 ms sopra 0,87 V |
| L45a | R147 | resistenza dell'inseguitore | aperto | 3 | media | 3 | 2 | 3 | 74.7 |  | 87 | alla diagnosi, L58 (ADR-071) | Tj max a 60 C 87 C; principale 0.0115 V (74.7 dB SPL), fissa 1 0.0037 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45c1 | Q501 | il mute che non si inserisce | corto D-S, poi lo spegnimento | 3 | media | 3 | 2 | 3 |  |  |  | alla diagnosi, L58 (ADR-076) | come prima: il rimedio non e' nel circuito |
| L45c2 | Q501 | il comando del jack (MUTE_CMD) | corto G-D, poi lo spegnimento | 3 | media | 3 | 1 | 3 |  |  |  | alla diagnosi, L58 (ADR-076) | come prima: il rimedio non e' nel circuito |
| L45a | C116 | condensatore del riferimento dei cascode | corto | 4 | alta | 3 | 3 | 2 | 125.9 | 15.3 | 85 | nel circuito, rimisurata | Tj max a 60 C 85 C; principale 4.18 V (125.9 dB SPL), fissa 1 1.32 V; Stax 15.3 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | JQ110A | JFET d'ingresso, lato segnale | corto D-S | 5 | alta | 3 | 3 | 2 | 137.5 | 124.4 | 104 | nel circuito, rimisurata | Tj max a 60 C 104 C; principale 16 V (137.5 dB SPL), fissa 1 13.6 V; Stax 124.4 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | JQ110B | JFET d'ingresso, lato retroazione | corto D-S | 4 | alta | 3 | 3 | 2 | 137.0 | 123.6 | 73 | nel circuito, rimisurata | Tj max a 60 C 73 C; principale 15 V (137.0 dB SPL), fissa 1 14.8 V; Stax 123.6 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | Q122 | VAS (DZT5401) | corto B-E | 5 | alta | 3 | 3 | 2 | 137.0 | 123.6 | 68 | nel circuito, rimisurata | Tj max a 60 C 68 C; principale 15 V (137.0 dB SPL), fissa 1 14.8 V; Stax 123.6 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | Q122 | VAS (DZT5401) | corto C-E | 4 | alta | 3 | 3 | 2 | 139.0 | 123.9 | 107 | nel circuito, rimisurata | Tj max a 60 C 107 C; principale 19 V (139.0 dB SPL), fissa 1 14 V; Stax 123.9 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | Q122 | VAS (DZT5401) | aperto | 4 | alta | 3 | 3 | 2 | 136.9 | 123.6 | 68 | nel circuito, rimisurata | Tj max a 60 C 68 C; principale 15 V (136.9 dB SPL), fissa 1 14.8 V; Stax 123.6 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | Q125 | carico del VAS (DZT5551) | corto C-E | 5 | alta | 3 | 3 | 2 | 136.1 | 66.6 | 123 | nel circuito (ADR-099), rimisurata sul sorgente | Tj max a 60 C 123 C; principale 13.6 V (136.1 dB SPL), fissa 1 13.5 V; Stax 66.6 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | Q125 | carico del VAS (DZT5551) | aperto | 4 | alta | 3 | 3 | 2 | 112.8 | 0.0 | 91 | nel circuito, rimisurata | Tj max a 60 C 91 C; principale 0.929 V (112.8 dB SPL), fissa 1 0.403 V; Stax 0.0 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | Q127 | moltiplicatore di Vbe | corto B-E | 5 | alta | 3 | 2 | 3 | 76.0 |  | 97 | nel circuito, rimisurata | Tj max a 60 C 97 C; principale 0.0135 V (76.0 dB SPL), fissa 1 0.00423 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | Q127 | moltiplicatore di Vbe | aperto | 5 | alta | 3 | 2 | 3 | 76.2 |  | 97 | nel circuito, rimisurata | Tj max a 60 C 97 C; principale 0.0137 V (76.2 dB SPL), fissa 1 0.00432 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | Q132 | finale NPN (MJE15032) | corto C-E | 5 | alta | 3 | 3 | 2 | 140.0 | 123.9 | 95 | nel circuito (ADR-099), rimisurata sul sorgente | Tj max a 60 C 95 C; principale 21.4 V (140.0 dB SPL), fissa 1 14.7 V; Stax 123.9 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | Q133 | finale PNP (MJE15033) | corto C-E | 5 | alta | 3 | 3 | 2 | 136.8 | 119.4 | 99 | nel circuito (ADR-099), rimisurata sul sorgente | Tj max a 60 C 99 C; principale 14.6 V (136.8 dB SPL), fissa 1 14.6 V; Stax 119.4 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | R126 | emettitore del carico del VAS (56) | corto | 5 | alta | 3 | 1 | 3 | 136.7 | 72.2 | 124 | nel circuito (ADR-099), rimisurata sul sorgente | Tj max a 60 C 124 C; principale 14.6 V (136.7 dB SPL), fissa 1 14.5 V; Stax 72.2 ms sopra 0,87 V; principale e fissa 1 contano sulla protezione a valle (ADR-081) |
| L45a | R128 | moltiplicatore di Vbe (alto) | aperto | 5 | alta | 3 | 2 | 3 | 76.5 |  | 98 | nel circuito, rimisurata | Tj max a 60 C 98 C; principale 0.0142 V (76.5 dB SPL), fissa 1 0.00445 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R129 | moltiplicatore di Vbe (basso) | corto | 5 | alta | 3 | 1 | 3 | 76.0 |  | 97 | nel circuito, rimisurata | Tj max a 60 C 97 C; principale 0.0135 V (76.0 dB SPL), fissa 1 0.00423 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| L45a | R129 | moltiplicatore di Vbe (basso) | aperto | 2 | bassa | 3 | 2 | 3 | 76.2 |  | 87 | rimisurata, nessun rimedio chiesto | Tj max a 60 C 87 C; principale 0.0137 V (76.2 dB SPL), fissa 1 0.0043 V; Stax Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv) |
| blocco | D158 | diodo base-emettitore del finale NPN (ADR-095) | corto |  |  | 3 | 2 | 3 | 87.9 | 0.0 | 115 | nel circuito, misurata | Tj max a 60 C 115 C; principale 0.0531 V (87.9 dB SPL), fissa 1 0.0169 V; Stax 0.0 ms sopra 0,87 V |
| blocco | D159 | diodo base-emettitore del finale PNP (ADR-095) | corto |  |  | 3 | 2 | 3 | 89.5 | 0.0 | 87 | nel circuito, misurata | Tj max a 60 C 87 C; principale 0.0636 V (89.5 dB SPL), fissa 1 0.0396 V; Stax 0.0 ms sopra 0,87 V |
| blocco | Q193 | il limite di corrente del VAS, MMBT5401 (ADR-099) | corto B-E |  |  | 3 | 2 | 3 | 75.6 | 0.0 | 79 | nel circuito, misurata | Tj max a 60 C 79 C; principale 0.0128 V (75.6 dB SPL), fissa 1 0.00406 V; Stax 0.0 ms sopra 0,87 V |
| blocco | R151 | gemella della degenerazione di retroazione (ADR-086) | aperto |  |  | 3 | 2 | 3 | 111.1 | 0.0 | 87 | nel circuito, misurata | Tj max a 60 C 87 C; principale 0.759 V (111.1 dB SPL), fissa 1 0.24 V; Stax 0.0 ms sopra 0,87 V |
| blocco | R151 | gemella della degenerazione di retroazione (ADR-086) | corto |  |  | 3 | 1 | 3 | 111.1 | 0.0 | 87 | nel circuito, misurata | Tj max a 60 C 87 C; principale 0.759 V (111.1 dB SPL), fissa 1 0.24 V; Stax 0.0 ms sopra 0,87 V |
| blocco | R152 | gemella della resistenza della cella RC (ADR-086) | corto |  |  | 3 | 1 | 3 | 63.3 | 0.0 | 87 | nel circuito, misurata | Tj max a 60 C 87 C; principale 0.00311 V (63.3 dB SPL), fissa 1 0.00102 V; Stax 0.0 ms sopra 0,87 V |
| blocco | R190 | 10 kOhm sul collettore dell'aiuto dello specchio (ADR-099) | aperto |  |  | 3 | 2 | 3 | 97.1 | 0.0 | 79 | nel circuito, misurata | Tj max a 60 C 79 C; principale 0.152 V (97.1 dB SPL), fissa 1 0.0479 V; Stax 0.0 ms sopra 0,87 V |
| blocco | R192 | 22 Ohm, seconda parte della degenerazione del VAS (ADR-099) | corto |  |  | 3 | 1 | 3 | 72.0 | 0.0 | 79 | nel circuito, misurata | Tj max a 60 C 79 C; principale 0.00851 V (72.0 dB SPL), fissa 1 0.0027 V; Stax 0.0 ms sopra 0,87 V |

