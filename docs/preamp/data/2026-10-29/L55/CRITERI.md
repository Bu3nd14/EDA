# L55 — i criteri, scritti prima delle corse (2026-10-29)

NC-056: il dispositivo d'uscita del blocco di guadagno. Questi criteri sono scritti e committati
**prima** della prima corsa di un candidato; il controllo sul blocco di oggi (`mje`) corre in
parallelo, ed è il caso noto, non un candidato. Un criterio che cambia dopo una corsa si dice nel
report, con la ragione.

## Il controllo (caso noto)

La variante `mje` (il `gain_block_flat.inc` di oggi senza modifiche) deve ridare la regressione di
L56 / L45d2b3b2b2 / ADR-054:

| | atteso |
|---|---|
| V1 blocco B, 0 / +3 / +10 dB | 65,16 / 73,29 / 105,11° (L56 «dopo») |
| V1 blocco A, trim, buffer | 68,38 / 73,36 / 65,31° |
| PSRR+ a +10 dB, 50 Hz / 1 / 10 / 20 kHz | 85,3 / 85,0 / 85,5 / 84,3 dB |
| corrente di riposo dei finali | 20,45 / 20,56 mA (uniforme 27 °C) |
| V4 a caldo (spec `--sot223--diss`) | 0 su 12 fuori, margine peggiore 2,7 dB, IMD −131,7 dB |

Se il controllo non le ridà entro l'ultima cifra stampata (o entro la differenza spiegata da un
commit successivo a quei lotti), **ci si ferma** e si cerca la causa prima di guardare un candidato.

**Corretto dopo la prima corsa del controllo** (2026-10-29, prima di ogni corsa di un candidato). Le
cifre di V1 della tabella sopra sono quelle della **regressione dei 21 deck** di L56 (`margini.py`),
un altro banco. Il banco di questo lotto è quello di L46a (`sintesi.py`, il criterio di L40), che sul
blocco di ADR-054 dava **64,94°** (ADR-054) e in L46b 64,91–64,94°. Il controllo `mje` dà **64,92 /
73,07 / 104,98°** (B), 67,81° (A), 65,06° (buffer), il gruppo B di I_DSS 65,13° minimo: lo stesso
banco ridà la sua storia. Il PSRR+ (85,0 / 85,5 / 84,3 dB) e la corrente di riposo (20,45 / 20,56 mA)
sono quelli di L56 / L45d2b3b2b2 alla cifra. La variante `mje_senza_d158d159` (i diodi di ADR-095
tolti) dà cifre identiche: i diodi non muovono V1. La regressione dei 21 deck si rifà solo se il
sorgente cambia (passo 5b del piano).

## I criteri, per ogni variante

| | criterio | fonte |
|---|---|---|
| **V1** | ≥ 60° su ogni combinazione: blocco B nei tre modi, fino a 4,7 nF al jack dopo 47 Ω + 4,7 µF; blocco A col suo cablaggio ≤ 1 nF; buffer delle fisse; gruppo B di I_DSS | REQUIREMENTS V1, ADR-019, ADR-024, ADR-031 |
| **V4** | THD a 20 kHz ≤ 0,001 % a 0,2 V RMS; dalla 5ª ≤ −140 dB; CCIF ≤ −110 dB; THD a 20 kHz ≤ 0,01 % a 2 V RMS. A 27 °C uniformi **e** a caldo (ogni giunzione alla sua Tj iterata, aria 27 / 57 °C, metodo di L56 / L45d2b3b2b2) | ADR-055 |
| **PSRR** | la quota di ADR-020 sul rail ±; se il PSRR del blocco scende sotto quello di oggi, il conto si rifà con `data/2026-09-23/L40/script/limiti_psrr.py` | ADR-020, ADR-056 |
| **E5** | il rumore peggiore ≤ 9,95 µV (tetto), confronto con 5,10 µV di oggi | E5, ADR-057 |
| **slew** | nessun requisito: confronto con il MJE (oggi ~3,8 V/µs in discesa), servono 1,51 V/µs per 12 V di picco a 20 kHz | L52 R6, ADR-054 |
| **classe A** | la corrente di riposo dei finali ~20,5 mA (R128 ritarata), sopra il picco sul carico peggiore | ADR-023, ADR-042 |
| **P7** | Tj ≤ 125 °C con 60 °C d'aria a riposo e nel corto all'uscita, con la Rth del contenitore e del dissipatore del candidato; la base-emettitore inversa ≤ V_EBO del candidato (i 1N4148 di ADR-095) | P7, ADR-021, ADR-095 |
| **i due corti dei finali** | il finale superstite ≤ 125 °C con 60 °C d'aria e ≤ Tj max del datasheet (oggi 99 / 95 °C col WA-T220-101E); P letta dal banco dei guasti sul candidato | ADR-099, P7 |
| **compensazione** | se C124 o C137 cambiano, la variante si dichiara coi numeri, e V1 / PSRR / V4 si rimisurano sulla variante | ADR-054 |
| **T7 / T8** | modello del costruttore, nessun fine vita annunciato, disponibilità verificata con fonte e data | ADR-016, ADR-017 |

## Che cosa decide l'utente

Il criterio non sceglie: dice quali varianti sono **dentro**. La scelta fra il MJE com'è e un
candidato dentro è dell'utente, con le cifre di ogni variante contro ogni limite (la domanda per
nome, le cifre ricontate dai CSV).
