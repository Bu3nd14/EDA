# Dati di L13 — E4 sulle tre uscite e a manopola che gira (2026-09-15)

Lotto **L13**, report `reports/2026-09-15-L13-e4-tre-uscite.md`. Chiude
**NC-008**, apre **NC-033**.

**Topologia**: quella di `main` a `74e762c` (L16, L17, L27). **Nessun valore
del circuito cambia.**

**Provenienza dei modelli**, letta dagli `.include` dei deck:
- LSK489 = `LSK489X`, segnaposto con `KF = 0`
  (`spice/preamp/placeholder_devices.lib`);
- l'unico modello del costruttore è l'LS352 (`models/bjt_pnp/ls350.lib`),
  senza `KF`;
- ogni altro dispositivo è un segnaposto scritto a mano (NC-017).

Per E4 il rumore 1/f non conta. Contano le transconduttanze dei segnaposto: la
Zout del nodo del blocco (~0,04 Ω) è una cifra del modello. Al jack domina la
47 Ω.

Tutti i deck girano con `scripts/run_simulation.sh`, ngspice rc 0, **0 righe
`Error`**. In ogni log compaiono 2 righe «warning, model type mismatch» su
`q121a`/`q121b ... ls350`, preesistenti: le stesse 2 stanno nei log di
`data/2026-09-14/L27/dopo/`. Si versionano `.csv` e `.log`; i `.txt` grezzi di
`wrdata`, i `.json` e i deck risolti no.

## `prima/tb_zout_psrr_noise/` — il deck di `main`, rieseguito senza modifiche

**Identico** a `data/2026-09-14/L27/dopo/tb_zout_psrr_noise/`:
- 14 CSV byte per byte;
- il log riga per riga, a meno delle righe con un percorso
  (`esplorazione/script/confronta.py`).

È la baseline del difetto: la sezione Zout lasciava `VSRC` a 1 V AC.

## `dopo/tb_zout_psrr_noise/` — lo stesso deck, sezione Zout a sorgente spenta

Unica modifica: `alter @vsrc[acmag] = 0` prima della sezione Zout, `= 1` dopo,
più un commento.
- **PSRR e rumore identici** a `prima/`: 10 CSV byte per byte, più
  `tb_zout_psrr_noise.csv`.
- Cambiano solo i 3 CSV `_zout_` e le righe Zout del log:

| | 0 dB prima → dopo | +3 dB prima → dopo | +10 dB prima → dopo |
|---|---|---|---|
| \|Z\| jack 1 kHz | 58,759 → **57,945** Ω | 59,113 → **57,954** Ω | 60,585 → **57,991** Ω |
| \|Z\| jack 20 kHz | 48,047 → **47,048** Ω | 48,488 → **47,071** Ω | 50,306 → **47,189** Ω |
| \|Z\| nodo OUT 1 kHz | 1,0355 → **0,0386** Ω | 1,4704 → **0,0549** Ω | 3,2621 → **0,1217** Ω |

## `dopo/tb_e4_uscite/` — il deck nuovo, `spice/preamp/tb/tb_e4_uscite.cir`

La catena intera, tutta in subckt: A → F1 / F2 → trim → attenuatore → B.
Matrice: trim {0, −6, −12} × attenuatore {0, 25, 50, 75, 100 %} × modo
{0, +3, +10 dB}, cioè 45 celle.

| File | Cosa |
|---|---|
| `tb_e4_uscite_tab.csv` | 135 righe: `out` (main, fix1, fix2), `trim`, `att`, `mode`, poi `zrmax` = max Re(Z) su 20 Hz–20 kHz, `zr20`/`zr1k`/`zr20k` = Re(Z) al jack, `zm20`/`zm1k` = \|Z\| al jack, `zn1k`/`zn20k` = \|Z\| al nodo del blocco prima della 47 Ω. Ohm |
| `tb_e4_uscite_guadagno.csv` | 45 righe: `g1k_db` = vdb(MAINJACK) a 1 kHz, carichi nominali, 1 V AC: il controllo positivo |
| `tb_e4_uscite_z_<out>_<modo>.csv` | curve a trim 0 e attenuatore al 50 %: col1 Re(Z), col3 \|Z\|, col5 \|Z\| nodo; colonne pari = frequenza |
| `tb_e4_uscite.log` | log completo |

### Numeri chiave

