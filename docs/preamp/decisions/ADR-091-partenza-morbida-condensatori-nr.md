# ADR-091 — La partenza morbida dei regolatori dei rail: 4,7 µF sul positivo, 470 nF sul negativo

Data: 2026-10-20 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- Risponde a **NC-063** (aperta in L45d2b1): i condensatori sul piedino NR di U501 / U502 erano
  10 µF e 10 µF, e non erano mai stati letti come partenza morbida.
- Non tocca la quota di **ADR-020**: il limite per eccesso del rumore dei rail è costruito su curve a
  C_NR più piccoli (sotto, «Perché»).
- Il firmware (`timer_spec.md` 4.1, i rail entro 2 s) non cambia.

## Contesto

Il condensatore sul piedino NR dei due regolatori dei rail è sia il filtro del rumore del riferimento
sia la partenza morbida.
- Con **10 µF** il rail + saliva in 1,39 s (SBVS204G eq. 5), il − in **12 s** (SBVS169D eq. 1).
- Il firmware vuole i due rail in regolazione entro **2 s**: andava in GUASTO a ogni accensione.
- Per ~10 s il blocco aveva il solo rail positivo.
- Il TPS7A3301 raccomanda C_NR **al più 1 µF** (SBVS169D, condizioni raccomandate).
- Il banco dell'alimentatore usava regolatori senza partenza morbida (i rail in ~31 ms), e nessuna
  sequenza aveva visto la differenza.

## Decisione

Parole dell'utente (2026-10-20): «+ 4,7 µF, − 470 nF».

- **C507** (NR di U501, TPS7A4701): **4,7 µF**. t_SS = 100 kΩ · C · ln((15 + 5) / 5) = 0,65 s.
- **C508** (NR di U502, TPS7A3301): **470 nF**. t_SS = 1,2 ms/nF · C = 0,56 s.

## Perché

Dal banco dell'alimentatore di L45d2b2a: il generatore con la partenza morbida nei regolatori
comportamentali, la scheda audio coi suoi condensatori sui rail e il firmware al punto fisso, sul
sorgente. Lo strumento è controllato sulle due equazioni entro lo 0,22 %, con due sabotaggi presi.

| | oggi (10 / 10 µF) | **4,7 µF / 470 nF** | 10 µF / 1 µF | 1 µF / 1 µF |
|---|---|---|---|---|
| il + sopra la soglia del firmware | 1178 ms | **556 ms** | 1178 ms | 171 ms |
| il − sopra la soglia | mai entro 2 s | **534 ms** | 1131 ms | 1131 ms |
| jack chiusi | — | **707 ms**, rail assestati | 1329 ms, il + 0,3 V sotto | 1282 ms |
| musica | GUASTO a 2,0 s | **0,72 s** | 1,34 s | 1,29 s |
| U501 all'avvio | 4,4 W, 0,36 A | **7,4 W, 0,45 A** | 4,4 W | **1,0 A, 16 W: in limite** |

- **I due rail salgono insieme** (22 ms di scarto alle soglie) e sono **assestati prima** che i
  jack si chiudano. Il margine sui 2 s del firmware è 1,3 s, anche con C_NR al +20 %.
- **Rete −10 %: gli stessi tempi.**
- **Il calore dell'avvio non conta**: +10…14 °C sulla giunzione partendo dall'aria (dallo standby
  il regolatore è freddo), contro +40 °C a regime (ADR-092). Stima a rete termica dichiarata: il
  datasheet non dà l'impedenza termica nel tempo.
- **Il rumore di ADR-020 resta dentro la quota**:
  - la curva del + è quella a C_NR 1 µF (SBVS204G fig. 5-1);
  - quella del − è a 10 nF (SBVS169D fig. 22);
  - i nostri sono più grandi, e un NR più grande filtra di più il riferimento (lo dicono i due
    datasheet), quindi il limite per eccesso regge senza rifare la misura.
- **Il negativo torna nel campo raccomandato** dal costruttore (≤ 1 µF).
- **V2 all'accensione regge con le rampe vere.** La matrice di L29c supponeva rampe di 10 o 300 ms
  e il rilascio 2,5 s dopo; col rilascio al tempo del firmware, 0,70 s dopo l'inizio delle rampe, il
  jack principale ha **4,9 µV** (~15 dB SPL a 1 m, contro il tetto di 100 µV), anche coi due
  condensatori a ±20 % in senso opposto. Prima era 0,04 nV: il rilascio arriva ora più vicino alla
  rampa, ma resta 26 dB sotto.

## Alternative scartate

- **10 µF sul +, 1 µF sul −**: cambia un solo valore, ma i jack si chiudono col + ancora in salita
  (14,69 V) e il margine sui 2 s è ~0,7 s.
- **1 µF e 1 µF**: a valle di U501 ci sono ~9,6 mF (C505, gli 800,8 µF della scheda audio, le otto
  celle da 1000 µF dietro 10 Ω). Il regolatore partirebbe in limite di corrente, 1,0 A e 16 W, e i
  rail sarebbero a 0,96 s l'uno dall'altro.
- **Allungare il tempo del firmware coi 10 µF**: 12 s di accensione col solo rail positivo, e il
  negativo fuori dal campo raccomandato.

## Da riaprire se

- La partenza morbida misurata sul prototipo si discosta di oltre il 30 % dalle equazioni, o i due
  rail arrivano alla soglia a più di 100 ms l'uno dall'altro.
- Il carico dei rail all'accensione cresce tanto che U501 tocca 0,8 A in rampa.
- V2 all'accensione, con le rampe di questo banco, esce dal suo tetto. In L45d2b2a il rilascio al
  tempo del firmware dà al più 4,9 µV al jack principale (~15 dB SPL a 1 m, tetto 100 µV), la rampa
  ≤ 0,31 µV, coi condensatori di filtro anche a ±20 % in senso opposto (`data/2026-10-20/L45d2b2a/v2/`).
