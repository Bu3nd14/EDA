# STATE — Preamplificatore di linea

**Leggi questo per primo** riprendendo il progetto.

**Documento vivo**: ogni sessione che tocca il preamp lo aggiorna prima
di chiudere, e lo committa insieme al lavoro. Se è disallineato dalla
realtà, il progetto non è ripartibile.

Ultimo aggiornamento: **2026-09-08** (L0 chiuso: piano a lotti depositato qui; prossimo lotto L1)

---

## Come si lavora da qui: a lotti piccoli e pushati

Il vincolo che governa il lavoro non è tecnico, è il **cap di token del
piano**. Un lotto che non arriva in fondo non lascia lavoro a metà:
lascia un repo in uno stato che la sessione dopo deve prima capire e poi
riparare. Quindi il lavoro è ordinato per **dimensione**, non per
importanza.

### Le regole

1. **Un lotto per volta.** Mai due agenti in parallelo: i loro resoconti
   tornano insieme, e il ritorno è la parte che consuma.
2. **Ogni lotto finisce con un commit pushato**, nell'ordine di
   `CLAUDE.md`: `git push` → `STATE.md` → il resto. Verificato con
   `git log --oneline origin/<branch>..HEAD`, mai assunto.
3. **Questo file nomina sempre il lotto successivo.** È ciò che rende
   economica una ripartenza a freddo: la sessione dopo non ricostruisce
   il contesto, lo legge.
4. **Il messaggio di commit dice quale lotto chiude**, così `git log` da
   solo racconta a che punto è il progetto.
5. **Nessun lotto si inizia sopra l'80% del cap.** Sopra l'80% si chiude
   quello in corso e si aggiorna lo stato, punto.
6. **Gli agenti scrivono su file, non nel discorso.** Un subagente che
   torna con quattromila parole di resoconto costa quanto il lavoro:
   deve lasciare un report in `reports/` e restituire dieci righe.
   L'orchestratore riesegue i numeri prima di riferirli all'utente.

Nota onesta sul punto 5: **l'orchestratore non vede la quota a 5 ore.**
Vede solo un contatore della sessione corrente, che è un'altra cosa. Il
numero vero lo legge l'utente con `/status`. Per questo il lavoro a lotti
conta più del protocollo di avviso: se ogni lotto finisce pushato, il
momento in cui il cap arriva smette di essere importante.

### I lotti

Dimensioni relative, non promesse: **XS** = pochi minuti, **S** = una
manciata di file, **M** = riempie una sessione da solo.

| # | Lotto | Dim. | Stato |
|---|---|---|---|
| L0 | Riallineare questo file e depositarci il piano | XS | **fatto** |
| L1 | Diagramma a blocchi del preamp intero | S/M | **prossimo** |
| L2 | Collaudare la convenzione di percorso `wrdata` su un deck solo | XS | da fare |
| L3 | Applicare la convenzione ai 3 deck che già scrivono | S | da fare |
| L4 | `wrdata` sui deck muti **senza** cicli | S | da fare |
| L5 | `wrdata` sui deck muti **con** cicli annidati | S/M | da fare |
| L6 | LSK489: passi 1-3 di ADR-013 (congela, trascrivi, provenance) | S | da fare |
| L7 | LSK489: passo 4, il controllo incrociato | S | da fare |
| L8 | Fase 3a — le parti nuove, fatti verificabili | M | da fare |
| L9 | Fase 3b — la rosa dei componenti di segnale | M | da fare |
| L10 | Simbolo KiCad dell'LSK489 | S | da fare |

Dopo, non pianificati in dettaglio perché dipendono dall'esito:
**alimentatore + sicurezza rete**, **Fase 4** (revisione topologia coi
componenti veri), **Fase 5** (misure), **dossier**, **G1**.

### Cosa contiene ciascun lotto

**L1 — diagramma a blocchi.** Quello del blocco di guadagno esiste, la
vista d'insieme no. `schemdraw 0.23` è nel venv e
`schematic/gain_block_draw.py` è il template: stesse convenzioni, SVG nel
repo. Sorgente della topologia: `circuits/preamp/preamp_audio.py` e
l'ASCII in `REQUIREMENTS.md`. **Da scrivere nell'intestazione del file**:
è un diagramma a blocchi, quindi **non** passa da `check_schematic.py`,
che confronta dispositivi con la netlist — va detto, o sembrerà
verificato meccanicamente quando non lo è.

**L2-L5 — i testbench diventano artefatti.** Oggi solo 3 dei 12 deck in
`spice/preamp/tb/` scrivono file dati, e **quei 3 scrivono nel posto
sbagliato**: le uniche 4 righe `wrdata` contengono un percorso assoluto
cablato dentro `.claude/worktrees/preamp-fase1/`. Quel worktree esiste
ancora, quindi eseguendo i deck da `main` i risultati **finiscono in
silenzio nell'albero vecchio** — nessun errore. È la stessa classe di
difetto già corretta una volta in `run_tests.sh` (`ROOT` cablato), ed è
destinata a rompersi quando quel worktree sparirà.

