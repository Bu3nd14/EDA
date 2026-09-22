# L29b2 — il mute LDR nel sorgente, e il rilascio reso decidibile (2026-09-22)

Lotto **L29b2**. **NC-028 resta aperta e bloccante**: manca il caso peggiore, **L29c**.
Dati: `data/2026-09-22/L29b2/`. ADR nuove: **ADR-039** (le LDR nel sorgente) e
**ADR-040** (il taglio con musica si giudica sul salto di livello, ≤ 20 dB in 100 ms;
il profilo del mute è la v4). E **ADR-041**, a lotto quasi chiuso: il cambio di guadagno
si interblocca col mute come il trim, niente mute automatico, LED anche per il
guadagno (parole dell'utente: «interlock al mute, come TRIM, nessuna invenzione»).

**In breve.**
- Il pavimento di mV «con le LDR attive» era l'arrotondamento del tempo scritto da
  `wrdata` (§1).
- Col profilo v3 il rilascio salta di 30 dB in 100 ms (§2).
- C2 a 1 mV non si può soddisfare: a 20 Hz nemmeno con un inviluppo ideale sotto
  ~14 s, e sulla principale la distorsione della catena ne vale già 0,65–0,96 mV
  (§3).
- L'utente ha dato il criterio: il pseudo-mute del Technics, 20 dB di colpo, non gli
  ha mai dato fastidio (ADR-040, §4).
- Con la **v4** il salto massimo vale **7,2 dB**, e A e B stanno nei limiti a ogni
  uscita, carico e frequenza misurati (§8).

**Provenienza dei modelli.** Ogni cifra sulla LDR porta l'etichetta «modello
comportamentale dal datasheet, con estrapolazione dichiarata»
(`models/optocoupler/vtl5c4_comportamentale.lib`, curva B). Del costruttore c'è solo
l'LS352. Il resto è segnaposto (NC-017), LSK489 compreso.

## 1. Il pavimento di C2 con le LDR: era la penna, non il circuito

L29b aveva lasciato il rilascio non decidibile: con le LDR attive il pavimento di C2
saliva a 4,6–7,2 mV sulla principale, nella coda del rilascio, col meccanismo non
attribuito. Tre candidati erano da falsificare uno alla volta: il passo, la forma del
modello, `method=gear` (quest'ultimo **solo come diagnosi**, decisione dell'utente del
2026-09-22).

**Localizzazione** (`pavimento/diag.py`, `ana.py`). Due corse nello stesso stato
fisico dopo 10 s (`ev` col relè, `norele` senza) differiscono di 6,4–7,0 mV sulla
principale. Salvando anche i nodi interni, la differenza c'è **già sulla sorgente
ideale** `BSRC = f(time)`: **2,2 mV**, e questa è identica nelle due corse per
costruzione. Il rapporto principale / sorgente vale 3,15, il guadagno. Quindi niente
del circuito: la differenza nasce nella **lettura**.

**Il meccanismo.** `wrdata` scrive ogni colonna, il tempo compreso, con 9 cifre
significative (`%.8e`). Il tempo si risolve così a **10 ns fino a 10 s e a 100 ns
oltre**. Fra due corse con griglie diverse l'arrotondamento vale fino a 2·A·ω·δt:
- sulla sorgente, sopra 10 s, **~2,4 mV** (misurato 2,2);
- sulla principale **~7,5 mV** (misurato 4,6–7,2).

Il salto cade nella finestra 10,0–10,5 s: è il cambio di decade del tempo, non un
evento.

**La prova** (`pavimento/esiti/`):

| Coda del rilascio | wrdata di default | `set numdgt=15` |
|---|---|---|
| ev contro norele, principale | 6,4–7,0 mV | **0,003 mV** |
| sorgente ideale | 2,1–2,2 mV | **0,001 mV** |
| TMAX 5 µs (default) | 6,2 mV | — |

- **TMAX falsificato** (5 µs non cambia niente).
- **La forma del modello e `gear` non servono**: non sono stati provati, perché il
  circuito non c'entra.

**Cosa ne segue, oltre questo lotto** (`docs/limitations.md` #30):
- con ogni probabilità il pavimento «diffuso, non attribuito» di C2 di **L29a**
  (0,51–0,80 mV) è lo stesso arrotondamento: corse sotto 10 s, risoluzione 10 ns;
- e così il pavimento di **1,08 mV a 20 kHz** che rendeva non decidibile quella cella:
  corse da 0,7 s, risoluzione 1 ns, 2·A·ω·0,5 ns ≈ 1,5 mV.

I deck versionati di L29a non sono stati rifatti.

**Questa correzione non cambia il metodo di V2.** Filtri, fit, riferimenti e soglie
restano quelli di ADR-035 e ADR-036. Cambia la precisione con cui ngspice **scrive**
le forme d'onda: `set numdgt=15` nel `.control`, fuori dal blocco CANALE. È detto qui e
in #30 perché non passi in silenzio. Il metodo cambia più avanti per un'altra ragione,
con una decisione dell'utente (ADR-040, §4).

## 2. Il profilo v3, Td 6 s: il rilascio salta

Banco di L29b rifatto con `numdgt=15` (`pavimento/build_nd.py`, corse in parallelo con
`dividi.py`), 1 kHz, 100 kΩ, `v2_metodo.py analizza` (`v3_td6_nd15/`). Pavimento
**lungo tutta la sequenza** (ev a 10 µs contro ev a 7 µs, `c2curva.py`): **≤ 31 µV**
sulla principale e ≤ 10 µV sulle fisse. Le cifre di C sono quelle del metodo di
ADR-035, oggi diagnostica (§4).

| Principale / fisse | C2 | Soglia di ADR-035 |
|---|---|---|
| inserzione | 2,50 / 0,60 mV | 1 mV |
| rilascio | 3,41 / 0,88 mV | 1 mV |
| inversione a d = 0,75 | 7,36 / 2,15 mV | 1 mV |
| relè, chiusura / apertura | 0,067 / 0,057 mV | 1 mV |
| A senza segnale | ≤ 33 nV | 100 µV |
| B2 | 0,29 µV | 100 µV |
| carico minimo sulla sorgente | 714 kΩ | E3 ≥ 100 kΩ |

**Perché il rilascio è peggio dell'inserzione** (`v3_td6_nd15/stati_ev.txt`):
- v3 fa lento il solo tratto della serie da 10 kΩ a ~2 MΩ, cioè da 0 a −9,5 dB contro
  R_IN;
- il resto, da 2 MΩ a 400 MΩ (da −9,5 a −52 dB), all'inserzione lo fa lo spegnimento
  della cella, che è lento per natura;
- al rilascio la cella **si accende alla velocità del LED**. Fra d = 0,475 e 0,45, cioè
  in 150 ms, R_s passa da 10^8,6 a 10^6,8 Ω e il livello va da −62 a −26 dB. La
  derivazione intanto è ancora a ~500 kΩ, perché il suo spegnimento è lento.

L'inversione ha lo stesso tratto (−20 → −13 dB in 0,1 s), più uno spigolo all'istante
in cui d cambia verso.

**Sulla matrice del deck versionato** (`matrice_v3/`, 20 Hz e 1 kHz, 10 e 100 kΩ), il
salto S di ADR-040 della v3 al rilascio vale **29,7 dB a 20 Hz** (sopra i 20 dB) e
17,8 dB a 1 kHz. Inserzione 7,2 dB, inversione ≤ 6,6 dB. A 1 kHz il salto è minore
perché il livello di partenza, a mute, è più alto: i 5 pF della cella in serie lasciano
passare più segnale che a 20 Hz.

## 3. Perché C ≤ 1 mV non si può soddisfare

**Il simulatore veloce** (`transizione/`). Riproduce la catena del comando in Python:
- profilo delle correnti;
- corrente nel LED (col 10 M del banco);
- stato delle celle, con le **stesse** equazioni del modello e le tabelle lette dal
  `.lib`;
- livello g(t) all'ingresso del blocco A;
- C2 con la pipeline di `v2_metodo` (in numpy: coincide entro 1e-11).

Tarato contro ngspice (`transizione/esiti/tara_v3.txt`, `tara_v4.txt`):
- lo stato delle celle coincide entro **0,002 decadi**;
- C2 calcolato dal g(t) di Python e da quello di ngspice coincide entro l'1–2 %;
- il passo delle celle è ininfluente.

Per costruirlo si è visto che `pwl()` di ngspice estrapola linearmente fuori dai punti
(`docs/limitations.md` #31).

**Tre limiti, misurati:**
1. **C2 misura gli spigoli, e a 20 Hz la pendenza.** Su inviluppi ideali alla
   principale (`transizione/esiti/forme_*.txt`):

   | C2 | 2 s | 4 s | 6 s | 10 s |
   |---|---|---|---|---|
   | coseno, 1 kHz | 0,76 | 0,38 | 0,25 | 0,15 mV |
   | coseno, 20 Hz | 6,78 | 3,39 | 2,26 | 1,36 mV |
   | lineare, 1 kHz | 7,52 | 3,76 | 2,51 | 1,50 mV |

   A 20 Hz nessuna dissolvenza sotto ~14 s passa 1 mV, nemmeno ideale.
2. **La distorsione della catena vale da sola 0,65–0,96 mV di C2 sulla principale.**
   È lo scarto sistematico fra il C2 dell'inviluppo e quello di `analizza`, e gli
   0,96 mV contro «mai» nel tratto ancora silenziato. Il contenuto armonico cambia col
   livello, e il riferimento non lo cancella. Coi modelli segnaposto (NC-017).
3. **Le celle non possono fare un coseno in 6 s.** Sopra ~80 kΩ la cella si spegne al
   massimo a 0,4 decadi/s (l'ipotesi pessimistica del modello), e la tabella dei tassi
   è a gradini. Dove il comando chiede di più la cella si stacca, e l'inviluppo prende
   uno spigolo. Una ricerca su profili a 21 nodi per LED, con d(t) ad accelerazione
   limitata, sei manovre e i vincoli E3 e relè (`transizione/cerca.py`), è rimasta a
   **6,7 volte** il coseno ideale della stessa durata. Stima, non misurata: con Td
   8–10 s si arriverebbe vicino al coseno.

## 4. Il criterio dell'utente: il salto di livello (ADR-040)

Portati questi limiti all'utente, la sua risposta: «il Technics che andiamo a
sostituire ha uno switch di pseudo mute di 20 dB e non mi ha mai dato fastidio
all'inserzione con la musica attiva, quindi 20 dB di salto li considero accettabili».
Fra tre strade ha scelto **«Criterio in dB + v4»**.

- **S** è il salto di livello: la variazione massima, in 100 ms, del livello del tono
  al jack. Il livello è l'ampiezza del fit, su max(10 ms, un periodo), in dB sotto il
  pieno del riferimento, tenuto a −70 dB. **Soglia 20 dB.**
- I 20 dB sono dell'utente; i 100 ms e i −70 dB sono una proposta di L29b2, dichiarata.
- **C2 diventa diagnostica**. A e B restano come sono.

**Nello strumento** (`scripts/v2_metodo.py`):
- le funzioni `ampiezza()` e `salto_db()`, e le righe `S_ins` / `S_rel` in `analizza`;
- il verdetto di `riassumi` su A, B e S;
- **30 controlli su 30**, compresi T15–T19: il gradino del Technics dà 20,000 dB a
  20 Hz, 1 kHz e 20 kHz; −30 dB cade; una dissolvenza uniforme da 60 dB in 6 s dà
  1,000 dB; sotto il pavimento vale 0;
- **14 sabotaggi su 14** rilevati, compresi i nuovi `s_senza_pavimento` e
  `s_soglia_di_c` (`metodo_s/`).

## 5. La v4: il profilo di progetto

Proposta di questo lotto, adottata dall'utente con ADR-040:
- la serie come v3 fino a 4,5 µA a d = 0,45, poi log-lineare fino al ginocchio del
  buio, **0,19 µA a d = 0,75**, e 10 nA a d = 0,8;
- la derivazione invariata.

La sovrapposizione con la derivazione (d da 0,5 a 0,75) avviene con R_s ≥ 2 MΩ, quindi
la sorgente non vede mai un carico basso (ADR-038 punto 3). Il carico minimo resta
714 kΩ.

Banco di L29b, 1 kHz, 100 kΩ (`v4_td6_nd15_proposta/`, misurata quando era ancora una proposta), come confronto:

| Principale / fisse | v3 | **v4** |
|---|---|---|
| salto dagli stati: inserzione / rilascio / inversione | 7 / **30** / 7 dB | 7 / 4 / 3 dB |
| C2 (diagnostica): inserzione | 2,50 / 0,60 mV | 2,50 / 0,60 mV |
| C2: rilascio | 3,41 / 0,88 mV | 1,47 / 0,30 mV |
| C2: inversione | 7,36 / 2,15 mV | 5,01 / 1,40 mV |
| relè; A; B2 | 0,067 mV; ≤ 33 nV; 0,29 µV | uguali |
| pavimento di C2 | ≤ 31 µV | ≤ 8 µV |

## 6. Il sorgente

`circuits/preamp/preamp_audio.py` (ADR-039):
- **U101 / U301**, la serie, fra il pin 1 del connettore d'ingresso e l'ingresso del
  blocco A;
- **U102 / U302**, la derivazione, dal nodo di R_IN a GND;
- i LED della stessa funzione in serie fra i canali, sul connettore **J3 `LDR_CMD`**;
- il contratto del comando (profilo v4, Td 6 s, 10 nA di riposo, relè 0,5 s dopo
  d = 1) è scritto accanto a J3;
- nessun riferimento esistente cambia: il diff della netlist aggiunge 5 componenti e
  sposta la sola rete dell'ingresso.

**Guardiani, tutti fatti fallire prima** (`falsi/esito.txt`):
- **2e** (`check_relay_safe_state.py`) ha una regola nuova per le LDR, scritta
  sull'intento: la serie fra `IN_x` e il nodo di R_IN = 1M, la derivazione da lì a GND,
  e sulle reti dei LED solo LED delle LDR e `LDR_CMD`. Rifiuta, tutti con rc 1:
  - F1, un LED sull'ingresso del blocco A;
  - F2, la derivazione dal lato del connettore;
  - F3, la serie oltre R_IN;
  - la netlist di `main`, che non ha LDR.
- **2f** (`preamp_blocks_draw.py`) disegna le due LDR fra il selettore e il blocco A,
  e asserisce parte, ruoli e nodi. F2, F3 e `main` la fanno cadere.
- **2g** (`check_deck_refs.py`) conta ora anche gli elementi V e B dei sottocircuiti
  inclusi: il modello della LDR è il primo che li usa. Rifiuta un dispositivo morto e
  la porta `K` della LDR lasciata su un nodo che nessun altro tocca.
- **2d** non cambia: copre il solo disegno del blocco di guadagno, e le LDR stanno
  fuori da `gain_block()`.

## 7. E3, E5, l'accoppiamento LED–cella e P7

`spice/preamp/tb/tb_e3_e5_ldr.cir`, deck nuovo e versionato. È la catena di
`tb_trim.cir` col trim candidato 2 e le due celle davanti al blocco A (`e3_e5/`).
- **E3**: |Zin| minima al connettore, con 68 pF di selettore:
  - **111,6 kΩ** in gioco, 113,6 kΩ in mute, 116,5 kΩ a metà;
  - uguale nelle tre posizioni del trim, contro ≥ 100 kΩ: **conforme**;
  - il margine scende dai 121,1 kΩ di L16 per i 5 pF della cella verso massa;
  - lungo la sequenza il carico non scende sotto 714 kΩ, con v3 e con v4.
- **E5**: la serie come resistore del suo valore di lavoro, perché il modello non ha
  rumore. Fa 88,3 Ω con la curva B, misurato nell'op, e 118 Ω con la curva D:
  - massimo **4,957 µV** (curva D, +10 dB, attenuatore al massimo, 430 Ω), contro
    4,918 senza LDR e ≤ 9,90 µV: **conforme**;
  - il rumore in eccesso di una fotoresistenza reale non è modellato, ed è da misurare
    sul prototipo.
- **Accoppiamento LED–cella, 0,5 pF.** Il comando non è progettato, quindi il deck ne
  ricava un **requisito**: rumore all'anodo della derivazione ≤ **0,69 mV/√Hz** piatto
  per 1 µV al jack (la quota di ADR-022, a +10 dB). Dal lato sorgente della serie il
  limite è 41 V/√Hz: irrilevante.
- **P7, riletto: regge per ragionamento.** L17 l'ha misurato conforme con i jack a
  massa **e il segnale presente** (`tb_mute_corto.cir`), il caso più severo. Col mute a
  monte, a mute inserito gli stadi d'uscita non hanno segnale. Nessun guasto del
  comando è peggio di L17:
  - comando spento: la serie si fa buia;
  - comando bloccato acceso sulla serie: è il caso di L17.

## 8. La matrice del deck versionato

`spice/preamp/tb/tb_v2_mute_ldr.cir`, **generato** da
`data/2026-09-22/L29b2/deck/genera_tb_v2_mute_ldr.py` (v4 di default, v3 per
confronto).
- Il blocco CANALE è identico: `v2_metodo.py canale` dà OK sui 4 deck.
- `set numdgt=15`.
- Pavimento lungo la sequenza per ogni cella (`evp`, `invp` a un altro TMAX).
- Si corre diviso (`dividi.py`) e in parallelo.
- **20 kHz solo a 100 kΩ**, scelta dell'utente: a 20 Hz e 1 kHz i 10 kΩ danno gli
  stessi numeri entro l'1 %, e una corsa a 20 kHz vale ~2,3 ore.

**Profilo v4** (`matrice_v4/`). I valori sono i peggiori sulle tre uscite; principale,
fisse e i due carichi coincidono entro l'1 %:

| | 20 Hz | 1 kHz | 20 kHz, 100 kΩ | Soglia |
|---|---|---|---|---|
| **S inserzione** | 7,2 dB | 7,2 dB | 6,6 dB | 20 dB |
| **S rilascio** | 4,1 dB | 5,3 dB | 6,1 dB | 20 dB |
| **S inversione** (ins. / ril.) | 2,9 / 2,2 dB | 3,0 / 2,2 dB | 2,3 / 1,0 dB | 20 dB |
| A senza segnale (una corsa per carico, tutte le manovre) | ≤ 3,9 µV | ≤ 3,9 µV | — | 100 µV |
| relè al jack: S; C2 (diagnostica) | 0 dB; 0,091 mV | 0 dB; 0,067 mV | 0 dB; 0,30 mV | 20 dB |
| B2 | ≤ 10 µV | ≤ 0,32 µV | ≤ 1,1 µV | 100 µV |
| C2 (diagnostica), il peggiore | 10,0 mV (inversione) | 5,0 mV (inversione) | 23 mV (21 mV già a 5 ms dall'inserzione: fondo del metodo, §3) | (1 mV) |
| pavimento di C2 | ≤ 0,3 µV | ≤ 7,8 µV | ≤ 59 µV | — |

**Tempi misurati.** Una corsa a 20 kHz (TMAX 0,5 µs, 17,5 s simulati) ha richiesto **circa
4 ore**, con 7 in parallelo su 10 core (`matrice_v4/tempi_20k.txt`). Il ritmo dei primi
minuti è molto più alto, e porta fuori strada; un'analisi Python in parallelo lo
dimezza.

## 9. Verdetto

- **La v4 regge il criterio di ADR-040 in tutta la matrice misurata**: tre uscite; 10 e
  100 kΩ a 20 Hz e 1 kHz; 100 kΩ a 20 kHz. Il salto massimo vale **7,2 dB in 100 ms**
  contro 20; A ≤ 3,9 µV e B ≤ 10 µV contro 100 µV. Il relè al jack non taglia mai
  musica sopra −70 dB.
- **E3 ed E5 reggono** con le celle nel sorgente; **P7 regge** per ragionamento.
- **La v3 non regge**: salta di 29,7 dB al rilascio a 20 Hz.
- **C2 resta sopra 1 mV** (diagnostica): 5–23 mV, soprattutto all'inversione e a 20 kHz.
  La causa è il metodo stesso (§3): pendenza a 20 Hz, e fondo della distorsione contro
  il riferimento.
- **NC-028 resta aperta e bloccante**: manca il caso peggiore, cioè guadagno e trim
  sotto mute, dispersione, accensione e spegnimento. Viene **dopo la Fase 4 (L39)**, per
  decisione dell'utente, perché dipende dai modelli.
- **Ogni cifra sulla LDR** porta l'etichetta «modello comportamentale dal datasheet, con
  estrapolazione dichiarata». La VTL5C4 dell'Excelitas è fuori produzione; la riedizione
  Xvive è da verificare prima di G2 (STATE.md).

## 10. Cosa non è stato fatto, e perché

- **20 kHz a 10 kΩ**: saltato per scelta dell'utente (§8).
- **Il comando ad accelerazione limitata**: non serve col criterio di ADR-040
  (inversione ≤ 3 dB), e resta un margine disponibile (ADR-039).
- **I deck di L29a non sono stati rifatti** con `numdgt=15`: le loro cifre di C2 hanno
  lo stesso arrotondamento (limitations #30), e C2 è oggi diagnostica.
- **Il caso peggiore** (passaggi di guadagno, trim, dispersione, accensione e
  spegnimento) è **L29c**.
