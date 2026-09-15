# L31 — I vettori di rumore di `tb_noise_vectors.cir` (2026-09-15)

Lotto **L31**. Chiude **NC-030**. Nessuna ADR. Dati: `data/2026-09-15/L31/`
(vedi il suo `README.md`).

**Ogni cifra di rumore di questo report è un pavimento senza 1/f.** Si simula
coi segnaposto a `KF = 0`, LSK489X compreso, più il modello LS352 del
costruttore (NC-004, NC-031).

## 1. La baseline

`tb_noise_vectors.cir` di `main` rieseguito con `run_simulation.sh`
(`prima/tb_noise_vectors/`):
- **una** riga `Error:` nel log, riga 485: `Error: no such vector onoise_q123`;
- ngspice rc **0**;
- nessun file `wrdata`, JSON a **0 righe**.

Il guardiano di `main` sui 17 deck esce **rc 0**, e conta questo deck come «OK
(0 citations)». Lo stesso vale per i 16 deck di `6748fbc`, prima di L27.

## 2. Prima il guardiano

`scripts/check_deck_refs.py` (blocco **2g**) controlla ora ogni
`onoise_<x>`/`inoise_<x>` di un deck.
- **Dove guarda**: fuori dai commenti e fuori dalle stringhe fra virgolette.
  `tb_uscite_fisse.cir` scrive `onoise_total_v` e `tb_trim.cir` `onoise_uv`
  come **intestazioni di CSV** dentro un `echo`, e senza togliere le virgolette
  sarebbero falsi allarmi.
- **Cosa accetta come `<x>`**:
  - un vettore del circuito, `spectrum` o `total`;
  - un nome definito dal deck con `let`;
  - un dispositivo;
  - un dispositivo più un suffisso di sotto-sorgente.
- **I suffissi sono letti, non ricordati.** Un deck sonda con una R, un D, un Q
  e un J, con ogni parassita non nullo, seguito da `display`, dà:

  | Tipo | Suffissi |
  |---|---|
  | R | `1overf`, `thermal` |
  | D | `1overf`, `1overfsw`, `id`, `idsw`, `rs`, `rsw` |
  | Q | `1overf`, `ib`, `ic`, `rb`, `rc`, `re` |
  | J | `1overf`, `id`, `rd`, `rs` |

  Il log dei deck tronca i nomi a 15 caratteri: il `d102_ids` di L27 è
  `d102_idsw`.

**Fatto cadere, prima di toccare il deck:**
- sui 17 deck di oggi, **rc 1 con esattamente 4 MISSING** (`onoise_q123`,
  `onoise_r121`, `onoise_jq110`, `onoise_jq111`), tutti in
  `tb_noise_vectors.cir:55`; gli altri 16 deck OK;
- `run_tests.sh`: **7 passed, 1 failed**, il 2g;
- sui 16 deck pre-L27, con l'include di allora: gli stessi 4 nomi e nient'altro;
- **13 sabotaggi su 13** come attesi (`esplorazione/sabotaggi_guardiano.txt`):
  - **passano** `_rb`, `_1overf`, `_idsw`, `_thermal`, gli elementi del deck,
    `let`, le virgolette, i commenti e `onoise_total`;
  - **cadono** un suffisso falso, un `inoise` morto, un nome morto in `wrdata`,
    `onoise_uv` senza `let` e `onoise_thermal` senza dispositivo.

## 3. I nomi, da una mappa per nodi

`esplorazione/script/map_noise_names.py` confronta la riga `wrdata` di L4
(`dd6fd14`) con l'include di oggi, per tipo e tupla di nodi. Include e deck di
allora sono esportati con `git show`. Lo script rifiuta su zero corrispondenze o
su più d'una (#23); non ne ha trovate.

| L4 | Nodi | Ruolo | Oggi | Il nome di L4, oggi |
|---|---|---|---|---|
| q123 | NHI NMIRI NME2 | specchio, uscita | **Q121B** | morto |
| q122 | NMIRI NMIRI NME1 | specchio, diodo | **Q121A** | **vivo, è il VAS** |
| r138 | OUT FB | R_f | **R136** | **vivo, è R_g** (FB RG) |
| r121 | VPLUS NME2 | degenerazione, uscita | **R120** | morto |
| r120 | VPLUS NME1 | degenerazione, diodo | **R119** | **vivo, è l'altra degenerazione** |
| rsrc | SRCN IN | sorgente | rsrc | giusto |
| jq110 | D1N G1 S1 | coppia d'ingresso | **JQ110A** | morto |
| jq111 | D2N G2 S2 | coppia d'ingresso | **JQ110B** | morto |

