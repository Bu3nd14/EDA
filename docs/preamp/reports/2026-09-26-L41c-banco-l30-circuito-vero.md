# L41c — il banco di L30 col circuito vero dell'alimentatore (2026-09-26)

**Mandato**: NC-036 punto 2. Il banco di L30 (ADR-046, P9) si rifà con l'alimentatore di
`circuits/preamp/psu.py` e il firmware del temporizzatore, al posto delle PWL e degli istanti
disegnati a mano. Con l'utente, la decisione sul corto dell'uscita di U503. Decisione:
**ADR-051**. Dati: `data/2026-09-26/L41c/` (README).

**Non toccati**: `psu.py`, la scheda audio (`preamp_audio.py`) e il firmware.

I transitori sono detti in **dB SPL di picco a 1 m** con la formula di NC-028: 100 µV ≈ 33,45 dB,
poi 20 log10 del rapporto. È un limite superiore.

**Sintesi.**
- **Tutto sotto la sua soglia**:
  - lo spegnimento morbido a 30 nV, contro i 100 µV di V2;
  - la perdita di rete, U501, U502 e U503 spenti a ≤ 1,37 mV, contro l'obiettivo di 2 mV.
- **Il controfattuale senza Δ fallisce**, come deve: ≥ 66 mV.
- **Il corto della linea a 12 V dei relè** dà 69,4 mV (~90 dB). L'utente lo accetta come guasto
  singolo sotto il tetto: ADR-051.
- **NC-036 chiusa.** Resta una sola voce bloccante, NC-004, per G1.

## 1. La catena, in due tempi

Una scheda sola non sta in un deck. La catena va quindi in due tempi, e in un senso solo:

1. **L'alimentatore** (`psu/`): il banco di L41b2, copiato ed esteso con nove casi. Ogni caso
   parte dal circuito di `psu.net` col core del firmware come micro, ed è iterato fino al punto
   fisso (`corri_seq.sh`).
2. **Il ponte** (`ponte/estrai_ponte.py`): dal giro al punto fisso scrive, per ogni caso, un JSON
   con:
   - i due rail;
   - le correnti delle due stringhe LED, dai 10 Ω di sense;
   - gli istanti dei contatti, all'**angolo peggiore del G6K** (en-g6k.pdf p. 2, bobina 12 V):
     - il jack si apre **il più tardi possibile**: bobina sotto 1,2 V (il 10 % del rilascio
       garantito), più 3 ms di rilascio massimo;
     - il guadagno cade **il più presto possibile**: bobina di K6, o `VRELAY`, sotto 9,6 V
       (l'80 % dell'eccitazione), più 0 ms.
3. **La scheda audio**: il generatore di V2 esteso con `--matrice l41c`. Stesse basi di L30:
   - sul sorgente: geometria iii, bleed dalla netlist, gemello di K1/K5;
   - senza segnale, +10 dB, 100 kΩ, 0 pF di cavo.

   Le correnti del ponte sostituiscono BILS/BILP, e portano da sé la cima a 12 mA di ADR-050.
   Ogni caso ha il **suo riferimento**: gli stessi punti fino a `t_ins`, poi fermi, e i contatti
   fermi.

**Cosa la catena non vede.**
- Nell'alimentatore la scheda audio è un carico: 56,6 Ω per rail, non la corrente vera dei blocchi
  mentre il rail scende.
- Le corse dell'alimentatore girano a 25 °C.

**I controlli di non regressione**:
- il deck V2 versionato (`--matrice sorgente`) e il deck di L30 (`--matrice l30`), rigenerati dal
  generatore esteso, sono **byte-identici**;
- `controlla_deck.py` rifiuta un deck con BILS/BILP diversi da quelli del ponte.

## 2. I criteri, scritti prima delle corse

**Sul lato alimentatore** (`psu/analizza_seq.py`):
- in ogni caso: il punto fisso, e C2 e C3 di L41b2;
- **r**: il jack si apre (al più tardi) prima che il guadagno possa muoversi (al più presto);
- **s**: il jack si apre prima che V+ scenda a 10,6 V, la perdita della regolazione di L30;
- più i criteri di L41b2 del caso corrispondente.

