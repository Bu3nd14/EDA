# L29c — il caso peggiore di V2 col mute reale (2026-09-23)

**NC-028 resta aperta e bloccante. ADR nuova: ADR-043.** Il mute reale (LDR v4 a monte più il
relè al jack) regge in ogni condizione **con la musica**: il salto di livello S resta sotto
11 dB contro 20, anche con le curve estreme della LDR. Tre condizioni **senza musica** stanno
invece fuori dai 100 µV di A:
- il cambio di guadagno o di trim fatto a mute inserito;
- l'accensione;
- lo spegnimento.

Hanno una causa sola: il contatto di mute in derivazione (0,1 Ω dietro 47 Ω) attenua solo
~1/471 un salto in continua dell'uscita del blocco. La strada scelta dall'utente è misurare un
**contatto in serie** al jack (L29d). Lo spegnimento, e un failsafe per il guasto
dell'alimentatore, diventano requisiti di L30 (ADR-043).

- **Dati**: `data/2026-09-23/L29c/`, con README.
- **Banco**: `spice/preamp/tb/tb_v2_casopeggiore.cir`, **generato** da
  `data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py`. Blocco CANALE identico ai deck di V2
  (`v2_metodo.py canale` OK su 3 deck), 2g OK.
- **Etichetta di ogni cifra**: modelli del costruttore (L39) sul circuito di ADR-042; VTL5C4
  comportamentale dal datasheet con estrapolazione dichiarata; nessun modello porta la
  dispersione, che si inietta (§5).

## 1. Il banco, e come si è fatto fidare

Tutto si aggiunge **fuori** dal blocco CANALE:
- **K1 e K5** commutano nel tempo: interruttori nativi (`SW`, come `tb_switch_v2.cir`) in
  parallelo a RRGB/RRG10B, 0,1 Ω chiusi, coi rimbalzi del contatto al jack. Sequenza di L27: 0→+10
  con K5 per primo.
- **Il trim** di `trim.py` (845 / 464 / 464 Ω) fra OUTA e l'attenuatore, con i quattro contatti e
  1 G + 15 pF da aperti.
- **VOSA/VOSB/VOSF1/VOSF2**, e il gruppo B con `altermod` e la sonda JPRB.
- **I rail** con `alter @vpp[pwl]`, e il comando dei LED che segue il rail positivo.

Tre controlli prima della matrice:

