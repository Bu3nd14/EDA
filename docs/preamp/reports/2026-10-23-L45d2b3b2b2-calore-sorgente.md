# L45d2b3b2b2 — il calore sul blocco del sorgente (2026-10-23)

Lotto di **NC-042** (prima di G1). Seconda parte di L45d2b3b2b, divisa dall'utente all'inizio di
L45d2b3b2b1: **«Due parti»** (b1 il sorgente; qui il calore, la Stax e il riposo a caldo). Verifica
**ADR-099** sul blocco generato da `circuits/preamp/gain_block.py`; **il circuito non cambia**, nessuna
decisione nuova, nessuna non conformità aperta o chiusa. Dati: `data/2026-10-23/L45d2b3b2b2/` (README).

## In una riga

Sul blocco del sorgente tutto ciò che ADR-099 prometteva c'è, e niente di ciò che la faceva riaprire è
successo: il calore dei guasti è quello del banco cella per cella, la Stax si accorcia, e il dissipatore
porta la corrente di riposo a caldo **verso** il valore di progetto, non lontano.

## Il calore dei quindici guasti e delle parti nuove

Sul banco del calore di L45d2b3b2a (rail ideali a ±15 V, 60 °C d'aria, le cinque posizioni) la variante
`sorg` è il blocco di `spice/preamp/` byte per byte; il generatore rifiuta ogni copia guasta che non abbia
le cinque parti di ADR-099. 135 corse, 135 rc 0.

- **Contro la variante misurata in L45d2b3b2a** (rv2, con la mappa delle sigle R161…R169 → R190…R194):
  **4320 celle di calore, 0 diverse** (tolleranza 1e-3). Al jack: 211 livelli sopra 0 dB SPL uguali a
  0,0 dB, 485 ampiezze sopra 1 µV entro lo 0,25 %, 140 tempi del massimo entro 0,1 ms. Il resto (1189
  celle) è il residuo numerico sotto la soglia d'udito, che cambia con l'ordine delle righe del netlist: a
  riposo il jack a −62 contro −105 dB SPL (1,8 nV contro 13 pV). Due colonne di `calore_*.csv` nominate
  R161 / R162 da una lista fissa dell'analizzatore sul sorgente non esistono più: dichiarato e messo da
  parte, le potenze delle parti nuove si confrontano a parte (uguali).
- **13 dei 15 guasti entro i limiti.** Il più caldo è il VAS: **123 °C** con D102 o D103 aperti o il suo
  carico in corto, **124 °C** con R126 in corto, contro i 125 °C di P7; **119 °C** coi dispositivi a 60 °C
  (1120 celle, 0 diverse dal banco). Il «Da riaprire se» di ADR-099 («il VAS supera 125 °C») non scatta.
- **I due rimasti sono i corti dei finali** (l'altro finale a 1,4–1,6 W): **160 / 149 °C senza
  dissipatore, 99 / 95 °C col WA-T220-101E** (a calcolo, con 2 °C/W d'interfaccia per ipotesi). A riposo
  i finali a 67 °C, in P7 a 69 / 70 °C.
- **Le parti nuove nei guasti**, uguali al banco: la 1 kΩ della coda (R194) al più **0,236 W** (R107 in
  corto: in distinta ≥ 0,5 W, come dice ADR-099), le altre ≤ 0,089 W, il limitatore Q193 al più 69 °C.

## La Stax dei casi oltre 100 ms

I 121 casi che sul blocco di ADR-097 tenevano la Stax sopra 0,87 V per più di 100 ms, con le stesse
impostazioni di L45d2b3b1. 121 rc 0, tutti a buon fine.

- **Nessuno oltre 150 ms (il tetto di ADR-086), nessuno oltre 125 ms.** Il più lungo 124,5 ms (un JFET
  d'ingresso, con il condensatore della Stax al +5 %).
- **D102 / D103 aperti: 145,8 → 91,5 ms.** ADR-098 li aveva mandati al lotto del calore proprio con
  questa attesa («un rimedio per il loro calore può accorciare anche la Stax»): è il limite del VAS.
- 19 casi si accorciano di più di 1 ms (lo specchio e R119 da 102–124 ms a 0; la sorgente di coda in
  corto da 102–124 a 86–90 ms); 6 si allungano, al più di 9,8 ms e al più fino a 119,6 ms (il finale PNP in
  corto, R107 in corto sulla fissa 2). Il «Da riaprire se» di ADR-098 non scatta.

## Il riposo e V4 a caldo, col dissipatore

Col metodo di L56 (ogni giunzione alla sua temperatura, iterata fino a convergenza, aria a 27 e 57 °C),
quattro modi di vedere i finali: senza dissipatore (il modello di L60d1, la base); col dissipatore
(24,5 °C/W invece di 62,5); senza, col moltiplicatore di Vbe alla temperatura del case del finale NPN
(l'accoppiamento in rame **perfetto** di ADR-034: un limite superiore, la geometria è di G2); e col
dissipatore e l'accoppiamento perfetto.

| Corrente di riposo dei finali (ADR-042: ~20,3 mA) | senza | col dissipatore | senza, accoppiato | col dissipatore, accoppiato |
|---|---|---|---|---|
| tutto a 27 °C | 20,5 mA | 20,5 | 20,5 | 20,5 |
| aria a 27 °C | 22,7 | 21,1 | 21,8 | 21,2 |
| aria a 57 °C | **24,2** (+19 %) | **22,5** (+11 %) | 23,2 (+14 %) | 22,5 (+11 %) |

- **Il dissipatore abbassa la corrente di riposo a caldo**, di circa il 7 %: il finale è più freddo
  (65 contro 79 °C a 57 °C d'aria) e la sua Vbe scende meno. Lo spostamento a caldo esisteva già senza
  dissipatore, ed è da L56 lo stato del progetto (+19 % a 57 °C); col dissipatore è minore (+11 %).
- **Col dissipatore l'accoppiamento in rame non conta quasi più**: il case del finale (64 °C) non è più
  caldo di quanto il moltiplicatore si scaldi da sé (65 °C), e l'accoppiamento perfetto sposta la
  corrente di uno 0,2 %. Senza dissipatore valeva il 4 %. **«Più lento»** (ADR-099) è un fatto dinamico
  che questo metodo, statico, non vede: la massa del dissipatore allunga il tempo con cui il finale
  insegue un cambio di potenza; resta al prototipo (il «Da riaprire se» di ADR-034).
- **Il limitatore del VAS a riposo è spento**: 0,06 µA a 27 °C, 1,3 µA a 57 °C d'aria, contro gli ~83 µA
  di base del VAS. Il VAS resta a 10,72 mA (27 °C), 10,88–11,21 mA a caldo.
- **V4 dentro, uguale a prima**: in tutti e quattro i modi 0 casi su 12 fuori a 20 kHz, margine peggiore
  **2,7 dB** (57 °C d'aria), intermodulazione **−131,7 dB** (margine 21,7 dB), il gradino della coda oltre
  la scansione. Contro il blocco di L60d1 (prima di ADR-097 e ADR-099, stesso metodo): margine 2,7 contro
  2,7 dB, distorsione 0,000725 contro 0,000722 %, intermodulazione −131,7 contro −131,8 dB.

**Una difficoltà del simulatore, risolta.** Con dissipatore e accoppiamento, un passo dell'iterazione a
27 °C non trovava il punto di lavoro e ripiegava su quello spento (il controllo di L56 l'ha rifiutato).
Ogni passo parte ora dal punto del passo prima, in tutti e quattro i modi; nessuna corsa ha usato il
ripiego.

## I «Da riaprire se»

| Da riaprire se | Il numero | Esito |
|---|---|---|
| ADR-099: il VAS supera 125 °C in uno dei guasti che lo limitano, sul blocco del sorgente | 124 °C (R126 in corto), 123 °C negli altri tre; 119 °C coi dispositivi a 60 °C | non scatta |
| ADR-099: il limite del VAS a caldo cambia la distorsione a 20 kHz o l'intermodulazione oltre V4 | 0 su 12 fuori, margine 2,7 dB, −131,7 dB; uguale al blocco senza limite | non scatta |
| ADR-099: la corrente di riposo, col dissipatore e l'accoppiamento in rame, si sposta oltre quanto ADR-042 accetta | col dissipatore +11 % sui 20,3 mA a 57 °C d'aria, contro il +19 % senza, che è lo stato da L56 | non scatta (vedi sotto) |
| ADR-099 / ADR-097: un rimedio cambia le correnti dei rail del blocco | a riposo il VAS 10,715 mA (banco 10,713), i finali 20,45 mA; nei guasti le stesse del banco | non scatta: la cella RC e R153 non si rimisurano |
| ADR-098: un guasto del blocco sulla Stax oltre 150 ms; il rimedio cambia lo stadio d'ingresso | al più 124,5 ms, D102 / D103 aperti 91,5 ms | non scatta |
| ADR-099: il WA-T220-101E esce di produzione | non riverificato in questo lotto (DigiKey «Active» il 2026-10-22) | — |

**Sulla corrente di riposo**, una lettura da dichiarare: ADR-042 sceglie i ~20,3 mA ma non fissa una
banda. La leggo così: il dissipatore non sposta la corrente «oltre» ciò che il progetto già accetta, perché
la sposta meno di quanto faccia oggi senza dissipatore. Se l'utente vuole una banda per la corrente di
riposo a caldo, è una decisione sua, con questi numeri.

## Per il lotto successivo (L45d2b3b3, la sintesi)

- Le righe del calore sul blocco del sorgente sono `sintesi_sorg.csv` (e `sintesi_sorgt60.csv` per i quattro
  guasti del VAS a 60 °C); i corti dei finali vanno nella sintesi col dissipatore (`dissipatore.csv`), 99 /
  95 °C, entro P7 e sotto il massimo assoluto.
- La Stax dei casi lunghi è `stax_lunghi.csv`.
- Le parti nuove hanno i loro undici modi in `sintesi_sorg.csv`, tutti entro.
