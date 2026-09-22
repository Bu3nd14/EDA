# L29b2 — il mute LDR nel sorgente, e il rilascio reso decidibile (2026-09-22)

Lotto **L29b2**. **NC-028 resta aperta e bloccante**: il caso peggiore è **L29c**, e
rilascio e inversione del profilo v3 sono **fuori soglia**, decidibili e misurati.
Dati: `data/2026-09-22/L29b2/`. ADR nuova: **ADR-039**.

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

**Il metodo di V2 non cambia.** Filtri, fit, riferimenti e soglie (ADR-035, ADR-036)
sono gli stessi, e `v2_metodo.py` non è toccato. Cambia la precisione con cui ngspice
**scrive** le forme d'onda: `set numdgt=15` nel `.control`, fuori dal blocco CANALE.
È detto qui e in #30 perché non passi in silenzio.

## 2. Rilascio e inversione del profilo v3, Td 6 s: decidibili, e fuori soglia

Banco di L29b rifatto con `numdgt=15` (`pavimento/build_nd.py`, corse in parallelo con
`dividi.py`), 1 kHz, 100 kΩ, `v2_metodo.py analizza` (`v3_td6_nd15/`). Pavimento
**lungo tutta la sequenza** (ev a 10 µs contro ev a 7 µs, `c2curva.py`): **≤ 31 µV**
sulla principale e ≤ 10 µV sulle fisse.

| Principale / fisse | C2 | Soglia |
|---|---|---|
| inserzione | **2,50 / 0,60 mV** | 1 mV |
| **rilascio** | **3,41 / 0,88 mV** | 1 mV |
| **inversione a d = 0,75** | **7,36 / 2,15 mV** | 1 mV |
| relè, chiusura / apertura | 0,067 / 0,057 mV | 1 mV |
| A senza segnale | ≤ 33 nV | 100 µV |
| B2 | 0,29 µV | 100 µV |
| carico minimo sulla sorgente | 714 kΩ | E3 ≥ 100 kΩ |

**Perché il rilascio è peggio dell'inserzione** (`v3_td6_nd15/stati_ev.txt`):
- v3 fa lento il solo tratto della serie da 10 kΩ a ~2 MΩ, cioè da 0 a −9,5 dB contro
  R_IN;
- il resto, da 2 MΩ a 400 MΩ (da −9,5 a −52 dB), all'inserzione lo fa lo spegnimento
  della cella, che è lento per natura;
- al rilascio la cella **si accende alla velocità del LED**: fra d = 0,475 e 0,45, cioè
  in 150 ms, R_s passa da 10^8,6 a 10^6,8 Ω e il livello da −62 a −26 dB. La
  derivazione intanto è ancora a ~500 kΩ, perché il suo spegnimento è lento.

L'inversione ha lo stesso tratto (−20 → −13 dB in 0,1 s), più uno spigolo all'istante
in cui d cambia verso (sotto).

**Una proprietà del metodo, registrata.** Nella finestra C2 del rilascio, finché la
corsa è ancora silenziata, C2 contro «mai» vale **0,96 mV** sulla principale: è il
residuo di regime della corsa di riferimento, la distorsione della catena, non un
evento. Sta sotto la soglia di 1 mV, ma di poco. Il metodo non è stato toccato.

## 3. Una proposta, non adottata: il profilo v4

Il profilo è una scelta dell'utente (ADR-038). La **v4** è una proposta di questo
lotto, misurata come lo erano v1 e v2 in L29b (`v4_td6_nd15_proposta/`):
- la serie come v3 fino a 4,5 µA a d = 0,45;
- poi log-lineare fino al ginocchio del buio, **0,19 µA a d = 0,75**;
- 10 nA a d = 0,8;
- la derivazione invariata.

La sovrapposizione con la derivazione (d da 0,5 a 0,75) avviene con R_s ≥ 2 MΩ, quindi
la sorgente non vede mai un carico basso (ADR-038 punto 3).

