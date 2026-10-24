# L45d2b3b3 — la sintesi della FMEA della scheda audio dopo i rimedi (2026-10-24)

Lotto **L45d2b3b3**, l'ultima parte di L45d2b3 (NC-042). Dati `data/2026-10-24/L45d2b3b3/` (README);
decisione **ADR-100**. **NC-042 chiusa**; NC-072 avanza. Il circuito non cambia; `run_tests.sh` **15 / 0**.
In una sessione, senza dividere.

## Che cosa si è fatto

1. **Le regole sul caso noto, prima dei numeri.** `script/regole.py` usa la matrice, le classi e i
   tassi di L45d1 (`motore.py`, `tipi.py`, importati). `script/verifica.py` le applica alle righe già
   pubblicate e ridà le loro colonne: la priorità delle 469 righe di L45d1, quella dopo ADR-071 delle
   173 di L45d2a, la gravità delle 112 del blocco, FIT e probabilità delle quattro tabelle. **0 diverse**;
   col sabotaggio (la matrice, l'obiettivo a 10 mV, i tassi × 3) **506 diverse**.
2. **Una corsa che mancava.** I modi delle cinque parti di ADR-099 avevano il calore (L45d2b3b2b2) ma
   non la Stax, e tre portano il blocco al rail. Il banco di `genera_stax_lunghi.py` di L45d2b3b2b2,
   provato prima su tre suoi casi: **86,4 / 124,5 / 113,7 ms, uguali**, deck e copia guasta uguali salvo
   titolo e percorso. Poi 44 corse (11 modi × A / F2 × C nominale / +5 %), tutte `ok`:
   - **Q193 in corto C-E, R192 aperta, R194 aperta: 115,5–124,0 ms** sopra 0,87 V sulla Stax (il
     peggiore R194 aperta in F2 col +5 %), dentro i 150 ms e anche i 125 ms del testo di PR-30;
   - gli altri otto modi 0 ms.
3. **Le colonne dopo il rimedio**, riga per riga (`script/dopo.py`, `fmea_dopo.csv`):
   - **le 469 righe delle tabelle di L45**: le 112 del blocco tutte dall'ultimo banco che le ha corse;
     le righe dei rimedi dell'alimentatore dalle corse sul sorgente di L45d2b2b1 / b2; quelle dei relè
     da L45d2b3b1; le accettate, quelle alla diagnosi e a G2 come prima, con la loro destinazione; 275
     basse che nessun rimedio tocca, invariate;
   - **70 righe nuove**: le parti aggiunte dopo L45 (il blocco: D154–D159, R150–R153, R160, le cinque di
     ADR-099; l'alimentatore: le parti di ADR-093 / ADR-094), 61 misurate e **9 a calcolo** — i modi che
     nessun banco ha corso, scritti come tali.

## I numeri

| | alta | media | bassa | esclusa |
|---|---|---|---|---|
| Le tabelle di L45, **prima** (dopo ADR-071) | 100 | 56 | 313 | — |
| Le tabelle di L45, **dopo** | **23** | 63 | 382 | 1 |
| Le parti nuove | 3 | 8 | 59 | — |
| **Tutte, dopo** | **26** | **71** | 441 | 1 |

Le righe di riferimento, sul circuito di oggi:

| Guasto | Prima | Dopo |
|---|---|---|
| Il finale PNP in corto (l'NPN si scalda) | 5, alta | **3, media**: l'NPN 99 °C col dissipatore; la Stax 119,4 ms |
| Il finale NPN in corto | 5, alta | **3, media**: il PNP 95 °C; la Stax 123,9 ms |
| D102 aperto | 5, alta | **3, bassa**: il VAS 123 °C (119 coi dispositivi a 60 °C); la Stax 91,5 ms |
| R126 in corto | 5, alta | **3, media**: il VAS 124 °C; la Stax 72,2 ms |
| Il moltiplicatore di Vbe (4 modi) | 5, alta | **3, media**: i finali 97–98 °C (ADR-090) |
| C145 in corto | 5, alta | **5, alta**: l'impulso in R144 / R152, NC-075 |

### Le 26 righe alte, e dove vanno

| Destinazione | righe | che cosa |
|---|---|---|
| accettate | 11 | la riserva del firmware a 2,2 ms coi sorveglianti ciechi (ADR-073, 10); C536 in corto, il regolatore dei 5 V a 2,99 W che si spegne da sé (ADR-097, 2) |
| alla diagnosi (L58) | 8 | il mute che non si inserisce: il NO di mute saldato e il transistor del mute in corto, poi allo spegnimento, alla perdita di rete o a un regolatore spento (ADR-076) |
| alla scelta della parte | 4 | NC-073: C509 / C510 in corto, R550 / R551 a ~83 W e 5,7–7,2 J; la bobina di K501 in corto, R552 a 2,7 W per ~0,2 s (176 °C). NC-075: C145 in corto |
| a G2 | 1 | il fusibile F501 (L45d2a) |
| **nuove, senza destinazione** | **2** | **R550 / R551 in corto** (calcolo): il regolatore torna dov'era prima di ADR-092 |

Le 71 medie: 30 alla diagnosi (il degrado silenzioso del blocco, ADR-071, e il mute che non si
inserisce allo spegnimento, ADR-076), 16 accettate (ADR-077, ADR-082, le invariate di L45d2a), 11 del
blocco al rail che sulla principale e sulla fissa 1 contano sulla protezione a valle (ADR-081) e sulla
Stax stanno entro 150 ms (gravità 3 con probabilità 3, o latenti), 13 guasti del blocco sotto il tetto
ma latenti, gravità 3 per pochi mV al jack — i quattro del moltiplicatore di Vbe (~76 dB SPL), R129
aperta e otto delle parti nuove (D158 / D159 in corto, Q193 base-emettitore, R151, R152, R190, R192) —,
1 a G2 (il pin di massa di J1). Le 13 latenti non hanno un rimedio chiesto: sono della stessa specie dei
28 di ADR-071, e L58 le trova nella tabella insieme a quelle.

## La domanda all'utente, e la risposta

R550 / R551 in corto: il regolatore a **91,6 / 113,7 / 135,9 °C** (+) e **91,6 / 114,4 / 137,2 °C**
(−) a rete −10 / 0 / +10 %, 60 °C d'aria, R_thJA del costruttore (`data/2026-10-20/L45d2b2a/rpre.csv`,
0 Ω), contro 125 °C; latente, ~0,025 FIT. Sdoppiare non basta: con una metà da 2,2 Ω in corto 129–130 °C
a +10 %. L'utente: **«Nel rame del layout»** — a NC-072, il rame va dimensionato anche senza la
resistenza. La soglia che NC-072 chiede già, ≤ 27 °C/W, dà **124 °C** a 0 Ω (121 °C con lo Schottky in
serie): dentro, con ~1 °C di margine; ADR-100 ne fa un vincolo.

La chiusura, coi numeri sopra: **«Chiudere, residui alle loro voci»** → **NC-042 chiusa** (ADR-100).

## Che cosa la sintesi non dice

- **275 righe sono del circuito di L45** (le basse dei controlli, dei rail e del comando che nessun
  rimedio ha toccato): non rifatte. Il «Da riaprire se» di ADR-100 le copre.
- **Le righe del blocco non fra i quindici** hanno il calore del blocco di L45d2b3b1 (prima di ADR-097 e
  ADR-099): i due rimedi abbassano le correnti dei guasti, non le alzano (ADR-099, «Da riaprire se» di
  ADR-097), e nessuna di quelle righe era oltre i limiti. Non rimisurate sul sorgente.
- **La Stax dei modi mai corsi su di lei** (lontani dal tetto anche a vuoto col 4,7 µF in L45b) non è
  stata corsa: `dopo.py` rifiuta un modo che a vuoto superava 0,87 V e non ha una corsa sulla Stax.
- **9 righe sono a calcolo**: R550 / R551, C507 / C508 aperti e in corto, R552 in corto, C536 aperto,
  D513 / D514 aperti.
- **I tassi** restano la stima dichiarata di L45c2 / L45d1 («No, stima dichiarata»).
- **Le cifre di distorsione** non entrano: la FMEA guarda colpi, continua e calore.

## Prossimo

**L57**, l'ingresso protetto per l'RCA a caldo (NC-059), nell'ordine deciso con l'utente dopo
L45d2b3b2a: L57 → L54 → L55 → L58 → L64 (il dossier) → L65 (la revisione) → G1.