**Sulla scheda audio** (`script/tabella.py`):
- spegnimento ≤ 100 µV (V2);
- perdita di rete e guasti ≤ 2 mV, l'obiettivo di ADR-046, e sotto il tetto di 0,87 V;
- il controfattuale **> 2 mV**;
- il corto di U503 senza verdetto, perché lo decide l'utente.

## 3. Il lato alimentatore: 9 casi su 9

`seq/analisi_seq.txt`. Istanti da TE, l'evento.

| Caso | Punto fisso | Jack aperto (tardi) | Guadagno (presto) | V+ < 10,6 V |
|---|---|---|---|---|
| spegnimento morbido (dal frontale) | giro 2 | 6532,3 ms | 6569,1 ms | 6813 ms |
| perdita di rete | giro 3 | 17,4 ms | 34,7 ms | 183 ms |
| perdita di rete, Δ all'angolo minimo | giro 3 | 17,4 ms | 33,4 ms | 183 ms |
| U501 spento (rail +) | giro 2 | 13,1 ms | 30,4 ms | 34,8 ms |
| U502 spento (rail −, il caso di L41b2) | giro 2 | 13,7 ms | 31,0 ms | — |
| U503 spento (`VRELAY_REG`) | giro 2 | 15,8 ms | 33,1 ms | 253 ms |
| U503 spento, angolo minimo | giro 2 | 15,6 ms | 31,6 ms | 253 ms |
| **controfattuale**, C528 a 10 pF | giro 3 | 17,4 ms | **14,4 ms** | 183 ms |
| **corto** dell'uscita di U503 | giro 2 | 3,1 ms | **0,1 ms** | 183 ms |

- Nello spegnimento lo stato finale è STANDBY, e i criteri i, j, k, l di L41b2 passano:
  - `MUTE_CMD` è rilasciato 6,522 s dopo il pin;
  - K501 si apre 63,4 ms dopo `PERMIT_CMD`.
- Nel controfattuale C3 e r falliscono, come devono: Δ = 0.
- **Lo spegnimento finisce a TE + 7,6 s.** Il primo giro fino a TE + 7,8 s si è fermato a
  TE + 7,641 s su «Timestep too small» in `xu511a.bout`, lo stesso nodo che aveva fermato L41b2.
  In quell'istante i rail erano a +0,73 / −0,70 V e le stringhe a 5 nA: dopo tutto quello che
  V2 legge. Il ponte tiene i rail fermi da lì in poi (a +0,83 / −0,81 V).

## 4. La scheda audio

`tabella.csv`. 17 corse su 18 fino in fondo, log puliti.

| Caso | Picco A_ins al jack | dB SPL di picco a 1 m | In L30 | Esito |
|---|---|---|---|---|
| spegnimento morbido | 30 nV (principale) | −37 | 0,07–2,7 µV | sotto V2 di 70 dB |
| perdita di rete | 0,12 µV | −25 | 0,51–1,36 mV (s) | sotto l'obiettivo |
| perdita di rete, angolo minimo | 0,18 µV | −22 | — | sotto |
| U501 spento | 1,03 mV | 54 | 1,04–1,77 mV (p) | sotto |
| U502 spento | **1,37 mV** | **56** | 1,18–1,62 mV (m) | sotto, il più vicino (3,3 dB) |
| U503 spento | 75 nV | −29 | come F (G) | sotto |
| U503 spento, angolo minimo | 75 nV | −29 | — | sotto |
| controfattuale senza Δ | **≥ 66 mV** | **≥ 90** | 69 mV | fallisce, come deve |
| corto della linea a 12 V | **69,4 mV** | **90** | = senza Δ | sotto il tetto di 22 dB (ADR-051) |

**Perché la perdita di rete è ~10⁴ volte sotto L30.** L30 faceva scendere i rail da subito, con la
pendenza di 265 mA sulla tenuta, e il jack era ancora collegato mentre il rail passava da 15 a
13,5 V. Sul circuito vero:
- i serbatoi grezzi tengono i regolatori in regolazione;
- il rivelatore di rete stacca il jack a 17,4 ms, con i rail ancora a 15 V;
- V+ scende sotto 10,6 V solo a 183 ms.

Nei guasti di U501 e U502 il rail scende invece subito, e le cifre tornano quelle di L30.