**Tre nomi vivi erano già il dispositivo sbagliato**, ed è il secondo modo di
limitations #22: nessun controllo di esistenza lo vede, nemmeno il 2g esteso.
- Il deck non ha scritto colonne sbagliate solo perché i quattro nomi morti
  fermavano il `wrdata`.
- NC-030 elencava solo i morti.
- Il mandato suggeriva «VAS Q122», che nella lista di L4 non c'era.

## 4. La correzione e i dati

Nel deck cambiano solo la riga `wrdata` e i commenti: la legenda delle colonne,
la mappa e la nota su 1/f. La frase sulla provenienza dell'LSK489 resta: è
NC-031, lotto L33.

Riesecuzione (`dopo/tb_noise_vectors/`):
- ngspice rc 0;
- **0** righe `Error`;
- CSV di **2 righe** e 20 colonne.

Il guardiano esce rc 0 sui 17 deck; `run_tests.sh` **8 passed, 0 failed**.

## 5. Il riscontro

`esplorazione/script/riscontro.py`, uscita in `esplorazione/riscontro.txt`. Tutti
i controlli tengono, a 1000 Hz.

| Controllo | Esito |
|---|---|
| CSV contro `print all` | 10 valori su 10 alle 7 cifre del log |
| Totali per dispositivo | 42 nel log = 42 R/D/Q/J di include e deck |
| Quadratura | √Σ = **8,605323e-09**, `onoise_spectrum` **8,605323e-09**, scarto +5,6e-08 |
| Gli 8 scritti | sono **i primi 8**, **85,21 %** della potenza |
| Contro `tb_noise_breakdown` B di L27 | `onoise` scarto 0, `inoise` −1,4e-08, al punto più vicino (1002,37 Hz) |

La classifica a 1 kHz, in quota della potenza di rumore:

| # | Dispositivo | Quota |
|---|---|---|
| 1 | R136, R_f | 33,51 % |
| 2 | R120, degenerazione dello specchio | 10,39 % |
| 3 | R119, degenerazione dello specchio | 10,37 % |
| 4 | RSRC, sorgente da 430 Ω | 9,60 % |
| 5 | Q121B | 8,00 % |
| 6 | Q121A | 6,05 % |
| 7 | JQ110B | 3,66 % |
| 8 | JQ110A | 3,62 % |
| 9 | Q122, il VAS | 2,94 % |

**Il riscontro è stato fatto cadere.** Sui dati di oggi, con la riga `wrdata` del
deck di `main`, esce rc 1 con **8 rifiuti** (`esplorazione/riscontro_sabotato.txt`):
- **7 colonne su 10**;
- **la classifica**: i dispositivi scritti porterebbero il 22,93 % della potenza
  e non sarebbero i primi 8.
Cosa avrebbero scritto i tre nomi vivi sbagliati:

| Nome | Avrebbe scritto | Invece di |
|---|---|---|
| `onoise_q122` | 1,474e-09 | 2,117e-09 |
| `onoise_r138` | 1,09e-12 | 4,98e-09 |
| `onoise_r120` | 2,774e-09 | 2,771e-09 |

Il caso di `onoise_r120` è numericamente quasi indistinguibile. Nessun confronto
di valori l'avrebbe visto.

La prima esecuzione del sabotaggio si è fermata con un `KeyError` invece di un
rifiuto ordinato. Lo script è stato corretto e rieseguito, sia sul caso vero sia
sul sabotaggio.

## 6. Due frasi che non erano vere

- **Il mandato**: «`tb_noise_breakdown.cir` stampa la ripartizione per
  dispositivo a 1 kHz». Non la stampa.
  - Calcola la `noise` a 1 kHz e fa subito `destroy all`, e il suo log dice solo
    `No. of Data Rows : 2`.
  - Il riscontro per dispositivo è quindi la quadratura sui totali di questo
    deck; il confronto con quel deck resta sullo spettro.
- **NC-030, «Perché minore»**: dava la stessa ripartizione per presente in
  `tb_noise_breakdown.cir`. La severità non cambia, perché nessun verdetto
  poggiava su nessuno dei due; la «Chiusura» della voce lo registra.

## 7. Cosa resta fuori

- **Un nome vivo sbagliato** in un vettore di rumore resta invisibile al 2g.
  L'unico rimedio è quello di #22: mappa per nodi e confronto dei numeri a ogni
  rinumerazione.
- **NC-031** (L33): la provenienza dichiarata dell'LSK489.
- **Osservato, non indagato**: `testbenches/01_op.cir` scrive il suo `wrdata` su
  un percorso assoluto, `/Users/roberto/EDA/results/01_op.csv`. Il blocco 2b
  lanciato da un worktree legge e scrive quindi nel checkout principale. Non
  riguarda il prodotto.

## 8. Conteggi

**15 voci aperte, 2 bloccanti** (NC-004, NC-017). Prossimo lotto: **L33**.
