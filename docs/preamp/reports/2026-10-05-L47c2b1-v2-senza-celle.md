# L47c2b1 — il mute coi soli relè: V2 senza celle, la matrice e il clic del taglio

Data: 2026-10-05 · Lotto: L47c2b1 · Decisioni: **ADR-063** (nata qui); esegue ADR-062.
Dati: `data/2026-10-05/L47c2b1/` (README).

## In breve

- **V2 regge col mute che taglia**: la matrice del deck versionato, 145 corse sul sorgente (geometria
  iii), **0 verdetti fuori su 247**.
- **Il clic del taglio è dichiarato**: la tabella intera, 18 valori, accanto al taglio ideale.
  All'inserimento il circuito sta 0,15–0,44 dB sopra il taglio ideale. Al rilascio a 1 kHz sta
  +4,6 dB (principale) e +5,2 dB (fisse) sopra: sono i rimbalzi del contatto che chiude sulla
  musica. A 20 Hz il rilascio è 25,7 dB **sotto** il taglio ideale: il condensatore d'uscita
  riporta la musica gradualmente.
- **NC-049 chiusa per superamento, NC-053 chiusa.** 15 voci aperte, 4 bloccanti.
- **Due problemi trovati sulle corse, decisi dall'utente** (ADR-063):
  - il banco si fermava a ogni chiusura del contatto in serie sulla musica;
  - con un taglio netto il residuo filtrato misura il taglio, non la musica che passa.

## All'inizio, con l'utente (per nome, in dB SPL)

- **Dividere L47c2b**: **«Due parti»**. L47c2b1 (questo) la matrice V2 senza celle e il clic;
  **L47c2b2** la catena dei guasti di L41c, i 21 deck veloci, il firmware sull'host.
- **Il clic**: **«Tabella intera»**. Principale e due fisse, 20 Hz / 1 kHz / 20 kHz, inserimento
  e rilascio, 18 valori in picco e dB SPL a 1 m, il peggiore in cima.

## Il banco senza celle

- **`genera_tb_v2_casopeggiore.py`** (L29c):
  - via le due celle, il loro comando, `VPWL` e `alter rsrc`: la sorgente torna sulla `RSRC` del
    blocco, come nella cella di L40;
  - i tempi dal firmware di L47c2a: il contatto in serie si muove **24 ms** dopo il tasto
    (`MUTE_CMD` 21 ms, più 3 ms del G6K), la derivazione 1 ms dopo;
  - `conta` da `S_*` a `C2_*` dichiarati; via la corsa «senza relè» (senza celle non è un mute);
  - via le matrici `l29c` (le inversioni) e `curve` (le curve della cella): rifiutano, col commit
    `dffa7148`;
  - `clic()`: i 20 kHz a 100 k e i tre toni a 10 k;
  - `l41c` senza le correnti dei LED.
- **`tb_v2_mute_ldr.cir` → `tb_v2_mute_taglio.cir`** (`git mv` del deck e del generatore): senza
  celle, `norele` e inversioni, 30 corse. Resta sulla geometria N del blocco: è il riferimento
  semplice e il termine del controfattuale.
- **`scripts/v2_metodo.py`**: S tolto (costanti, `ampiezza`, `salto_db`, T15–T19, due
  sabotaggi); C2 è il clic del taglio, dichiarato.
- **Il controfattuale**: il deck versionato con tutte le aggiunte in posizione neutra contro la
  cella a 1 kHz e 100 k del deck del taglio. C2 identico all'inserimento, 0,03 % al rilascio, B2
  0,06 %, senza segnale entrambi al pavimento (~10⁻¹¹ V). `controfattuale/confronto_taglio.csv`.
- **Una trappola evitata**: `L29c/script/verifica_partenza.py` legge le colonne degli stati per
  posizione. Senza le tre colonne delle celle avrebbe letto altre grandezze, senza errore. Una copia
  con gli indici nuovi e il controllo della forma sta in `script/`.

## La prima matrice si ferma: la sonda

La prima matrice (`matrice_interruttore/`) ha dato **34 corse fermate su 145** su «Timestep too
small», tutte quelle con la musica dove il contatto in serie si muove. Il log accusa il JFET
d'ingresso; le forme d'onda dicono altro. A 1,0244 s il rimbalzo del modello di L29c **richiude**
la serie, 400 µs dopo l'apertura, col lato condensatore a −12,02 V e il jack a −3 µV.