| Principale / fisse | v3 | **v4** |
|---|---|---|
| C2 inserzione | 2,50 / 0,60 mV | 2,50 / 0,60 mV |
| **C2 rilascio** | 3,41 / 0,88 mV | **1,47 / 0,30 mV** |
| C2 inversione | 7,36 / 2,15 mV | 5,01 / 1,40 mV |
| relè | 0,067 / 0,057 mV | 0,067 / 0,057 mV |
| A, B2 | ≤ 33 nV, 0,29 µV | ≤ 33 nV, 0,29 µV |
| carico minimo | 714 kΩ | 714 kΩ |
| pavimento di C2 | ≤ 31 µV | ≤ 8 µV |

- Con v4 il rilascio scende **sotto l'inserzione**, e le fisse stanno sotto soglia in
  tutti e due i versi. La principale resta fuori, come l'ideale che ADR-036 aveva
  accettato «per ora».
- **L'inversione ha un secondo meccanismo**: il picco cade all'istante dell'inversione
  (t = 5,502 s), dove d cambia verso di colpo e l'inviluppo ha uno spigolo. Un comando
  con **accelerazione limitata** lo smusserebbe. Non è stato misurato: è un cambio del
  comando, quindi è dell'utente.

## 4. Il sorgente

`circuits/preamp/preamp_audio.py` (ADR-039):
- **U101 / U301**, la serie, fra il pin 1 del connettore d'ingresso e l'ingresso del
  blocco A;
- **U102 / U302**, la derivazione, dal nodo di R_IN a GND;
- i LED della stessa funzione in serie fra i canali, sul connettore **J3 `LDR_CMD`**;
- il contratto del comando (profilo v3 Td 6, 10 nA di riposo, relè 0,5 s dopo d = 1)
  è scritto accanto a J3;
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
- **2d** non cambia: copre il solo disegno del blocco di guadagno, e le LDR stanno
  fuori da `gain_block()`.

## 5. E3, E5 e l'accoppiamento LED–cella

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
  ricava un **requisito**:
  - rumore all'anodo della derivazione **≤ 0,69 mV/√Hz** piatto, per 1 µV al jack (la
    quota di ADR-022, a +10 dB);
  - dal lato sorgente della serie il limite è 41 V/√Hz: irrilevante.

## 6. P7, riletto

ADR-038 lasciava un'ipotesi: P7 resta conforme senza una misura nuova. **Regge, per
ragionamento:**
- L17 ha misurato P7 conforme con i jack a massa **e il segnale presente**
  (`tb_mute_corto.cir`). È il caso più severo, perché gli stadi d'uscita erogano la
  corrente del segnale nel corto.
- Col mute a monte, a mute inserito il segnale è tolto prima del blocco A (serie
  ≥ 2 MΩ, derivazione a ~88 Ω), e gli stadi d'uscita non ne hanno.
- Nessun guasto del comando rende la condizione peggiore di quella di L17:
  - comando spento: la serie si fa buia, e il segnale sparisce;
  - comando bloccato acceso sulla serie: il segnale arriva ai jack a massa, cioè
    esattamente il caso di L17.

Nessuna misura nuova. Il ragionamento sta qui e in NC-028.

## 7. Il deck versionato

`spice/preamp/tb/tb_v2_mute_ldr.cir`, **generato** da
`data/2026-09-22/L29b2/deck/genera_tb_v2_mute_ldr.py`. Il profilo è un argomento: v3
di default, v4 in opzione.
- Il blocco CANALE è identico: `v2_metodo.py canale` dà OK sui 4 deck.
- `set numdgt=15`.
- Tre uscite × 100 e 10 kΩ × 20 Hz / 1 kHz / 20 kHz: 50 corse, col pavimento lungo la
  sequenza per ogni cella (`evp`, `invp` a un altro TMAX).
- Si corre diviso (`dividi.py`) e in parallelo; le corse a 20 kHz (TMAX 0,5 µs) valgono
  circa un'ora e ~2,3 GB l'una.

**ESITO DELLA MATRICE: vedi §7.1**, scritto a corse finite.

### 7.1 Esito

(da riempire a corse finite)

## 8. Verdetto

(da riempire)
