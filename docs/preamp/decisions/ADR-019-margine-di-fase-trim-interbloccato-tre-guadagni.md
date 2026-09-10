# ADR-019 — Margine di fase minimo 60°, trim interbloccato col mute, tre livelli di guadagno

Data: 2026-09-10 · Stato: accettata

## Contesto

Il 2026-09-10, chiuso il lotto L22+L23, l'utente ha posto **tre requisiti
nuovi**. Non sono correzioni di ciò che il progetto aveva sbagliato: sono
decisioni di prodotto che mancavano, e due delle tre rendono **non conforme**
la topologia attuale.

Questa ADR le registra e ne ricava le conseguenze. Non le discute: la
discussione è avvenuta, e le tre risposte alle domande di chiarimento sono
riportate qui perché sono la parte che decide.

## Decisione

### 1. Il margine di fase minimo del progetto è **60°**, su ogni combinazione della matrice V1

Compreso il **blocco A col carico canonico** e compreso il **caso peggiore
capacitivo** da 4,7 nF. È la lettura più severa fra quelle proposte, ed è
stata scelta esplicitamente.

Diventa la soglia di accettazione che **V1** non aveva. Chiude **NC-012**.

### 2. Il trim d'ingresso funziona solo a mute inserito, con interlock **elettrico**

Il comando del trim raggiunge i propri relè **solo se il mute è attivo**.
Fuori mute, agire sul selettore del trim non cambia nulla; il valore
impostato resta applicato quando si esce dal mute.

Sono quindi **due comandi distinti** — uno per il mute, uno per il trim — e
il primo abilita il secondo. Non è una convenzione d'uso: è un
interblocco realizzato sulla scheda, quindi **verificabile**.

### 3. I livelli di guadagno sono **tre**: 0 dB, +3 dB, +10 dB

E **a relè diseccitati il guadagno resta 0 dB**. Nessun guasto di bobina, e
nessuno stato di accensione, può portare il sistema a un guadagno più alto di
quello minimo. Il valore esatto del gradino intermedio e il numero di relè
escono dal dimensionamento.

## Perché, e cosa costa

### Sul margine di fase: la soglia rende decidibile ciò che non lo era, e il verdetto è negativo

**NC-012** diceva testualmente che «la convenzione di progetto è 60°, ma una
convenzione non scritta non è un requisito», e che senza soglia «nessuna
misura di margine di fase può passare o fallire». Ora la soglia c'è.

Diceva anche una seconda cosa, ed è la ragione per cui la domanda è stata
posta invece di assumere: **una soglia senza il carico a cui si riferisce non
è un requisito migliore**. La risposta è «ovunque», e con essa il progetto
oggi **non è conforme in due punti misurati**:

| Configurazione | Margine misurato | Contro 60° |
|---|---|---|
| Blocco B, 0 dB, a vuoto | 63,02° | conforme |
| Blocco B, +10 dB, a vuoto | 86,09° | conforme |
| **Blocco B, 0 dB, 4,7 nF di cavo** | **56,46°** | **NON conforme**, −3,5° |
| **Blocco A, carico canonico, 4,7 nF** | **41,98°** | **NON conforme**, −18° |

I due numeri esistono già nel repo: il primo è stato rimisurato in L22, il
secondo è l'evidenza di **NC-002**, che smette di essere una voce
«indecidibile» e diventa una non conformità di merito.

**Cosa costerà**, dichiarato e non nascosto: 18° di margine sul blocco A non
si recuperano con un ritocco. Le strade sono più compensazione (il Miller da
470 pF, che però costa banda e slew rate), meno guadagno d'anello (che costa
distorsione, ed è metà della ragione per cui ADR-003 ha scelto i discreti),
o una rete di isolamento all'uscita diversa dai 47 Ω attuali. È una scelta di
progetto, non un aggiustamento, e va fatta coi numeri.

Vale la pena essere onesti su un punto: **41,98° non è un circuito instabile**.
La soglia a 60° è un margine di progetto — copre la dispersione dei
componenti, la capacità di cavi che nessuno ha misurato e i modelli che
ancora non sono tutti veri. È esattamente il genere di margine che esiste per
non dover indovinare.

### Sul trim: l'interlock elettrico è la sola forma verificabile

Delle tre forme proposte, due erano più economiche. L'interlock **elettrico**
è stato scelto perché è l'unico che un banco può provare: si applica il
comando del trim a mute rilasciato e si verifica che **non succeda nulla**.
Un vincolo di pannello non è falsificabile e un mute automatico all'atto della
regolazione avrebbe richiesto logica di temporizzazione, che **ADR-009**
(nessun microcontrollore) rende sgradevole da fare bene.