| Prova | Esito |
|---|---|
| `trtol=1`, `+ rshunt=1e12`, `method=gear` | ferme a 1,0244 s |
| cavo al jack 100 pF | ferme a 1,0244 s |
| apertura della serie senza rimbalzo | 20 Hz corre; 1 kHz si ferma alla chiusura del rilascio |
| la serie = `BSERx` del blocco, fronte ~4,55 µs | **corrono tutte** |

L'interruttore ideale del banco (100 mΩ ↔ 1 TΩ, tempo zero) non regge una chiusura su volt di
musica, e al rilascio la chiusura sulla musica c'è sempre. Il contatto comportamentale contro
l'interruttore ideale (con l'apertura netta), sulla stessa corsa a 20 Hz:

| | Comportamentale | Ideale |
|---|---|---|
| C2 all'inserimento | 9,015 V | 8,939 V (+0,8 %: il rimbalzo che l'apertura netta non ha) |
| C2 al rilascio | 0,4723 V | 0,4728 V |
| B2 | 0,732 V | 0,700 V |
| senza segnale | al pavimento | al pavimento (~10⁻¹¹ V) |

**Trovato con la sonda: con la musica B2 misura il taglio.** Sulla principale a 20 Hz:

| | Valore |
|---|---|
| B2 (filtrato da t = 0, picco da 20 ms dopo il contatto) | 0,732 V |
| lo stesso metodo sul taglio ideale | 0,698 V |
| il jack grezzo nella stessa finestra | **4,3 µV** |
| il riferimento sempre in mute | 0,45 nV |

**Le scelte dell'utente**, con questi numeri in dB SPL:
- **«Musica che passa davvero»**: con la musica il verdetto è sul jack grezzo nella finestra del
  mute (B2g) e sul riferimento sempre in mute (B1); B2 filtrato va col clic;
- **«Tutta la matrice»**: il contatto comportamentale in tutte le 145 corse.

→ **ADR-063** (precisa ADR-032 e ADR-062); nota in `REQUIREMENTS.md`, V2. `v2_metodo.py` ha
`b_grezzo`, B2g in `analizza`, il controllo T15 (un taglio ideale da 12 V a 20 Hz: filtrato
0,803 V, grezzo 0) e il sabotaggio `b_grezzo_filtrato`: **24 controlli, 13 sabotaggi su 13**.

## La seconda matrice

- **Le finestre di A**: la prima stesura dei tempi lasciava 0,5 s fra il contatto e il cambio di
  guadagno (prima la sfumatura ne dava 3), e A all'inserimento usciva «finestra corta: non
  accetta» su 29 righe. I valori erano 0,03–18 nV, ma il metodo vuole ≥ 2 s. Corretto nel
  generatore:
  - il cambio a contatto + 2 s;
  - il mute semplice della dispersione tenuto 2 s;
  - sui mute di 0,1 e 1 s conta il rilascio: la stessa inserzione conta su quelli di 2 e 20 s.

  Ricorse le sole 84 corse che cambiano (`script/da_rifare.py` confronta il deck nuovo con le
  corse già fatte; i `.dat` superati in `matrice/superate/`).
