# Registro delle non conformità — preamplificatore

**Documento vivo**: sempre vero al presente. Le voci si aprono e si
chiudono qui; il *perché* di ognuna sta nel report di gate datato che
l'ha aperta, in `reports/`, che non si riscrive mai.

Ultimo aggiornamento: **2026-09-09** (creato in L3c; **G0 eseguito in
L5d**: 8 voci aperte, 2 bloccanti. **L'accesso a G1 non è concesso**
finché NC-001 e NC-004 restano aperte)

---

## A cosa serve

Deciso il 2026-09-09: **il gate non è attaccato alla PR, è attaccato ai
risultati dei test.** Un diff è l'artefatto sbagliato su cui giudicare un
progetto analogico — le righe modificate di `gain_block.py` non dicono
niente sul margine di fase, e nel momento in cui una PR è aperta le
misure che risponderebbero alla domanda del gate non esistono ancora.

Quindi `design-reviewer` gira **offline, dopo il merge**, su `main`, sul
dossier e sui dati, e produce **non conformità** invece di un veto. Il
lavoro non si ferma ad aspettare un gate: il gate lo genera.

## Severità, e cosa blocca davvero

| Severità | Significato | Effetto |
|---|---|---|
| **bloccante** | un requisito non è soddisfatto, oppure manca l'evidenza per dire se lo è | la fase successiva non si apre: niente layout, niente fabbricazione. **A G0 significa: non si accede a G1**, quindi la topologia non si congela |
| **maggiore** | scostamento reale, con margine residuo o rimedio noto | va chiusa prima del gate successivo |
| **minore** | osservazione da registrare, nessun rimedio richiesto ora | resta aperta e visibile |

## G0 — il gate che sta prima del congelamento

Aggiunto il 2026-09-09 su proposta dell'utente, con un argomento di costo:
**gli errori a catena costano moltissimo**, e G1, G2 e G3 stanno tutti dopo
il punto in cui un errore ha già propagato. G0 chiede una cosa sola:
*quello che il progetto ha misurato finora dice che il circuito fa quello
che ha promesso?*

**Giudica il prodotto, non l'ambiente.** Circuito, comportamento misurato,
ADR e **i disegni che rappresentano il circuito**. Non i banchi di prova,
non gli script, non la toolchain: se il revisore ci inciampa lo annota
sotto «osservazioni fuori scope» e non apre una non conformità.

Le sei domande, il perché della sesta e cosa blocca una voce bloccante
stanno in `../../AGENTS.md`, sezione **G0**. Qui sta solo l'effetto: una
voce **bloccante** aperta a G0 impedisce l'accesso a **G1**, e si chiude o
con una modifica del circuito o con una ADR che accetti lo scostamento
consapevolmente e per iscritto.

**Il BLOCK non è sparito, si è spostato.** Prima era un veto su un merge;
ora è una non conformità bloccante che impedisce l'**avanzamento di
fase**. È ciò che quella regola voleva dire fin dall'inizio. In
particolare: **su un progetto collegato alla rete elettrica l'assenza di
un'analisi di sicurezza è una non conformità bloccante automatica a G3**,
e questa riga non si annacqua per omissione.

## Formato di una voce

```
### NC-<numero> — <titolo>

| | |
|---|---|
| Requisito | E4 / V2 / ADR-008 — quello che la voce viola |
| Severità | bloccante / maggiore / minore |
| Aperta da | reports/<data>-gate-G<n>.md |
| Stato | aperta / chiusa il <data> da <cosa l'ha chiusa> |

**Evidenza.** Il file di dati e la misura, non un'impressione.
**Cosa serve per chiuderla.** Concreto e verificabile.
```

Ogni voce nomina il **file di dati** che la sostiene, sotto
`docs/preamp/data/<YYYY-MM-DD>/`. Una non conformità senza evidenza
apribile non è una non conformità, è un'opinione.

---

## Voci aperte

Aperte tutte da `reports/2026-09-09-gate-G0.md`, il primo gate eseguito
(L5d, 2026-09-09). Otto voci: **2 bloccanti, 1 maggiore, 5 minori**.
**L'accesso a G1 non è concesso** finché NC-001 e NC-004 restano aperte.

I numeri riportati qui sono stati **rieseguiti dall'orchestratore** prima
di essere trascritti: la riesecuzione sta in fondo a quel report, sezione
«Verifica dell'orchestratore».

### NC-001 — Il mute in derivazione porta lo stadio d'uscita fuori dalla Classe A

