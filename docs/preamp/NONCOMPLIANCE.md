# Registro delle non conformità — preamplificatore

**Documento vivo**: sempre vero al presente. Le voci si aprono e si
chiudono qui; il *perché* di ognuna sta nel report di gate datato che
l'ha aperta, in `reports/`, che non si riscrive mai.

Ultimo aggiornamento: **2026-09-14** (creato in L3c; **G0 eseguito in
L5d**; **revisione umana del dossier in L5e**; **L7** ha aperto NC-013;
**L8** ha aperto NC-014…NC-017; **L8b** ha registrato **ADR-016**; **L24**
ha eseguito T7 su tutti i dispositivi attivi e aperto NC-018 e NC-019;
**L22 + L23** hanno **chiuso NC-015 e NC-016** e aperto NC-020; **L26** ha
registrato i **tre requisiti nuovi dell'utente** (**ADR-019**), che
**chiudono NC-012** dandole la soglia che chiedeva e **aprono NC-021…NC-023**.
La soglia di margine di fase a **60° ovunque** rende **NC-002 decidibile**, e
il verdetto è **negativo**: quella voce sale a **bloccante**. **L25** ha
promosso i cinque modelli in `models/` — primo dei tre passi di **NC-017**,
che resta bloccante per la sola sostituzione in Fase 4 — e rimisurandoli alle
condizioni dei loro datasheet ha aperto **NC-024** e **NC-025**: il MJE15032
manca il proprio minimo di h_FE, ed **entrambi** i MJE mancano il proprio
minimo di f_T quando la si legge come il datasheet la definisce. **L21** ha
**chiuso NC-014** — il polo 2 del relè, corretto, riverificato sulla netlist e
protetto da un guardiano permanente in `run_tests.sh` — e, trovandolo mentre
verificava, ha aperto **NC-026**: il disegno a blocchi non è rigenerabile da
L22, quindi le sue asserzioni non girano. **L10** ha chiuso NC-026 e aperto
NC-027. **L14** ha chiuso **NC-003, NC-006 e NC-007**: tre punti in cui il repo
diceva una cosa diversa da quella che i suoi dati misurano. **L15** ha scritto
il vincolo di **NC-005** accanto a E3 (`REQUIREMENTS.md`, «Nota su E3»): la
voce resta aperta per la misura, che è di L16. **L18** ha fatto lo stesso con
**NC-011**: la quota del ripple è **ADR-020**, e sta nella «Nota su E5 — la
quota del ripple d'alimentazione». La voce resta aperta per il rimedio e la
verifica, che sono del lotto dell'alimentatore. **L11** (2026-09-14) ha
registrato **ADR-021** e **ADR-022**. Ha misurato il mute e il corto su
ciascuna uscita, e la topologia di oggi regge il criterio termico: **chiude
NC-001**. Ha trovato il gradino che il rilascio del mute porta sul jack e
**apre NC-028**. **L17** (2026-09-14) ha registrato **ADR-023** — la classe A si
giudica sui percorsi ascoltabili — e ha dato a ogni uscita fissa il proprio
buffer: **chiude NC-010**. Misurando il calore a riposo dei quattro blocchi
in più ha **aperto NC-029**. **L12** (2026-09-14) ha registrato **ADR-024** —
la sonda capacitiva di V1 è il cavo al jack, e il blocco A si giudica col suo
cablaggio — e **ADR-025**, il C_f da 22 a 330 pF: **chiude NC-002 e NC-021**.
**L27** (2026-09-14) ha registrato **ADR-026** — il terzo livello di guadagno,
due rami di R_g in parallelo su due relè — e l'ha misurato su tutta la matrice:
**chiude NC-022**. Estendendo i deck ha trovato un deck che da tempo non scrive
dati, e **apre NC-030**. **L16** (2026-09-14) ha registrato **ADR-027** — un
solo trim, fra il blocco A e l'attenuatore, a relè bistabili con LED e
permissivo dal mute — e l'ha misurato e provato sulla netlist: **chiude NC-005 e
NC-023**, e dà a NC-009 la sua cifra con la metrica, che resta da pubblicare
nel dossier (L32).
**L32** (2026-09-15) ha rigenerato il dossier sui dati di L27 e L16 e, leggendo
la provenienza dagli `.include`, ha **aperto NC-031**. **L31** (2026-09-15) ha
esteso il blocco 2g ai vettori di rumore per dispositivo, l'ha fatto cadere sul
deck di allora, e ha rinominato i vettori con una mappa per nodi: **chiude
NC-030**. **L33** (2026-09-15) ha corretto le etichette di provenienza
dell'LSK489: quindici deck, solo nei commenti, e sette README datati annotati
in coda. Ha aggiunto il blocco **2h**, che confronta ciò che un deck dichiara
con i suoi `.include`, e l'ha fatto cadere su `main`: **chiude NC-031**.
**L34** (2026-09-15) ha messo per iscritto le decisioni di una sessione di
domande dell'utente: **ADR-028** (comandi sul frontale e LED a pannello),
**ADR-029** (ingombro del telaio) e **ADR-030** (guadagno interbloccato dal
mute, subordinato alla misura di L29). **Apre NC-032** e aggiorna NC-028.
**15 voci aperte, 2 bloccanti.**
L'accesso a G1 non è concesso finché NC-004 e NC-017 restano aperte.

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

Le sette domande, il perché della sesta e della settima, e cosa blocca una
voce bloccante stanno in `../../AGENTS.md`, sezione **G0**. La settima è
stata aggiunta in L5e: la prima esecuzione di G0 ha dimostrato che le
domande di confronto trovano le affermazioni **false** e non le
**omissioni di giudizio** — vedi NC-010. Qui sta solo l'effetto: una
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

Diciassette voci, da **quattro** origini distinte:

- **NC-001 … NC-008** da `reports/2026-09-09-gate-G0.md`, il primo gate
  eseguito (L5d): 2 bloccanti, 1 maggiore, 5 minori.
- **NC-009 … NC-012** da `reports/2026-09-09-revisione-utente-dossier.md`,
  la revisione umana del dossier (L5e): 1 bloccante, 3 maggiori.
- **NC-013** da `reports/2026-09-09-L7-controllo-incrociato-lsk489.md`, il
  controllo incrociato del modello LSK489 (L7): 1 maggiore. È la prima
  voce che non nasce da una revisione ma da un **controllo prescritto da
  una ADR** — ADR-013 passo 4.

- **NC-014 … NC-017** da `reports/2026-09-10-L8-parti-nuove.md`, il primo
  lotto del giro componenti (L8): **2 bloccanti**, 2 maggiori. Come NC-013,
  non nascono da una revisione: nascono dall'aver **letto le fonti dei
  costruttori** invece di fidarsi di quello che il progetto assumeva.

In tutto: **6 bloccanti, 6 maggiori, 5 minori**. **L'accesso a G1 non è
concesso** finché NC-001, NC-004, NC-010, NC-014 e NC-017 restano
aperte.

**La scadenza esterna non c'è più, ed è stato per decisione.** NC-015
aveva il last-time buy del THAT320 al 2026-09-30; il 2026-09-10 l'utente
l'ha **scartato** — l'approvvigionamento non era praticabile e un
componente a fine vita non entra in un progetto nuovo. Da lì **ADR-016**
e i requisiti **T7** e **T8**, che è il motivo per cui NC-017 è passata da
maggiore a bloccante: misura la distanza da un requisito, non da una
preferenza.

**Quattro voci sono ora la stessa storia** e conviene leggerle insieme:
NC-004 (rumore e distorsione senza evidenza) è bloccata da NC-017 (sei
dispositivi su sette senza modello vendor), che a sua volta trascina
NC-015 (il THAT320 esce) e NC-016 (il suo footprint, che se ne va con
lui).

Le due revisioni non si sovrappongono per caso: G0 giudica incrociando
affermazioni con sorgenti e trova le **affermazioni false**; la revisione
umana vede ciò che il progetto **presenta come normale** e che nessuna
sorgente del repo contraddice. NC-010 è della seconda specie, ed è il
motivo per cui il controllo cieco su G0 era stato allestito.

I numeri riportati qui sono stati **rieseguiti** prima di essere
trascritti: per NC-001…NC-008 la riesecuzione sta in fondo al report di
G0, sezione «Verifica dell'orchestratore»; per NC-009…NC-012 sta nel
report di L5e, che riporta ogni misura col file da cui viene.

### NC-001 — Il mute in derivazione porta lo stadio d'uscita fuori dalla Classe A

| | |
|---|---|
| Requisito | **V2** · **T1**/ADR-003 (Classe A pura) · **F6**/ADR-012 · P5 |
| Severità | **bloccante** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | **CHIUSA il 2026-09-14 da L11** — ADR-021, deck versionato, verdetto termico conforme. Vedi «Chiusura» in fondo alla voce e «Voci chiuse» |

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

**Decisione dell'utente, 2026-09-13.** Il mute deve potersi tenere inserito
**a tempo indefinito**, a costo di cambiare la topologia. A mute inserito la
classe B **è accettabile**, ma il mute **non deve mettere a rischio la
termica**. Le due strade qui sopra cambiano così:
- **la strada 2 resta**, ma il calcolo termico va fatto **a regime**, non
  «per tutta la durata del temporizzatore». Un calcolo su una durata finita
  non chiude la voce;
- **se a regime i dispositivi d'uscita non reggono**, resta solo la strada 1.

La decisione va registrata in una ADR nuova, che supera la durata «qualche
secondo» di ADR-012 e ammette l'eccezione a T1 a mute inserito. È il primo
passo di L11.

**Secondo requisito dell'utente, 2026-09-13: protezione dal corto sulle
uscite.** «Non possiamo essere certi che le uscite non vengano messe in
corto.»
- **Il mute ne è un caso particolare.** Il contatto NC mette a massa lo stesso
  nodo del jack su cui arriva un corto esterno. La stessa ADR li registra
  entrambi.
- **Il requisito descrive l'esito, non la tecnica** (precisato dall'utente lo
  stesso giorno). Nessun dispositivo esce dai limiti termici e SOA, **a regime
  e nel transitorio prima dell'intervento**. Limitazione di corrente, distacco
  attivo e mute attivo sono tutti ammessi.
- **Conseguenza sulla strada 1.** Una resistenza in serie al contatto chiude la
  via del mute, non quella del corto esterno: da sola non basta più. E il mute
  di oggi, in derivazione, **non protegge** dal corto; lo farebbe solo un mute
  in serie.
- **Operazionali e microcontrollore fuori dal percorso del segnale sono
  ammessi** (decisione dell'utente dello stesso giorno, da registrare come
  ADR-022). Una protezione attiva può quindi usarli, alle condizioni scritte
  nel mandato di L11.
- **Se, una volta registrato il requisito**, la topologia non lo soddisfa su
  una via che né questa voce né NC-010 coprono, L11 apre la voce che manca.

**Chiusura (L11, 2026-09-14).** La voce si chiude per la strada 2, nella forma
che la decisione dell'utente le ha dato.

1. **Decisione registrata: ADR-021.**
   - Mute tenibile a tempo indefinito.
   - Classe B ammessa solo a mute inserito e in corto.
   - Criterio: Tj ≤ 125 °C a 60 °C ambiente, a regime e nel transitorio, SOA
     dentro le curve.
   - Requisito **P7** con la sua nota in `REQUIREMENTS.md`, eccezione scritta
     in **T1**, **F6** aggiornato.
2. **Misura versionata**: `spice/preamp/tb/tb_mute_corto.cir`, dati in
   `data/2026-09-14/`.
   - Copre un canale intero, A → attenuatore → B.
   - Casi: normale, mute (tre jack a massa insieme, come il cablaggio),
     corto franco su ciascuna delle tre uscite.
   - Modalità 0 e +10 dB, 1 e 20 kHz, ampiezza e manopola spazzate.
   - Transitorio di inserzione e rilascio.
3. **Verdetto: conforme, senza protezione e senza dissipatore.**
   - MJE peggiore **484 mW → Tj 90,2 °C** contro 1,04 W ammessi. È il blocco
     A **a mute inserito**, con le due fisse in parallelo: il caso che G0
     non aveva simulato.
   - Dispositivo più caldo: Q125, Tj 96,5 °C.
   - Picchi istantanei sulle MJE ≤ 1,55 W, con V_CE ≤ 30 V e I_C ≤ 207 mA:
     sotto la curva da 250 ms della Fig. 2 del datasheet di più di un ordine
     di grandezza.
   - Contatti di mute ≤ 153 mA RMS contro 2 A.
4. **Confronto con G0**, che era sulla topologia col THAT320. Nella stessa
   configurazione di G0 (blocco B, mute, 1 kHz, fondo scala) oggi I_C(Q132)
   vale:
   - **65,063 mA** a 0 dB, contro 65,07;
   - **203,017 mA** a +10 dB, contro 203,21.

   Scarto ≤ 0,1 %. Il nome `@q134` di G0 **non esiste più**: i dispositivi
   d'uscita sono Q132/Q133 in `gain_block.subckt`.
5. **Il deck è stato fatto fallire.** Senza le tre righe `SMUTE`, le 36 righe
   di mute diventano identiche a quelle normali (0 su 36, contro 32 su 36).
   **Controprova indipendente** della potenza da tensioni e correnti:
   scarti ≤ 0,23 %.
6. **La frase «Classe A garantita» è corretta** in `gain_block.py` (AST
   identico a HEAD, controllo fatto fallire) e in `gain_block_draw.py` →
   `gain_block.svg`.

**Cosa la chiusura consegna, e non risolve:**
- **tre vincoli di distinta sulle resistenze** (la 47 Ω dell'uscita principale
  ≥ 1,1 W a 60 °C), scritti in P7 e nei commenti dei sorgenti;
- **NC-028**, il gradino al rilascio del mute, che V2 chiedeva di misurare e
  che la misura ha trovato;
- **la sensibilità ai modelli**: coi modelli vendor la corrente di riposo
  sale a 20,1 mA e il MJE peggiore a 496 mW. Verdetto invariato, ma si ripete
  quando la Fase 4 ritara la polarizzazione (NC-024, NC-025).

Report: `reports/2026-09-14-L11-mute-e-corto.md`.

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

