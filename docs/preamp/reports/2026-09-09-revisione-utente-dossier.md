# Revisione umana del dossier — 2026-09-09

**Documento datato: non si riscrive.** Come i report di gate, registra
un'esecuzione. Le voci che apre vivono in `../NONCOMPLIANCE.md`.

## Che cosa è, e perché non è un gate

Il 2026-09-09, poche ore dopo l'esecuzione di **G0**
(`2026-09-09-gate-G0.md`), l'utente ha letto il dossier per conto proprio e
ha prodotto quattro osservazioni. Non è una seconda esecuzione di G0: è
l'**altra metà** della revisione, quella che G0 per costruzione non può
fare.

G0 giudica incrociando affermazioni con sorgenti — un'etichetta contro un
`.log`, una connessione contro la netlist. È un metodo forte e ha trovato
NC-001 proprio così. Ma non può giudicare **ciò che il progetto presenta
come normale e che nessuna sorgente del repo contraddice**. Quel giudizio
richiede qualcuno che conosca il dominio e che guardi il disegno. È il
motivo per cui `architecture.md` chiama la revisione umana dello schematico
una precondizione di G1 e G2, e questo report ne è la prima esecuzione.

## Il controllo cieco è chiuso

`STATE.md` teneva aperto un **controllo cieco**: l'utente aveva trovato un
errore nel diagramma a blocchi e aveva chiesto che non fosse
l'orchestratore a cercarlo. G0 non l'ha trovato — alla sua sesta domanda ha
risposto «il diagramma a blocchi non mente» — e la domanda era quale delle
due ipotesi fosse vera: o l'errore stava in qualcosa che il revisore aveva
verificato e giudicato corrispondente, **o stava in una classe di proprietà
che nessuna sorgente del repo può falsificare**.

**È la seconda.** L'errore è che il diagramma mostra il **Blocco A che
pilota tre carichi in parallelo** — le due uscite fisse e l'attenuatore del
volume — e non c'è niente, nel disegno o nel codice, che dica che quel
parallelo è un problema. Nessuna etichetta è falsa. Nessuna connessione è
sbagliata. Il disegno è **fedele** a `preamp_audio.py`, ed è esattamente
per questo che il metodo di G0 non poteva arrivarci: non c'era nessuna
affermazione da falsificare.

Il valore del controllo cieco era misurare la sensibilità reale del gate, e
l'ha misurata: **G0 vede le affermazioni false, non le omissioni di
giudizio.** La conseguenza operativa è in `AGENTS.md`, sezione G0.

## Le quattro osservazioni, e cosa è stato eseguito

Tutti i numeri qui sotto sono stati **eseguiti**, non citati. Dove
riproducono un risultato già presente nel repo lo si dice, perché una
riesecuzione indipendente vale come conferma e non come scoperta.

### Premessa: il banco del Blocco A usa valori superati

Prima osservazione dell'utente, e coincide con **NC-002**, già aperta da
G0. `spice/preamp/tb/tb_loop_blockA.cir` righe 28-33 usa `RSEP = 100`,
`CFIX = 2.2u`, `RJ = 50k`; `circuits/preamp/preamp_audio.py` righe 123-140
cabla **47 Ω, 4,7 µF, 470 kΩ**.

Rieseguito col carico canonico — è la **seconda riesecuzione indipendente**
di questo numero, dopo quella dell'orchestratore di L5d:

| C sul nodo OUT | Margine di fase |
|---|---|
| ~0 (a vuoto) | 69,83° |
| 1 nF | 64,05° |
| 2,2 nF | 56,59° |
| **4,7 nF** | **41,85°** |

Coincide con NC-002 entro qualche centesimo di grado. **Confermata, già
registrata, non ancora corretta**: il rimedio è L12.

### 1. Il margine di sovraccarico in +10 dB è mezzo decibel

**Osservazione.** Con una sorgente moderna a fondo scala (FiiO K11,
2,7 V RMS = E6) dentro la modalità +10 dB, l'uscita richiesta si avvicina
al limite lineare del circuito.