- **Le corse**: 144 su 145 passano la guardia (#35, #36, #42) e partono dal punto giusto (#33).
  Fallisce `off_r10m_d20_iii`, uno spegnimento brusco di L29c, escluso dal verdetto come in L29d2
  e L47b2b1.

### Il verdetto (`matrice/verdetto.csv`): 0 fuori su 247

| Gruppo | Senza segnale: A | Senza segnale: B2 | Con la musica: jack grezzo (B2g) | Con la musica: sempre in mute (B1) |
|---|---|---|---|---|
| 1 guadagno sotto mute | ≤ 0,123 µV | ≤ 0,005 µV | ≤ 52,5 µV | ≤ 0,93 µV |
| 2 trim sotto mute | ≤ 0,073 µV | ≤ 0,001 µV | ≤ 37,4 µV | ≤ 0,93 µV |
| 3 dispersione | ≤ 0,424 µV | ≤ 0,018 µV | — | — |
| 4 durata del mute (anche 20 kHz e 10 k) | ≤ 0,000 µV | ≤ 0,000 µV | ≤ **55,0 µV** (20 kHz, principale) | ≤ 16,9 µV (20 kHz) |
| 5 accensione | ≤ **7,30 µV** | — | — | — |

Soglia 100 µV (~33 dB SPL). Il peggiore con la musica, 55,0 µV, sono ~48 dB SPL di picco a 1 m:
il tono di prova a piena scala che passa dal contatto aperto a 20 kHz.

### Il clic del taglio (`matrice/clic.csv`)

C2 di `v2_metodo` nella finestra [t − 20 ms, t + 224 ms], il peggiore fra 100 k e 10 k. Accanto,
il **taglio ideale**: le forme d'onda del circuito stesso, il riferimento mai in mute fino al
contatto e poi il sempre in mute (al rilascio il contrario), letto con lo stesso C2. dB SPL di
picco a 1 m con la formula di NC-028 (un limite superiore). La stessa formula sulle tre uscite,
dichiarata.

| Uscita | Tono | Evento | Carico | C2 | dB SPL | Taglio ideale | Circuito − ideale |
|---|---|---|---|---|---|---|---|
| principale | 1 kHz | rilascio | 100 k | 11,47 V | 134,6 | 6,72 V | **+4,64 dB** |
| principale | 20 Hz | inserimento | 10 k | 9,09 V | 132,6 | 8,94 V | +0,15 dB |
| principale | 1 kHz | inserimento | 100 k | 7,06 V | 130,4 | 6,72 V | +0,43 dB |
| principale | 20 kHz | rilascio | 100 k | 4,48 V | 126,5 | 4,15 V | +0,66 dB |
| principale | 20 kHz | inserimento | 100 k | 4,32 V | 126,2 | 4,15 V | +0,35 dB |
| fisse 1 e 2 | 1 kHz | rilascio | 100 k | 3,88 V | 125,2 | 2,13 V | **+5,19 dB** |
| fisse 1 e 2 | 20 Hz | inserimento | 10 k | 2,89 V | 122,7 | 2,84 V | +0,15 dB |
| fisse 1 e 2 | 1 kHz | inserimento | 100 k | 2,24 V | 120,5 | 2,13 V | +0,44 dB |
| fisse 1 e 2 | 20 kHz | rilascio | 100 k | 1,43 V | 116,6 | 1,33 V | +0,64 dB |
| fisse 1 e 2 | 20 kHz | inserimento | 100 k | 1,38 V | 116,3 | 1,33 V | +0,35 dB |
| principale | 20 Hz | rilascio | 100 k | 0,47 V | 106,9 | 9,10 V | −25,70 dB |
| fisse 1 e 2 | 20 Hz | rilascio | 100 k | 0,15 V | 97,0 | 2,89 V | −25,67 dB |

Le due fisse sono uguali in ogni cella; il CSV ha le 18 righe.

**Come si legge.**
- **Le cifre assolute sono la musica**: 12 V di picco al jack della principale (il tono di prova a
  piena scala, +10 dB) sono ~135 dB SPL con la formula. Il taglio ideale ne dà quasi altrettanti.
  Il mute che taglia **è** un salto di quell'ordine, ed è quello che PR-21 firmata dice.
- **Quello che aggiunge il circuito** è la colonna di destra:
  - all'inserimento ≤ 0,44 dB;
  - al rilascio a 1 kHz +4,6 / +5,2 dB: il contatto che chiude sulla musica rimbalza (la sequenza
    di L29c, 150–520 µs);
  - a 20 kHz ≤ 0,66 dB.
- **A 20 Hz il rilascio è dolce**: a mute inserito il lato condensatore è a massa e il 4,7 µF segue
  la musica; al rilascio il jack riparte dalla tensione del condensatore e la musica torna con la
  sua costante di tempo, non a gradino. Il taglio ideale non lo sa, e sta 25,7 dB sopra.
- **La fase** del tono all'istante del contatto è nel CSV: 90° a 1 kHz e 20 kHz (il picco),
  263–270° a 20 Hz. È la fase del deck, non un caso peggiore cercato.

**La coda del filtro dopo il taglio** (B2 con la musica, dichiarata col clic): fino a **0,88 V**
sulla principale a 20 Hz e 10 k; 6,7 mV a 1 kHz.

## Non conformità

- **NC-049 chiusa per superamento**: S tolto dal banco, la matrice senza celle e senza S.
- **NC-053 chiusa**: la musica a mute inserito regge su tutte le uscite e i tre toni.
- 15 voci aperte, 4 bloccanti (NC-040, NC-041, NC-048 per G1; NC-044 per G2). NC-050 resta al
  carico congelato.

## Verifiche

- `v2_metodo.py autotest` 24 controlli, `sabotaggi` 13 su 13; `v2_metodo.py canale` sui 5 deck V2;
  i deck generati senza `NSL32`, `XLS`, `XLP`, `BILS`, `VPWL`.
- `run_tests.sh`: vedi `STATE.md` (fine L47c2b1).

## Non fatto qui (L47c2b2)

La catena dei guasti di L41c sull'alimentatore di L47c2a (il ponte senza le correnti dei LED,
`controlla_deck.py` di L41c rifiuta il deck di oggi, provato), i 21 deck veloci, il firmware
sull'host.