| Controllo | Esito |
|---|---|
| La cella di L40 (1 kHz, 100 k) rifatta col deck di `main` | **identica** a L40: 132 grandezze su 132, scarto 0 |
| Il banco nuovo con le aggiunte neutre, contro quella cella (controfattuale) | S identico; A, B2, C entro **0,09 %**; solo i pavimenti numerici si muovono (diagnostica) |
| Da dove parte ogni corsa (`verifica_partenza.py`, prima riga delle forme d'onda) | 0 corse fuori su tutte le cartelle, dopo le correzioni sotto |

**Le trappole del banco, trovate e chiuse.**
1. **Il transient op** (`docs/limitations.md` #33). Col trim montato l'op della `tran` fallisce
   gmin e source stepping. ngspice ripiega su una pseudo-transitoria, scrive «finished
   successfully» e parte con OUTA a +13 V: il blocco A agganciato al rail, il jack a 13 V in
   continua dietro un condensatore. rc 0, nessuna riga `Error`. Le opzioni di solutore aggiustano
   una corsa e ne rompono un'altra.
   - Rimedio: gli interruttori nativi al posto della conduttanza esponenziale, e un `.nodeset`
     sulle uscite dei blocchi.
   - `corri.sh` rifiuta ogni corsa col transient op. Se una corsa fallisce riprova senza
     `.nodeset`, poi con un `.nodeset` esteso a INA e SELA, e scrive in `tempi.txt` quale prova
     l'ha fatta partire.
   - Tre riferimenti delle curve DA hanno avuto bisogno della terza prova.
2. **Il cambio a caldo con l'interruttore netto** si ferma su «Timestep too small» a un rimbalzo
   di K5. Si fa in un deck a parte (`caldo/`) dove K1 e K5 hanno anche il contatto morbido del
   blocco. Le tre corse a caldo riuscite con l'interruttore netto danno lo stesso A entro lo
   **0,4 %**: il modello del contatto non sposta il risultato.
3. **Lo spegnimento a 0 V esatti** (rampa da 10 ms) si ferma in fondo alla rampa. Le discese si
   fermano a ±1 mV, e tutte le 24 corse sono state rifatte così.
4. `corri.sh` nella prima versione lanciava tutte le corse insieme: `$(jobs -r)` gira in una
   sottoshell che non vede i job. Corretto con `${#jobstates}` e provato.

## 2. I passaggi di guadagno (punto 1): il criterio 3 di ADR-030

Senza segnale, jack principale; le fisse non cambiano guadagno e restano a pV.

| Passaggio | **A caldo** | Sotto mute: il cambio a relè chiuso | Sotto mute: il rilascio |
|---|---|---|---|
| 0 ↔ +3 dB | **13,8 mV** | 27 µV | 0,03 µV |
| +3 ↔ +10 dB | **57 mV** | **111 µV** | 0,03 µV |
| 0 ↔ +10 dB | **69 mV** | **112–116 µV** | 0,03 µV |

- **Il criterio 3 di ADR-030 è soddisfatto**: sotto mute il cambio vale ~600 volte meno che a
  caldo. L'interblocco di ADR-041 (L36) è giustificato dalla misura.
- **Ma il cambio a relè chiuso sfora di poco i 100 µV.** Il picco cade 31 µs dopo la
  commutazione, e segue il salto d'offset in continua dell'uscita principale (−30,9 mV a 0 dB,
  −97,4 mV a +10 dB: 66 mV) attraverso il partitore del contatto chiuso, 0,1 / 47,1 Ω. Per 0↔+3
  il calcolo dà 27 µV, e 27 µV si misurano.
- **Con musica** (1 kHz e 20 Hz, 100 k): S d'inserzione ≤ 7,16 dB, S del rilascio 0 dB, B2 ≤
  8,5 µV. Reggono.
- **A 20 kHz** (0→+10, 100 k, TMAX 0,5 µs): il rilascio a +10 dB dà S = 0 dB e B2 1,35 µV.
  Regge, anche con lo slew più lento di ADR-042.

## 3. Il trim (punto 2)

Senza segnale, +10 dB, jack principale:
- **0 → −6 e 0 → −12 dB: 101,7 µV**; −6 → 0: 97,9 µV; −12 → 0: 99,6 µV; fra −6 e −12: 49–51 µV.
  Il relè 1 è un deviatore che apre prima di chiudere: per 1 ms l'ingresso del blocco B perde
  l'offset del blocco A (1 ms di trasferimento è un'ipotesi dichiarata).
- Il rilascio: 0,03 µV. Con musica a 1 kHz: S ≤ 7,16 dB, B2 ≤ 0,34 µV.

## 4. La durata del mute (punto 4)

+10 dB, 100 k, 1 kHz e 20 Hz e senza segnale. Inversioni a d = 0,25 / 0,5 / 0,75; relè tenuto
0,1 / 1 / 2 / 20 s.

| | Peggiore | Soglia |
|---|---|---|
| S d'inserzione / del rilascio | 7,16 / 5,45 dB | 20 dB |
| A del rilascio, senza segnale | 3,76 µV (inversione a 0,75) | 100 µV |
| B2 | 8,5 µV (20 Hz, relè 0,1 s) | 100 µV |
| relè al jack contro la stessa sequenza senza relè | S = 0 | 20 dB |

**Regge.** Il mute di 20 s non peggiora il rilascio: la serie più buia non allarga il salto.
Una nota di metodo: l'inversione a d = 0,25 si rilascia 1,5 s dopo l'inserzione, quindi la
finestra di A dell'inserzione è per costruzione più corta dei 2 s che il metodo chiede. Vale
13 nV, e il tratto successivo lo copre A del rilascio. Si legge «non decidibile per
costruzione», non «fuori».

A 20 kHz, mute di 2 s (100 k): S d'inserzione **6,61 dB**, del rilascio **6,12 dB**, B2 27 µV.
Sono le cifre di L29b2 (6,6 / 6,1 dB, relè tenuto 1 s): lo slew più lento di ADR-042 non
sposta il verdetto, e nemmeno la durata del mute.

## 5. La dispersione dell'LSK489 (punto 3)

VOS ±20 mV (il massimo del datasheet) sugli ingressi dei blocchi, il gruppo B (Vto per I_DSS
2,59 / 7,98 / 14,93 mA letti dalla sonda) e l'attenuatore al massimo e a −20 dB. Sequenze:
0↔+10, trim 0↔−12, mute semplice. 132 corse.

| | Peggiore | Soglia |
|---|---|---|
| **Il cambio di guadagno o di trim a relè chiuso** | **267 µV** (attenuatore al massimo); 147 µV a −20 dB | 100 µV |
| A del rilascio dopo il cambio | 69,7 µV | 100 µV |
| B2 | 20,8 µV | 100 µV |
| Il mute semplice, con tutta la dispersione | ≤ 8,9 µV | 100 µV |
| Il segno opposto dei VOS (controllo) | ≤ 31 µV | — |

- Il gruppo B non sposta quasi niente: conta l'offset d'ingresso, non I_DSS.
- **Il segno**: VOSB sta fra W e WB, quindi un VOS positivo toglie tensione al gate e si somma
  alla parte sistematica. Il caso peggiore è quello marcato `p`. La prima stesura del
  generatore lo diceva al contrario; il risultato no, perché si corrono entrambi i segni.

## 6. Accensione e spegnimento (punto 5)

Ipotesi dichiarate nel generatore, perché ADR-039 non le fissa e l'alimentatore è di L30:
- rampe dei rail di 10 e 300 ms, simmetriche o con un rail in ritardo di 50 ms;
- all'accensione relè del jack chiuso e LED a d = 1, rilascio 2,5 s dopo;
- allo spegnimento relè chiuso con 0 / 5 / 20 / 100 ms di ritardo, e nessuna dissolvenza.

| | Peggiore | Soglia |
|---|---|---|
| **Spegnimento**, rampa da 10 ms, relè con ≥ 5 ms di ritardo | **2,9 mV – 17,5 V**: volt in 8 corse su 9 | 100 µV |
| Spegnimento, rampa da 10 ms, relè senza ritardo | 1,9–17 mV | 100 µV |
| Spegnimento, rampa da 300 ms, relè entro 5 ms | 0,23–0,24 mV | 100 µV |
| Spegnimento, rampa da 300 ms, relè a 20 / 100 ms | 0,39–5,2 mV | 100 µV |
| **Accensione**, principale / fisse | 0,07–5,6 mV / **1,6–11 mV** | 100 µV |
| Accensione, il rilascio del mute dopo il temporizzatore | 0,03 µV | 100 µV |

**Il meccanismo è fisico.** Sotto ~9,5–10,4 V di rail il blocco perde la regolazione:
- allo spegnimento, nella rampa da 10 ms, l'uscita scatta in 60 µs da −0,1 a −9,1 V;
- all'accensione, fra 0 e ~7 V di rail, l'uscita sale a +0,84 V e poi rientra.

Col relè aperto il salto arriva intero; col relè chiuso ne arriva 1/471. **Nessun ritardo del
relè basta da solo.** All'accensione la tenuta dei rail non aiuta: quella zona va attraversata.
→ **ADR-043** per lo spegnimento e il failsafe; l'accensione va a L29d.

## 7. Le curve della VTL5C4 (punto 6)

Serie e derivazione in A (resistenza più bassa) e D (più alta), indipendenti. Eventi:
inversioni a 0,25 e 0,75, relè 1 e 2 s; 1 kHz, 20 Hz, senza segnale.

| Serie / derivazione | S peggiore | B2 | A del rilascio |
|---|---|---|---|
| A / A | 9,36 dB | 11,7 µV | 3,78 µV |
| A / D | 10,97 dB | 18,5 µV | 1,87 µV |
| D / A | 5,89 dB | 4,96 µV | 6,03 µV |
| D / D | 10,97 dB | 7,8 µV | 1,72 µV |
| B / B (il deck versionato, §4) | 7,16 dB | 8,5 µV | 3,76 µV |

**Regge**: la dispersione delle parti porta S da 7,2 a ~11 dB, contro 20.

## 8. Verdetto

| Punto | Esito |
|---|---|
| 1 guadagno sotto mute: rilascio, S, B2 | regge |
| 1 **il cambio a relè chiuso** | **111–116 µV, e 267 µV con la dispersione**: fuori |
| 1 criterio 3 di ADR-030 (a caldo contro sotto mute) | soddisfatto: 69 mV contro 116 µV |
| 2 trim: rilascio, S, B2 | regge |
| 2 **il cambio del trim a relè chiuso** | **98–102 µV**: fuori di poco |
| 3 dispersione | peggiora solo il cambio a relè chiuso (267 µV) |
| 4 durata del mute, S | regge (≤ 7,2 dB) |
| 5 **accensione e spegnimento** | **fuori**: mV-V |
| 6 curve della LDR | regge (S ≤ 11 dB) |
| 20 kHz (guadagno 0→+10 sotto mute, mute di 2 s) | regge (S ≤ 6,6 dB, B2 ≤ 27 µV) |

**Non fatto, e dichiarato**: il piano prevedeva il carico da **10 kΩ** sulla cella peggiore di
ogni punto. Tutta la matrice è a 100 kΩ. Per le celle fuori soglia il carico conta poco, perché il
jack è in corto sul contatto chiuso (0,1 Ω contro 47 Ω); in L29b2 i due carichi coincidevano
entro l'1 %. È un ragionamento, non una misura: la cella da 10 kΩ passa a L29d.

**NC-028 resta aperta e bloccante.** La musica è sistemata, i salti in continua no. Le decisioni
dell'utente del 2026-09-23:
- **ADR-043**: lo spegnimento è un requisito di L30; e un failsafe per il guasto
  dell'alimentatore, che non dipenda dall'alimentatore sano;
- **L29d**, prima di L36: un contatto **in serie** al jack, misurato sulla matrice di L29c in
  due varianti: (i) serie più derivazione, (ii) serie sola. Le LDR restano, perché S le vuole:
  un contatto taglia la musica di colpo.

## 9. I tempi

| Cosa | Corse | Tempo |
|---|---|---|
| 1 kHz, 20 Hz, senza segnale (17,5–36,5 s simulati) | 117 + 132 + 72 + 9 | 1–15 min l'una, 7 in parallelo |
| 20 kHz (19 s simulati, TMAX 0,5 µs) | 3 | 6,4 / 6,7 / **11,4 h** (il riferimento mai in mute), coi core contesi |
| `analizza` in parallelo (`analizza_par.py`) | — | 245 s per la cella da 11 corse; ~2 h per le 87 veloci, con 3 processi e i core pieni |