**Eseguito** su `../data/2026-09-09/tb_dc_headroom_10db.csv`,
reimplementando la metrica del dossier dalla definizione (la finestra in
cui il guadagno locale `dVout/dVin` resta entro l'1% del suo valore a 0 V):

| Grandezza | Valore |
|---|---|
| Guadagno misurato a 0 V, modalità +10 dB | 3,146030 (**+9,9553 dB**) |
| Finestra lineare all'1% | v(IN) da −4,150 a +4,100 V |
| Uscita ai bordi della finestra | da −13,0947 a **+12,8595 V** |
| Saturazione vera | da −14,0161 a +13,2176 V |
| **Limite lineare** | **9,0930 V RMS** |
| Richiesti da 2,7 V RMS × guadagno **misurato** | 8,4943 V RMS |
| **Margine** | **+0,59 dB** |

Con il guadagno **nominale** (+10 dB esatti, ×3,16228) i richiesti sono
8,538 V RMS e il margine **0,55 dB**. Le due cifre differiscono solo
perché il guadagno reale è +9,955 dB e non +10,000: la conclusione non
cambia di niente.

**Confermata come misura — ma la decisione esisteva già.** Cercato prima
di aprire la voce: **ADR-015, del 2026-09-08, ha già accettato questo
margine consapevolmente e per iscritto**, scegliendo di restare a ±15 V e
indicando il trim di ADR-011 come rimedio («l'unica cosa che separa quella
modalità dal clipping»). È esattamente la forma con cui uno scostamento si
chiude, quindi **il margine in sé non è una non conformità** e la voce che
si apre non è «bisogna decidere»: la decisione c'è.

Quello che ADR-015 ha lasciato scoperto è però reale, ed è doppio.

**Primo: circolano tre cifre per la stessa quantità.**

| Cifra | Metrica | Dove circola |
|---|---|---|
| **0,75 dB** | clipping vero (9,31 V RMS) contro il richiesto nominale | ADR-015 |
| **0,55 dB** | limite allo scostamento dell'1% (9,0930) contro il nominale | dossier, KPI |
| **0,59 dB** | limite all'1% contro il richiesto col guadagno **misurato** | questa riesecuzione |

Nessuna è sbagliata: misurano cose diverse. Ma fra la più ottimista e la
più conservativa c'è il **36%** del margine, e nessun documento dice quale
sia quale.

**Secondo: il rimedio su cui ADR-015 poggia non esiste nel progetto.** Il
trim di ADR-011 non è in `circuits/` — `preamp_audio.py` lo dichiara fuori
dal proprio perimetro — non ha dimensionamento, e porta ora **due** vincoli
portanti che tirano in direzioni opposte: attenuare abbastanza (ADR-015) e
lasciare la Zin ≥ 100 kΩ (E3, che è **NC-005**). Nessuno ha verificato che
esista un partitore che li soddisfi entrambi. E la conseguenza operativa
che ADR-015 chiede di scrivere «sul pannello o nella documentazione d'uso»
non è stata eseguita, perché né l'uno né l'altra esistono.

**Apre NC-009** in questa forma, non in quella dell'osservazione
originale. Il ragionamento dell'utente — «rendere definitivo il trim o
alzare i rail» — è la stessa alternativa che ADR-015 ha già valutato e
deciso; ripercorrerla sarebbe riaprire una decisione chiusa invece di
eseguirla.

### 2. Le uscite fisse non sono isolate — ed è l'errore del diagramma

**Osservazione.** Il Blocco A pilota due uscite a livello fisso più
l'attenuatore del volume, in parallelo e senza isolamento reciproco.
L'utente segnala due conseguenze: rischio per la Classe A sui picchi, e
modulazione reciproca fra i rami. Aggiunge un fatto che rende la
condizione non ipotetica: **l'impedenza d'ingresso del Singxer non è
nota e da spento potrebbe andare a zero** — ed è esattamente il caso che
**V1 elenca** («Singxer (Zin ignota)») fra i carichi da coprire, e che
nessuna misura copriva.

**Eseguito** con un banco nuovo, `spice/preamp/tb/tb_blockA_carichi.cir`,
versionato insieme ai suoi dati. Blocco A a guadagno unitario, 2,7 V RMS a
1 kHz, carico canonico, spazzando l'impedenza a valle di una uscita fissa:

| RJ1 | I_C(Q134) max | I_C(Q134) **min** | Regime |
|---|---|---|---|
| 470 kΩ (normale) | 14,759 mA | **14,352 mA** | **Classe A** |
| 10 kΩ | 14,943 mA | 14,167 mA | Classe A |
| 1 kΩ | 16,552 mA | 12,524 mA | Classe A |
| 100 Ω | 27,956 mA | **2,396 mA** | Classe A, margine quasi finito |
| 10 Ω | 57,258 mA | **−0,23 µA** | **Classe B** |
| 0,01 Ω | 65,456 mA | **−0,34 µA** | **Classe B** |

I due dispositivi d'uscita si interdicono a turno, ciascuno sulla propria
semionda: lo stadio esce dalla **Classe A pura**, che è **T1**. La soglia
sta fra 100 Ω e 10 Ω di impedenza a valle, cioè fra ~147 Ω e ~57 Ω di
carico totale contando i 47 Ω di separazione.

Il picco a impedenza nulla, **65,46 mA**, è lo stesso ordine dei
**65,07 mA** che NC-001 misura per il mute: stessa fisica, un carico da
qualche decina di ohm sul nodo d'uscita. Ma **le vie d'ingresso sono
diverse**, e questo decide il rimedio: una resistenza in serie al contatto
del relè di mute — il rimedio plausibile di NC-001 — non fa niente contro
un apparecchio spento a valle, perché lì non c'è nessun relè di mezzo.

**Confermata, ed è l'errore del diagramma a blocchi.** Apre **NC-010**,
proposta **bloccante**.

**La seconda metà dell'osservazione NON è confermata.** I file `_ac_`
misurano di quanto si muove il livello sul nodo OUT — l'ingresso
dell'attenuatore — fra fissa carica e fissa in corto:

| Frequenza | Scarto |
|---|---|
| 20 Hz | 0,000 dB |
| 1 kHz | **−0,0034 dB** |
| 20 kHz | −0,0056 dB |
| 100 kHz | −0,0166 dB |

L'anello chiuso tiene il nodo: il livello non si muove in modo
apprezzabile. Va scritto per intero, perché registrare solo la metà che
torna sarebbe la forma più comoda di errore. La distinzione però conta: il
danno non è sul **livello**, è sul **regime di lavoro**, e una spazzata AC
di piccolo segnale non può vedere la Classe B. La distorsione che ne
deriva non è calcolabile da questa libreria segnaposto e arriverà coi
modelli vendor (L6-L7).

### 3. Il PSRR del rail positivo è l'anello debole

**Osservazione.** Il rail positivo ha una reiezione molto peggiore del
negativo, e questo vincola l'alimentatore.

**Eseguito** sui CSV già versionati in `../data/2026-09-09/`:

| Configurazione | 100 Hz | 1 kHz | 10 kHz | 100 kHz |
|---|---|---|---|---|
| rail **+**, +10 dB | 62,07 | 49,56 | **29,76** | **10,15** |
| rail **+**, 0 dB | 72,02 | 59,51 | 39,72 | 19,72 |
| rail **−**, +10 dB | 79,02 | 90,54 | 86,93 | 61,44 |

Il divario fra i due rail a 10 kHz è di **57 dB**. Le cifre citate
dall'utente sono riprodotte esattamente.

**Confermata.** Apre **NC-011** — non perché il numero sia sconosciuto (è
già pubblicato nel dossier) ma perché **non vincola nessuno**:
l'alimentatore non è ancora progettato e nessun documento gli dice quanto
ripple può lasciare sul rail positivo.

### 4. Il margine di fase è sotto i 60° raccomandati

**Osservazione.** Con 4,7 nF di carico capacitivo il margine peggiore
pubblicato scende a 56,95°, sotto i 60° convenzionalmente raccomandati.

**Eseguito**: cercata una soglia di accettazione in `REQUIREMENTS.md`,
nelle quattordici ADR e in `AGENTS.md`. **Non esiste.** V1 enumera con
cura le combinazioni da coprire — blocco, posizione dell'attenuatore,
carico, sorgente — e non dice **quale valore sia accettabile**.

**Confermata, e riformulata.** Apre **NC-012**, ma non nella forma «56,95°
è troppo poco»: nella forma **«senza una soglia dichiarata, nessuna misura
di margine di fase può passare o fallire»**. Nella formulazione originale
la voce sarebbe un'opinione contro un'altra; in questa è un buco nei
requisiti, ed è la voce che rende decidibili sia NC-002 sia NC-003.

## Riepilogo

| Osservazione | Esito | Voce |
|---|---|---|
| Banco del Blocco A coi valori superati | confermata, **già nota** | NC-002 (aperta da G0) |
| 1 · headroom 0,59 dB | misura confermata, **ma ADR-015 aveva già deciso**: la voce si sposta sul rimedio inesistente e sulle tre cifre | **NC-009**, maggiore |
| 2a · uscite fisse non isolate → Classe B | confermata | **NC-010**, bloccante |
| 2b · modulazione reciproca del livello | **non confermata** (0,0034 dB a 1 kHz) | nessuna |
| 3 · PSRR del rail positivo | confermata | **NC-011**, maggiore |
| 4 · margine di fase senza soglia | confermata, riformulata | **NC-012**, maggiore |

Quattro voci nuove. Con le otto di G0 il registro sale a **dodici aperte,
tre bloccanti**.

## Limite di questo report

Tutti i numeri vengono da **modelli segnaposto**
(`spice/preamp/placeholder_devices.lib`), scritti a mano e senza rumore
1/f. Sono credibili sui regimi di lavoro in continua e sulle correnti —
che è ciò su cui NC-010 poggia — e **non lo sono** su distorsione e
rumore. Nessuna cifra di THD compare qui, di proposito.