**Un numero piccolo deve provare di contenere l'evento** (`script/verifica_eventi.py`). Su
`MAIN_A`, l'uscita del blocco prima del relè, il cambio di guadagno sposta l'uscita di 0,29 V in
ogni caso, e U501 di 2,86 V. Al jack non arriva, perché il contatto è già aperto e il lato del
condensatore è a massa (119 µV su `MAINC`). Nel corto, `MAINC` vede 67 mV prima che il jack si
apra.

**Il controfattuale si ferma all'apertura del jack.** Si ferma a 1,0178 s su «Timestep too small»
nel JFET d'ingresso (`xa.jq110a`), 3 ms dopo il cambio di guadagno a jack collegato. Fanno lo
stesso `method=gear`, un passo massimo di 1 µs e reltol 1e-5: la forma già vista in due
controfattuali di L30. Dopo l'aborto il `.dat` è tutto zeri (limitations #35).

Il picco grezzo fra il cambio di guadagno e l'aborto (`script/cf_fino_all_aborto.py`) è
**66,5 mV** sul jack principale, 0,3 ms dopo il cambio. È un limite inferiore, e basta per un
criterio che chiede di superare 2 mV. Coincide con i 69 mV di L30 e con i 69,4 mV del corto,
che ha la stessa sequenza (guadagno prima del jack) ed è arrivato in fondo. **Il banco vede Δ.**

## 5. La decisione dell'utente: il corto della linea a 12 V dei relè

Portata coi numeri. Il corto dà 69,4 mV, ~90 dB SPL di picco a 1 m: 22 dB sotto il tetto
(~112 dB), 30 dB sopra l'obiettivo (~60 dB).

La causa: C523 (la tenuta), C524 e U504 (il micro) stanno sullo stesso nodo `VRELAY_REG`, e da lì,
attraverso Q505, passano a tutte le bobine. Un corto in un punto qualsiasi della linea scarica
la tenuta.

Le due strade:
1. accettarlo come guasto singolo sotto il tetto, come il corto di un rail in ADR-046;
2. una tenuta separata per le bobine di K6 e K1/K5 dietro un diodo. Copre solo una parte dei
   corti, chiede un pin in più su J1, e sarebbe stato un lotto a sé.

**L'utente**: «accetto la 1, scrivi l'ADR e chiudi NC-036». **ADR-051.**

## 6. Una trappola nuova: `alter: too many args.` (limitations #36)

Un `alter @v[pwl] = [ … ]` con 1000 numeri o più viene ignorato. ngspice stampa solo quella riga
ed esce 0, e la sorgente resta com'era: 400 punti passano, 500 no. Trovata prima delle corse, con
un deck di prova il cui minimo restava a 15,000 V. Il ponte riduce ogni PWL a ≤ 350 punti
(Douglas-Peucker; lo scarto massimo è ≤ 0,5 mV sui rail ed è scritto nel JSON), e
`controlla_deck.py` fa da guardia.

## 7. Cosa cambia nel repo

- `docs/preamp/data/2026-09-26/L41c/`: `psu/`, `seq/`, `ponte/`, `deck/`, `corse/`, `script/`,
  `tabella.csv`, README;
- `docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py`: `--matrice l41c
  --ponte`. Il deck V2 e il deck di L30 rigenerati sono byte-identici;
- `docs/preamp/decisions/ADR-051-corto-linea-rele-guasto-accettato.md` e il suo indice;
- `NONCOMPLIANCE.md`: **NC-036 chiusa**; 10 voci aperte, 1 bloccante (NC-004);
- `docs/limitations.md`: la #36;
- `.gitignore`: le forme d'onda di L41c.

## 8. Quello che resta

- **NC-004**, bloccante per G1: il rumore 1/f fuori dalla coppia d'ingresso.
- **L28**, prima di G2.
- **NC-037**: il giro BOM di T2, a G2.
- **NC-011**: la quota di ADR-020 coi TPS7A4701.
- **Da fare sul prototipo**:
  - i tempi dei relè (rilascio e soglie reali del G6K);
  - la risposta del blocco al calo del rail nel guasto di U502, il caso più vicino all'obiettivo
    (3,3 dB).