Quindi il lavoro non è "aggiungere 9 righe": è rendere coerenti tutti e
12 i deck su un percorso derivato dal repo. Si collauda su **un** deck
(L2) prima di replicare su dodici. I deck con `foreach` sono l'ultimo
lotto perché non sono meccanici: `tb_ac.cir` ha un doppio ciclo (2
modalità × 4 impedenze di sorgente = 8 curve) e chiude ogni iterazione
con `destroy all`, quindi il `wrdata` va **dentro il ciclo, prima del
`destroy all`**, col nome file parametrizzato.

Serve al dossier **e** a `design-reviewer` per rieseguire le misure a G1:
non è lavoro anticipato.

**L6-L7 — i modelli veri.** `vendor/` non contiene **nessun** PDF (13
sottodirectory, zero datasheet congelati) e `models/jfet/` ha solo
`generic_njf.lib`: il passo 1 di ADR-013 non è iniziato. Finché i modelli
sono segnaposto, **ogni cifra di distorsione è priva di significato** —
ed è l'intera ragione per cui si è andati a discreti. I due lotti sono
separati perché il passo 4 è il punto in cui la trascrizione può
risultare sbagliata: in quel caso il lavoro è tornare su L6, non andare
avanti.

**L8 prima di L9** perché le parti nuove sono fatti chiudibili mentre la
rosa è un giudizio aperto: se il cap arriva, è meglio che tagli la
seconda.

## Il dossier: formato deciso, non ancora iniziato

L'utente vuole poter **guardare** il progetto. Formato **deciso con lui**,
da non riproporre in altre forme:

- **SVG dentro il repository** come formato primario — è testo, quindi
  versiona e si confronta con `git diff`, e si apre in ogni browser
- **più una pagina** con schema e grafici impaginati insieme, da aprire
  da qualsiasi dispositivo
- **niente PDF**: se lo vuole su carta lo stampa dal browser. Detto
  esplicitamente

Contenuto previsto: lo schematico, i grafici delle misure (risposta nelle
due modalità, guadagno d'anello con il margine di fase segnato, PSRR dei
due rail, Z_out in frequenza, il transitorio del relè **affiancato al
controfattuale a −13,68 V**, recupero da sovraccarico), la tabella dei
punti di lavoro e le previsioni dichiarate.

La pagina ha senso **dopo** che ci sono grafici veri da impaginare: viene
dopo le misure, non prima. Il lavoro preliminare che la rende possibile è
L2-L5.

**Nota di scoping dell'utente**: non serve un disegno da 205 componenti.
Servono **il blocco di guadagno** (44 componenti, l'oggetto da giudicare,
usato quattro volte) — che esiste — e un **diagramma a blocchi** del
preamp intero, che è L1.

## Dove siamo

**Fase 2 consegnata, e la pausa è finita.** Il progetto si era fermato —
non per un difetto, ma perché mancava all'ambiente una capacità che serve
a tutti i progetti: produrre qualcosa che un umano possa guardare. Quella
capacità ora esiste ed è verificata (`scripts/check_schematic.py`, blocco
2d di `run_tests.sh`), quindi il lavoro riprende dalla lista dei lotti.

Verificato all'apertura della sessione del piano a lotti, non assunto:
`check_schematic.py` esce 0 con 44 dispositivi nella netlist e 44 nel
disegno; `run_tests.sh` dà 5 passed / 0 failed; `main` è pulito e allineato
a `origin`. **Le tre azioni "da fare" della vecchia sezione in volo (PR →
merge → pull) erano già state fatte**: la PR #8 è dentro `main`.

### Perché c'era stata la pausa

**Non si può rivedere un progetto che nessuno può guardare.** La
simulazione verifica i numeri; non verifica se il percorso del segnale è
corto, dove passa il ritorno di massa, o se una scelta di polarizzazione
convince chi conosce il dominio. Quel giudizio è dell'utente, e richiede
di *vedere* il circuito.

