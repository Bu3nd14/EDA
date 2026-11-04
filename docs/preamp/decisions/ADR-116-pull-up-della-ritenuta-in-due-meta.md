# ADR-116 — I pull-up di AT_MRQ e di AT_ON in due metà in serie: un corto non mette più i 5 V sull'anodo della ritenuta

Data: 2026-11-04 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Modifica ADR-102** (il temporizzatore a comparatori, punto 2): il pull-up di AT_MRQ (200 kΩ, R572) diventa
  **R572 + R588, 100 kΩ + 100 kΩ**; quello di AT_ON = VRELAY_EN (10 kΩ, R576) diventa **R576 + R589,
  4,99 kΩ + 4,99 kΩ** (9,98 kΩ). I valori totali e i tempi di ADR-102 / ADR-105 non cambiano.
- Il rimedio di **NC-079** (L68, maggiore, prima di G1), che ADR-115 non decideva.
- Non tocca ADR-103 (R585), ADR-104 / ADR-105 (i diodi e i condensatori di temporizzazione), ADR-115.

## Contesto

L68 ha trovato (NC-079) che con **R572** o **R576** in corto, e poi un rail che cade (in musica o
all'accensione), la ritenuta Q513 / Q514 scatta col suo anodo su AT_ON, che il corto ha messo sui 5 V
senza resistenza (direttamente per R576, attraverso D537 per R572). L69 (`data/2026-11-03/L69/`, report
`reports/2026-11-04-L69-ritenuta.md`) ha misurato il meccanismo con la potenza piedino per piedino:
U504 al limite di 0,25 A, **205 / 218 °C** (limite 125); **Q513 0,20 / 0,22 W e Q514 0,19 / 0,22 W, fino a
149 °C** (403 K/W, 60 °C d'aria; Tj max 150), **259 mA di picco** d'emettitore contro i 200 mA del datasheet;
i 5 V a 2,62 / 1,78 V. (L68 stimava Q513 0,37 W e Q514 0,07 W: la somma è quella, la divisione no.)

## Le opzioni misurate

Sul banco di L68, con le opzioni come aggiunte al solo banco (`--l69ra`, `--l69rd`, `--serie2`), a 60 °C
d'aria; i due corti col rail − che cade, e a circuito sano gli otto eventi (criteri di L54b3b contro
`L64b/an_l64b.csv`); per le due opzioni finali anche a rete −10 % / +10 % e col comparatore a 2,2 V.

| Opzione | Parti in più | Q513 / Q514 / U504 col corto, a rete ±10 % | Che cosa fa la ritenuta col corto |
|---|---|---|---|
| A — resistenza in serie all'anodo (220 Ω … 2,2 kΩ; a 1 kΩ) | 1 | 61 / 68 / 64–77 °C, 4 mA | Scatta ma **non tira giù AT_ON** (il corto lo tiene a 4,7–5 V): musica fuori, **K501 resta chiuso**, i rail a 15 V col rail guasto |
| B — R576 in due metà + 1 kΩ in serie a D537 | 2 | 60 / 61 / 62–78 °C | R576: come il circuito sano. R572: **K501 resta chiuso** (AT_MRQ inchiodato ai 5 V tiene il permesso e AT_MT) |
| **C — R572 e R576 ciascuno in due metà** | **2** | **60 / 60 / 62 °C, 6 mA di picco** | **Come il circuito sano**: AT_ON a 0,70–0,72 V, K501 aperto a 129,4 / 132,6 ms (76–77 ms dopo il permesso, ≥ 50) |

Con A e C tutti gli eventi sani restano dentro i criteri: otto a rete nominale; accensione, perdita, buco
di 20 ms, spegnimento, inserimento e il guasto a ±10 %; accensione e accensione a freddo col comparatore a
2,2 V. B è dominata da C (le stesse due parti, R572 non risolto).

## Decisione

L'utente (2026-11-04), con le due opzioni davanti coi numeri: **«Due metà per pull-up»** (C).

- R572 100 kΩ (5 V → AT_MRQ_M) + **R588** 100 kΩ (AT_MRQ_M → AT_MRQ).
- R576 4,99 kΩ (5 V → AT_ON_M) + **R589** 4,99 kΩ (AT_ON_M → AT_ON). 4,99 kΩ è il valore E96 più vicino a
  metà di 10 kΩ; il totale, 9,98 kΩ, sta nella tolleranza dell'1 %.

## Conseguenze

- Un corto di una metà qualsiasi lascia l'altra: il circuito fa quello che fa sano, compresa la ritenuta
  dopo un guasto dei rail con la rete presente (P9 (b)). Il corto di **tutte e due** le metà è un doppio
  guasto, fuori dalla FMEA a guasto singolo.
- Una metà aperta è quello che era il pull-up aperto (R572 / R576 aperte di L68): le righe di R588 / R589
  aperte valgono quelle.
- Due resistenze in più sull'alimentatore (189 parti); lo schema completo ridisegnato (le due coppie in
  cima alle colonne di U514 e U515).
- Le corse del temporizzatore di L68 rifatte sul sorgente nuovo; le righe di R572 / R576 riscritte e quelle
  di R588 / R589 aggiunte nella FMEA (la settima fonte di `fmea_oggi.csv`). NC-079 chiusa.