| | |
|---|---|
| Requisito | **V2** · **T1**/ADR-003 (Classe A pura) · **F6**/ADR-012 · P5 |
| Severità | **bloccante** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | aperta |

**Evidenza.** I contatti NC dei relè di mute cortocircuitano a massa i
nodi **jack**, cioè a valle dei 47 Ω e del 4,7 µF
(`circuits/preamp/preamp_audio.py`, righe 132-141 e 242-243). Il carico
che lo stadio vede a mute inserito è |47 + 1/jωC| ≈ 58,6 Ω a 1 kHz, non i
100 kΩ su cui è costruita l'affermazione «Classe A garantita» scritta in
rosso su `docs/preamp/schematic/gain_block.svg`.

Regime di riposo dai dati versionati:
`docs/preamp/data/2026-09-09/tb_op.log` dà `@q134[ic] = 1.455730e-02`.
**Per la condizione di mute non esiste alcun file** in
`docs/preamp/data/2026-09-09/`: l'assenza è essa stessa l'evidenza
rispetto a V2, che quel transitorio lo richiede esplicitamente.

Simulata dal revisore e **rieseguita in modo indipendente
dall'orchestratore**, con risultati coincidenti a tutte le cifre:

| Condizione | I_C picco di Q134 |
|---|---|
| non mutato, 0 dB | 14,589 mA (minimo 14,524 — Classe A) |
| **mutato, 0 dB** | **65,07 mA** |
| non mutato, +10 dB | 17,37 mA |
| **mutato, +10 dB** | **203,2 mA**, ~14× la corrente di riposo |

A mute inserito i due dispositivi d'uscita **si interdicono a turno**,
ciascuno sulla propria semionda: lo stadio lavora in classe B in una
condizione che F6 impone di attraversare a **ogni commutazione di
guadagno**, cioè col segnale presente. Non è un problema di stabilità
(margine di fase coi jack cortocircuitati: 72,76°): è un problema di
regime di lavoro, dissipazione e correnti di rail, e contraddice T1.

**Cosa serve per chiuderla.** Una delle due, per iscritto:

1. una modifica di topologia in `circuits/preamp/preamp_audio.py` che
   limiti la corrente a mute inserito (resistenza in serie al contatto, o
   spostamento del punto di derivazione), **più** un deck versionato che
   misuri I_C dei due dispositivi d'uscita e il transitorio di inserzione
   e rilascio del mute, coi dati sotto `docs/preamp/data/<data>/` come V2
   richiede; oppure
2. una **ADR nuova** che accetti consapevolmente il regime fuori Classe A
   durante il mute, col calcolo termico che mostra che MJE15032/33
   reggono la condizione per tutta la durata del temporizzatore, e la
   correzione della frase «Classe A garantita» su `gain_block.svg` e in
   `gain_block.py`.

### NC-004 — E5 e V4 senza alcuna evidenza: rumore e distorsione non sono note

| | |
|---|---|
| Requisito | **E5** (rumore in uscita < 10 µV RMS) · **V4** |
| Severità | **bloccante** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | aperta |

**Evidenza.** `docs/preamp/data/2026-09-09/` non contiene alcun file di
rumore, per scelta dichiarata nel suo `README.md` («`KF = 0` su ogni
dispositivo segnaposto»), e nel repo non esiste alcun modello vendor:
`spice/preamp/placeholder_devices.lib` è interamente scritta a mano. **Il
progetto dice la verità; il requisito resta senza evidenza**, e la
tabella delle severità assegna «bloccante» proprio a questo caso.

Non è un rimprovero, è il meccanismo: il rumore **può cambiare la
topologia**. Il breakdown in `circuits/preamp/gain_block.py` dà come
contributori dominanti a 1 kHz lo **specchio di corrente** (~5,3 e
~5,0 nV/√Hz) e le sue degenerazioni da 47 Ω (4,85 nV/√Hz ciascuna),
**non** i JFET (1,6). Se col 1/f dei modelli veri quel pavimento sale, il
rimedio non è un componente diverso: è il dimensionamento dello specchio.
Congelare la topologia prima di saperlo è l'errore a catena che G0 esiste
per intercettare.

**Cosa serve per chiuderla.** I modelli vendor (**L6-L7, che questa voce
non blocca**, come `AGENTS.md` prescrive), poi una riesecuzione di
`spice/preamp/tb/tb_noise_breakdown.cir` coi risultati versionati sotto
`docs/preamp/data/<data>/`, il totale 20 Hz–20 kHz non pesato confrontato
coi 10 µV di E5 nel caso peggiore (blocco B a +10 dB, sorgente 2,5 kΩ), e
la provenienza di ogni modello dichiarata accanto alla cifra, come V4
richiede.

