# ADR-068 — Il VAS e il suo carico in SOT-223 (DZT5401 / DZT5551): lo stesso die, il package che dissipa

Data: 2026-10-12 · Stato: accettata

## Contesto

Due fatti emersi in L56 sullo stesso stadio:

1. **Il calore vero**, col calcolo iterato fino a convergenza (`data/2026-10-12/L56/script/caldo.py`):
   il VAS (Q122, MMBT5401, 403 / 357 °C/W) e il suo carico (Q125, MMBT5551, 417 °C/W) arrivano a
   86–96 °C con l'aria a 27 °C e a **114–124 °C con l'aria a 57 °C**, già nel blocco di prima di
   L56. Il controllo usato fin qui (310 mW) è la potenza nominale del SOT-23 a 25 °C: a 60 °C
   d'aria e 417 °C/W il tetto di P7 (Tj ≤ 125 °C) ammette **0,156 W**.
2. **P7 col corto all'uscita**, dopo ADR-067: l'inseguitore spinge il VAS più a fondo di quanto lo
   specchio saturo permettesse, e nel caso peggiore (blocco B, +10 dB, 20 kHz, corto al principale)
   Q125 dissipa **0,191 W → 140 °C** a 60 °C d'aria, contro 125 °C (prima di L56 0,144 W, 120 °C).

Decisione dell'utente del 2026-10-12: «Rimedio subito in L56», fra rimedio ora, voce nuova col
rimedio in L55, voce maggiore.

## Decisione

**Q122 diventa DZT5401 e Q125 DZT5551, Diodes Incorporated, SOT-223 (impronta
`Package_TO_SOT_SMD:SOT-223-3_TabPin2`), sulla piazzola minima raccomandata.** In ogni istanza
del blocco. La simulazione resta sulle schede `MMBT5401` / `MMBT5551` di `models/`: il costruttore
serve per i DZT **lo stesso modello, parametro per parametro** (sotto).

## Perché

- **Lo stesso die, la stessa scheda.** Il file collettivo del costruttore «Transistors >100V»
  (`vendor/bjt_pnp/diodes_inc/DZT5401/`, scaricato da www.diodes.com) contiene `.MODEL DZT5401` e
  due copie di `.MODEL DZT5551` (2010 e 2011): `script/dzt_identico.py` le confronta coi file del
  costruttore dei MMBT già congelati e stampa «IDENTICO» per tutte e tre (27 e 28 parametri). È la
  strada di ADR-017 (cambia il package, non il die), e T7 resta soddisfatta: modello del
  costruttore della parte montata.
- **Il calore** (Tj = Ta + P·R_thJA, iterato), a 125 °C/W:

| | SOT-23 | **SOT-223, piazzola minima** |
|---|---|---|
| VAS e carico, aria 27 °C | 86–96 °C | **45,5 °C** |
| VAS e carico, aria 57 °C | 114–124 °C | **75 °C** |
| Q125 col corto (P7), 60 °C d'aria | 140 °C | **84 °C** |
| potenza di VAS e carico, aria 27 °C | 164 / 165 mW | 148 / 149 mW (meno deriva termica della corrente) |

- **La distorsione non si muove**: 0 casi su 48 fuori da V4, margine ≥ 2,7 dB, intermodulazione
  ≤ −131,8 dB, come col SOT-23 (sul blocco di ADR-067 le cifre ormai non dipendono dal calore).
- **Piazzola minima, non rame grande.** La linguetta del SOT-223 è il collettore: per il VAS è NX,
  il nodo del polo dominante, per il carico NY. Il rame di 50 × 50 mm (62,5 °C/W) sarebbe capacità
  parassita su quei nodi; la piazzola minima basta con 41 °C di margine su P7.
- **Ciclo di vita**: nessun marchio di fine vita nei datasheet (DS31218 Rev. 4-2 © 2026, DS31219
  Rev. 4-2 giugno 2023), la stessa evidenza dei MMBT in L24.

## Ipotesi dichiarate

- **125 °C/W per il DZT5551**: il suo datasheet dà solo 62,5 °C/W su 50 × 50 mm di rame; la cifra
  della piazzola minima è quella del DZT5401, stesso package. Anche raddoppiata (250 °C/W) Q125 nel
  corto starebbe a 108 °C.
- **La corrispondenza fra i piedini del simbolo e le piazzole** (E, C, B e la linguetta su C, letti
  dal disegno del datasheet) si verifica al layout (G2), come per ogni BJT del progetto: nella
  netlist i piedini dei simboli si chiamano C / B / E, non 1 / 2 / 3.

## Alternative scartate

- **Limitare la corrente del VAS**: tocca un nodo di segnale e la topologia; il package risolve
  anche il calore in funzionamento normale, che il limitatore non tocca.
- **TO-92 (2N5401 / 2N5551)**: L24 (ADR-017) non ha trovato un modello del costruttore per il TO-92.
- **Rame grande sotto i SOT-23**: il SOT-23 non scende abbastanza (357 °C/W col rame del datasheet)
  e il rame sta sul collettore, cioè su NX / NY.

## Cosa precisa

- **ADR-017**: per Q122 e Q125 il package passa da SOT-23 a SOT-223; die, costruttore e modello
  restano. Gli altri MMBT restano in SOT-23 (coda 69 mW → 89 °C, inseguitore 33 mW → 73 °C a 60 °C
  d'aria).
- **ADR-021 / P7**: il controllo dei 310 mW in `p7.py` è la potenza nominale a 25 °C, non il tetto di
  P7; la cifra che conta è Tj ≤ 125 °C a 60 °C d'aria con la R_thJA del package.

## Da riaprire se

- Il layout (G2) non riesce a dare la piazzola minima raccomandata o mette i due SOT-223 vicino a una
  fonte di calore (i MJE, il moltiplicatore di Vbe di ADR-034).
- Diodes marca uno dei due DZT come fine vita.
