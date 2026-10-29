# 2026-10-29 — L55, il dispositivo d'uscita del blocco di guadagno

**Documento datato: non si riscrive.** Le voci vivono in `../NONCOMPLIANCE.md`. Dati, comandi e casi
noti in `../data/2026-10-29/L55/` (README). Decisione: **ADR-106**. Cifre di modello: ngspice 47, i
modelli di `models/`; le cifre a caldo con la temperatura delle giunzioni dichiarata.

## Perché

NC-056 (L52, rilievo R6, minore, da valutare prima di G1): il MJE15032 / MJE15033 è un 8 A / 250 V a
~20 mA, la sua CJE di 3,06 nF ha guidato ADR-042 e ADR-054, e ADR-054 aveva valutato i ZXT ma non un
driver di taglia intermedia. La chiusura chiedeva un driver col modello del costruttore sul banco del
blocco contro il MJE, con T7 e T8, e la decisione dell'utente.

## 1. Il candidato

`bom-component-manager` (`modelli/README.md`). Il solo che regge T7 + T8 con le scorte: **onsemi MJE243G /
MJE253G**, TO-225, 100 V / 4 A, V_EBO 7 V, modelli onsemi in `/download/models/lib/` (contenuto e tipo
controllati, limitations #18 / #20), «Active», a magazzino a Farnell, RS, TME (findchips, 2026-10-29).
La ricetta `_tb_mje24x` dentro ogni finestra del datasheet (h_FE a 0,2 e 1 A, f_T 59,9 MHz contro 40, C_ob
29,2 / 19,7 pF contro 50): `validate_models.py` **89 / 89**. Scartati: i Toshiba TTC004B / TTA004B,
TTC015B, TTA008B (T8: «Not Recommended for New Design»), MJE182 / MJE172 (Vbe 0,92 V a 20 mA), MJD243
(manca il PNP), MJE340 / MJE350 (capacità a cifre tonde, nessuna f_T), D44H11 / D45H11 e MJD44H11 /
MJD45H11 (capacità come il MJE), ZXTN / ZXTP19060CG (il PNP senza scorte, 42 °C/W).

A 20 mA, 15 V (lo stesso script, il MJE come caso noto): Cpi **1,70 / 2,19 nF** contro 8,09 / 7,81 nF,
f_T 87,7 / 61,2 MHz contro 12,2 / 12,3. La CJE a zero scende di 14–19 volte, la Cpi solo di 4–5: a 20 mA
pesa la diffusione.

## 2. I casi noti

| banco | caso noto | esito |
|---|---|---|
| freddo (L46a) | `mje` contro la storia del banco | V1 64,92° (ADR-054 64,94°, L46b 64,91–64,94°), PSRR+ 85,0 / 85,5 / 84,3 dB e riposo 20,45 / 20,56 mA alla cifra di L56. Le cifre di V1 attese in `CRITERI.md` erano della regressione dei 21 deck, un altro banco: **corrette prima di ogni corsa dei candidati**, dichiarato |
| freddo | `mje_senza_d158d159` | identico: i diodi di ADR-095 non muovono V1 |
| a caldo (L45d2b3b2b2) | `mje--sot223--diss`, `--molt` | 0 su 12, 2,7 / 3,0 dB, 0,000726 / 0,00735 %, −131,7 dB, riposo 21,06 / 22,48 mA: L45d2b3b2b2 alla cifra |
| congelamento delle capacità | `mje_fz` contro `mje`, freddo e caldo | identici all'ultima cifra stampata |
| guasti dei finali | `fmje` contro `calore_sorg.csv` | 465 celle, 0 diverse; 99 / 95 / 67 / 69 / 70 °C di ADR-099 |

## 3. Il modello del MJE253 a caldo (limitations #82)

I 40 deck a caldo del candidato (ogni giunzione alla sua Tj) si fermano al primo punto della `tran`
(«Timestep too small; initial timepoint», nominando l'LSK489). Le prove su un deck: senza `temp=` sui soli
finali passa; con `dtemp=` o `method=gear` no. Il VJC del MJE253 è **0,0329 V**, e la scala SPICE della
temperatura lo porta a −0,0065 V a 36,5 °C e −0,104 V a 60 °C; il MJE243 (0,40 V) e il MJE (0,60 V) restano
positivi fino a 125 °C. A 27 °C il modello ridà la C_ob del datasheet. Rimedio di banco dichiarato: le
capacità di giunzione ferme a TNOM (`TLEVC=1`, coefficienti zero) in copie che stanno solo nel banco,
provate sul MJE (sopra). **Un modello del costruttore che regge T7 ma non vale alla temperatura del
telaio**: per un'adozione andrebbe detto nella ADR.

## 4. Le misure

Il candidato: R128 da 1,58k a **1,78k** per la Vbe più alta (riposo 20,75 / 20,70 mA; 1,74k dà 20,08 /
20,03). Il Miller: 470, 330, 220 pF. A **220 pF il blocco A scende a 59,54°**, sotto i 60°: fuori.

| | MJE | candidato, 470 pF | candidato, 330 pF |
|---|---|---|---|
| V1 peggiore (≥ 60°) | 64,92° | 69,83° | 67,69° (blocco A) |
| THD 20 kHz 0,2 V, 27 °C / a caldo (≤ 0,001 %) | 0,00045 / 0,000726 % | 0,00044 / 0,000719 % | 0,00033 / 0,000604 % |
| margine peggiore a caldo | 2,7 dB | 2,8 dB | 4,2 dB |
| THD 20 kHz 2 V a caldo (≤ 0,01 %) | 0,00735 % | 0,00729 % | 0,00613 % |
| intermodulazione a caldo (≤ −110 dB) | −131,7 dB | −132,2 dB | −137,0 dB |
| rifiuto del rail + 1 / 10 / 20 kHz | 85,0 / 85,5 / 84,3 dB | 85,3 / 85,3 / 84,5 dB | 88,3 / 88,2 / 87,3 dB |
| quota di ADR-020, il tono più stretto | V− 10,4 mV a 20 kHz | V− 13,5 mV | V− 20,5 mV |
| slew in discesa | −5,92 V/µs | −6,16 V/µs | −8,23 V/µs |
| rumore (E5, la catena D) | 4,337 µV | 4,337 µV | 4,339 µV |
| riposo dei finali con 57 °C d'aria | 22,48 mA (+10,7 % su ADR-042) | 20,09 mA (−1,1 %) | 20,09 mA |

La quota di ADR-020: il candidato a 470 pF abbassa il PSRR+ a 10 kHz di 0,2 dB (V+ 18,3 contro 18,8 mV);
rifatta con `limiti_psrr.py`, ogni tono resta sopra quello del MJE altrove, e tutti molto sopra il ripple
dei rail regolati. La corrente di riposo del candidato **scende** col calore, quella del MJE sale.

**Il calore dei finali** (`dissipatore.csv`, 60 °C d'aria; il caso a 27 °C è il peggiore — L45d2b3b2b2:
coi dispositivi a 60 °C 1,543 contro 1,607 W):

| | potenza | MJE col WA-T220-101E | candidato col TV4 | dissipatore che serve al candidato per 125 °C |
|---|---|---|---|---|
| NPN, col PNP in corto | 1,607 / 1,678 W | 99 °C | **113 °C** (200 senza) | ≤ 28,4 °C/W |
| PNP, con l'NPN in corto | 1,429 / 1,468 W | 95 °C | **106 °C** | ≤ 33,9 °C/W |
| a riposo | 0,30 W | 67 °C | 69 °C | |
| P7 (mute o uscita in corto) | 0,40 / 0,42 W | 70 °C | 73 °C | |

Il TV4: 21 °C/W (21,6 per il TV4G) in tutti gli elenchi dei distributori; la curva del costruttore non si
è trovata, né il disegno che lo accoppi al TO-225.

## 5. All'utente

La domanda per nome, le cifre ricontate dai CSV (`script/tabella_opzioni.py`), le tre opzioni tutte dentro
ogni limite. **Decisione dell'utente**: **«MJE as it is»** → ADR-106. NC-056 chiusa.

## 6. Una voce nuova: il VAS a 126 °C (NC-076)

Correndo i modi dei finali sul blocco di oggi (il caso noto) è uscito che **col finale NPN in corto
base-emettitore il VAS dissipa 0,53 W e fa 126 °C** in SOT-223 con 60 °C d'aria, contro i 125 di P7, in
tutte le cinque posizioni e con tutti e due i dispositivi. La riga della FMEA (`L45d2b3b3/fmea_dopo.csv`)
dice ancora 115 °C, dal blocco di prima di ADR-097 / ADR-099: dopo i rimedi i modi fuori dai quindici non
erano stati rifatti. **Decisione dell'utente**: «New entry, major, before G1» → **NC-076 aperta**, la riga
corretta in `fmea_correzione.csv`. Il meccanismo, gli altri modi fuori dai quindici e il rimedio sono di
un lotto suo prima di G1.

## Che cosa non so

- Se altri modi fuori dai quindici di ADR-099 sono cambiati coi rimedi: qui si sono corsi solo quelli dei
  finali (NC-076).
- La curva vera del TV4 (pesa solo se si adotta il candidato).
- Le cifre di distorsione restano di modello (CLAUDE.md): il confronto fra varianti sullo stesso banco è
  la grandezza credibile, non il valore assoluto.

## Le voci

- **Chiusa NC-056** (ADR-106).
- **Aperta NC-076** (maggiore, prima di G1).
- **17 voci aperte, 1 bloccante** (NC-044, per G2); **nessuna bloccante per G1**.
- Limitations **#82** (il VJC del MJE253) e **#83** (l'emettitore su 1 TΩ in una ricetta).

## Il lotto dopo

**L58**, la diagnosi e la distinta dell'alimentatore (prompt in `NEXT-SESSION.md`); NC-076 a un lotto
suo prima di L64.