### NC-002 — Il blocco A non ha evidenza di stabilità valida

| | |
|---|---|
| Requisito | **V1** · ADR-008 addendum (47 Ω) · ADR-007 addendum (4,7 µF) |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | aperta |

**Evidenza.** In `docs/preamp/data/2026-09-09/` i file `tb_loop_blockA_*`
sono **zero**: i quattro file d'anello versionati sono tutti blocco B. Il
blocco A è **due delle quattro istanze** del prodotto. L'unico banco che
lo copre, `spice/preamp/tb/tb_loop_blockA.cir` righe 28-32, usa
`RSEP = 100` e `CFIX = 2.2u` — i valori **superati** dagli addendum che
`preamp_audio.py` implementa.

Rifatto col carico canonico (47 Ω, 4,7 µF, scarico 470 kΩ) e **rieseguito
dall'orchestratore**: 69,83° a vuoto, 64,08° a 1 nF, 56,65° a 2,2 nF,
**41,98° a 4,7 nF** sul nodo OUT. I 47 Ω isolano **meno** dei 100 Ω del
deck: il circuito reale è più esposto di quello simulato, non meno.
41,98° resta un margine stabile — non è un oscillatore — ma è **sotto il
56,945° che il dossier pubblica come caso peggiore**, e nessuno di questi
numeri esiste nel repo.

**Cosa serve per chiuderla.** Aggiornare `tb_loop_blockA.cir` ai valori
di `preamp_audio.py` (47 Ω, 4,7 µF, scarico 470 kΩ, attenuatore 10 kΩ),
spazzare la capacità sia sul nodo OUT sia sui due jack, versionare i CSV
sotto `docs/preamp/data/<data>/` e riportarli nel dossier accanto ai
quattro del blocco B. Se il caso peggiore del blocco A resta sotto quello
del blocco B, il KPI va corretto di conseguenza (NC-003).

### NC-003 — Il KPI «margine di fase, peggiore» non è il peggiore del prodotto

| | |
|---|---|
| Requisito | **V1** · regola operativa 6 di `AGENTS.md` |
| Severità | **minore** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | aperta |

**Evidenza.** `docs/preamp/dossier/index.html`, riquadro KPI in testa
alla pagina: «Margine di fase, peggiore — 56,945 gradi», senza
qualificatore. Il valore viene da
`docs/preamp/data/2026-09-09/tb_loop_0db_4.7n.csv` ed è riprodotto, ma il
blocco A col carico canonico e la stessa sonda da 4,7 nF dà **41,98°**
(NC-002). Il corpo della sezione 6 è invece corretto («il caso peggiore
fra questi quattro»): è il KPI, cioè ciò che un lettore porta via, a fare
una claim sul prodotto che i dati non sostengono.

**Cosa serve per chiuderla.** O il KPI porta il qualificatore («peggiore
fra i quattro casi del blocco B pubblicati»), o comprende il blocco A una
volta che NC-002 avrà prodotto i dati.

### NC-005 — E3 non è verificabile: il valore lo determinerà il trim, che non è progettato

| | |
|---|---|
| Requisito | **E3** (Zin ≥ 100 kΩ) · F2/ADR-011 |
| Severità | **minore** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | aperta |

**Evidenza.** Nessun file in `docs/preamp/data/2026-09-09/` misura
l'impedenza d'ingresso. In topologia `R_IN = "1M"` in
`circuits/preamp/gain_block.py` è l'unico elemento che fissa la Zin del
blocco A, ma la catena reale ha a monte il partitore di trim 0/−6/−12 dB
di ADR-011, che `preamp_audio.py` dichiara esplicitamente fuori dal
proprio perimetro. Un partitore dimensionato senza vincolo — poniamo
10 k/3,3 k per i −12 dB — porterebbe Zin a ~13 kΩ, **violando E3 di un
ordine di grandezza** senza che nulla nel repo lo segnali.

**Cosa serve per chiuderla.** Scrivere il vincolo dove verrà letto: nel
file della scheda ingressi quando esisterà, o intanto in
`REQUIREMENTS.md` o in ADR-011 come nota di dimensionamento («la
resistenza vista all'ingresso, in ogni posizione del ponticello di trim,
deve restare ≥ 100 kΩ»), e verificarlo con una misura AC quando la scheda
sarà in `circuits/preamp/`.