**AGGIORNATA IL 2026-09-10 da L24, e la notizia è cattiva.** I modelli
vendor ora esistono per sei dispositivi attivi su sette
(`reports/2026-09-10-L24-t7-dispositivi-attivi.md`), ma **nessuno dei
cinque congelati in L24 porta `KF`/`AF`**: né MMBT5401, né MMBT5551, né
MJE15032, né MJE15033, né il 1N4148. Con i due modelli THAT
(`docs/limitations.md` #17) questo significa che **nel repo solo l'LSK489
ha rumore 1/f**. *Precisato da L33 (NC-031):* è vero della libreria
`models/`, non delle simulazioni. Nessun deck include
`models/jfet/lsk489.lib`; l'LSK489 simulato è il segnaposto `LSK489X` con
`KF = 0`, quindi oggi **nessun dispositivo simulato ha rumore 1/f**. Quindi questa voce **non si chiude «quando arrivano i
modelli veri»**: le cifre che usciranno dalla Fase 4 restano un pavimento
senza flicker, e il pavimento senza flicker cade proprio dove l'analisi
dice che il rumore è dominante — lo specchio di corrente e le sue
degenerazioni. Va scritto **accanto a ogni numero**, non sottinteso.

**Cosa serve per chiuderla.** I modelli vendor (**L6-L7, che questa voce
non blocca**, come `AGENTS.md` prescrive), poi una riesecuzione di
`spice/preamp/tb/tb_noise_breakdown.cir` coi risultati versionati sotto
`docs/preamp/data/<data>/`, il totale 20 Hz–20 kHz non pesato confrontato
coi 10 µV di E5 nel caso peggiore (blocco B a +10 dB, sorgente 2,5 kΩ), e
la provenienza di ogni modello dichiarata accanto alla cifra, come V4
richiede.

### NC-010 — Le uscite fisse non sono isolate: un apparecchio spento a valle porta il Blocco A in Classe B

| | |
|---|---|
| Requisito | **T1**/ADR-003 (Classe A pura) · **V1** (carico «Singxer (Zin ignota)») · F3/ADR-008 |
| Severità | **bloccante** |
| Aperta da | `reports/2026-09-09-revisione-utente-dossier.md` |
| Stato | **chiusa il 2026-09-14 da L17** |

**Evidenza.** Il Blocco A pilota **tre carichi in parallelo** senza
isolamento reciproco: l'attenuatore da 10 kΩ e le due uscite a livello
fisso, ciascuna 47 Ω + 4,7 µF + 470 kΩ di scarico
(`circuits/preamp/preamp_audio.py`, righe 123-140). Il suo nodo di
controreazione **è** il nodo che li pilota tutti.

Se l'apparecchio a valle di una fissa si spegne e la sua impedenza
d'ingresso crolla, quel ramo diventa un carico da qualche decina di ohm
sul nodo d'uscita. Da
`docs/preamp/data/2026-09-09/tb_blockA_carichi_*.csv`, Blocco A a guadagno
unitario con 2,7 V RMS a 1 kHz (E6):

| Impedenza a valle | I_C(Q134) max | I_C(Q134) **min** | Regime |
|---|---|---|---|
| 470 kΩ (normale) | 14,759 mA | **14,352 mA** | **Classe A** |
| 1 kΩ | 16,552 mA | 12,524 mA | Classe A |
| 100 Ω | 27,956 mA | **2,396 mA** | Classe A, margine quasi finito |
| 10 Ω | 57,258 mA | **−0,23 µA** | **Classe B** |
| 0,01 Ω | 65,456 mA | **−0,34 µA** | **Classe B** |

I due dispositivi d'uscita si interdicono a turno: lo stadio esce dalla
Classe A pura, che è **T1**. La soglia sta fra 100 Ω e 10 Ω di impedenza a
valle — fra ~147 Ω e ~57 Ω di carico totale, contando i 47 Ω di
separazione. Il picco a impedenza nulla, **65,46 mA**, è lo stesso ordine
dei 65,07 mA che **NC-001** misura per il mute: stessa fisica, via
d'ingresso diversa.

**È il caso che V1 chiedeva già di coprire** — elenca «Singxer (Zin
ignota)» fra i carichi — e che nessuna misura copriva. L'impedenza
d'ingresso del Singxer non è nota, e da spento può andare a zero.

**Ciò che l'evidenza NON sostiene**, e va detto: la modulazione reciproca
del livello. Fra fissa carica e fissa in corto, il livello sul nodo che
alimenta l'attenuatore si muove di **0,0034 dB a 1 kHz** e 0,0056 dB a
20 kHz (`tb_blockA_carichi_ac_*.csv`): l'anello chiuso tiene il nodo. Il
danno è sul **regime di lavoro**, non sul livello — e una spazzata AC di
piccolo segnale non può vederlo.

**Cosa serve per chiuderla.** Una delle due, per iscritto:

1. **Disaccoppiare le uscite fisse** con buffer inseguitori dedicati,
   lasciando il Blocco A a pilotare il solo attenuatore, più la
   riesecuzione di `spice/preamp/tb/tb_blockA_carichi.cir` sulla topologia
   nuova, coi dati versionati; oppure
2. una **ADR** che accetti il regime, col calcolo termico dei dispositivi
   d'uscita nella condizione e — questa è la parte che il progetto non ha
   — il **vincolo scritto sull'impedenza minima ammessa a valle**, che dai
   dati qui sopra sta intorno ai 150 Ω di carico totale.

**Nota sul rimedio di NC-001.** Le due voci hanno la stessa fisica ma non
lo stesso rimedio: una resistenza in serie al contatto del relè di mute
non fa niente contro un apparecchio spento, perché su questa via non c'è
nessun relè. Chi chiuderà NC-001 deve saperlo, o chiuderà una via sola.

**Requisito dell'utente, 2026-09-13: protezione dal corto sulle uscite.**
Ciascuna delle tre uscite deve reggere un corto al connettore a tempo
indefinito, senza mettere a rischio la termica. Lo registrerà **ADR-021** al
primo passo di L11, insieme al mute. Per questa voce cambiano due cose:
- **Il caso 0,01 Ω della tabella** non descrive più soltanto un apparecchio
  spento a valle: è una condizione che il progetto deve reggere.
- **La strada 2 perde metà del suo contenuto.** Il «vincolo scritto
  sull'impedenza minima ammessa a valle» non è più una via di chiusura, perché
  il requisito chiede di reggere proprio il corto. Resta possibile accettare
  la classe B in quella condizione, se passa il criterio di ADR-021: limiti
  termici e SOA **a regime e nel transitorio prima dell'intervento**.

La tecnica di protezione è libera: limitazione di corrente, distacco attivo o
mute attivo, anche con operazionali o microcontrollore fuori dal percorso del
segnale (ADR-022). Il rimedio resta di **L17**, che progetta contro il criterio
di ADR-021.

**AGGIORNATA IL 2026-09-14 da L11.**
- **`tb_blockA_carichi.cir` rieseguito sulla topologia di oggi**
  (`data/2026-09-14/`). La tabella qui sopra, che era col THAT320, coincide a
  quattro cifre: a 0,01 Ω I_C(Q132) massima **65,456 mA**, minima −0,34 µA.
  Lo stadio d'uscita non ha sentito la sostituzione dello specchio.
- **Il corto su una fissa passa il criterio di ADR-021.**
  `tb_mute_corto.cir` dà:
  - col corto su una fissa, MJE a **299,5 mW** al massimo (Tj 78,7 °C) e
    I_C di picco **80,95 mA** (0 dB, 20 kHz, fondo scala);
  - col mute, che mette a massa **entrambe** le fisse, **483,7 mW** (Tj
    90,2 °C) e 160,15 mA: è il caso peggiore del progetto;
  - le 47 Ω delle fisse a 0,155 W.
- **Quindi la parte «corto» di questa voce è conforme.** Resta aperta la
  parte per cui la voce esiste: un apparecchio **spento** a valle, con Zin
  fra ~150 Ω e il corto, porta il blocco A in classe B **fuori** dalle due
  condizioni in cui ADR-021 la ammette. È ancora **T1**, e il rimedio è ancora
  di **L17**.

**CHIUSA IL 2026-09-14 da L17**, per la strada 1, con una decisione
dell'utente che la voce non prevedeva.

**La decisione** (**ADR-023**): la classe A si giudica sui **percorsi
ascoltabili**. L'utente ha escluso la strada 2 perché un corto o un apparecchio
spento su una fissa portava fuori dalla classe A «tutto l'ascolto primario»,
e ha dichiarato ininfluente, se la termica è a posto, che ne esca un blocco
che nessuno ascolta.

**Il rimedio.** Un `GAINBLOCK` a guadagno unitario per ogni uscita fissa
(`preamp_audio.py`); la netlist passa da 197 a 357 componenti.

**L'evidenza**, `data/2026-09-14/L17/`:
- `tb_blockA_carichi.cir`, fissa 1 da 470 kΩ a 0,01 Ω, a 1 kHz e 20 kHz:
  - blocco A a **14,356 mA** e buffer della fissa 2 a **14,509 mA** in ogni
    riga;
  - va in classe B solo il buffer della fissa 1.
- **Lo stesso deck col cablaggio di ADR-008** ritrova il blocco A in classe B
  a ≤ 22 Ω (1 kHz) e ≤ 47 Ω (20 kHz). A 10 Ω e 1 kHz dà −0,2 µA, contro i
  −0,23 µA di L11.
- `tb_mute_corto.cir` a quattro blocchi:
  - 294 righe di percorsi ascoltabili, **0 fuori dalla classe A**;
  - P7 sui buffer: MJE al massimo 298,1 mW, Tj 78,6 °C;
  - apparecchio spento a 10 Ω: 261,3 mW.
- **Il blocco 2f** (`preamp_blocks_draw.py`) asserisce sulla netlist che ogni
  fissa parte dal proprio buffer. Fatto fallire sulla netlist di `main`.

Report: `reports/2026-09-14-L17-buffer-uscite-fisse.md`.

### NC-002 — Il blocco A non ha evidenza di stabilità valida, e col nuovo requisito è sotto soglia

| | |
|---|---|
| Requisito | **V1** (soglia **60°**, ADR-019) · ADR-008 addendum (47 Ω) · ADR-007 addendum (4,7 µF) |
| Severità | **bloccante** — alzata il 2026-09-10 da **maggiore** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | **CHIUSA il 2026-09-14 da L12** — ADR-024 e ADR-025. Vedi «Chiusura» in fondo alla voce e «Voci chiuse» |

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

**AGGIORNATA IL 2026-09-10 (L26): questa voce era indecidibile e ora non lo
è più.** V1 non aveva una soglia di accettazione — era esattamente il
contenuto di NC-012 — quindi i 41,98° non erano né conformi né non conformi.
**ADR-019 fissa il minimo a 60° su ogni combinazione della matrice V1, blocco
A e caso peggiore capacitivo compresi**, e il verdetto diventa negativo:
**41,98° contro 60°, mancano 18°**. Per questo la severità sale a bloccante.

Diciotto gradi non si recuperano con un ritocco. Le strade — più
compensazione, meno guadagno d'anello, una rete d'isolamento d'uscita diversa
dai 47 Ω — costano tutte qualcosa a un altro requisito, e la scelta va fatta
coi numeri di ciascuna. È il lotto **L12**, che cambia natura: non più «misura
il blocco A coi valori veri» ma «portalo sopra soglia».

**Riesecuzione indipendente, la seconda** (L5e, 2026-09-09): 69,83° a
vuoto, 64,05° a 1 nF, 56,59° a 2,2 nF, **41,85° a 4,7 nF**. Coincide entro
qualche centesimo di grado. L'utente ha segnalato lo stesso difetto per
conto proprio rileggendo il dossier — vedi
`reports/2026-09-09-revisione-utente-dossier.md`.

**Cosa serve per chiuderla.** Aggiornare `tb_loop_blockA.cir` ai valori
di `preamp_audio.py` (47 Ω, 4,7 µF, scarico 470 kΩ, attenuatore 10 kΩ),
spazzare la capacità sia sul nodo OUT sia sui due jack, versionare i CSV
sotto `docs/preamp/data/<data>/` e riportarli nel dossier accanto ai
quattro del blocco B. Se il caso peggiore del blocco A resta sotto quello
del blocco B, il KPI va corretto di conseguenza (NC-003).

**AGGIORNATA IL 2026-09-14 da L17.**

**Le istanze sono cambiate.** Coi buffer delle fisse (ADR-023) il blocco A
pilota solo l'attenuatore e due ingressi, e ogni fissa ha un `GAINBLOCK` a
guadagno unitario con l'anello che il blocco A aveva. Questa voce vale ora per
il blocco A **e** per i quattro buffer.

**Il deck del blocco A è ai valori veri** (`tb_loop_blockA.cir`), con un
controllo sul carico canonico di ADR-008. Il buffer ha un deck suo,
`tb_loop_bufferfissa.cir`. Dati in `data/2026-09-14/L17/`:

| Istanza, 4,7 nF | Sonda sul nodo | Sonda al jack |
|---|---|---|
| Blocco A, carico nuovo | **40,96°** | — |
| Blocco A, carico canonico (controllo) | 41,02° | — |
| Buffer delle fisse | **40,98°** | **62,27°** (minimo 61,74° a 2,2 nF) |

**Il controllo** sta entro 1° dai valori del 2026-09-09, che erano col
THAT320.

**La domanda che L12 deve fare per prima.** ADR-019 fissa la sonda da 4,7 nF
«ovunque», ma non dice **in che punto**:
- per il buffer la differenza fra nodo e jack vale 21°;
- per il blocco A, dopo L17, sul nodo resta solo il cablaggio verso
  l'attenuatore.

**Chiusura (L12, 2026-09-14).**

**La risposta dell'utente** (**ADR-024**):
- la sonda è il **cavo d'interconnessione**, e sta al jack;
- conta il **minimo** della spazzata fino a 4,7 nF;
- il blocco A si giudica col suo **cablaggio verso l'attenuatore**, con una
  capacità realistica presa ≤ 1 nF.

**Con quel criterio il blocco A passava già**: coi valori di L17, 63,32°
(sorgente phono 430 Ω, 1 nF). I buffer, al jack, 61,51°.

**Il rimedio del progetto** è quello di NC-021 (**ADR-025**, C_f da 22 a
330 pF), e vale anche qui. Dati in `data/2026-09-14/L12/dopo/`:
- blocco A **63,36°** (430 Ω, 1 nF), 62,69° agli spigoli di tolleranza;
- buffer delle fisse **61,63°** (Stax, 2,7 nF), 61,16° agli spigoli;
- con 4,7 nF sul nodo il blocco A darebbe 40,91°: il numero resta nel deck come
  informazione, non come verdetto.

**I «cosa serve» della voce, fatti**: `tb_loop_blockA.cir` ai valori veri
(L17), con le sorgenti di V1 (L12); la capacità spazzata sul nodo e sui jack;
CSV versionati. Il dossier legge ancora `data/2026-09-09`: resta da
rigenerare.

Report: `reports/2026-09-14-L12-margine-di-fase.md`.

### NC-009 — Il margine di headroom poggia su un trim che non esiste nel progetto, e la sua cifra circola in tre versioni

| | |
|---|---|
| Requisito | **E6** × **E2** · **ADR-015** (che decide di accettarlo) · ADR-011 · F2 |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-09-revisione-utente-dossier.md` |
| Stato | aperta |

**Il margine in sé non è una non conformità**, ed è importante dirlo:
**ADR-015 lo ha accettato consapevolmente e per iscritto** il 2026-09-08,
scegliendo di restare a ±15 V e indicando il trim di ADR-011 come rimedio.
È esattamente la forma con cui la tabella delle severità dice che uno
scostamento si chiude. Quello che segue riguarda due cose che quella
decisione ha lasciato scoperte.

**Evidenza 1 — tre cifre per la stessa quantità.** Da
`docs/preamp/data/2026-09-09/tb_dc_headroom_10db.csv`, rieseguito in L5e:

| Cifra | Metrica | Dove circola |
|---|---|---|
| **0,75 dB** | clipping vero (9,31 V RMS) contro il richiesto **nominale** (8,538) | ADR-015 |
| **0,55 dB** | limite allo **scostamento dell'1%** (9,0930 V RMS) contro il richiesto nominale | dossier, KPI |
| **0,59 dB** | limite all'1% contro il richiesto col guadagno **misurato** (8,4943; il guadagno reale è +9,9553 dB, non +10,000) | questa riesecuzione |

Nessuna delle tre è sbagliata: misurano cose diverse. Ma il dossier ne
pubblica una e la ADR un'altra, senza dire quale sia quale, e la differenza
fra la più ottimista e la più conservativa è il **36%** del margine. È la
stessa famiglia di NC-007: un numero pubblicato che non dice cosa misura.

**Evidenza 2 — il rimedio non esiste nel progetto.** ADR-015 poggia
interamente sul trim di ADR-011 («l'unica cosa che separa quella modalità
dal clipping»). Quel trim **non è in `circuits/`**:
`circuits/preamp/preamp_audio.py` lo dichiara esplicitamente fuori dal
proprio perimetro, non ha dimensionamento, e niente nel repo verifica che
esista. Porta ora **due vincoli portanti e non ne ha soddisfatto nessuno**:

1. attenuare abbastanza da riportare il margine dove ADR-015 lo vuole
   (con K11 a −6 dB l'uscita richiesta scende a 4,27 V RMS);
2. lasciare la Zin ≥ 100 kΩ in **ogni** posizione — che è **NC-005**, ed è
   scritto per esteso in `REQUIREMENTS.md`, «Nota su E3» (L15).

I due vincoli tirano in direzioni opposte: un partitore che attenua di
6 dB con resistenze basse viola E3; uno con resistenze alte presenta al
blocco A una resistenza di Thévenin alta (≥ 25 kΩ a −6 dB con Zin al minimo
di 100 kΩ), che porta rumore Johnson all'ingresso e cambia la sorgente vista
dalla matrice V1. *(Corretto in L15: il testo diceva che le resistenze alte
«caricano la sorgente», che è il contrario — la caricano meno.)* Nessuno ha
ancora verificato che esista un punto che li soddisfi entrambi.

E la parte di ADR-015 che dice «va scritto sul pannello o nella
documentazione d'uso» non è stata eseguita: **non esiste né un pannello né
una documentazione d'uso**, quindi la mitigazione dipende oggi dal fatto
che l'utente si ricordi.

**Cosa serve per chiuderla.**

1. Il trim entra in `circuits/preamp/` con **entrambi** i vincoli
   verificati — attenuazione e Zin — e una misura AC che lo dimostri;
   chiude anche NC-005.
2. Il dossier pubblica **una** cifra di margine dicendo quale metrica usa,
   e le altre due o spariscono o vengono etichettate. Va allineata anche
   la riconciliazione già segnalata in `STATE.md`.
3. La conseguenza operativa di ADR-015 finisce dove verrà letta, non solo
   dentro la ADR.

Se invece si decide che il +10 dB con sorgenti a fondo scala va
**impedito** e non mitigato (per esempio bloccando la commutazione), serve
una ADR nuova che superi ADR-015: non si fa modificandola.

**Stato dopo L16 (2026-09-14).** Criterio 1 **soddisfatto**, 2 **metà**, 3
**metà**.

1. **Il trim è nel progetto** (ADR-027): fra il blocco A e l'attenuatore,
   −6,003 / −11,939 dB simulati, E3 conforme in ogni posizione (NC-005 chiusa).
   I due vincoli non tirano più in direzioni opposte: fuori dall'ingresso del
   blocco A il partitore può essere a bassa impedenza.
2. **Una cifra, con la sua metrica**, in `reports/2026-09-14-L16-trim.md`.
   - **M1**, limite lineare all'1 % contro il richiesto col guadagno misurato
     (+9,9645 dB) e il trim misurato: **+6,58 dB** a +10 dB col trim a −6 dB.
   - Caso raggiungibile per errore, trim a 0 dB: **+0,58 dB**.
   - Etichettate: **M2** (saturazione contro nominale, la cifra di ADR-015)
     +6,79 / +0,79 dB; **M3** (1 % contro nominale, la cifra del dossier)
     +6,55 / +0,55 dB.
   - Dati: `data/2026-09-14/L16/dopo/tb_dc_headroom/`.

   Resta da **pubblicarla nel dossier**: **L32**.
3. **La conseguenza operativa**: il trim è comune e si ritocca a ogni cambio di
   sorgente, e il LED (F9) mostra il valore impostato. Una legenda di pannello
   o una documentazione d'uso non esistono ancora.

**Resta aperta**, maggiore, per il dossier (L32) e per il punto 3.

**Stato dopo L32 (2026-09-15).** Criterio 1 **soddisfatto**, 2 **soddisfatto**,
3 **metà**. Report: `reports/2026-09-15-L32-dossier.md`.

2. **Il dossier pubblica una cifra sola, con la sua metrica**
   (`dossier/index.html`, «Escursione e headroom»):
   - **M1 +6,58 dB** a +10 dB col trim a −6 dB, con la definizione scritta
     accanto;
   - +0,58 dB col trim a 0 dB, come caso raggiungibile per errore;
   - M2 e M3 compaiono solo in una tabella secondaria, etichettate (+6,79 e
     +6,55 dB a trim −6).

   La cifra è **ricalcolata** dai CSV di `data/2026-09-14/L16/dopo/tb_dc_headroom/`
   con le attenuazioni di `tb_trim_e3.csv`. Il builder la confronta con
   `headroom_nc009.py`, lanciato sugli stessi file, su nove celle (tre modi × tre
   posizioni del trim), e rifiuta oltre l'arrotondamento. Una metrica alterata
   nel builder è stata rifiutata. Il paragrafo del dossier che rimandava lo
   0,75 dB di STATE.md non esiste più.

**Resta aperta**, maggiore, per il solo punto 3: la legenda di pannello o la
documentazione d'uso di ADR-015.

### NC-011 — Il PSRR del rail positivo non vincola nessuno

| | |
|---|---|
| Requisito | **E5** (rumore in uscita) · alimentatore, non ancora progettato |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-09-revisione-utente-dossier.md` |
| Stato | aperta — **metà scritta chiusa da L18** (2026-09-13, ADR-020); restano la scelta del rimedio e la verifica, lotto dell'alimentatore |

**Evidenza.** Da `docs/preamp/data/2026-09-09/tb_zout_psrr_noise_psrr*.csv`,
topologia **col THAT320**, come all'apertura:

| Configurazione | 100 Hz | 1 kHz | 10 kHz | 100 kHz |
|---|---|---|---|---|
| rail **+**, +10 dB | 62,07 | 49,56 | **29,76** | **10,15** |
| rail **+**, 0 dB | 72,02 | 59,51 | 39,72 | 19,72 |
| rail **−**, +10 dB | 79,02 | 90,54 | 86,93 | 61,44 |

**Rimisurata in L18** sulla topologia di oggi, con lo specchio LS352, da
`docs/preamp/data/2026-09-13/tb_zout_psrr_noise_psrr*.csv` (100 Hz / 1 kHz /
10 kHz / 100 kHz):
- rail **+**, +10 dB: 62,17 / 49,62 / **29,82** / **10,20**;
- rail **−**, +10 dB: 74,37 / 87,75 / 86,23 / 61,56.

Il rail + si muove di meno di 0,11 dB. Il rail − perde fino a 4,74 dB (a
20 Hz), ma resta 12 dB sopra il + a 100 Hz e 56 dB sopra a 10 kHz. La
conclusione della voce non cambia.

Il divario fra i due rail a 10 kHz, all'apertura, era di **57 dB**: la topologia non è
simmetrica rispetto all'alimentazione, e il rail positivo è l'anello
debole. Il numero **è già pubblicato** nel dossier; quello che non esiste
è la sua **conseguenza**. L'alimentatore non è ancora progettato e nessun
documento gli dice quanto ripple può lasciare sul rail positivo alle
frequenze in cui la reiezione vale 30 dB o 10 dB — che è precisamente la
banda in cui uno switching o un raddrizzatore lavorano.

È la stessa forma di NC-005: un vincolo che esiste nei fatti e non è
scritto dove verrà letto.

**Cosa serve per chiuderla.** Il vincolo scritto in `REQUIREMENTS.md` o
nella ADR dell'alimentatore, nella forma «il ripple residuo ammesso sul
rail positivo, alle frequenze in cui il PSRR vale X dB, deve stare sotto
Y», ricavato da E5; più la scelta del rimedio (regolatore a bassissimo
rumore, oppure cella locale a moltiplicatore di capacità dedicata agli
stadi d'ingresso). La verifica finale è una misura sul prototipo, non una
simulazione.

**Metà chiusa il 2026-09-13 da L18.** Il vincolo è scritto. **ADR-020**
riserva all'alimentazione **1 µV RMS** dei 10 µV di E5. Il verbo e la tabella
per tono stanno nella «Nota su E5 — la quota del ripple d'alimentazione» di
`REQUIREMENTS.md`; per esempio, sul rail + a 10 kHz il limite è ≤ 31,0 µV RMS.
Il verbo è stato fatto fallire su casi noti
(`reports/2026-09-13-L18-vincolo-psrr.md` §4).

**La voce resta aperta** per le due cose che L18 non poteva fare:
1. **la scelta del rimedio**, che vuole i numeri di dropout e di calore
   dell'alimentatore;
2. **la verifica contro ADR-020**, prima sullo spettro simulato dei rail e poi
   sul prototipo.

Sono del lotto dell'alimentatore, insieme al limite sopra 20 kHz che E5 non
può dare.

### NC-012 — V1 non dichiara la soglia di accettazione del margine di fase

| | |
|---|---|
| Requisito | **V1** |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-09-revisione-utente-dossier.md` |
| Stato | **CHIUSA il 2026-09-10 (L26)** — la soglia c'è: **60°**, decisa dall'utente e registrata in **ADR-019**. Vedi «Voci chiuse» in fondo |

**Evidenza.** `docs/preamp/REQUIREMENTS.md`, sezione V1, enumera con cura
le combinazioni su cui il margine di fase va misurato — blocco, posizione
dell'attenuatore, carico, sorgente — e **non dice quale valore sia
accettabile**. Cercata anche nelle quattordici ADR e in `AGENTS.md`:
nessuna soglia.

Conseguenza: **nessuna misura di margine di fase può passare o fallire.**
I 56,945° che il dossier pubblica come caso peggiore e i 41,85° del blocco
A col carico canonico (NC-002) non sono né conformi né non conformi. La
convenzione di progetto è 60°, ma una convenzione non scritta non è un
requisito, e senza soglia il KPI del dossier è un numero senza verdetto.

Una soglia senza il **carico a cui si riferisce** non è però un requisito
migliore: 56,945° è misurato con una sonda da 4,7 nF, che il banco stesso
dichiara «margine di prova, non un valore realistico». La soglia e la
capacità di prova vanno scritte insieme.

**Cosa serve per chiuderla.** La soglia in `REQUIREMENTS.md` sotto V1, col
carico di prova dichiarato accanto, e i KPI del dossier riferiti a quella.
È la voce che rende decidibili **NC-002** e **NC-003**: finché non c'è, le
altre due discutono di un confine che nessuno ha tracciato.

### NC-013 — Il modello vendor dell'LSK489 descrive un esemplare d'angolo, non il tipico

| | |
|---|---|
| Requisito | **ADR-013** passo 4 / **E5** / **V4** — la credibilità dei numeri di rumore e distorsione |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-09-L7-controllo-incrociato-lsk489.md` |
| Stato | aperta |

**Evidenza.** Il controllo incrociato di ADR-013 passo 4, eseguito in L7
alle condizioni di prova del datasheet (RevA40 pagina 2, gruppo **A**,
25 °C — non i 27 °C di default di ngspice, perché il modello porta
`Vtotc=-2.5m`):

| Grandezza | Misurata | Finestra LSK489A | Verdetto |
|---|---|---|---|
| I_DSS (V_DG = 15 V, V_GS = 0) | **2,59283 mA** | 2,5 … 8,5 mA | dentro, 3,7% sopra il minimo, **52,9% sotto il tipico** |
| V_GS(off) (V_DS = 15 V, I_D = 1 nA) | **−1,124355 V** | −1,5 … −3,5 V | **fuori**, 0,376 V sotto il minimo in modulo |
| V_GS (V_DS = 15 V, I_D = 500 µA) | −0,650211 V | −0,5 … −3,5 V | dentro |

V_P misurato su **tre strade indipendenti** concordi entro 1,0 mV:
attraversamento della soglia di 1 nA, estrapolazione ai minimi quadrati di
√I_D → 0 su 6315 campioni, e `Vto + Vtotc·(T − Tnom)` letto dal modello.

**Non è un errore di trascrizione, ed è misurato e non argomentato.**
Dentro il modello I_DSS e V_P sono legati da `Beta`, che è trascritto:
tenendo `Beta = 2.2m` e portando `Vto` al minimo V_GS(off) del datasheet
(−1,50 V) la I_DSS sale a **4,392 mA**, comodamente dentro la finestra A.
Le due finestre del datasheet sono quindi compatibili fra loro e il
modello sta sotto **entrambe in modo coerente**: uno scarto solo, non due.
Un `Vto` sbagliato avrebbe mosso le due grandezze in direzioni scorrelate.
La trascrizione è stata inoltre **riverificata** lo stesso giorno —
`pdf_glyphs.py` riproduce gli stessi 223 byte e lo stesso sha256 di L6, e
il `diff` contro la riga del `.lib` è vuoto.

La discrepanza è quindi fra il **modello SPICE del costruttore** e il
**datasheet dello stesso costruttore**, non fra il PDF e ciò che il repo
ne ha trascritto.

*Nota sull'evidenza.* Questa voce non nomina un file sotto
`docs/preamp/data/<data>/`, e la deviazione è deliberata: non è una misura
del prodotto ma del modello, e il suo mandato vietava esplicitamente di
toccare i dati del dossier. La regola che quella convenzione protegge —
«una non conformità senza evidenza apribile è un'opinione» — è comunque
soddisfatta, e in forma più forte: ogni deck sta nel report ed è
rieseguibile, e i tre numeri li **riesegue la suite a ogni giro**
(`scripts/validate_models.py`, ricetta `tb_lsk489`).

**Conseguenza.** Il modello descrive un esemplare allo spigolo a bassa
I_DSS del gruppo A. Non lo rende inutilizzabile — è il modello che il
costruttore pubblica, ed è il primo del repo ad avere il `Kf` che i
segnaposto non hanno. Ma:

- le polarizzazioni che la **Fase 4** calcolerà con esso sono un **caso
  d'angolo**: esemplari reali avranno transconduttanza più alta;
- le cifre di rumore che chiuderanno la metà mancante di **NC-004** sono
  perciò conservative sul contributo del JFET d'ingresso — direzione
  giusta, ma va detta;
- il progetto **non deve dipendere** da una I_DSS di 2,6 mA: è il minimo
  garantito, non il valore atteso.

**Cosa serve per chiuderla.** Non ritoccare il modello — la trascrizione è
corretta e ritoccarla cancellerebbe la traccia. Serve **quantificare la
sensibilità del progetto** a I_DSS: rieseguire il punto di lavoro e il
rumore del blocco di guadagno con `Vto` ai due estremi compatibili con la
finestra A (il modello vendor com'è, e un `Vto` che porti I_DSS al tipico
di 5,5 mA), e registrare in `REQUIREMENTS.md` o in una ADR quale
dispersione il progetto tollera. Se ne esce che il progetto è sensibile,
la scelta di ADR-013 va riaperta con un numero in mano. Lotto **L20**.

**Non chiude NC-004**, e non la aggrava: la rende leggibile.

### NC-003 — Il KPI «margine di fase, peggiore» non è il peggiore del prodotto

| | |
|---|---|
| Requisito | **V1** · regola operativa 6 di `AGENTS.md` |
| Severità | **minore** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | **CHIUSA il 2026-09-13 (L14)** — il KPI dice «blocco B, peggiore dei 4 casi pubblicati», e il corpo del dossier lo dice anche lui. Vedi «Voci chiuse» in fondo |

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
| Stato | **CHIUSA il 2026-09-14 da L16** — metà scritta L15, misura AC L16. Vedi «Chiusura» in fondo alla voce e «Voci chiuse» |

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

**Il vincolo è scritto (L15, 2026-09-13).** Sta in `REQUIREMENTS.md`,
«Nota su E3», accanto al requisito che lo impone e non in ADR-011: le ADR
non si riscrivono, e la nota non è una decisione ma una conseguenza di E3
che non cambia l'insieme dei progetti conformi. È formulato **indipendente
dal meccanismo** («in ogni posizione del trim»), non «del ponticello»: F2
dice ponticello, F8/ADR-019 presuppongono relè, e la tensione è di L16. Il
criterio di passaggio è scritto: minimo di |Zin| su 20 Hz–20 kHz ≥ 100 kΩ
al connettore, blocco A collegato, in tutte e tre le posizioni. Il
controesempio della voce è stato **ricalcolato**: 13,29 kΩ, −12,13 dB.
**Resta aperta** per la misura, che chiude L16 insieme a NC-009 (il cui
criterio 1 la contiene già). Report: `reports/2026-09-13-L15-vincolo-e3.md`.

**Chiusura (2026-09-14, L16).**
- **Il trim misurato all'ingresso** del blocco A reggeva E3 solo con al massimo
  22 pF di selettore, e **non reggeva E5**: 10,12 µV con la scala più piccola
  consentita.
- **ADR-027** lo mette fra il blocco A e l'attenuatore: la Zin al connettore è
  quella del blocco A.
- **Misura AC** (`data/2026-09-14/L16/dopo/tb_trim/tb_trim_e3.csv`): minimo di
  |Zin| su 20 Hz–20 kHz **identico nelle tre posizioni e senza trim**:
  - 1,000 MΩ senza capacità a monte;
  - 349,8 kΩ con 22 pF;
  - **121,1 kΩ con 68 pF**.

  E3 è conforme in ogni posizione. Report: `reports/2026-09-14-L16-trim.md`.

### NC-006 — `gain_block.py` porta due valori superati per il riferimento di cascode

| | |
|---|---|
| Requisito | Regola di tracciabilità di `CLAUDE.md` · ADR-014 |
| Severità | **minore** |
| Aperta da | `reports/2026-09-09-gate-G0.md` |
| Stato | **CHIUSA il 2026-09-13 (L14)** — i due commenti citano il valore implementato e il log della topologia di oggi, `data/2026-09-10/tb_op-LS352.log`. Vedi «Voci chiuse» in fondo |

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
| Stato | **CHIUSA il 2026-09-13 (L14)** — il dossier pubblica lo scarto riferito a 1 kHz come misura della claim e lo scarto assoluto col suo nome, il partitore; il KPI cita il primo. Vedi «Voci chiuse» in fondo |

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

### NC-014 — Il polo 2 del G6K-2F-Y è cablato con NO e NC invertiti: sul canale destro il mute fallisce nel verso sbagliato

| | |
|---|---|
| Requisito | **ADR-012** (mute su tutte le uscite, con guasto verso il silenzio) · **ADR-004** (il relè di guadagno diseccitato deve lasciare il blocco a guadagno unitario) · F6 |
| Severità | **bloccante** |
| Aperta da | `reports/2026-09-10-L8-parti-nuove.md` |
| Stato | **CHIUSA il 2026-09-11 (L21)** — riga 79 corretta, netlist rigenerata e verificata, e un guardiano permanente in `run_tests.sh` perché non rientri in silenzio. Vedi «Voci chiuse» in fondo |

**Evidenza.** Il datasheet Omron congelato in
`vendor/relays/omron/G6K/en-g6k.pdf` (Cat. No. K106-E1-11, revisione letta
dal footer), pagina 6 del PDF, riga `G6K-2F-Y`, blocco «Terminal
Arrangement / Internal Connections (TOP VIEW)», dà:

| Polo | COM | **NC** | **NO** |
|---|---|---|---|
| 1 (riga bassa) | 3 | **2** | **4** |
| 2 (riga alta) | 6 | **7** | **5** |

`circuits/preamp/preamp_audio.py:79` dichiara invece
`K_COM2, K_NO2, K_NC2 = "6", "7", "5"`: **NO e NC del polo 2 sono
scambiati**. Il polo 1 (riga 78) è corretto.

Il diagramma è grafica vettoriale, quindi è stato letto **tre volte in
modo indipendente** e le tre coincidono: raster a 2400 dpi; coordinate
vettoriali via `pdftocairo -svg`, dove alla quota delle punte l'asse della
lama dista **0,445 pt** dal contatto di sinistra (si toccano) contro
**3,387 pt** da quello di destra, rapporto **7,6:1**; e le polilinee del
simbolo KiCad `G6K-2`, che danno lo stesso verso con rapporto **19:1**. Il
dettaglio sta al §1 del report.

**Perché l'errore è entrato, e non è sciatteria.** Le due lame pendono
dalla stessa parte, ma la riga alta è numerata 8-7-6-5 da sinistra a
destra e quella bassa 1-2-3-4. La regola implicita «NO = COM+1» è quindi
**giusta per il polo 1 e sbagliata per il polo 2**. Il codice lo dichiarava
apertamente come non confermato (righe 70-76).

**Cosa rompe.** `preamp_audio.py` assegna il polo 1 al canale L e il polo 2
al canale R. Con i pin veri, sul **canale destro**:

- **relè di mute, bobina diseccitata** — cioè all'accensione e ad
  alimentazione assente: il pin 7 non è collegato, quindi l'uscita **non è
  messa a massa** e il transitorio d'accensione passa. È il guasto
  silenzioso, ed è esattamente quello contro cui ADR-012 è stata scritta,
  con il ramo cuffie che finisce in un paio di elettrostatiche;
- **relè di mute, bobina eccitata** — ascolto normale: il pin 5 va a
  massa, quindi il **canale destro è cortocircuitato**. Guasto rumoroso,
  si trova al primo collaudo;
- **relè di guadagno, bobina diseccitata**: `R_g` va a massa attraverso
  quello che è in realtà l'NC, quindi il canale destro parte a **+10 dB**
  mentre il sinistro parte a 0 dB. ADR-004 vuole il contrario.

**Cosa serve per chiuderla.** Correggere la riga 79 di
`circuits/preamp/preamp_audio.py` in `K_COM2, K_NO2, K_NC2 = "6", "5", "7"`,
rigenerare `preamp_audio.net` e verificare sulla netlist rigenerata che il
contatto verso massa di ogni relè di mute cada su **2 e 7** e che il ramo
`R_g` del relè di guadagno cada su **4 e 5**. Non è stato fatto in L8: la
topologia è Fase 4, e L8 aveva il mandato esplicito di non toccare
`circuits/`.

**FATTO IL 2026-09-11 IN L21**, esattamente così. Riga 79 corretta, netlist
rigenerata, e sulla netlist: il nodo `GND` porta ora **K1 pin 4 e 5** (il
relè di guadagno, i due NO) e **K2/K3/K4 pin 2 e 7** (i tre relè di mute, i
due NC). Prima portava K1 4+7 e K2/K3/K4 2+5. Il **diff normalizzato** della
netlist tocca **esattamente quattro numeri di pin** e nient'altro.

**E il pinout è stato riletto alla fonte, non ereditato da L8**, su tre gambe
indipendenti che concordano — vedi il report di L21. Le due misure ripetibili
danno lo stesso verso su **entrambi** i poli: nel PDF l'armatura passa a
**0,44 pt** dal proprio contatto NC e a **3,39 pt** dal NO (rapporto 7,6:1),
e nel simbolo KiCad la punta dell'armatura ha la **stessa x esatta** del
contatto NC (3,81 mm dall'altro).

**Quello che chiude davvero la voce, però, è il guardiano.** Una verifica una
tantum non impedisce a un'inversione di rientrare, e questo difetto fallisce
in silenzio nel verso che brucia un trasduttore. `scripts/check_relay_safe_state.py`
legge **solo la netlist generata** e asserisce l'intento delle ADR — mute
diseccitato ⇒ uscita a massa, guadagno diseccitato ⇒ `R_g` flottante — con il
pinout del datasheet come dato citato. Gira nel blocco **2e** di
`run_tests.sh`. È stato **fatto fallire** sulla netlist di prima: 12
rilevazioni, tutte e sole sul polo 2.

### NC-015 — Il THAT320 è fine vita, e la finestra di acquisto chiude il 2026-09-30

| | |
|---|---|
| Requisito | **ADR-013** (lo specchio di corrente d'ingresso è un THAT320) · T2 (il progetto deve essere riproducibile) |
| Severità | **bloccante** |
| Aperta da | `reports/2026-09-10-L8-parti-nuove.md` |
| Stato | **CHIUSA il 2026-09-10 (L22 + L23)** — la parte sostitutiva è scelta, verificata e montata: **LS352**, ADR-018. Vedi «Voci chiuse» in fondo |

**Evidenza.** `vendor/bjt_array/that/THAT320/THAT-EOL-Memo.pdf`
(sha256 `1e777dd3ac23…`), memo di **Les Tyler, President, THAT
Corporation**, datato **1 settembre 2026**:

> Effective immediately, the following products are on EOL status:
> … **300-series transistor arrays**

e, nello stesso memo:

> until **September 30, 2026**, we are offering a last-time buy (LTB)
> opportunity … contact our IC sales folks at sales@thatcorp.com

Motivo dichiarato: il processo Dielectric Isolation su wafer da 4 pollici
con cui THAT fabbrica la serie 300 è diventato insostenibile.

Il quadro distributivo è coerente con l'EOL, e quello che si è visto è
scritto per intero al §2.2 del report: **DigiKey non tratta THAT
Corporation** (zero risultati su `THAT320` e su `320P14-U`, e il
costruttore non compare fra i fornitori); Mouser, Farnell/Newark e TME
rifiutano le richieste automatiche, quindi **non sono verificati**; l'unica
pagina di vendita realmente letta, un negozio tedesco, dà **€ 8,50** ed è
**esaurito**.

**Il memo è del 1° settembre; ADR-013 è dell'8.** Era già pubblico quando
la topologia è stata disegnata e quando la Fase 1 scrisse «Stock esatto non
verificato». Non era assente: è stato mancato.

**Perché è bloccante.** Non si congela una topologia sopra una parte che
non si può più comprare. Vale l'effetto standard: niente avanzamento di
fase, quindi niente layout e niente fabbricazione, non un veto su un merge.

**DECISA IL 2026-09-10.** L'utente ha risposto che l'approvvigionamento
entro il 30 settembre non è praticabile e che **un componente a fine vita
non entra in un progetto nuovo**. Il last-time buy è quindi **scartato**, e
la strada è la **sostituzione**. Registrata in **ADR-016**, che ne ricava
anche la regola generale — requisito **T8**.

Nota che ADR-013 non è stata riaperta e non doveva esserlo: **il THAT320
non era oggetto di una decisione.** ADR-013 lo nomina una volta sola, di
passaggio, dentro la discussione di un'alternativa scartata; è entrato
nella topologia come scelta implementativa in `gain_block.py` che citava
quella parentesi. Una parte entrata così **non ha mai avuto
un'istruttoria**, ed è il motivo per cui il suo stato di ciclo di vita non
era stato controllato da nessuno.

**Cosa serve ora per chiuderla.** Scegliere e verificare una coppia PNP
appaiata — o un'altra forma di specchio — che soddisfi **T7 e T8
insieme**: in produzione e con un modello SPICE del costruttore. Poi
rifare punto di lavoro e cifre di rumore dello stadio d'ingresso, perché
il THAT320 portava appaiamento monolitico e rbb = 25 Ω. Lotto **L22**.

### NC-016 — Il footprint del THAT320 nel codice è a 8 pin, ma la parte esiste solo a 14

| | |
|---|---|
| Requisito | ADR-013 · precondizione di **G2** (il layout deve poter piazzare le parti vere) |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-10-L8-parti-nuove.md` |
| Stato | **CHIUSA il 2026-09-10 (L22 + L23)** — la parte sostitutiva porta il proprio footprint e il proprio simbolo, e il duale è ora UNA Part a due unità. Vedi «Voci chiuse» in fondo |

**Evidenza.** Datasheet `THAT_300-Series_Datasheet.pdf`, Document 600041
Rev 04, Tabella 1 «Ordering Information»: le varianti THAT320 ordinabili
sono **esattamente due**, `320P14-U` (**DIP14**) e `320S14-U` (**SO14**).
Non esiste una versione a 8 pin. La sezione «Package Characteristics»
conferma: «14 Pin PDIP» e «14 Pin SOP».

`circuits/preamp/gain_block.py:303-304` assegna a entrambi i dispositivi
dello specchio `FP_SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"`.

**Cosa serve per chiuderla — chiarito il 2026-09-10.** NC-015 è stata
decisa: **il THAT320 esce dal progetto** (ADR-016). Quindi questa voce
**non si chiude correggendo il footprint del THAT320**: si chiude quando
la parte sostitutiva è scelta e porta con sé il proprio footprint e il
proprio simbolo, col pinout letto dal datasheet di *quella* parte.

Resta però un residuo reale, e per questo la voce non si chiude da sola:
finché `gain_block.py:303-304` dichiara `SOIC-8` per un dispositivo a 14
pin, **il codice contiene un footprint che non corrisponde a nessuna parte
esistente**, e chiunque generasse un PCB oggi lo piazzerebbe. Va corretto
insieme alla sostituzione, non dopo. Due
vincoli che il layout dovrà rispettare comunque, entrambi dal datasheet:
l'appaiamento è specificato **a coppie** (`|VBE1−VBE2|` e `|VBE3−VBE4|`),
quindi lo specchio usa 1&2 oppure 3&4 e mai uno per coppia; e «the
substrate should be ac-grounded», mentre la topologia attuale non collega
alcun pin di substrato.

### NC-017 — Sei dispositivi attivi su sette non hanno un modello SPICE del costruttore

| | |
|---|---|
| Requisito | **T7** (ADR-016) · **E5 / V4** via **NC-004** · ADR-013 (la regola di provenienza dei modelli) |
| Severità | **bloccante** — alzata il 2026-09-10 |
| Aperta da | `reports/2026-09-10-L8-parti-nuove.md` |
| Stato | aperta — **estesa il 2026-09-10** da 2N5401/2N5551 a **tutti** i dispositivi attivi |

**AGGIORNATA IL 2026-09-10, e la voce ha cambiato dimensione.** Nasceva
come «mancano i modelli di due parti». Con **ADR-016** l'utente ha posto la
regola generale — **T7: ogni dispositivo attivo del percorso di segnale ha
un modello SPICE del costruttore** — e la voce ora misura la distanza da
quel requisito, non da una preferenza. Per questo la severità sale a
**bloccante**: la tabella di severità qui sopra dice che un requisito non
soddisfatto, o senza evidenza per dire se lo sia, è bloccante.

Lo stato dei sette dispositivi attivi, da L8 e dalla Fase 1:

| Dispositivo | Modello vendor | Sotto T7 |
|---|---|---|
| LSK489 | **sì** — PDF vendor, trascritto in L6, validato in L7 | **conforme** |
| THAT320 | sì, nativo — ma la parte è fine vita | **fuori per T8**, vedi NC-015 |
| 2N5551 | **no**, in nessuna forma | **non conforme** → sostituire |
| 2N5401 | **no**, in nessuna forma | **non conforme** → sostituire |
| MJE15032 | **non confermato** (Fase 1: «pagina models esiste, file finale non confermato») | **da verificare** |
| MJE15033 | **non confermato**, idem | **da verificare** |
| 1N4148 | mai verificato | **da verificare** |

Uno solo su sette è conforme oggi. I due MJE sono i **dispositivi
d'uscita**: se cadono, la sostituzione non è un cambio di package, è una
**modifica di topologia** dello stadio d'uscita.

**Evidenza.** Le due parti sono usate **cinque volte** nel blocco di
guadagno: il 2N5401 è il VAS (`gain_block.py:316`), il 2N5551 è pozzo di
coda (262), i due cascode di ADR-014 (291-292), il carico del VAS (328) e
il moltiplicatore di Vbe (350). Restano segnaposto scritti a mano.

Cercato, e non trovato in forma macchina dal costruttore (§3.4 del
report): la pagina modelli di onsemi carica l'elenco via JavaScript e
risponde «Loading…» a un client non-browser; l'indice modelli di Central
Semiconductor — che *è* autore di modelli per la serie 2N — è anch'esso
solo-JavaScript; Diodes Incorporated risponde 403. **Non è nemmeno un caso
da trascrizione come l'LSK489**: non è stato trovato alcun PDF del
costruttore contenente il testo `.MODEL`.

Mirror di terze parti esistono e **non sono stati usati**: un mirror non è
provenienza vendor, ed è precisamente la regola che ADR-013 impone.

**Perché conta più di quanto sembri.** I segnaposto sbagliano in
**direzioni opposte**, quindi un margine di fase calcolato con essi non è
conservativo in modo noto:

| Dispositivo | Segnaposto | Realtà letta dal datasheet |
|---|---|---|
| `NSS2N5551` | `TF = 0,5 ns` («f_T ~ 300 MHz») | f_T **100 MHz min**, e misurata a **10 mA** mentre il circuito lavora a 2-6 mA, dove è più bassa ancora |
| `PTHAT320` | `TF = 1,5 ns` («f_T ~ 100 MHz») | f_T **325 MHz** tip. — il segnaposto è ~3× **lento** |

**Nota che vale per la Fase 4.** Le varianti del 2N5551 **selezionate per
beta** sono state dismesse: il datasheet Rev. 7 elenca come DISCONTINUED
`2N5551CTA`, `2N5551YTA` e `2N5551YBU`, e la Nota 5 dice che il suffisso
`-Y` significa h_FE 180~240. Resta disponibile solo la dispersione piena
**50…250**, il che riguarda la coerenza di beta nella coppia di cascode e
nei generatori di corrente.

**AGGIORNATA IL 2026-09-10 da L24 — la voce cambia natura una seconda
volta.** Nasceva come «mancano i modelli di due parti», ADR-016 l'ha resa
«sei su sette non soddisfano T7», e L24 l'ha ridotta a **ciò che resta da
eseguire invece che da scoprire**. Report:
`reports/2026-09-10-L24-t7-dispositivi-attivi.md`; decisione: **ADR-017**.

Stato dei sette dispositivi **dopo L24**:

| Dispositivo | T7 | T8 | Resta |
|---|---|---|---|
| LSK489 | sì, in `models/` | sì | niente (NC-013 è un'altra voce) |
| **MJE15032** | **sì** — modello onsemi, congelato, ngspice lo esegue | **Active** come `MJE15032G` | promozione in `models/` |
| **MJE15033** | **sì** — idem | ordinabile, **senza pagina prodotto** | promozione in `models/` |
| **1N4148** | **sì** — modello onsemi `1n914.lib` | **Active**, sei OPN | promozione in `models/` |
| **2N5401** | **sì come MMBT5401** (Diodes) | nessun marchio di dismissione | promozione **e** sostituzione |
| **2N5551** | **sì come MMBT5551** (Diodes) | idem | promozione **e** sostituzione |
| THAT320 | sì | **no, fine vita** | **NC-015 → L22** |

**Lo stadio d'uscita regge**: i due MJE hanno il modello, quindi la
modifica di topologia che ADR-016 temeva non serve.

**La conclusione di L8 su 2N5401/2N5551 era giusta sui percorsi provati e
sbagliata come affermazione generale.** Il 403 di Diodes vale per le
pagine HTML sotto `/design/` e `/part/`, non per i file di modello, che
stanno su `/spice/download/` e rispondono `200 text/plain` a un `curl`
nudo. Il percorso onsemi invece **è stato ri-provato con il pattern che ha
funzionato per i MJE** (`/download/models/lib/<parte>.lib`) e continua a
dare il soft 404: quella metà della conclusione di L8 tiene.

**La severità resta bloccante**, e non è una formalità: T7 non è
soddisfatto *nel repo* finché `models/` non porta i modelli e la topologia
non li usa. La distanza da percorrere però è ora nota e limitata.

**AGGIORNATA IL 2026-09-10 da L25 — il primo dei tre passi è fatto.** Report:
`reports/2026-09-10-L25-promozione-modelli.md`. I cinque modelli sono in
`models/`, ognuno con la propria `.provenance.json` (il cui hash del sorgente
vendor `validate_models.py --check-provenance` **ri-calcola** a ogni run) e
una ricetta di regressione che lo rimisura alle condizioni del suo datasheet.
La libreria passa da **28 a 38 check**, tutti verdi.

**Ora tutti e sette i dispositivi attivi hanno un modello del costruttore in
`models/`.** È la prima volta da G0, e vale la pena dirlo per intero: T7 è
soddisfatto sul piano dei modelli. Non lo è ancora sul piano della topologia,
che è la ragione per cui questa voce resta bloccante.

**Cosa serve per chiuderla — riscritto il 2026-09-10 dopo L25.**

1. ~~**Promuovere** i cinque modelli congelati in `models/`~~ — **FATTO in
   L25.** Il testo `.MODEL` promosso è **byte per byte** quello del
   costruttore (nessuno dei cinque portava `mfg=`, quindi non c'è stata
   nemmeno la rimozione che LSK489 e LS350 avevano richiesto), e la proprietà
   è verificata con `diff` e non dichiarata. La promozione ha però aperto
   **NC-024** e **NC-025**: rimisurando alle condizioni dei datasheet, il
   MJE15032 manca il proprio minimo di h_FE e **entrambi** i MJE mancano il
   proprio minimo di f_T quando la si legge come il datasheet la definisce.
2. **Sostituire** in `circuits/preamp/` (Fase 4), rigenerare gli artefatti
   e rifare le misure. ADR-017 dichiara di quanto ci si muove: i
   segnaposto sono 1,9× e 3,6× **veloci** sulla f_T al punto di lavoro.
   **È l'unico passo rimasto**, ed è ciò che tiene aperta questa voce.
3. ~~**L22** per il THAT320~~ — **FATTO**, chiusa come NC-015 con l'LS352
   (ADR-018).

**Il testo che segue è la formulazione precedente**, di ADR-016, tenuta
perché è ciò che il lotto ha eseguito:

1. **Verificare** MJE15032, MJE15033 e 1N4148: esiste un modello del
   costruttore, e in quale forma? È il passo che decide quanto è grande il
   resto del lavoro, perché i due MJE stanno nello stadio d'uscita.
2. **Sostituire** 2N5401 e 2N5551 — e i MJE, se il modello manca — con
   parti che soddisfino **T7 e T8 insieme**: in produzione, e con un
   modello del costruttore. La sostituzione del 2N5401 tocca il VAS, che
   con il Miller da 470 pF fissa il polo dominante di tutto
   l'amplificatore: le cifre di margine di fase andranno rifatte.
3. **Congelare** ogni modello in `vendor/` con hash e URL, e poi
   **promuoverlo in `models/`** col controllo incrociato contro il
   datasheet, come L6+L7 hanno fatto per l'LSK489.

**Un mirror di terze parti non chiude questa voce.** ADR-016 lo scarta
esplicitamente: la provenienza è ciò che si verifica, e accettare un
mirror qui svuoterebbe la procedura di ADR-013.

Se per una funzione necessaria non esistesse **alcuna** parte in
produzione con modello del costruttore, si applica la clausola «Da
riaprire se» di ADR-016: o si rilassa T7 per quella funzione **con la
lacuna dichiarata accanto a ogni numero che ne dipende**, o si cambia
topologia per non aver bisogno di quel dispositivo.

### NC-018 — Il codice nomina due OPN che il costruttore marca *Obsolete*

| | |
|---|---|
| Requisito | **T8** (ADR-016) — nessun componente a fine vita entra nel progetto |
| Severità | **minore** |
| Aperta da | `reports/2026-09-10-L24-t7-dispositivi-attivi.md` |
| Stato | aperta |

**Evidenza.** `circuits/preamp/gain_block.py:367-368` istanzia i due
dispositivi d'uscita con i valori `"MJE15032"` e `"MJE15033"`. Letto
verbatim dal blocco JSON-LD `offers/itemProductList` della pagina prodotto
di onsemi il 2026-09-10:

| OPN | itemCondition | availability | prezzo |
|---|---|---|---|
| MJE15032 | **Obsolete** | unavailable | 0.0 |
| MJE15032G | **Active** | available | 0.6 |

La tabella ORDERING INFORMATION del datasheet (dicembre 2024, Rev. 7)
elenca del resto **solo** `MJE15032G` e `MJE15033G`, TO-220 Pb-Free.

**Perché è minore e non maggiore.** Il *dispositivo* è conforme a T8: la
versione ordinabile è attiva. È la stringa della distinta a nominare una
variante piombata fuori catalogo. Non cambia una cifra elettrica e non
blocca nessuna fase.

**Perché è comunque una voce e non una nota.** Una distinta che nomina un
OPN obsoleto è esattamente il modo in cui una parte a fine vita entra in
un progetto senza che nessuno lo decida — la dinamica che ha prodotto
ADR-016. Ha un costo di una riga e si dimentica in un secondo.

**Cosa serve per chiuderla.** In Fase 4, quando `gain_block.py` viene
toccato: i due valori diventano `MJE15032G` e `MJE15033G`. Da verificare
sulla netlist rigenerata, non sul sorgente.

### NC-019 — Il moltiplicatore di Vbe perde il proprio metodo di accoppiamento termico

| | |
|---|---|
| Requisito | La regola di piazzamento dichiarata in `circuits/preamp/gain_block.py:350`, conseguenza di **ADR-017** |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-10-L24-t7-dispositivi-attivi.md` |
| Stato | aperta |

**Evidenza.** `gain_block.py:350` porta una regola esplicita, già
consegnata a `pcb-automation-engineer`:

> This transistor **MUST be thermally coupled to the NPN output device's
> tab** (thermal compound + cable tie is enough at 225 mW) or the bias
> drifts.

**ADR-017** sostituisce quel transistor con un **MMBT5551 in SOT-23**,
perché Diodes Incorporated offre quel die solo a montaggio superficiale.
**Un SOT-23 non si fascetta al tab di un TO-220.** Il metodo prescritto
non è applicabile alla parte scelta.

Non è un difetto di ADR-017: è il costo che ADR-017 dichiara. Ma è un
requisito di progetto che oggi nessun artefatto soddisfa, ed è
esattamente ciò che la tabella delle severità chiama «scostamento reale,
con rimedio noto».

**Perché conta.** Il moltiplicatore di Vbe esiste per **inseguire
termicamente** la V_BE dei dispositivi d'uscita. Se non li insegue, la
corrente di riposo deriva — e il commento dello stesso file spiega che
1,69 kΩ è un valore *spazzato*, non calcolato, con 50 Ω che spostano I_q
di 0,78 mA. Un accoppiamento termico che non funziona non è un difetto
cosmetico di layout: rimette in gioco il punto di lavoro di Classe A che
ADR-003 richiede.

**Cosa serve per chiuderla.** Una regola di piazzamento nuova e
verificabile — un percorso di rame sul PCB fra la piazzola del SOT-23 e
quella del tab del TO-220, dimensionato e dichiarato — scritta dove verrà
letta (il commento in `circuits/preamp/` **e** la consegna a
`pcb-automation-engineer`), **oppure** la decisione motivata di tenere
quel singolo dispositivo in un package a foro passante, con la lacuna T7
dichiarata accanto ai numeri che ne dipendono, secondo la clausola «Da
riaprire se» di ADR-016. Va risolta **prima del G2**.

### NC-020 — La f_T del modello LS352 sta il 35% sotto il minimo del suo datasheet

| | |
|---|---|
| Requisito | **T7** (ADR-016) · **ADR-018** · la disciplina di controllo incrociato di **ADR-013** |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-10-L22-L23-specchio-ingresso.md` |
| Stato | aperta |

**Evidenza.** Modello vendor `models/bjt_pnp/ls350.lib`, misurato alle
condizioni del datasheet (I_C = 1 mA, V_CE = 5 V, 25 °C):

| Grandezza | Misurata | Finestra LS352 | Esito |
|---|---|---|---|
| f_T | **129,5 MHz** | **200 MHz min** (275 tip) | **FUORI**, −35% |

Verificata su **tre gambe concordi**, perché una sola misura non basta a
dichiarare fuori norma il modello di un costruttore: attraversamento
|h_fe| = 1 a 129,5 MHz; prodotto guadagno-banda 124,5 MHz a 1 MHz; 128,8 MHz
a 10 MHz.

Le altre cinque grandezze controllate sono **dentro** (h_FE a tre correnti,
C_OBO, NF), quindi il verdetto è **misto** e non un rigetto della parte.

**Non è un errore di trascrizione**: le due letture indipendenti del PDF
vendor sono byte-identiche (stesso sha256) e una terza, visiva, concorda.
La discrepanza è fra il modello SPICE del costruttore e il datasheet **dello
stesso costruttore** — la stessa forma di NC-013 sull'LSK489.

**Perché è maggiore e non bloccante.** La direzione è quella sicura: il
modello è **più lento** della parte garantita, quindi margine di fase e
guadagno d'anello calcolati con esso sono **pessimistici**. Ma non di una
quantità nota, ed è esattamente il difetto che NC-002 e NC-012 già
descrivono per i segnaposto: *non conservativo in modo noto*.

**Quanto pesa oggi, misurato.** Sostituendo il THAT320 con questo modello il
margine di fase si muove di **mezzo grado** (63,54° → 63,02° a 0 dB senza
carico) e il guadagno d'anello DC di **0,06 dB**. Nello specchio il
dispositivo è un carico attivo a 2,1 mA, non un elemento del percorso di
segnale in alta frequenza, quindi la sua f_T conta poco — ma questo va
riverificato in Fase 4, quando anche il VAS e lo stadio d'uscita avranno
modelli veri.

**Cosa serve per chiuderla.** O una misura su un esemplare reale, o la
constatazione — in Fase 4, coi modelli veri ovunque — che nessuna cifra di
stabilità del progetto dipende dalla f_T di questo dispositivo entro il
margine di errore. Non si chiude "correggendo" il modello: quello che il
costruttore pubblica è ciò che si congela.

### NC-021 — Il blocco B a 0 dB sta sotto i 60° nel caso peggiore capacitivo

| | |
|---|---|
| Requisito | **V1**, soglia 60° (**ADR-019**) |
| Severità | **bloccante** |
| Aperta da | `reports/2026-09-10-L26-requisiti-utente.md` |
| Stato | **CHIUSA il 2026-09-14 da L12** — ADR-024 e ADR-025. Vedi «Chiusura» in fondo alla voce e «Voci chiuse» |

**Evidenza.** Margine di fase del blocco B rimisurato in L22 con lo specchio
LS352:

| Configurazione | Misurato | Contro 60° |
|---|---|---|
| 0 dB, a vuoto | 63,02° | conforme |
| **0 dB, 4,7 nF di cavo** | **56,46°** | **−3,5°** |
| +10 dB, a vuoto | 86,09° | conforme |
| +10 dB, 4,7 nF | 80,6° | conforme |

Il lato debole è la **modalità 0 dB**, ed è coerente col fatto che è la
modalità con più guadagno d'anello: il relè è aperto, R_g non è in circuito e
la controreazione è totale.

**Perché è bloccante.** Non perché 56,46° sia instabile — non lo è — ma perché
è **sotto un requisito**, e l'effetto standard di una bloccante è fermare
l'avanzamento di fase, non un merge. Si congela una topologia sopra un
requisito soddisfatto, non sopra uno mancato di tre gradi e mezzo.

**Va letta insieme a NC-002**, che è lo stesso problema più grave sul blocco A
(41,98°), e a **NC-020**: il modello LS352 è più *lento* della parte
garantita, quindi questi margini sono pessimistici — ma di quantità ignota,
quindi non si può dedurne che la parte reale passi.

**Cosa serve per chiuderla.** La stessa scelta di NC-002, e conviene farla una
volta sola per entrambi i blocchi: più compensazione, meno guadagno d'anello,
o una rete d'isolamento d'uscita diversa. Lotto **L12**.

**Chiusura (L12, 2026-09-14).**

**Il caso peggiore era peggiore di quanto dicesse la voce.** Col criterio di
**ADR-024** — cavo al jack, ogni cavo fino a 4,7 nF, le sorgenti di V1 — il
blocco B a 0 dB stava a **54,97°**, con l'attenuatore a metà corsa (2,5 kΩ) e
2,7 nF. I 56,46° erano il valore a 4,7 nF con sorgente nulla, non il minimo.

**Il rimedio (ADR-025): C137 da 22 a 330 pF, C0G**, uguale in tutte le
istanze. Scelto fra le strade della voce, coi numeri
(`data/2026-09-14/L12/esplorazione/`):

| Strada | Blocco B 0 dB, minimo | Costo |
|---|---|---|
| **C_f 330 pF** (scelta) | **61,21°** | banda a +10 dB da 333 a 183 kHz |
| Miller 1 nF | 61,74° | slew a 20 kHz fondo scala; −6,5 dB di PSRR e guadagno d'anello a 20 kHz |
| Miller 680 pF + 68 Ω | 61,25° | ancora in slew; E4 a 82 Ω a 20 Hz |
| C_f 330 pF + 56 Ω | 62,27° | tre reti d'uscita e i loro deck; E4 a 70 Ω |

**Dopo**, `data/2026-09-14/L12/dopo/`:
- 0 dB **61,21°**, 60,73° agli spigoli (C ±5 %, R ±1 %); +10 dB 102,96°;
- punto di lavoro identico; PSRR, E5, slew, V2, V3, classe A e P7 invariati.

**Cosa resta vero**: NC-020 e NC-025 dicono che questi margini sono
pessimistici di quantità ignota, e la guardia di 0,7° agli spigoli si rimisura
in Fase 4. La modalità +3 dB non esiste ancora (L27).

Report: `reports/2026-09-14-L12-margine-di-fase.md`.

### NC-022 — La topologia ha due livelli di guadagno, il requisito ne chiede tre

| | |
|---|---|
| Requisito | **E2**, **F5** (**ADR-019**) |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-10-L26-requisiti-utente.md` |
| Stato | **CHIUSA il 2026-09-14 da L27** — ADR-026. Vedi «Chiusura» in fondo alla voce e «Voci chiuse» |

**Evidenza.** `circuits/preamp/gain_block.py` implementa **un solo** ramo
commutato: `R_G = "698"` verso massa attraverso un relè, quindi due stati —
1 e 1 + R_f/R_g = 3,149 (+9,96 dB). Il livello **+3 dB non esiste**, né nel
codice né nella netlist né nel diagramma a blocchi.

**Cosa serve per chiuderla**, e non è una riga:

1. **il dimensionamento** del secondo ramo verso massa, col principio di
   ADR-004 conservato — si commuta R_g, mai R_f — e con lo stato a relè
   diseccitati che deve restare **0 dB** (ADR-019);
2. **i relè**: quanti, con quanti poli, e il budget di corrente delle bobine
   che ne esce, che è un dato per `psu-engineer`;
3. **i dodici deck**: ogni `foreach` che oggi spazza `0db / 10db` ne vuole
   tre, con la trappola di `limitations.md` #10 sui `$var` nei nomi `wrdata`;
4. **il diagramma a blocchi**, che calcola il guadagno da R_f/R_g e lo
   asserisce: `scripts/check_schematic.py` va esteso, non aggirato;
5. **la matrice V1**, che passa da tre a quattro configurazioni di blocco.

Lotto **L27**.

**Chiusura (L27, 2026-09-14).** I cinque punti, nell'ordine:

1. **Il dimensionamento (ADR-026).** Due rami di R_g in parallelo verso massa:
   **3,57 kΩ** su K1 (+3,047 dB) e **866 Ω** su K5, chiuso solo insieme a K1
   (+9,972 dB). A riposo 0 dB; nessuno stato dei contatti supera il +10 dB.
2. **I relè.** K5 è un secondo G6K-2F-Y, un polo per canale. Il budget delle
   bobine, cinque eccitate, è 105,5 / 45,5 / 23,0 mA a 5 / 12 / 24 V.
   `check_relay_safe_state.py` lo riconosce ed è stato fatto fallire.
3. **I deck.** Tutti e 16 terminano `RG10`, sei spazzano tre modi. Il blocco 2g
   rifiuta ora un nodo di contatto non terminato: la trappola è la limitazione
   #27, e il controllo è stato fatto fallire sui deck di `main`.
4. **Il diagramma a blocchi** asserisce +3 dB ± 0,1 dB, il +10 dB e la
   connettività in parallelo. Fatto fallire su tre netlist sabotate.
5. **V1**, `data/2026-09-14/L27/dopo/tb_loop/`:
   - 0 dB **61,83°** (spigoli 61,45°);
   - +3 dB **69,79°** (spigoli 68,67°);
   - +10 dB 102,99°.

   V2, P7, classe A, E4, E5 e PSRR rimisurati anche a +3 dB, tutti conformi.

Report: `reports/2026-09-14-L27-terzo-livello-di-guadagno.md`.

### NC-023 — Il trim non ha interlock col mute, e il trim non esiste ancora

| | |
|---|---|
| Requisito | **F8** (**ADR-019**) · ADR-011 |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-10-L26-requisiti-utente.md` |
| Stato | **CHIUSA il 2026-09-14 da L16** — decisioni dell'utente e «Chiusura» in fondo alla voce |

**Evidenza.** Il trim d'ingresso di ADR-011 **non è ancora nel progetto**: è
il lotto **L16**, che deve dimensionarlo coi due vincoli insieme
(attenuazione richiesta da ADR-015 e Zin ≥ 100 kΩ). Non esistendo il trim,
non esiste nemmeno il suo comando, quindi l'interlock elettrico che **F8**
richiede è interamente da fare.

**Cosa serve per chiuderla.** Che L16, quando dimensiona il trim, includa il
**permissivo**: l'alimentazione delle bobine dei relè del trim passa per un
contatto del relè di mute. Il dettaglio da non sbagliare è **quale** contatto:
i relè di mute sono a riposo in mute (ADR-012), quindi il permissivo si prende
dal contatto che è chiuso **in** mute, non da quello che lo è a riposo — ed è
precisamente il tipo di errore che **NC-014** ha già prodotto una volta sul
polo 2 dello stesso relè.

E va verificato **sulla netlist**, come L21 farà per NC-014: applicare il
comando del trim a mute rilasciato e provare che non succede nulla. Un
interlock che non è stato provato a fallire non è un interlock.

**Decisione dell'utente (2026-09-14, dopo L27).** Parole sue: «1. rele 2. trim
per ingresso (meglio se possibile coi bistabili)».
- **Il trim è a relè**, e F2 («a ponticello») si allinea senza ADR: F8
  escludeva già il ponticello.
- **Un trim per ingresso**, come ADR-011.
- **Relè bistabili, se possibile.**

**Cosa cambia in «Cosa serve per chiuderla».** F8 chiede anche che **il valore
impostato resti applicato all'uscita dal mute**. Alimentare le bobine
*attraverso* il contatto del mute, come diceva questa voce, basta per
l'interlock ma **perde il valore** con relè monostabili: uscendo dal mute si
diseccitano e il trim torna a riposo. Quindi:
- **coi bistabili** (G6KU-2F-Y) il contatto del mute abilita gli **impulsi**
  di set/reset, e lo stato resta senza corrente;
- **coi monostabili** il mute abilita il **comando** verso una memoria di
  stato, che è logica e ricade sotto ADR-022. È una strada da riportare
  all'utente coi numeri prima di sceglierla.

Il resto vale com'è: il contatto giusto è quello chiuso **in** mute, e la prova
sulla netlist va fatta fallire. È un ragionamento, non ancora una simulazione:
lo verifica L16.

**Seconda decisione dell'utente (2026-09-14, all'apertura di L16)**, che supera
il «per ingresso» della prima. Parole sue: «voglio introdurre una
semplificazione, ora abbiamo un piano in cui ogni ingresso puó avere il suo
guadagno indipedente, ma non abbiamo un modi per vedere quale guadagno é settato
per ingresso. Credo sia meglio avere un guadagno comune per tutti gli ingressi,
quindi Trim a valle della selezione, ma con un´indicazione a LED del guadagno
selezionato». Discussi i costi, ha scelto: **trim comune a valle del selettore,
LED presi dallo stato vero dei relè**.
- Si perde il pareggio fra sorgenti di ADR-011, e la protezione dell'headroom
  del K11 a +10 dB torna a dipendere dall'uso: il LED la rende visibile, non la
  impone.
- Cambia l'insieme dei progetti conformi, quindi serve una ADR: **ADR-027**.
- Un LED preso dalla posizione del comando **mentirebbe** fuori mute: deve
  leggere i contatti.

**Terza decisione dell'utente (2026-09-14, durante L16): dove sta il trim.** Il
trim all'ingresso del blocco A non rispetta E5 con nessun partitore passivo
che rispetti E3: nella cella +10 dB, attenuatore al massimo, trim −6 dB il
rumore al jack vale 10,60 µV con la scala scelta e **10,12 µV** con la più piccola
che E3 consenta, contro 9,90 µV (senza trim 4,77 µV;
`data/2026-09-14/L16/esplorazione/`). Proposte due posizioni dopo il blocco A,
l'utente ha scelto: «Voglio B: le fisse come copia fedele della sorgente, é
quello che deve fare un´uscita fissa bufferizzata, il TRIM riguarda solo il
guadagno dell´uscita Variabile». **Il trim sta fra il blocco A e l'attenuatore**,
dopo la presa dei buffer delle fisse.

**Chiusura (2026-09-14, L16) — ADR-027.**
- **Il permissivo** è **K6**, un G6K-2F-Y monostabile con la bobina su
  `MUTE_CMD` accanto a K2–K4. `VTRIM` passa per i suoi **due NC in serie**:
  chiusi a bobina diseccitata, cioè in mute.
- **I relè del trim** sono bistabili G6KU-2F-Y (K7, K8; spie K9, K10),
  pilotati da SW1: in mute seguono il comando, fuori mute tengono il valore
  senza corrente.
- **Provato sulla netlist**, non dedotto: `check_relay_safe_state.py` (blocco
  2e). Da `VRELAY`, fuori mute, nessuna bobina bistabile è raggiungibile in
  nessuno dei 4 stati dei relè di guadagno; in mute lo sono tutte.
- **Fatto fallire** su netlist generate da varianti di scratch
  (`data/2026-09-14/L16/esplorazione/falsi/`), tutte rc 1:
  - permissivo sui NO di K6;
  - `VTRIM` presa direttamente da `VRELAY`;
  - bobina di K6 su un'altra net;
  - reset ≠ 0 dB;
  - polarità delle spie invertita;
  - polo 2 invertito.
- **Resta dichiarato in ADR-027**: una bobina di K6 interrotta lascerebbe il trim
  comandabile fuori mute, in silenzio. Report: `reports/2026-09-14-L16-trim.md`.

### NC-024 — L'h_FE del modello MJE15032 sta sotto il minimo del suo datasheet

| | |
|---|---|
| Requisito | **T7** (ADR-016) · **ADR-017** · la disciplina di controllo incrociato di **ADR-013** |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-10-L25-promozione-modelli.md` |
| Stato | aperta |

**Evidenza.** Modello vendor `models/bjt_npn/mje15032.lib`, misurato alle
condizioni del proprio datasheet (MJE15032/D, dicembre 2024 Rev. 7),
ngspice 47, `set temp = 25`:

| Grandezza | Misurata | Finestra | Esito |
|---|---|---|---|
| h_FE @ I_C = 0,5 A, V_CE = 5 V | **66,389** | **70 min** | **FUORI**, 5,1% sotto |
| h_FE @ I_C = 1,0 A | 61,335 | 50 min | dentro |
| h_FE @ I_C = 2,0 A | 53,488 | 10 min | dentro |

**Non è un errore di trascrizione, perché non si è trascritto niente**: il
file è byte per byte come il costruttore lo serve — proprietà verificata con
`diff` fra le righe non-commento del file promosso e dell'originale
congelato. È **il modello del costruttore che non rispetta il minimo del
datasheet dello stesso costruttore**, esattamente la forma di **NC-013**
sull'LSK489 e di **NC-020** sull'LS352.

**Perché è aperta ora e non in L24.** Il numero è di L24, che lo aveva
misurato e registrato in ADR-017 e nel proprio report — ma non nel registro.
Il registro è il posto in cui una discrepanza genera lavoro invece di restare
sepolta in una ADR, e le altre due voci della stessa famiglia ci sono. L25 la
apre promuovendo il modello, e la **blocca**: `tb_mje15032()` in
`validate_models.py` asserisce 66,389 *dichiarandolo sotto il minimo*, senza
proclamare una conformità che non c'è.

**Direzione dell'errore**, che è ciò che decide se è sicura: il modello ha
**meno guadagno** della parte garantita, quindi le cifre di corrente di
pilotaggio e di carico visto dal driver che ne escono sono **pessimistiche**.
È la direzione sicura — ma non è «conservativa di una quantità nota», e il
modello non descrive una parte conforme.

**Una correzione a L24 che va con questa voce**: l'h_FE a 2,0 A, che L24
dichiarava «non raggiunto», si raggiunge. Era l'estensione del suo sweep di
base, non una proprietà del modello, che spazzato fino a V_b = 1,6 V arriva a
I_C = 6,8 A in modo liscio e monotòno. A 2,0 A vale 53,5 contro un minimo di
10: **dentro**.

**Cosa serve per chiuderla.** La stessa cosa che serve a NC-013: quantificare
in **Fase 4** quanto il progetto dipenda dall'h_FE dei dispositivi d'uscita a
questa corrente, sapendo che il punto di lavoro reale è **14,71 mA** —
34 volte sotto il punto specificato più basso — dove il datasheet non dice
nulla e il modello dice 75,73. Oppure accettare lo scarto con una ADR che ne
dichiari l'effetto.

### NC-025 — La f_T di entrambi i modelli MJE sta sotto il minimo del datasheet, letta come il datasheet la definisce

| | |
|---|---|
| Requisito | **T7** (ADR-016) · **ADR-017** · la disciplina di controllo incrociato di **ADR-013** |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-10-L25-promozione-modelli.md` |
| Stato | aperta |

**Evidenza.** `models/bjt_npn/mje15032.lib` e `models/bjt_pnp/mje15033.lib`,
alle condizioni del datasheet MJE15032/D — I_C = 500 mA, |V_CE| = 10 V,
25 °C — con la corrente di collettore **verificata** dall'`op`
(`5,000000e-01` e `−5,00000e-01`):

| Modello | f_T misurata | Minimo | Esito |
|---|---|---|---|
| MJE15032 (NPN) | **27,667 MHz** | 30 MHz | **FUORI**, 7,8% sotto |
| MJE15033 (PNP) | **29,286 MHz** | 30 MHz | **FUORI**, 2,4% sotto |

**La voce nasce da una definizione, non da una misura nuova, ed è la parte
che conta.** La **Nota 2** del datasheet dice `fT = hfe · ftest` e la riga di
prova dà **ftest = 1,0 MHz**: la f_T che il costruttore garantisce è il
**prodotto guadagno-banda misurato a 1 MHz**, non l'attraversamento a
|hfe| = 1. A 1 MHz questi dispositivi stanno solo ~2,6 ottave sopra il proprio
polo di beta, quindi la lettura a 1 MHz è **materialmente più bassa**
dell'asintoto — e lo è anche sulla parte vera, che è precisamente perché il
costruttore specifica la frequenza di prova.

Le due letture, sullo stesso modello e allo stesso punto di lavoro:

| | a ftest = 1 MHz (definizione del datasheet) | attraversamento \|hfe\| = 1 |
|---|---|---|
| MJE15032 | **27,667 MHz** — fuori | 30,713 MHz — dentro |
| MJE15033 | **29,286 MHz** — fuori | 30,719 MHz — dentro |

**Il confronto che vuol dire qualcosa è quello fatto come il datasheet lo
definisce**, perché è contro quella prova che il minimo di 30 MHz è scritto.
Fatto così, **nessuno dei due modelli raggiunge il minimo del proprio
costruttore**.

**Cosa questo corregge.** L24 aveva registrato **31,04** e **31,38 MHz** e
li aveva letti come dentro. La differenza non è un disaccordo sul modello: è
il metodo. È la stessa famiglia dell'altra correzione di L25 — la f_T del
MMBT5401, dove L24 aveva misurato a una **corrente** diversa da quella del
datasheet — e insieme dicono una cosa sola: **le condizioni di prova sono
metà del numero, e la definizione della grandezza è l'altra metà.**

**Direzione dell'errore**: il modello è **più lento** della parte garantita,
quindi margine di fase e guadagno d'anello calcolati con esso sono
**pessimistici**. Direzione sicura, quantità non nota — la stessa forma di
NC-020 sull'LS352, e da leggere insieme a essa, perché **tre dispositivi su
sette** del percorso di segnale portano ora un modello più lento del proprio
minimo pubblicato.

**Perché non è bloccante.** Non manca l'evidenza e non è violato un requisito
di prodotto: T7 chiede un modello del costruttore e il modello c'è. È lo
scarto fra modello e datasheet a essere registrato, e il suo effetto va
quantificato dove conta.

**Cosa serve per chiuderla.** Rifare in **Fase 4** margine di fase e guadagno
d'anello dello stadio d'uscita con questi modelli e dichiarare, accanto a ogni
cifra in alta frequenza, che poggia su dispositivi che il modello descrive
**più lenti** del garantito. Se il polo dominante si sposta abbastanza da
mettere in discussione il Miller da 470 pF, ADR-017 prevede già che il valore
di compensazione si ridecida con una ADR propria.

### NC-026 — Il disegno a blocchi non è rigenerabile da L22: le sue asserzioni non girano da un giorno

| | |
|---|---|
| Requisito | La garanzia dichiarata in `../architecture.md` e in `STATE.md` §L1: **nessuna cifra sul disegno è scritta a mano**, tutte vengono lette dalla netlist e **asserite** |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-11-L21-polo-2-rele.md` |
| Stato | **CHIUSA il 2026-09-13 (L10)** — il disegno gira, e lo esegue il blocco 2f. Vedi «Voci chiuse» in fondo |

**Evidenza.** `docs/preamp/schematic/preamp_blocks_draw.py` termina con
`KeyError: 'R237'` alla riga 117. Quattro riferimenti che cita non esistono
più nella netlist:

| Nel disegno | Nella netlist | Cos'è |
|---|---|---|
| `R237`, `R437` | **`R236`, `R436`** (1,50 kΩ) | R_f del blocco B |
| `R239`, `R439` | **`R238`, `R438`** (698 Ω) | R_g del blocco B |

Sono gli scarti di **−1** che **L22** ha prodotto fondendo le due Part
dell'LS352 in una sola. L22 aveva applicato la mappa vecchio→nuovo «ai tre
deck che citano riferimenti espliciti e al disegno» — ma *quel* disegno era
`gain_block_draw.py`, che ha un manifesto ed è coperto dal blocco 2d di
`run_tests.sh`. Il disegno a **blocchi** non ha manifesto, per scelta
dichiarata in `STATE.md` §L1 (un diagramma a blocchi omette i dispositivi di
proposito), quindi **niente lo esegue** e il guasto è rimasto invisibile.

**Non è un difetto introdotto da L21**: verificato sulla netlist di *prima*
della correzione dei relè, dove i quattro riferimenti mancano identicamente.

**Quanto è grave, misurato e non stimato.** Applicando i quattro rinomini su
una copia di scratch, lo script **gira pulito** e tutte le sue asserzioni
passano — compresa quella che ricalcola il guadagno da R_f/R_g e pretende che
cada nella finestra di E2 (**+9,963 dB**). Confrontando l'SVG che ne esce con
quello committato, al netto del timestamp e degli id casuali di matplotlib,
**una sola cifra differisce**:

> `205 componenti` sul disegno committato, **201** nella netlist di oggi.

Quindi il disegno committato **non è sbagliato sul circuito**: è fermo all'8
settembre — prima di L22 — e sbaglia il solo conteggio dei componenti. Il
danno vero non è quella cifra, è che **la garanzia non è più in vigore**:
nessuna delle asserzioni può girare, quindi da L22 in poi il disegno potrebbe
divergere senza che nulla lo dica.

**Cosa serve per chiuderla.** I quattro rinomini, la rigenerazione dell'SVG, e
una risposta alla domanda che il difetto solleva: *chi esegue questo script?*
Le due strade sono un manifesto anche per il diagramma a blocchi (che però
omette i dispositivi di proposito, ed è la ragione per cui non ce l'ha), o un
blocco di `run_tests.sh` che si limiti a **eseguirlo** e a pretendere exit 0 —
il che basta, perché lo script asserisce già da sé tutto ciò che legge.

### NC-027 — I pin SS dell'LSK489 sono disegnati dal suo datasheet ma non definiti

| | |
|---|---|
| Requisito | ADR-013 · precondizione di **G2** (il layout deve sapere cosa fare di ogni pin) |
| Severità | **minore** |
| Aperta da | `reports/2026-09-13-L10-simbolo-lsk489.md` |
| Stato | aperta |

**Evidenza.** Il datasheet congelato
`vendor/jfet/linear_systems/LSK489/LSK489DSRevA38.pdf` (Rev A40), pag. 1,
disegno «SOIC-A Top View», assegna i pin **3 e 7** a «**SS**». Nessuna riga di
testo del documento dice cosa sia SS né come trattarlo, e il modello SPICE non
ne parla. L'unica definizione trovata — «SS: SUBSTRATE, LEAVE THESE PINS
FLOATING (N/C)» — è stampata per l'**LSK389**: datasheet LSK389 Rev A27
pag. 7, e Data Book Linear Systems pag. 15, ultima della sezione LSK389.
L'LSK489 si dichiara «fit, form and pin compatible» con l'LSK389, ma una
compatibilità dichiarata non è l'istruzione scritta per *questa* parte.

**Cosa fa oggi il progetto.** Pin 3 e 7 scollegati in
`circuits/preamp/gain_block.py`, come l'unica istruzione esistente chiede, e
come erano *di fatto* prima di L10. Nel simbolo sono `passive`, non
`no_connect`: il simbolo non afferma ciò che il datasheet non afferma.

**Cosa serve per chiuderla.** Un documento del costruttore che definisca SS
**per l'LSK489** — una revisione del datasheet, una nota applicativa, una
risposta scritta di Linear Systems — congelato in `vendor/` come addendum; o
una ADR che accetti esplicitamente di applicare l'istruzione dell'LSK389 in
forza della compatibilità dichiarata. Prima di G2, perché un substrato
lasciato flottante o collegato è una scelta di layout.

### NC-028 — Il rilascio del mute con segnale presente porta sul jack un gradino che decade in 0,3 s

| | |
|---|---|
| Requisito | **V2** (transitorio del relè di mute, al rilascio) · **F6**/ADR-012 (il mute esiste per non mandare botti alle uscite) · **ADR-019** (il trim si regola a mute inserito) |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-14-L11-mute-e-corto.md` |
| Stato | aperta |

**Evidenza.** `data/2026-09-14/tb_mute_corto_transitorio.csv` e
`tb_mute_corto_trans_{0,10}.csv`. Segnale da 2,7 V RMS a 1 kHz, manopola al
massimo, mute inserito a 10 ms e rilasciato a 30 ms.

**Il meccanismo.** A mute inserito il 4,7 µF d'uscita porta la corrente del
segnale verso massa attraverso i 47 Ω, e quindi si carica alla tensione del
segnale, ≈ 0,58 × V_out a 1 kHz. Al rilascio quella carica resta: il jack
vede il segnale **più** un gradino. Il gradino poi scarica sulla resistenza a
valle.

| Uscita | Picco prima del mute | Picco dopo il rilascio | Gradino medio misurato | Decadimento |
|---|---|---|---|---|
| principale, +10 dB | 11,99 V | **17,39 V** | **5,37 V** | τ = **0,320 s** misurata (calcolata 4,7 µF × 68,8 kΩ = 0,323 s) |
| principale, 0 dB | 3,81 V | 5,61 V | 1,79 V | τ = 0,321 s |
| fissa FIX1 | 3,81 V | 5,61 V | 1,72 V | τ = 46 ms (Singxer ipotizzato 10 kΩ) |

La stessa commutazione **senza segnale** dà un gradino di picovolt: **il
transitorio d'accensione, che è la ragione di ADR-012, è pulito.** Il
gradino ha l'ampiezza del segnale nell'istante del rilascio, e a frequenza
più bassa la reattanza del condensatore sale e il gradino si avvicina al
picco del segnale.

**Perché è una voce e non una nota.** F6 mette il mute proprio sulla
commutazione del guadagno, e ADR-019 lo usa per regolare il trim. In entrambi
i casi il mute si rilascia **con la musica presente**, e il rilascio produce
un gradino della stessa natura di quello che il mute doveva togliere. Va
nell'ingresso del finale (×21) e nell'SRM-T1.

**Perché maggiore e non bloccante.** V2 chiede di misurare il transitorio, e
ora la misura esiste. Ma V2 **non ha una soglia** su quanto botto sia
accettabile, quindi la voce non è decidibile in negativo: è la forma che
NC-002 aveva prima di ADR-019. Nessun componente è a rischio: P7 è conforme.

**AGGIORNATA IL 2026-09-14, dopo L11, su domanda dell'utente: e se il contatto
mettesse a massa prima del condensatore?**

**Da dove vengono i numeri.** Simulazioni di **scratch**, non versionate: deck
ricavati dal `tb_mute_corto.cir` risolto, con segnaposto tranne LS352 e
LSK489. **L29 deve rifarle con un deck versionato** prima di usarle per
decidere.

**Le prove.** Segnale da 2,7 V RMS a 1 kHz, +10 dB, inserzione e rilascio sul
**picco** del segnale. Una prima prova commutava sugli zeri e nascondeva
proprio il gradino da confrontare. Tre posizioni del contatto di mute:
- **dopo** il condensatore, com'è cablato;
- **prima**, fra i 47 Ω e il 4,7 µF;
- su **entrambi** i lati.

| Uscita principale | Dopo (oggi) | Prima | Entrambi |
|---|---|---|---|
| Gradino al rilascio con musica | **−3,62 V** (5,37 V rilasciando sullo zero) | −72 mV | −166 mV |
| Gradino all'inserzione | nessuno | +98 mV | nessuno |
| Residuo sul jack a mute inserito, picco-picco | 4 mV | 4 mV | 1,6 µV |
| Guadagno 0 → +10 dB sotto mute, senza segnale: al rilascio | pV | **−124 mV** (−67 mV dopo 25 ms) | **−155 mV** (−96 mV dopo 25 ms) |
| Mute di 2 s senza segnale: all'inserzione / al rilascio | pV / pV | **+104 mV / −154 mV** (−41 mV dopo 300 ms) | non misurato |
| Contatti di mute | 6 | 6 | 12 |

Col contatto prima, o su entrambi i lati, il jack sale per **2,2 µs** a
14,7 V subito dopo il rilascio. È l'anello che si riprende quando i 255 mA di
carico spariscono di colpo: è fuori banda, e un relè vero si apre in
millisecondi.

**Il compromesso, in una frase per lato.**
- **Oggi**, a mute inserito, il condensatore resta collegato all'uscita
  attraverso i 47 Ω. Quindi segue sempre l'offset in continua, e nessun
  gradino d'offset arriva mai al jack. Ma si carica anche con la **musica**.
- **Col contatto prima**, la musica non lo carica. Però durante il mute si
  scarica sul carico (τ 0,32 s). Ogni inserzione, e ogni rilascio dopo un
  mute lungo, **accensione compresa**, portano sul jack un gradino **pari
  all'offset in continua del blocco**.
- **Il volume non lo riduce**: l'offset nasce nel blocco B, dopo
  l'attenuatore.
- **Il contatto su entrambi i lati non aiuta sull'offset**: il condensatore
  si scarica comunque.

**Quanto vale l'offset.**

| Parte | Condizioni | 0 dB | +10 dB |
|---|---|---|---|
| Sistematica, simulata | segnaposto, sorgente 2,5 kΩ | −16,6 mV | −52,2 mV |
| Sistematica, simulata | modelli vendor MJE/MMBT, sorgente 2,5 kΩ | −14,2 mV | −44,6 mV |
| Sistematica, simulata | segnaposto, sorgente 1,5 Ω | −33 mV | −104 mV |
| Casuale, dal datasheet | LSK489 \|V_GS1 − V_GS2\|: **8 mV tipici, 20 mV massimi** (Rev A40, pag. 1), ×1 a 0 dB e ×3,15 a +10 dB | fino a ±20 mV | fino a ±63 mV |

Lo specchio LS352 aggiunge poco: 0,2 mV tipici di ΔV_BE.

**Quanto si sente: stima d'ordine di grandezza, calcolata e non misurata.**
- **Il calcolo.** Finale ×21,1, Heresy 96 dB/1 W/1 m, cioè 2,83 V. Il fronte
  di un gradino ΔV al jack arriva a circa 96 + 20·log(21,1·ΔV / 2,83) dB SPL
  di picco a 1 m.
- **È un limite superiore grossolano.** Tratta il picco del fronte come un
  tono, e un clic di millisecondi si sente meno di un tono.
- **I risultati:**

| ΔV al jack | ≈ dB SPL di picco a 1 m |
|---|---|
| 1 mV | 53 |
| 14 mV | 76 |
| 45 mV | 86 |
| 104 mV | 94 |

- **Per confronto**, il gradino della musica di oggi, a un normale livello
  d'ascolto con qualche centinaio di mV al jack, arriva fra 95 e 100 dB.
- **Per l'SRM-T1** il numero dipende dal suo guadagno, che il progetto non
  conosce.

**Cosa serve per chiuderla.**
1. **Una soglia dell'utente** su V2: ampiezza massima del gradino al jack, o
   regola d'uso scritta come vincolo. «Volume al minimo prima di rilasciare»
   funziona **solo** sul gradino della musica e **solo** sull'uscita
   principale.
2. **Poi un rimedio misurato.** Le forme note:
   - **contatto prima del condensatore**, simulato qui sopra. Toglie il
     gradino della musica e ne mette uno pari all'offset, a ogni mute;
   - **abbassare l'offset**: bilanciare la parte sistematica del blocco, e
     scegliere coppie LSK489 con V_GS appaiata. È ciò che rende piccolo il
     gradino del contatto prima;
   - **rilascio lento**: un elemento a resistenza graduale in derivazione, che
     porta un gradino d'offset sotto la banda udibile. Un elemento a stato
     solido normalmente aperto **non** mette a massa a macchina spenta, quindi
     il relè NC di ADR-012 resta. Non serve contro il gradino della musica:
     lo rallenta, ma resta di volt;
   - **mute in serie**, che non carica il condensatore ma cambia lo stato
     sicuro (ADR-012, `check_relay_safe_state.py`);
   - **una sequenza di rilascio col segnale azzerato a monte**: toglie il
     gradino della musica, non quello d'offset.

   Nessuno di questi è ancora verificato. Va letta insieme a ADR-021, che
   lascia libera la tecnica del mute attivo, e a P7: col contatto prima, il
   carico a mute è 47 Ω anche in bassa frequenza, e la termica va rimisurata.

**AGGIORNATA IL 2026-09-15, da L34: il cambio di guadagno a caldo e
l'interblocco di ADR-030.**

- **Cosa cambia per questa voce.** L'utente vuole togliere il bump del cambio
  di guadagno con un interblocco dal mute (ADR-030, strada B), ma solo se una
  misura lo giustifica. Parole sue: «altrimenti rischiamo di aggiungere relè e
  LED senza motivo, introducendo un bump per togliere un bump».
- **Il gradino del cambio a caldo, calcolato e non misurato.** Coi Vos_in della
  tabella sopra, al jack principale:
  - 0↔+3 dB: ~6–14 mV;
  - +3↔+10 dB: ~25–59 mV;
  - 0↔+10 dB: ~31–114 mV.

  Con la formula sopra sono ~69–95 dB SPL di picco. Tabella in ADR-030; le
  fisse non sono toccate.
- **Il confronto che serve.** Per ogni rimedio elencato in «Cosa serve per
  chiuderla»: cambio a caldo contro cambio sotto mute seguito dal rilascio.
  - Col mute di oggi il cambio sotto mute non lascia gradino d'offset, perché il
    4,7 µF segue l'uscita attraverso i 47 Ω; resta il gradino della musica al
    rilascio.
  - Col contatto prima del condensatore ne lascia uno d'offset.
- **Chi lo fa**: **L29**, esteso. Da quell'esito dipende **L36**.
- **Evidenza**: il calcolo in
  `reports/2026-09-15-L34-decisioni-comandi-guadagno-telaio.md`. Nessun dato
  nuovo.


### NC-029 — Con i buffer delle fisse la dissipazione a riposo raddoppia, e P5 non la copre

| | |
|---|---|
| Requisito | **P5** (~3-4 W in mobile chiuso) · **ADR-021** (60 °C nel telaio) · ADR-003 (~0,55 W per blocco) |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-14-L17-buffer-uscite-fisse.md` |
| Stato | aperta |

**Evidenza.** `data/2026-09-14/L17/tb_mute_corto_regime.csv`, colonna
`p_rail`, caso 0 senza segnale. È la potenza media che i due rail erogano a un
canale a riposo:
- **3,2248 W** per canale;
- **6,45 W** per i due;
- **0,806 W per blocco**, contro gli ~0,55 W che ADR-003 stimava.

**Il confronto con prima.** Con quattro blocchi invece di otto, la stessa
cifra per blocco dà circa 3,2 W. È calcolato, non misurato sulla topologia di
prima.

**Cosa manca ancora.** L'alimentatore: regolatori, raddrizzatori, trasformatore
e bobine dei relè. La sola scheda audio supera già i 3-4 W che P5 prevede per
l'apparecchio intero.

**Perché maggiore e non bloccante.**
- **P5 è una previsione di ventilazione, non un limite**: nessuna soglia è
  superata.
- **Ma i 60 °C nel telaio** su cui ADR-021 e ADR-023 hanno misurato P7 sono
  stati scelti per quel telaio: stanza a 35 °C più ~25 °C di aumento.
- **Raddoppiare il calore interno** può far cadere l'ipotesi, e con lei il
  margine di P7: il dispositivo più caldo è a 96,4 °C, cioè 28,6 °C sotto il
  limite.

**Cosa serve per chiuderla.**
1. **Una stima termica del telaio** con la dissipazione totale: scheda audio
   più alimentatore.
2. **Se l'aumento resta dentro i 60 °C**, P5 si aggiorna al numero vero.
3. **Se non ci resta**, o una ventilazione e un montaggio progettati, con una
   ADR che aggiorni P5, oppure ADR-021 si riapre, come il suo «Da riaprire se»
   prevede.
4. **La conferma finale** è la temperatura misurata nel telaio del prototipo.

Lotto **L30**.

### NC-030 — `tb_noise_vectors.cir` non scrive dati: cita vettori di rumore di dispositivi che non esistono più

| | |
|---|---|
| Requisito | **V4** (le misure con la loro provenienza) · la disciplina di `docs/limitations.md` #22 |
| Severità | **minore** |
| Aperta da | `reports/2026-09-14-L27-terzo-livello-di-guadagno.md` |
| Stato | **CHIUSA il 2026-09-15 da L31** — vedi «Chiusura» in fondo alla voce e «Voci chiuse» |

**Evidenza.** `data/2026-09-14/L27/dopo/tb_noise_vectors/tb_noise_vectors.log`,
riga 485: `Error: no such vector onoise_q123`.
- ngspice esce **0**;
- il `wrdata` si ferma e non viene scritto nessun file dati: il JSON ha 0 righe.

**I nomi morti.** La riga `wrdata` del deck cita, fra gli altri, `onoise_q123`,
`onoise_r121`, `onoise_jq110` e `onoise_jq111`. Nell'include del blocco, anche
in quello di `main` prima di L27, non esistono né Q123 né R121: il VAS è Q122,
lo specchio Q121A/B. Esistono JQ110A/B, non JQ110 né JQ111. L27 ha aggiunto al
deck solo le due righe di terminazione di `RG10`, quindi il difetto è
**preesistente**, con ogni probabilità dalle rinumerazioni di L22 e L10. Nessun
dato versionato di questo deck esiste dopo quelle date.

**Perché nessuno l'ha visto.** Il blocco 2g controlla i dispositivi citati come
`@nome[…]` e dopo `alter`, non i nomi dei vettori che `noise` costruisce da sé
(limitazione #27, «Cosa non vede»).

**Perché minore.** Il deck è informativo: la ripartizione del rumore per
dispositivo è anche in `tb_noise_breakdown.cir`, che funziona. Nessun verdetto
poggia su questo file.

**Cosa serve per chiuderla.**
1. Rinominare i vettori a partire dall'include generato, non da un elenco scritto
   a mano.
2. Estendere `check_deck_refs.py` ai nomi `onoise_<dispositivo>` e
   `inoise_<dispositivo>`, e farlo fallire sul deck di oggi.

Lotto **L31** (XS).

**Chiusura (L31, 2026-09-15).** Report `reports/2026-09-15-L31-vettori-di-rumore.md`,
dati `data/2026-09-15/L31/`.
1. **Il guardiano, prima della correzione.**
   - `check_deck_refs.py` controlla ora ogni `onoise_<x>`/`inoise_<x>` fuori da
     commenti e virgolette. I suffissi di sotto-sorgente sono letti da un deck
     sonda.
   - Sul deck di `main`: **rc 1, esattamente 4 MISSING** (q123, r121, jq110,
     jq111), e `run_tests.sh` 7 passed / 1 failed sul 2g.
   - Nessun falso allarme sugli altri 16 deck, né sui 16 deck pre-L27.
   - 13 sabotaggi su 13 come attesi.
2. **I nomi, da una mappa per nodi** dall'include di L4 a quello di oggi
   (`esplorazione/mappa.txt`), non da un elenco:
   - q123 → Q121B e q122 → Q121A (specchio);
   - r121 → R120 e r120 → R119 (degenerazione);
   - r138 → R136 (R_f);
   - jq110 / jq111 → JQ110A / JQ110B.

   **Tre nomi vivi erano già sbagliati** (#22, secondo modo): `onoise_q122`,
   `onoise_r120` e `onoise_r138` avrebbero scritto il VAS, l'altra degenerazione
   e R_g. L'«Evidenza» sopra non lo diceva; il 2g non li vede.
3. **I dati.** Log con **0** righe `Error`, CSV con **2 righe** e 20 colonne. A
   1 kHz, come pavimento senza 1/f:
   - la quadratura dei 42 totali per dispositivo dà 8,605323e-09 contro
     `onoise_spectrum` 8,605323e-09;
   - gli 8 dispositivi scritti sono i primi 8 della classifica, con l'85,21 %
     della potenza;
   - lo spettro coincide con `tb_noise_breakdown` B di L27.
4. **Una frase di questa voce non era vera**: «la ripartizione del rumore per
   dispositivo è anche in `tb_noise_breakdown.cir`». Quel deck la calcola e la
   distrugge senza stamparla; il suo log dice solo `No. of Data Rows : 2`. La
   severità non cambia: nessun verdetto poggiava su nessuno dei due.

### NC-031 — La provenienza dichiarata dell'LSK489 non è quella simulata

| | |
|---|---|
| Requisito | **V4** (la provenienza del modello accanto a ogni cifra) · ADR-013 · letta insieme a **NC-004** e **NC-017** |
| Severità | **minore** |
| Aperta da | `reports/2026-09-15-L32-dossier.md` |
| Stato | **CHIUSA il 2026-09-15 da L33** — vedi «Chiusura» in fondo alla voce e «Voci chiuse» |

**Evidenza.** Da L32, che ricava la provenienza dagli `.include` invece di
leggerla dai commenti.
- **Cosa si simula.** `circuits/preamp/gain_block.py:325-326` istanzia
  `LSK489X`. Il modello è definito **solo** in
  `spice/preamp/placeholder_devices.lib:55-56`: Shichman-Hodges scritto a mano,
  `KF=0`.
- **Il modello del costruttore** sta in `models/jfet/lsk489.lib` e si chiama
  `LSK489A`. Nessun file di `spice/`, `circuits/` o `scripts/` lo include, se non
  la ricetta di `validate_models.py`.
- **Cosa si dichiara.**
  - I README di `data/2026-09-14/L12/`, `L27/` e `L16/`: «segnaposto più LS352 e
    LSK489 vendor».
  - Dodici deck di `spice/preamp/tb/` portano il commento di L22 «the only real
    device model in this deck besides the LSK489». Sono `tb_ac`, `tb_bias_sweep`,
    `tb_dc_headroom`, `tb_loop`, `tb_loop_blockA`, `tb_noise_breakdown`,
    `tb_noise_vectors`, `tb_op`, `tb_switch_v2`, `tb_switch_v2_counterfactual`,
    `tb_v3_overload` e `tb_zout_psrr_noise`.
  - `tb_trim.cir:43` dice «KF = 0 but on the LSK489».

**Cosa cambia, e cosa no.**
- **Nessun numero cambia.** Cambia cosa si crede di un numero: nei dati di oggi
  l'unico modello del costruttore è l'LS352, e **nessun dispositivo simulato ha
  rumore 1/f**, JFET compresi.
- NC-004 dice «nel repo solo l'LSK489 ha rumore 1/f». È vero della libreria, non
  delle simulazioni.
- Il modello d'angolo di NC-013 non entra ancora in nessuna cifra simulata.

**Perché minore.** Nessun verdetto poggia sulla frase. Il dossier, da L32, scrive
la provenienza ricavata dagli `.include`, e quella è giusta.

**Cosa serve per chiuderla.**
1. Correggere i commenti dei tredici deck.
2. Precisare i tre README datati con una nota che non ne riscriva il testo.
3. Decidere se un guardiano debba confrontare la provenienza dichiarata con
   quella degli `.include`, e in quel caso farlo fallire sullo stato di oggi.

La sostituzione vera del modello nel circuito resta la Fase 4 (NC-017).

Lotto **L33** (XS).

**Chiusura (L33, 2026-09-15).** Report:
`reports/2026-09-15-L33-provenienza-lsk489.md`. Dati: `data/2026-09-15/L33/`.
1. **Il conto rifatto non era quello di questa voce**
   (`esplorazione/conta.py`).
   - **Quindici deck**, non tredici: anche `tb_blockA_carichi.cir:40` e
     `tb_mute_corto.cir:54` dicevano «tutto tranne LS352 e LSK489 e'
     segnaposto».
   - **Cinque README datati espliciti**, non tre: anche
     `data/2026-09-14/L17/` e `data/2026-09-10/`. Più **due impliciti**,
     `data/2026-09-13/` e `data/2026-09-14/`, che scrivono «ogni altro
     dispositivo ancora segnaposto» dopo aver nominato l'LSK489.
   - Fuori conto e non toccata, perché output datato: la copia
     `data/2026-09-14/L16/esplorazione/deck/tb_blockA_carichi_trim.cir:40`.
2. **Il guardiano c'è: blocco 2h**, `scripts/check_deck_provenance.py`. Il
   criterio è la `provenance()` del dossier, importata e non riscritta; le
   affermazioni sono lette dai commenti nelle forme trovate.
   - **Fatto cadere prima di correggere**: sui deck di `main` rc 1 con
     **esattamente 15** contraddizioni, una per deck; `run_tests.sh` 8 / 1 sul
     2h. Sui 16 deck di `6748fbc` (L12), 14: la stessa frase, prima di
     `tb_trim`.
   - **11 sabotaggi su 11** come attesi, fra cui una frase negata e una vera in
     forma diretta, che non devono scattare.
3. **Solo commenti, provato**: `solo_commenti.py` confronta i deck con quelli di
   `main`. 15 deck cambiati, ogni riga tolta o aggiunta comincia con `*`, le
   righe non di commento sono identiche. Fatto cadere su una copia con una riga
   `VPP … DC 16`.
4. **I sette README** sono annotati in coda, con una nota di L33. Il testo resta
   intatto: il diff ha solo righe aggiunte.
5. **Nessun numero rieseguito, dossier non rigenerato.** Le sue 16 righe di
   provenienza dicevano già «del costruttore: LS352», con l'LSK489 fra i
   segnaposto.
6. **NC-004 precisata**: «nel repo solo l'LSK489 ha rumore 1/f» è vero di
   `models/`, non delle simulazioni.
7. Suite **9 passed / 0 failed**.

### NC-032 — I comandi e i LED del frontale di ADR-028 non esistono nel circuito

| | |
|---|---|
| Requisito | **F10**, **F11** · ADR-028 · letta insieme a **F5**/ADR-030 e **P8**/ADR-029 |
| Severità | **maggiore** |
| Aperta da | `reports/2026-09-15-L34-decisioni-comandi-guadagno-telaio.md` |
| Stato | aperta |

**Evidenza.** Letta su `circuits/preamp/` e sulla netlist generata
`circuits/preamp/preamp_audio.net`, a `3f625aa`:
- **Nessun comando pilota le bobine.**
  - `GAIN_CMD` ha un solo nodo, K1 pin 8; `GAIN10_CMD` un solo nodo, K5 pin 8.
  - `MUTE_CMD` porta soltanto le bobine dei relè: K2, K3, K4 e il permissivo K6.
  - Non ci sono commutatore del guadagno, interruttore di mute, né un
    connettore che porti queste net al pannello.
- **Nessun LED di mute.**
- **I LED del trim sono sulla scheda.** D4–D6 hanno footprint
  `LED_THT:LED_D3.0mm` (`trim.py`, `FP_LED`), mentre SW1 è già un header di
  cablaggio (`FP_SW`).
- **Il temporizzatore d'accensione** che F10 combina con l'interruttore
  appartiene all'alimentatore, non ancora progettato.

**Perché maggiore e non bloccante.** Nessuna cifra del progetto cambia, e i
comandi mancanti stanno fuori dal percorso del segnale. Ma senza di loro la
topologia non si congela a G1, e il 2e (`check_relay_safe_state.py`) non può
verificare un comando che non esiste.

**Cosa serve per chiuderla.** **L35**, dopo L29 e L36:
1. header di cablaggio al posto dei LED del trim;
2. il comando del guadagno sul rotativo a 3 posizioni, cablato così che K5 non
   sia mai comandato senza K1 (ADR-026), con o senza l'interblocco di ADR-030
   secondo l'esito di L29;
3. l'interruttore di mute combinato col temporizzatore d'accensione;
4. il LED rosso di mute, da un contatto che dica lo stato;
5. `check_relay_safe_state.py` esteso ai comandi nuovi, e fatto fallire su una
   netlist sbagliata.

## Voci chiuse

**NC-031 — La provenienza dichiarata dell'LSK489 non è quella simulata**
(minore). **CHIUSA il 2026-09-15 da L33.**
- **Quindici deck e sette README datati**, non tredici e tre. I deck sono
  corretti solo nei commenti, e lo prova uno script; i README sono annotati in
  coda.
- Il **2h** confronta ciò che i commenti affermano con la `provenance()` del
  dossier. Fatto cadere sui 15 deck di `main` e su 11 sabotaggi.

Il testo completo della voce resta sopra, con la sua «Chiusura». Report:
`reports/2026-09-15-L33-provenienza-lsk489.md`.

**NC-030 — `tb_noise_vectors.cir` non scrive dati: cita vettori di rumore di
dispositivi che non esistono più** (minore). **CHIUSA il 2026-09-15 da L31.**
- Il **2g** controlla ora i nomi `onoise_*`/`inoise_*`. È stato fatto cadere sul
  deck di allora (4 MISSING) e su 13 sabotaggi, senza falsi allarmi.
- **Vettori rinominati con una mappa per nodi**; tre nomi vivi erano già il
  dispositivo sbagliato (#22).
- 0 righe `Error`, 2 righe di dati, quadratura dei 42 totali = spettro.

Il testo completo della voce resta sopra, con la sua «Chiusura». Report:
`reports/2026-09-15-L31-vettori-di-rumore.md`.

**NC-023 — Il trim non ha interlock col mute, e il trim non esiste ancora**
(maggiore). **CHIUSA il 2026-09-14 da L16.**
- **ADR-027**: permissivo **K6** sul comando del mute, due NC in serie; trim a
  bistabili G6KU-2F-Y, che tengono il valore all'uscita dal mute (F8).
- **Provato sulla netlist** dal 2e, per raggiungibilità da `VRELAY`, e **fatto
  fallire** su sei varianti generate.

**NC-005 — E3 non è verificabile: il valore lo determinerà il trim** (minore).
**CHIUSA il 2026-09-14 da L16.**
- Il trim sta fra il blocco A e l'attenuatore.
- Minimo di |Zin| su 20 Hz–20 kHz identico nelle tre posizioni: 1,000 MΩ, e
  121,1 kΩ con 68 pF di selettore.

Il testo completo delle due voci resta sopra, con la loro «Chiusura». Report:
`reports/2026-09-14-L16-trim.md`.

**NC-022 — La topologia ha due livelli di guadagno, il requisito ne chiede tre**
(maggiore). **CHIUSA il 2026-09-14 da L27.**
- **ADR-026**: due rami di R_g in parallelo, 3,57 kΩ su K1 e 866 Ω su K5.
  Guadagni calcolati dalla netlist: +3,047 e +9,972 dB.
- **V1** al minimo della spazzata: 61,83° / 69,79° / 102,99°, e ai limiti di
  tolleranza 61,45° / 68,67°.
- **V2, P7, classe A, E4, E5, PSRR** conformi anche a +3 dB.
- **Guardiani** estesi e fatti fallire: 2e, 2f, 2g. **Apre NC-030.**

Il testo completo della voce resta sopra, con la sua «Chiusura». Report:
`reports/2026-09-14-L27-terzo-livello-di-guadagno.md`.

**NC-021 — Il blocco B a 0 dB sta sotto i 60° nel caso peggiore capacitivo**
(bloccante). **CHIUSA il 2026-09-14 da L12.**
- **ADR-024**: la sonda è il cavo al jack, e conta il minimo fino a 4,7 nF. Il
  caso peggiore vero era 54,97°, con l'attenuatore a metà corsa.
- **ADR-025**: C_f da 22 a 330 pF in tutte le istanze. Blocco B a 0 dB
  **61,21°**.
- **Non regressione** rimisurata: PSRR, E5, slew, V2, V3, classe A e P7
  invariati.

**NC-002 — Il blocco A non ha evidenza di stabilità valida** (bloccante).
**CHIUSA il 2026-09-14 da L12.**
- **ADR-024**: il blocco A si giudica col suo cablaggio, capacità realistica
  ≤ 1 nF.
- Deck ai valori veri e con le sorgenti di V1: blocco A **63,36°**, buffer
  delle fisse **61,63°**.

Il testo completo delle due voci resta sopra, con la loro «Chiusura». Report:
`reports/2026-09-14-L12-margine-di-fase.md`.

**NC-010 — Le uscite fisse non sono isolate: un apparecchio spento a valle
porta il Blocco A in Classe B** (bloccante). **CHIUSA il 2026-09-14 da L17.**
- **ADR-023**: la classe A si giudica sui percorsi ascoltabili.
- **Il rimedio**: un `GAINBLOCK` per ogni uscita fissa.
- **Le misure**, `data/2026-09-14/L17/`:
  - con un apparecchio da 470 kΩ a 0,01 Ω sulla fissa 1, il blocco A resta a
    14,356 mA e il buffer dell'altra fissa a 14,509 mA;
  - il cablaggio di ADR-008 nello stesso deck ritrova la classe B;
  - `tb_mute_corto` a quattro blocchi: 0 righe ascoltabili fuori dalla classe
    A, P7 conforme.
- **Guardiano**: il blocco 2f, fatto fallire sulla netlist di `main`.
- **Apre NC-029**, il calore.

Il testo completo della voce resta sopra, con la sua «Chiusura». Report:
`reports/2026-09-14-L17-buffer-uscite-fisse.md`.

**NC-001 — Il mute in derivazione porta lo stadio d'uscita fuori dalla Classe
A** (bloccante). **CHIUSA il 2026-09-14 da L11**, per la strada 2 riformulata
dalla decisione dell'utente.
- **ADR-021** ammette la classe B a mute inserito e in corto, col criterio Tj
  ≤ 125 °C a 60 °C ambiente, a regime e nel transitorio.
- **`tb_mute_corto.cir`** misura mute e corto su tutte e tre le uscite:
  - tutti i dispositivi conformi senza protezione né dissipatore;
  - MJE peggiore 484 mW, Tj 90,2 °C;
  - le cifre di G0 riprodotte entro lo 0,1 %.
- **Il deck è stato fatto fallire** togliendo i contatti di mute.
- **«Classe A garantita» è corretta** in `gain_block.py` e sul disegno.
- **Consegna** tre vincoli di distinta sulle resistenze (P7) e **apre
  NC-028**.

Il testo completo della voce resta sopra, con la sua «Chiusura». Report:
`reports/2026-09-14-L11-mute-e-corto.md`.

**NC-007 — Lo «scarto ADR-014» pubblicato non misura la claim di ADR-014**
(minore). **CHIUSA il 2026-09-13 da L14.** Il dossier pubblica ora due cifre
distinte, ciascuna col proprio nome. Lo **scarto assoluto** fra sorgente 2500 Ω
e 1,5 Ω vale −0,02167 dB a 1 kHz in entrambe le modalità, e −0,02163 dB (0 dB)
e −0,02154 dB (+10 dB) a 20 kHz: è il partitore con la Zin, e la pagina dice
che non misura la claim. Lo **scarto a 20 kHz riferito a 1 kHz**, che è la
claim, vale **4,35·10⁻⁵ dB** a 0 dB e **1,37·10⁻⁴ dB** a +10 dB. Le cifre
vengono dai `print` di `tb_ac.log` e sono state ricalcolate in modo
indipendente dai CSV (4,352·10⁻⁵ e 1,370·10⁻⁴). Il KPI in testa cita il
**peggiore delle due modalità**, 1,37·10⁻⁴, e dice che è il peggiore. La
seconda copia della cifra, cioè la tabella di `data/2026-09-09/README.md`, ha
preso una nota datata e non è stata riscritta. Letto su `index.html`
generato, non su `build_dossier.py`. Report:
`reports/2026-09-13-L14-correzioni-di-testo.md`.

**NC-006 — `gain_block.py` porta due valori superati per il riferimento di
cascode** (minore). **CHIUSA il 2026-09-13 da L14.** Le righe 314-315 e
320-321 dicono ora `v(ncasc) = 9.887 V` e drain a 9,21 V, e citano ADR-014 e
**`data/2026-09-10/tb_op-LS352.log`**, non il `2026-09-09/tb_op.log` che la
voce citava: quello è la topologia col THAT320. `tb_op.cir`, rieseguito il
2026-09-13, dà 81 valori su 81 identici al log LS352; cambiano solo i nomi di
47 righe, per la rinumerazione di L10. Che nessuna riga di codice sia
cambiata lo prova l'**AST**: `ast.dump` identico fra HEAD e il file nuovo,
stesso numero di righe, controllo fatto fallire su una copia con
10.0k → 10.1k. La riga 153, la storia della bozza da 8,485 V, resta.

**NC-003 — Il KPI «margine di fase, peggiore» non è il peggiore del
prodotto** (minore). **CHIUSA il 2026-09-13 da L14**, col qualificatore e non
portando il blocco A nel KPI, che resta NC-002/L12. Il KPI dice «Margine di
fase, blocco B — 56,945 gradi · peggiore dei 4 casi pubblicati». La sezione 6
si apre ora dicendo che tutti i dati d'anello sono del blocco B e che il blocco
A non è pubblicato. La riga V1 e il titolo di `fig_loop.svg` portano lo stesso
qualificatore. Verificato sul deck che `tb_loop.cir` è il blocco B.

**NC-026 — Il disegno a blocchi non è rigenerabile da L22** (maggiore).
**CHIUSA il 2026-09-13 da L10.** `preamp_blocks_draw.py` cita ora
R113/R313, R235/R435 e R237/R437 — la mappa **ricavata dalla netlist**,
composta con la fusione dell'LSK489 che L10 ha prodotto sopra — e gira: tutte
le asserzioni passano, guadagno ricalcolato **+9,963 dB**, e l'SVG rigenerato
differisce dal committato per la sola cifra `205 componenti` → **197**. Alla
domanda *chi lo esegue* risponde il blocco **2f** di `run_tests.sh`, che lo
esegue e pretende exit 0, scrivendo l'SVG in `results/`. Fatto fallire sulla
netlist di prima: `KeyError: 'R237'`.

**La voce era più larga di quanto dicesse.** Lo stesso scarto di −1 aveva
rotto **due deck**, trovati facendo la baseline:
`tb_switch_v2_counterfactual.cir` apriva un `r138` che non esisteva più
(ngspice: «no such device», exit 0 — lo stato «anello aperto» era identico a
quello chiuso, −0,0522 V; riparato, **−13,773 V**), e `tb_bias_sweep.cir`
spazzava `r130`, diventato l'**altro** ramo del moltiplicatore di Vbe (I_q
5,207 mA invece di **14,714** a 1690 Ω). Il primo tipo è ora coperto dal
blocco **2g** (`scripts/check_deck_refs.py`), fatto fallire sui deck di prima:
due rilevazioni, entrambe `r138`. Il secondo tipo **non è coperto da nessun
controllo automatico**: vedi `limitations.md` #22. Report:
`reports/2026-09-13-L10-simbolo-lsk489.md`.

**NC-014 — Il polo 2 del G6K-2F-Y è cablato con NO e NC invertiti**
(bloccante). **CHIUSA il 2026-09-11 da L21.** La riga 79 di
`circuits/preamp/preamp_audio.py` dice ora `K_COM2, K_NO2, K_NC2 = "6", "5",
"7"`, e sulla netlist rigenerata il nodo `GND` porta **K1 pin 4 e 5** e
**K2/K3/K4 pin 2 e 7** — prima K1 4+7 e K2/K3/K4 2+5. Il diff normalizzato
tocca **quattro numeri di pin** e nient'altro.

Il pinout è stato **riletto alla fonte** invece di ereditato da L8, su tre
gambe concordi, e le due ripetibili danno lo stesso verso su entrambi i poli:
0,44 pt contro 3,39 pt nel PDF, e stessa x esatta nel simbolo KiCad. La
trappola è ora scritta per esteso nel codice: **entrambe le armature
riposano sul pad immediatamente a sinistra del proprio COM, ma le due righe
sono numerate in versi opposti**, quindi «NO = COM+1» vale per il polo 1 e non
per il polo 2.

**La voce si chiude col guardiano, non con la correzione.** Un difetto che
fallisce in silenzio nel verso che manda il transitorio d'accensione sulle
cuffie non è chiuso da una verifica una tantum:
`scripts/check_relay_safe_state.py` asserisce l'intento delle ADR sulla
netlist generata e gira nel blocco **2e** di `run_tests.sh` (la suite passa da
5 a 6 blocchi). È stato **fatto fallire** sulla netlist di prima — 12
rilevazioni, tutte e sole sul polo 2 — e su quattro casi sintetici. Report:
`reports/2026-09-11-L21-polo-2-rele.md`.

**NC-012 — V1 non dichiara la soglia di accettazione del margine di fase**
(maggiore). **CHIUSA il 2026-09-10 da L26.** La soglia è **60°**, decisa
dall'utente e registrata in **ADR-019**, e vale su **ogni** combinazione della
matrice V1 — blocco A compreso, caso peggiore capacitivo da 4,7 nF compreso.
La voce chiedeva anche che la soglia arrivasse **col carico a cui si
riferisce**, e su quello la domanda è stata posta esplicitamente prima di
scrivere: fra «al carico reale», «anche a 4,7 nF» e «ovunque», la risposta è
stata la più severa.

Chiudendosi ha reso decidibili le due voci che dipendevano da lei, e in
entrambi i casi il verdetto è negativo: **NC-002** (blocco A, 41,98°) sale a
bloccante, e nasce **NC-021** (blocco B a 0 dB, 56,46°). Era esattamente ciò
che la voce prevedeva scrivendo che senza soglia «nessuna misura di margine di
fase può passare o fallire».

**NC-015 — Il THAT320 è fine vita** (bloccante). **CHIUSA il 2026-09-10 da
L22 + L23.** Il sostituto è scelto, verificato e montato: **Linear Systems
LS352**, dual PNP monolitico, |V_BE1−V_BE2| 0,2 mV tip / 0,5 max, con modello
del costruttore congelato in `vendor/bjt_pnp/linear_systems/LS350/`,
trascritto sotto la procedura a due letture di ADR-013 (byte-identiche),
controllato contro il proprio datasheet (cinque grandezze su sei dentro; la
sesta è NC-020) e bloccato da una ricetta di regressione in
`validate_models.py`. Lo specchio è stato **riprogettato** come ADR-016
richiedeva e non solo ri-approvvigionato: la degenerazione sale da 47 a
220 Ω, spazzata e non argomentata, e lo stadio d'ingresso finisce **25,7% più
silenzioso** di quando montava il THAT320 (caso peggiore 5,697 → 4,231 µV).
Decisione: **ADR-018**. Report:
`reports/2026-09-10-L22-L23-specchio-ingresso.md`.

**NC-016 — Il footprint del THAT320 è a 8 pin ma la parte esiste solo a 14**
(maggiore). **CHIUSA il 2026-09-10 da L22 + L23.** Si è chiusa come la voce
stessa prescriveva — non correggendo il footprint della parte uscente, ma
perché la parte entrante porta il proprio. Il `SOIC-8` che il codice
dichiarava ora **corrisponde a una parte che esiste davvero in SOIC-8**, col
pinout letto dal disegno del datasheet (1=C1 2=B1 3=E1 4=N/C 5=N/C 6=E2 7=B2
8=C2). E il residuo peggiore è sparito: il duale era istanziato come **due**
Part, cioè due package sul PCB per un dispositivo solo, ed è ora **una** Part
a due unità — verificato sulla netlist, dove i componenti su SOIC-8 passano da
quattro a tre (l'LS352 più i due LSK489, che restano il gap noto di **L10**).
PDIP-8 e DFN-8 sono elencati dal costruttore ma il datasheet **non ne disegna
il pinout**, quindi non sono stati usati: un pinout non pubblicato è
esattamente come il SOIC-8 fantasma è nato.
