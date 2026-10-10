# ADR-062 — Il mute taglia coi soli relè al jack: via le fotoresistenze, il loro pilota, il profilo e S

Data: 2026-10-04 · Stato: accettata — ADR-063 precisa solo come si misura: lo strascico a bassa frequenza che resta subito dopo il taglio fa parte del clic, e si dichiara con lui; a mute inserito si misura quello che arriva davvero all'uscita

**Rapporti con le decisioni precedenti.**
- **Supera ADR-038** sulla sfumatura a monte. I relè al jack restano, in geometria iii (ADR-044).
- **Supera ADR-039 e ADR-040**: il profilo della sfumatura e il criterio di S.
- **Supera ADR-058, ADR-059, ADR-060 e ADR-061**: la cella NSL-32SR3, il tempo di 3 s, la cima di
  7 mA, il profilo v5, la nota su E3 durante la sfumatura e l'impronta propria della cella.
- **Supera ADR-049 e ADR-050 sul solo pilota delle LDR**: il DAC MCP4822, i convertitori
  esponenziali, la cima e la calibrazione. Il micro, Δ e Δ₂ in hardware e l'interruttore di
  `VRELAY` in standby restano.
- **Cambia PR-21** del contratto (ADR-053: il PRB cambia solo con una ADR), con la firma
  dell'utente.
- Gli `Stato:` delle ADR superate non si toccano qui: si allineano con l'utente alla
  rigenerazione del dossier, come quelli già in elenco (NEXT-SESSION).

## Contesto

Dopo L47b2b1 l'utente ha chiesto perché il mute fosse così complicato, e se accettare un salto con
la musica lo semplificasse (STATE, «Dopo L47b2b1»). Rilette le voci del PRB, la complessità
serviva a una sola voce. **PR-21**, «il mute sfuma, non taglia» (S ≤ 20 dB in 100 ms, dal
Technics), era l'unica ragione di:
- le quattro NSL-32SR3 e il loro modello, ricavato da una sola cella misurata;
- il pilota in `psu.py`: DAC, due convertitori esponenziali appaiati, specchi e sense, 33 parti;
- il profilo v5 e la calibrazione nel firmware;
- la nota su E3 durante la sfumatura;
- NC-043, NC-049 e NC-053.

Il silenzio dei cambi (**PR-20**, ≤ 100 µV) lo fanno i relè al jack (ADR-044), il permissivo
sfasato (ADR-045) e l'interblocco del guadagno (ADR-030, ADR-041). La sicurezza senza firmware
(**PR-24**) la fanno Δ, Δ₂ e i comparatori in hardware. Nessuna delle due dipende dalla sfumatura.

**Il prezzo, detto all'utente prima della scelta**:
- all'inserimento la musica si interrompe di colpo: ~70 dB in un istante, invece dei 20 del
  Technics;
- al rilascio torna di colpo al livello di prima;
- un contatto che apre su un picco può fare un clic.

Una via di mezzo è stata proposta e non scelta: un gradino fisso di −20 dB alla Technics per il
mute d'uso, col silenzio dei relè solo per cambi, accensione e spegnimento.

## Decisione

**Il mute taglia coi soli relè al jack.** Le fotoresistenze, J3, il pilota delle LDR, il profilo,
la calibrazione e la misura S escono dal progetto.

Le risposte dell'utente all'inizio di L47c (2026-10-04, domande per nome):

1. **Il testo nuovo di PR-21**, firmato: «Il mute taglia: con la musica il silenzio arriva di
   colpo, e al rilascio la musica torna di colpo al livello di prima». **Nessun tetto al clic**:
   il clic del taglio con la musica si misura e si dichiara, in picco e in dB SPL, ma non è un
   verdetto.
2. **S in V2**: tolto. Non resta nemmeno come diagnostica.
3. **Il tempo fra il tasto e i relè**: subito. Restano l'antirimbalzo e la finestra Δ del
   permissivo (ADR-045). `T_FADE_US` e `T_MUTE_HOLD_US` (0,5 s dopo d = 1) escono dal firmware.