### NC-006 — `gain_block.py` porta due valori superati per il riferimento di cascode

| | |
|---|---|
| Requisito | Regola di tracciabilità di `CLAUDE.md` · ADR-014 |
| Severità | **minore** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | aperta |

**Evidenza.** `circuits/preamp/gain_block.py` contiene, nella stessa
funzione, tre valori incompatibili per lo stesso nodo: il blocco delle
costanti dice «~10 V da un partitore 4,99k/10,0k» — corretto, ed è ciò
che il codice implementa; un commento sopra le resistenze vere dice
«**8,485 V**»; un altro sopra i cascode dice «i drain a **7,8 V**».
`docs/preamp/data/2026-09-09/tb_op.log` misura `v(ncasc) = 9.886765e+00`
e `v(d1n) = 9.208879e+00`. I due commenti descrivono la bozza precedente,
che il blocco delle costanti racconta di aver abbandonato. Il disegno
`gain_block.svg` porta invece i valori giusti: **il disegno è più
affidabile del sorgente di verità**, che è il rapporto opposto a quello
che il repo vuole.

**Cosa serve per chiuderla.** Allineare i due commenti al valore
implementato, col riferimento a ADR-014 e al `tb_op.log` che lo misura.

### NC-007 — Lo «scarto ADR-014» pubblicato non misura la claim di ADR-014

| | |
|---|---|
| Requisito | **ADR-014** · V1 |
| Severità | **minore** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | aperta |

**Evidenza.** Il dossier presenta come verifica della claim falsificabile
di ADR-014 lo «scarto a 20 kHz» fra sorgente 1,5 Ω e 2500 Ω: 0,022 dB. Da
`docs/preamp/data/2026-09-09/tb_ac_0db_1.5.csv` e
`docs/preamp/data/2026-09-09/tb_ac_0db_2500.csv`, **rieseguito
dall'orchestratore**, quella differenza c'è identica a tutte le
frequenze — 0,02167 dB a 20 Hz, 0,02167 a 1 kHz, 0,02163 a 20 kHz — ed è
esattamente il partitore fra i 2500 Ω e il 1 MΩ di `R_IN`:
20·log₁₀(10⁶/(10⁶+2500)) = **−0,02169 dB**. È una perdita di livello a
banda larga, **che ci sarebbe identica anche senza cascode**.

La claim di ADR-014 riguarda la *forma* della risposta, non il livello:
riferito a 1 kHz lo scarto vero è **4,35·10⁻⁵ dB**, che è il numero che
`gain_block.py` cita («0.0001 dB»). Circolano quindi due cifre per la
stessa claim, e quella pubblicata nel KPI è la meno pertinente — nonché
quella che un cascode difettoso lascerebbe invariata.

**Cosa serve per chiuderla.** Il dossier presenta lo scarto **riferito a
1 kHz** come misura della claim di ADR-014 (o entrambe le cifre, dicendo
cosa misura ciascuna), e il KPI in testa cita quella.

### NC-008 — E4 verificata su un'uscita su tre e a manopola ferma

| | |
|---|---|
| Requisito | **E4** («… costante con la posizione del volume») · F3 · ADR-008 |
| Severità | **minore** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | aperta |

**Evidenza.** `docs/preamp/data/2026-09-09/tb_zout_psrr_noise_zout_0db.csv`
e `tb_zout_psrr_noise_zout_10db.csv` misurano l'impedenza al solo **jack
principale**, con l'ingresso a massa e quindi con l'attenuatore in una
sola condizione. Il prodotto ha **tre** uscite (F3): le due fisse escono
dal blocco A attraverso 47 Ω + 4,7 µF + scarico 470 kΩ e non compaiono in
nessun file versionato. La seconda clausola di E4 — costanza con la
posizione del volume — non è esercitata da nessun dato.

Il rischio è basso: il blocco B è un inseguitore ad anello chiuso, e gli
sweep degli assi di V1 fatti al gate mostrano che il ramo principale non
dipende praticamente dalla sorgente. Ma «basso» non è «misurato», ed E4
la clausola ce l'ha scritta.

**Cosa serve per chiuderla.** Estendere
`spice/preamp/tb/tb_zout_psrr_noise.cir` alle due uscite fisse e ad
almeno tre posizioni dell'attenuatore (minimo, metà corsa, massimo), e
versionare i CSV sotto `docs/preamp/data/<data>/`.

## Voci chiuse

*Nessuna.*