Dal verificatore `esplorazione/script/e4.py`, uscita 0, controlli A–G tutti
passati; esito in `esplorazione/e4_verdetto.txt`.

| Uscita | Celle | Re(Z) max 20 Hz–20 kHz | Re(Z) 1 kHz | \|Z\| 1 kHz | Nodo 1 kHz | Dispersione su trim × attenuatore |
|---|---|---|---|---|---|---|
| MAIN 0 dB | 15 | 60,0504 Ω | 47,0313 Ω | 57,9449 Ω | 0,03864 Ω | < 1e-4 Ω |
| MAIN +3 dB | 15 | 60,0656 Ω | 47,0465 Ω | 57,9539 Ω | 0,05485 Ω | 1e-4 Ω |
| MAIN +10 dB | 15 | 60,1281 Ω | 47,1092 Ω | 57,9914 Ω | 0,1216 Ω | 1e-4 Ω |
| FIX1, tutti i modi | 45 | 53,1318 Ω | 47,0339 Ω | 57,9515 Ω | 0,03864 Ω | 0 |
| FIX2, tutti i modi | 45 | 53,1318 Ω | 47,0339 Ω | 57,9515 Ω | 0,03864 Ω | 0 |

- Il massimo di Re(Z) cade a **20 Hz** su tutte e tre le uscite: è lo scarico
  (220 kΩ sulla principale, 470 kΩ sulle fisse) in parallelo al condensatore.
- FIX1 riproduce **53,1318 Ω** di L17 e L27 a tutte le cifre.
- MAIN riproduce il \|Z\| 1 kHz del deck flat corretto a 6 cifre.
- **Controllo positivo**: a trim 0 e attenuatore al massimo −0,011 / +3,035 /
  +9,956 dB; al 50 % −6,05 dB; al 25 % −12,07 dB; al minimo ≤ −130 dB. Trim −6 e
  −12 spostano di −6,00 e −11,94 dB. Tutto entro 0,15 dB dall'atteso.

## `esplorazione/`

| File | Cosa |
|---|---|
| `script/confronta.py` | due cartelle di output: CSV byte per byte, log senza le righe coi percorsi |
| `script/e4.py` | il verdetto. Controlli: A completezza, B tabella = log, C controllo positivo, D sonda al jack, E soglia 100 Ω, F costanza < 1 Ω (lettura del lotto), G numeri noti |
| `e4_verdetto.txt` | l'uscita di `e4.py` su `dopo/tb_e4_uscite/` |
| `falsi/genera.py` | 8 copie sabotate di `tb_e4_uscite.cir`; rifiuta se una sostituzione non compare quante volte attesa |
| `falsi/c*.cir` | le copie, deck risolvibili con `@REPO@` |
| `falsi/verifica.py`, `falsi/esito.txt` | ogni copia giudicata da `e4.py` (o dal 2g per `cf`): **8 su 8 rifiutate come attese** |

Le cartelle `falsi/out_<x>/` non sono versionate. Per rifarle:
1. `run_simulation.sh falsi/c<x>.cir falsi/out_<x>` per ogni copia;
2. `verifica.py <repo>`.

I sabotaggi, e cosa li ha fatti cadere:

| | Sabotaggio | Cade su |
|---|---|---|
| a | `VSRC` accesa durante l'iniezione | F (MAIN non costante, fino a 3,1 Ω), G (fisse 54,13 invece di 53,13), D |
| b | sonda del MAIN su `BOUT` invece del jack | D (Re(Z) 0,036 Ω, niente condensatore), G |
| c0 | attenuatore scollegato, gate a 2,5 k fissi | A: segnale zero esatto, `vdb(0)` dà `Error` (#28), guadagni vuoti. **Prima forma di c: non esercitava C** |
| c | attenuatore scavalcato: gate sull'uscita del trim | **C soltanto**: la sua tabella Zout è identica a quella vera, e senza il controllo positivo passerebbe |
| d | iniezione sul cursore: il passivo di ADR-002 | D, E, F (0,001 … 2599 Ω), G |
| e | FIX2 iniettata, letta su FIX1 | D (diafonia ~0 Ω), G |
| f | RG10 di B non terminato | 2g: 3 MISSING, 1 DANGLING |
| g | K1 non chiude mai | C (a +3 dB il guadagno resta quello di 0 dB) |