Finora l'ambiente non produceva nulla di guardabile: `generate_schematic()`
non è mai stato chiamato, e comunque darebbe un file illeggibile
(limitazione #5). E **non esiste alcuno strumento che pianifichi
automaticamente uno schematico analogico leggibile** — ricercato e
provato su ASG, lcapy e netlistsvg, vedi limitazione #16.

Non è un problema del preamp: si ripresenta identico con
l'**alimentatore**, il **phono** e il **finale**. Per questo è stato
risolto a livello di ambiente e non dentro `docs/preamp/`.

### Cosa è stato costruito

- `scripts/check_schematic.py` — confronta un disegno con la netlist
  **nelle due direzioni**: niente inventato, niente omesso. Collaudato
  facendolo fallire di proposito su dispositivo inventato, dispositivo
  omesso e pin cablato male.
- `scripts/run_tests.sh` blocco **2d** — scopre da solo ogni manifesto
  sotto `docs/*/schematic/` e lo verifica.
- Convenzione documentata in `../architecture.md`, sezione **"Revisione
  umana dello schematico"**.
- **La revisione umana dello schematico è ora precondizione di G1 e G2**
  (`../../AGENTS.md`).

Due difetti latenti di `run_tests.sh` sono emersi e sono stati corretti:
`ROOT` era cablato, quindi la suite eseguita da una copia isolata testava
**silenziosamente un altro albero**; e il controllo degli artefatti smoke
pretendeva file gitignorati, quindi la suite **non poteva passare su un
clone fresco**.

### Stato precedente

**Fase 2: bozza di topologia consegnata. In attesa della Fase 3.**

Le Fasi 0 e 1 sono chiuse. **Quattordici** decisioni sono in
`decisions/`.

`circuits/preamp/` **esiste ed è la fonte di verità**:

| File | Cosa |
|---|---|
| `gain_block.py` | il blocco di guadagno (ADR-006), 44 componenti |
| `preamp_audio.py` | due canali, quattro blocchi, relè condivisi (205 comp.) |
| `spice_export.py` | esportatore SKiDL -> ngspice |

I banchi di prova stanno in `spice/preamp/tb/` (11 deck) e i modelli
segnaposto in `spice/preamp/placeholder_devices.lib` — **deliberatamente
fuori da `models/`**, che resta a 24/24.

**Tutte le cifre prodotte in Fase 2 sono PREVISIONI da modelli
segnaposto scritti a mano.** Nessuna cifra di distorsione esiste: il
`.four` gira ma il suo risultato è privo di significato. La verifica
indipendente è la Fase 5.

**Esito Fase 1: la topologia regge — le parti esistono.** Il punto debole
non è l'approvvigionamento ma la **provenienza dei modelli SPICE**, cioè
l'opposto di quanto temuto. Vedi
`reports/2026-09-08-fase1-parti-critiche.md`.

**Il finale è stato identificato**: il cj Evolution 250 è un **MV50
riconfigurato in triodo**, 30 W, Zin 100 kΩ confermata dal manuale
ufficiale. La diagnosi di ADR-001 regge su tutto l'intervallo plausibile
di sensibilità. Vedi `reports/2026-09-08-identificazione-cj-ev250.md`.

## Il progetto in una frase

Preamplificatore di linea a **guadagno unitario**, Classe A pura a
componenti discreti senza operazionali, per sostituire un Technics
SU-9070 la cui struttura di guadagno sbagliata (46 dB di attenuazione
richiesta) è stata identificata come causa misurabile della mancanza di
dinamica lamentata.

## Il piano

| Fase | Cosa | Owner | Stato |
|---|---|---|---|
| 0 | Requisiti | orchestratore + utente | **fatto** |
| 1 | Verifica parti critiche (JFET, BJT, modelli SPICE vendor) | `bom-component-manager` | **fatto** |
| 2 | Bozza di topologia in `circuits/preamp/` | `analog-topology-designer` | **fatto** |
| 3 | Giro componenti completo | `bom-component-manager` | da fare |
| 4 | Revisione della topologia alla luce dei componenti | `analog-topology-designer` | da fare |
| 5 | Misure (stabilità per prima) | `measurement-analyst` | da fare |
| 6 | Alimentatore + **sicurezza rete** — parte in parallelo dalla Fase 2 | `psu-engineer` | da fare |
| **G1** | Congelamento topologia | `design-reviewer` | da fare |
| — | Layout → **G2** → fabbricazione → **G3** | | da fare |

**Perché la Fase 1 viene prima della bozza**: se i JFET complementari non
esistono, l'intero stadio d'ingresso cambia forma. Meglio saperlo prima
di disegnare tutto attorno a loro.

**Perché G1 viene dopo il giro componenti**: congela una topologia che
sappiamo costruibile con parti che esistono davvero, non una disegnata
sulla carta.

## Prossimo passo concreto

**L1 — il diagramma a blocchi del preamp intero.** Vedi "Cosa contiene
ciascun lotto" più sopra. È il primo lotto perché restituisce subito un
oggetto guardabile e non dipende da nient'altro.

### Materiale già raccolto per L8-L10 (il giro componenti)

Da non ricercare di nuovo: sono le domande che la Fase 1 non copriva e
che la bozza di Fase 2 ha lasciato aperte.

- **2N5401** (VAS) e **2N5551** (cascode, generatori, moltiplicatore di
  Vbe): parti nuove, non verificate in Fase 1.
- **Modello SPICE LSK489**: procedura obbligatoria di ADR-013 — è L6-L7,
  precede il resto perché la credibilità della distorsione ci poggia
  sopra.
- **THAT320**: stock non ancora fissato, e va confermata la BVceo ≥ 35 V.
- **Omron G6K-2F-Y**: confermare quale contatto è NO e quale NC. Il
  progetto fallisce in sicurezza solo se sono quelli giusti.
- **Simbolo KiCad dell'LSK489** (L10): non esiste. Oggi il duale è
  disegnato come due JFET separati. Serve un simbolo a 2 unità col
  pinout letto dal datasheet **prima del G2**, o il PCB piazzerà due
  package.

La rosa dei componenti di segnale (L9) **non restituisce un vincitore**:
restringe su basi misurabili — assorbimento dielettrico, rumore in
eccesso, coefficiente di tensione — e la scelta finale fra parti tutte
buone è dell'utente, all'ascolto. È la ragione per cui esiste P6.

### Due tensioni fra requisiti, segnalate e non aggirate

1. **E6 × E2 contro E7.** 2,7 V RMS a +10 dB vogliono 8,54 V RMS in
   uscita; con rail a ±15 V il blocco clippa a 9,31 V RMS simulati.
   Margine 0,75 dB. Il rimedio è il trim di ADR-011 (−6 dB sull'ingresso
   del K11), che con ADR-015 **non è più opzionale**.
2. **E4 contro E8 a 20 Hz.** Con accoppiamento capacitivo la |Zout| al
   jack a 20 Hz è ~1,7 kΩ (è la reattanza del 4,7 µF). A 1 kHz è
   58,8 Ω. E4 letta alla lettera non è soddisfacibile a 20 Hz da nessun
   circuito con condensatore d'uscita.

## Domande aperte

| Cosa | Chi risponde | Blocca? |
|---|---|---|
| Condensatore verso il Singxer: 2,2 o 4,7 µF | utente | No |
| Trascrizione del modello LSK489 da PDF | Fase 2 | No, ma **la credibilità della distorsione ci poggia sopra** |
| Impedenza d'ingresso Singxer SA-1 V2 | — | **Non pubblicata**, verificato sul manuale ufficiale |
| Valore del cap d'uscita del phono a valvole | utente | **Rinviata** — non ha accesso agli schematici né può aprire agevolmente il telaio |
| ~~Quale JFET d'ingresso~~ | — | **CHIUSA**: LSK489 (ADR-013) |
| ~~Conferma specifiche cj EV250~~ | — | **CHIUSA**: email costruttore + manuale MV50 |

## Decisioni chiuse il 2026-09-08

| Cosa | Esito |
|---|---|
| Rail ±15 V o ±18 V | **±15 V** — ADR-015. Il trim di ADR-011 in modalità +10 dB **non è più opzionale** |
| Condensatore verso il Singxer | **4,7 µF su tutte e tre le uscite** — ADR-007 addendum. Chiude la domanda sull'impedenza ignota del Singxer |
| Resistenze di isolamento ADR-008 | **47 Ω** invece di ~100 Ω — soddisfa E4 con margine |

Nessuna decisione dell'utente è pendente.

## Attenzione per chi riprende

`REQUIREMENTS.md` contiene ora una sezione **Requisiti di verifica**
(V1–V5). Non è burocrazia: il relè del guadagno commuta la rete di
controreazione, quindi **il margine di fase è diverso nelle due
modalità**, e l'impedenza dell'attenuatore varia con la manopola, quindi
**varia anche con la posizione del volume**. Se non si verifica tutta la
matrice, si verifica solo il caso in cui il circuito passa.

## Come è organizzata la documentazione

Tre cicli di vita, tenuti separati di proposito:

- **Vivi** — `STATE.md`, `REQUIREMENTS.md`. Riscritti, sempre veri al
  presente.
- **Immutabili** — `decisions/ADR-*.md`, i verdetti dei gate. Scritti una
  volta, mai corretti, solo superati da documenti nuovi.
- **Datati** — `reports/`. Output di un'esecuzione. Una misura è vera di
  una versione specifica del circuito: senza data è inutile.

I report di fase sono **cronaca**, non il posto dove si cerca il
"perché". Il perché sta nelle ADR.

## Da leggere per riprendere

1. Questo file.
2. `REQUIREMENTS.md` — cosa deve fare.
3. `reports/2026-09-08-analisi-catena.md` — la base di evidenza: i
   numeri della catena dell'utente e perché il progetto esiste.
   Poi `2026-09-08-identificazione-cj-ev250.md` (il finale è un MV50 in
   triodo) e `2026-09-08-fase1-parti-critiche.md` (cosa esiste davvero).
4. `decisions/README.md` e le ADR — perché il circuito è così.
5. `../../CLAUDE.md` — l'ambiente EDA, se non lo conosci.
