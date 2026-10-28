# L54b3a — la robustezza del temporizzatore al banco: i modelli del costruttore, la rete sporca, i fronti veloci, i rimbalzi

Data: 2026-10-28 · Lotto: L54b3a (prima parte di L54b3, diviso dall'utente all'inizio: «Due parti») ·
Decisione: **ADR-104** · Dati: `docs/preamp/data/2026-10-28/L54b3a/` (README: i criteri scritti prima
delle corse, le tabelle, come rifare).

## In breve

| Prova | Esito |
|---|---|
| I modelli del costruttore (BC847A/B/C, BC857A/B/C, BAT54, Diodes Inc.) | nel repository, `validate_models.py` 83 / 83 |
| I transistor della ritenuta del costruttore | come i generici: L54b2 identico |
| **Il BAT54 del costruttore** sui nodi da megaohm | **la ritenuta scattava a ogni accensione** → ADR-104: BAS416 a bassa perdita, R571 1 MΩ |
| I buchi di rete (½–15 periodi), il ritorno durante la discesa, +15 %, i cali all'accensione | passano, alle tre reti |
| **I cali lenti** che portano i regolatori fuori regolazione con la rete presente | **14 su 27 spengono l'apparecchio** (la ritenuta) → ADR-104: «Lasciare com'è» |
| Il sorgente con ADR-104, la lista della sicurezza di L54b2 (31 casi) | nessun verdetto cambia |
| I rimbalzi del frontale e di SW3 (1–5 ms, 36 treni) | come la transizione pulita |
| I fronti veloci su V5 e `VRELAY_REG` (±1 / ±5 V, 10 ns) contro la ritenuta | nessuno scatto, nemmeno senza l'1 nF; con l'1 nF la base a ≤ 8,4 mV |
| Il controllo numerico (passo 5 µs) | identico |

## Che cosa è cambiato nel progetto

- `circuits/preamp/psu.py`: D535, D541, D536 **BAS416** (silicio a bassa perdita, SOD-323), R571 **1 MΩ**
  (ADR-104). Netlist: solo i valori e il simbolo delle quattro parti; schematico 167 / 167, manifesto uguale.
- `models/`, `vendor/`: i sette modelli di Diodes Inc. con la provenienza; `scripts/validate_models.py` le
  sette ricette.
- `docs/limitations.md` #79 (il BAT54 generico perdeva 20 nA) e #80 (i regolatori ideali e i transistor
  senza capacità: un banco di disturbi veloci che non può vedere niente).

## Le due decisioni dell'utente (ADR-104)

1. **I cali lenti: «Lasciare com'è».** Dopo un calo che porta i regolatori fuori regolazione con la rete
   presente l'apparecchio resta spento in modo sicuro e si riaccende dal frontale. La soglia sul grezzo dei
   relè (~4 parti) ne riprendeva 12 su 14 ed è misurata sul banco (`--qualifica v:12.7`) se servisse; la
   soglia sui tre grezzi è scartata dai numeri (perde lo scatto col corto davanti al regolatore +).
   **Correzione**: la domanda diceva 16 cali e «14 su 16»; ricontati sono 14 e 12 su 14.
2. **I diodi: «Diodi a bassa perdita, R571 1 MΩ».** La musica dopo un buco di 20 ms a 559 ms (≥ 500).

## I fronti veloci: come è stato dimensionato l'1 nF

La prima iniezione (in serie all'uscita del regolatore) non arrivava al nodo: i condensatori di bulk lo
tengono, e il regolatore del banco eroga soltanto. Le 48 corse di quella forma sono nel repository ma non
valgono. La forma giusta mette l'impulso in serie ai terminali delle parti sul nodo, oltre il
disaccoppiamento: è il caso peggiore di una pista senza disaccoppiamento locale. Su V5, a tutte le pull-up
del temporizzatore, +5 V in 10 ns per 10 µs portano la base di Q513 a 130,5 mV senza condensatori, 8,4 mV
con l'1 nF, contro ~0,45 V d'innesco. Il fronte che i datasheet danno per i gradini della scheda è ~10 mV:
oltre 54 dB di margine. L'1 nF resta, e riduce l'effetto di un impulso di 40 volte.

## Al prototipo resta

I disturbi irradiati e quelli condotti dalla rete sopra le decine di kHz; il layout (le capacità e le
perdite superficiali sui nodi da megaohm, i ritorni fra RLY_RET e GND); l'inrush vero del toroide.

## Per la seconda parte (L54b3b)

Le tolleranze e la temperatura, coi modelli del costruttore e il BAS416: in particolare AT_PRT (4,7 MΩ,
D538 1N4148: la sua perdita a 60 °C), la musica dopo un buco di 20 ms (559 ms, il margine di ADR-104), i
BAT54 rimasti su nodi da ≤ 200 kΩ (D533, D534, D537), la VBE del BC847B fuori datasheet (708 mV).

`run_tests.sh` e `validate_models.py` alla chiusura: in `STATE.md`.