Conseguenza sulla topologia: il trim di **ADR-011** non è più un attenuatore
passivo qualsiasi. I suoi relè prendono l'alimentazione della bobina
attraverso il contatto del mute — cioè il mute diventa il **permissivo** del
trim. Chi disegna quella parte deve tenere presente **ADR-012**: i relè di
mute sono a riposo in mute, quindi il permissivo si prende dal contatto
giusto, e questo è precisamente il tipo di dettaglio su cui **NC-014** è già
nata una volta (polo 2 del relè invertito nel codice).

### Sui tre livelli: il principio di sicurezza si conserva, il costo è la matrice

Il gradino a +3 dB serve perché il salto 0 → +10 dB è grosso: fra una sorgente
già calda e una debole, dieci decibel sono più di quanto serva, e obbligano a
compensare col volume ogni volta che si cambia ingresso.

**Il principio di ADR-004 non cambia e non deve cambiare**: il relè commuta
R_g verso massa, mai R_f, quindi l'anello di controreazione **non passa per il
relè** e non si apre mai — a contatti aperti, bloccati, sporchi o rimbalzanti
il guadagno è 1. Con due rami commutati verso massa il principio si conserva
per costruzione, e la scelta «riposo = 0 dB» lo rende esplicito: entrambi i
rami aperti = guadagno minimo.

**Cosa costa, ed è la parte che nessuno vede finché non la incontra:**

- **la matrice V1 cresce di una riga.** Oggi enumera «blocco A · B a 0 dB · B
  a +10 dB»; diventano quattro configurazioni, per ogni posizione
  dell'attenuatore, per ogni carico, per ogni sorgente;
- **i dodici deck spazzano due modalità.** Ogni `foreach` che oggi fa
  `0db / 10db` ne vuole tre, e i nomi dei file dati cambiano di conseguenza —
  con la trappola di `limitations.md` #10 sui `$var` nei nomi `wrdata` che
  aspetta chiunque li tocchi;
- **servono più relè o relè con più poli**, quindi cambia il budget di
  corrente delle bobine che il progetto consegnerà a `psu-engineer`, e cambia
  il pannello;
- **il diagramma a blocchi** dichiara «+10 dB» calcolandolo da R_f/R_g e
  asserendolo contro la finestra di E2: `scripts/check_schematic.py` e
  l'asserzione del disegno vanno estesi, non aggirati;
- **tutte le cifre pubblicate a «+10 dB» restano valide** — quel livello non
  cambia — ma nessuna copre il livello nuovo.

## Cosa questa ADR supera, e cosa no

**Supera E2 e F5** nella loro forma a due livelli, e **estende V1** con la
soglia che non aveva. I requisiti sono aggiornati in `REQUIREMENTS.md`.

**Non supera ADR-004**: il suo principio — il relè commuta R_g, mai R_f — è
ciò che rende sicura anche la versione a tre livelli, e viene esteso, non
sostituito. Se il dimensionamento dovesse richiedere di violarlo, non è questa
ADR a decidere: serve una ADR nuova che ne prenda il posto.

**Non supera ADR-011** (trim per ingresso): ne aggiunge una condizione di
comando. Il dimensionamento del trim — l'attenuazione richiesta e il vincolo
Zin ≥ 100 kΩ — resta quello, ed è il lotto **L16**.

**Non riapre ADR-012** (relè di mute): il mute resta quello che è. Ma il suo
contatto acquista una seconda funzione, e questo va scritto dove qualcuno lo
leggerà prima di disegnare il PCB.

**Non decide come si recuperano i 18° del blocco A.** Registra che vanno
recuperati.

## Da riaprire se

- **Il dimensionamento mostra che 60° ovunque non è raggiungibile** senza
  sacrificare un altro requisito — banda, distorsione o impedenza d'uscita. In
  quel caso la scelta fra abbassare la soglia per una configurazione
  specifica e accettare il costo è dell'utente, non del progetto, e va presa
  con i numeri di entrambe le strade sul tavolo.
- **Il valore del gradino intermedio** risulta scomodo da realizzare con due
  valori E96 entro una tolleranza sensata: allora si decide se spostarlo o se
  accettarne lo scarto, con una ADR sua — come fu per il +9,96 dB che E2
  chiama «+10 dB».
- **Il permissivo del trim** risulta incompatibile col cablaggio dei relè di
  mute deciso in ADR-012: allora è il cablaggio a essere sbagliato, non
  l'interlock, e va corretto lì.
