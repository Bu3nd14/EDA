# L62b — i quattro diodi di riserva nel sorgente, e la verifica

Data: 2026-10-19 · Lotto: L62b · Non conformità: **NC-062** (chiusa) · Decisione: **ADR-090** (di
L62a, non riscritta) · Dati: `docs/preamp/data/2026-10-19/L62b/`

## Prima di tutto

- **Il blocco del sorgente dà le cifre della variante di L62a.** Sul banco di L62a, 211 confronti
  con la variante `diodi` (sintesi dei guasti modo per modo, riposo a 27 / 60 / 90 °C, blocco sano):
  **0 diversi** (`confronto_L62a.csv`). Nessun gradino al jack è cambiato, quindi la seconda lettura
  col metodo puntuale non serve (limitations #64).
- **Una cosa che L62a non aveva misurato: la corrente dei diodi non è di «qualche µA».** A blocco sano
  la catena porta **94 µA a 27 °C, 134 µA a 60 °C, 177 µA a 90 °C** (sotto, «La corrente dei diodi»).
  Il riposo si sposta di −0,05 / −0,09 / −0,13 mA, come L62a aveva misurato senza dirne la causa.

## Il circuito

`circuits/preamp/gain_block.py`, sezione 11, **in fondo alla funzione** (limitations #22: nessuna
sigla esistente si sposta): quattro 1N4148 (DO-35, modello D1N914 come D102 / D103) in serie fra NX e
NY, anodo verso NX, sulle reti nuove NXD1–NXD3.
- Sul blocco del file: **D154–D157**. Sulla scheda audio la sigla segue le parti di ogni istanza:
  D152–D155 (blocco A), D253–D256 (blocco B), D551–D554 e D651–D654 (le due fisse), e lo stesso
  sull'altro canale. **554 parti** (erano 522), nessuna sigla duplicata.
- Il disegno del blocco ha i quattro diodi in colonna nel riquadro 3, accanto a R128 / R129. Prima di
  disegnarli il controllo del disegno di `run_tests.sh` cadeva come deve («59 dispositivi nella
  netlist, 55 nel disegno», D154–D157 omessi); dopo, `run_tests.sh` 13 / 0.

## I guasti

Il banco di L62a (`genera_L62b.py`: la variante `base` è ora il blocco generato), cinque posizioni
del canale, con 60 °C d'aria:

| Guasto | Finali | 22 Ω | Gradino alla principale | In L62a senza diodi |
|---|---|---|---|---|
| Q127 emettitore aperto | 97 °C | 0,040 W | 66 dB SPL (76 a +10 dB) | 216 °C, 3,28 W |
| Q127 base-emettitore in corto | 97 °C | 0,039 W | 66 dB SPL | 214 °C, 1,72 W |
| R129 in corto | 97 °C | 0,039 W | 66 dB SPL | 214 °C, 1,72 W |
| R128 aperta | 98 °C | 0,041 W | 66 dB SPL | 137 °C, 7,54 W |
| un diodo aperto | 79 °C | 0,009 W | — | — |
| un diodo in corto | 78 °C | 0,009 W | 38 dB SPL (48 a +10 dB) | — |

Nessuna parte del blocco oltre i suoi limiti, in nessuna posizione. Il controllo `CTRL_OUT_VP` (uscita
in corto col rail) dà 16,0 V alla principale, oltre il tetto, come deve.

## Il blocco sano

- **Riposo** 20,45 / 20,56 mA (era 20,50 / 20,61); −0,05 / −0,09 / −0,13 mA a 27 / 60 / 90 °C.
- **V1**: ogni margine al più +0,05° rispetto al blocco senza diodi; i minimi dei quattro deck
  d'anello 47,20 / 43,13 / 43,20 / 64,10°, quelli della variante di L62a.
- **P7**: finali 0,362 / 0,363 W (83 °C con 60 °C d'aria), 22 Ω 0,295 / 0,332 W, 47 Ω della
  principale 1,282 W, Q146 0,027 W: uguali, scarto ≤ 2 mW caso per caso. Una sola colonna si muove: il
  picco positivo della corrente di collettore del finale PNP nel mute in corto, da 3,1 a 7,1 mA in
  quattro casi, senza effetto sulle potenze.
- **La regressione dei 21 deck veloci** (`regressione/misure.csv`, sulle misure dei log): niente che
  non sia il riposo e ciò che ne segue. Il rumore cambia di 1e-6 relativo, E3 ed E4 al più di 1e-4,
  il PSRR di 6e-4, la risposta di 4e-3 (a 100 kHz).
- **V2**: il banco della regressione cambia al più di 4e-4 relativo (lo spread massimo 2,602 → 2,601 V).
  **La matrice di V2 non si rifà**: il blocco non cambia dove V2 guarda.
- **V4 a caldo** (il metodo di L56, SOT-223, quattro condizioni): **0 su 48 fuori**, THD a 20 kHz ≤
  0,00072 % a 0,2 V e ≤ 0,0073 % a 2 V, intermodulazione ≤ −131,8 dB, la coda oltre +23,6 %: **cifra
  per cifra le cifre di L60d1**. Lo stesso coi quattro diodi alla temperatura del finale NPN (79 °C
  con 57 °C d'aria), il caso dei diodi montati vicino ai finali.

## La corrente dei diodi

Il «Da riaprire se» di ADR-090 dice: «i diodi conducono a blocco sano più di qualche µA a 60 °C
d'aria (il riposo si sposta di più di 0,5 mA)».
- **La cifra fra parentesi è rispettata con margine**: −0,09 mA a 60 °C, −0,13 a 90 °C.
- **La frase prima no**: 134 µA a 60 °C. Sono 2,6 V a cavallo di quattro giunzioni al silicio: il
  modello D1N914 a 0,5 V per diodo conduce già decine di µA. L62a aveva misurato il riposo, non la
  corrente, e «qualche µA» era una stima.
- **Che cosa costa**: i 94–177 µA si tolgono a Q127 (9,69 → 9,60 mA), e il riposo dei finali scende
  di 0,05–0,13 mA. V1, P7, V2 e V4 a caldo non lo vedono. Il diodo è una resistenza dinamica di
  ~1 kΩ (4 · 26 mV / 94 µA) in parallelo a un moltiplicatore di pochi ohm.

Leggo la clausola sul suo criterio misurabile, e per questo chiudo NC-062. **La lettura è
dell'utente**: se preferisce la frase alla lettera, la clausola è scattata e la strada è una ADR
nuova, con un rimedio da misurare.

## Limiti dichiarati

- Il calore dei guasti è Tj = Ta + P · R_thJA dalle potenze a 27 °C, come in L45a / L62a.
- La potenza dei diodi coi guasti è a calcolo (~8 mW per diodo): i diodi non hanno `[p]` nei deck.
- V4 a caldo mette Q127 alla propria Tj, non a quella del finale a cui è accoppiato in rame (il metodo
  di L56 / L60d1, invariato).
- Tutte le cifre vengono da modelli del costruttore senza dispersione fra esemplari; la distorsione è
  una cifra di modello.

## Che cosa resta, e a chi

- **NC-062 chiusa**; il registro ha **18 voci aperte, 1 bloccante** (NC-044, per G2): **nessuna
  bloccante per G1**.
- **L45d2b2** è il prossimo lotto: legge i massimi e la dissipazione dei finali sul blocco con i diodi.
- **Il layout (G2)**: i diodi **lontano dai finali** (commento in `gain_block.py`); il moltiplicatore
  resta accoppiato in rame al finale NPN (ADR-082, NC-019).
- **All'utente**: la lettura della clausola sulla corrente dei diodi (sopra).