4. **L'impronta** `library/preamp.pretty/NSL-32SR3_LED3.30`: tolta.
5. **Il lotto diviso in due**: L47c1 e L47c2.

**La divisione, con una correzione dichiarata.** La proposta all'utente metteva l'alimentatore
nella seconda parte. Ma il controllo del cablaggio fra le schede (2j) confronta J3 pin per pin
sulle due: J3 non può uscire da una scheda sola. Quindi:
- **L47c1** toglie tutto l'hardware: le celle e J3 dalla scheda audio, il pilota e J3 da `psu.py`.
  Riscrive questa decisione, il PRB e i requisiti, i controlli 2e e 2j coi loro falsi, e corre E3
  ed E5 senza celle;
- **L47c2** fa le misure dell'alimentatore col carico nuovo (la tenuta di `VRELAY`, NC-050; il
  commento di `C_VRELAY`, NC-051; lo standby, NC-037), il firmware, la matrice V2 col clic del
  taglio (NC-049, NC-053) e la catena dei guasti di L41c.

`models/optocoupler/nsl32sr3_comportamentale.lib` resta in `models/`, validato e con la sua
provenienza, ma fuori dai deck canonici. I deck V2 (`tb_v2_casopeggiore.cir`,
`tb_v2_mute_ldr.cir`) hanno ancora le celle fino a L47c2, e lo dicono.

## Perché

- **Una sola voce del PRB comprava tutta la complessità, e l'utente l'ha cambiata.** Il resto del
  mute non dipende dalla sfumatura. In `psu.py` escono 33 parti su 151; sulla scheda audio
  quattro celle e J3. Nel firmware escono la legge esponenziale, le tabelle, la calibrazione e due
  costanti di tempo.
- **Il rischio del modello sparisce.** Ogni cifra della sfumatura veniva da un modello ricavato da
  dati pubblicati e da una sola cella misurata nella regione del mute (ADR-058). La distorsione
  della cella non era modellata, il declassamento del LED non era pubblicato, e la parte fu scelta
  perché la VTL5C4 era fuori produzione (NC-043). Senza celle niente di questo resta nel percorso
  del segnale.
- **L'ingresso torna quello del blocco A.** E3 senza celle: **114,7 kΩ** al connettore, 20 kHz,
  selettore a 68 pF. Con le celle a cella accesa era **105,8 kΩ**: L47b2a riportava 110,7, ma il
  `meas min` saltava i 20 kHz (limitations #45). E5 peggiore **5,496 µV** contro 5,530 con le
  celle (limite 9,90). `data/2026-10-05/L47c1/e3_e5/`.
- **Una preferenza, dichiarata come tale**: l'utente accetta il taglio di colpo, che il Technics
  non faceva. Non c'è un numero dietro: è il suo giudizio d'ascolto, sapendo il prezzo.

## Alternative scartate

- **Tenere la sfumatura con la NSL-32SR3** (L47b2b2, il pilota vero): era il lotto successivo;
  superato da questa decisione.
- **Il JFET** come cella (ADR-059): distorce del 20–60 % nella sfumatura; scartato dall'utente sui
  numeri.
- **L'attenuatore a relè a gradini**: «costa molto» (Dopo L47a); scartato dall'utente.
- **Un gradino fisso a −20 dB alla Technics** per il mute d'uso: proposto in «Dopo L47b2b1», non
  scelto.
- **S tenuto come diagnostica**: l'utente ha preferito toglierlo.

## Da riaprire se

- l'ascolto sul prototipo trova il taglio, o il clic del contatto che apre su un picco, fastidioso
  (PR-21 ha la firma dell'utente: la riapre lui);
- il clic del taglio misurato in L47c2 risulta di un ordine che l'utente, visti i dB SPL, non
  accetta: è il tetto che questa ADR ha lasciato fuori di proposito;
- serve di nuovo un ingresso al blocco A diverso da quello nudo (il selettore di L48 ne è il primo
  candidato): E3 qui è misurato senza niente davanti.
