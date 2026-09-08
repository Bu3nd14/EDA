# Prompt per la sessione successiva

Copia il blocco qui sotto in una sessione nuova aperta su
`/Users/roberto/EDA`. È scritto per essere autosufficiente: non presuppone
nulla della conversazione precedente.

Cancella questo file quando le fasi che descrive sono chiuse.

---

```
Riprendo il progetto del preamplificatore hi-fi in questo repository.

Leggi PRIMA, in quest'ordine, e non saltare:
  1. CLAUDE.md — orientamento all'ambiente, percorsi assoluti, trappole
     che falliscono in silenzio, e la regola di fine sessione
  2. docs/preamp/STATE.md — dove siamo, cosa è aperto, prossimo passo
  3. docs/preamp/REQUIREMENTS.md — requisiti congelati, inclusa la
     sezione "Requisiti di verifica" V1-V5
  4. docs/preamp/decisions/ — le ADR. Sono la ragione per cui il
     circuito è così. Non ridiscuterle: se ne trovi una tecnicamente
     sbagliata dillo esplicitamente, ma non aggirarla in silenzio
  5. docs/limitations.md — obbligatorio prima di scrivere codice

Contesto in due righe: preamplificatore di linea a guadagno unitario,
Classe A pura a discreti senza operazionali, per sostituire un Technics
SU-9070 la cui struttura di guadagno sbagliata (46 dB di attenuazione
richiesta) è la causa misurabile della mancanza di dinamica lamentata.
La Fase 2 ha consegnato il primo circuito canonico in circuits/preamp/.

Come lavoriamo, per non ripartire col piede sbagliato:

- Definisco i requisiti CONVERSANDO. Non aprire con un questionario a
  scelta multipla: raccontami cosa hai trovato e i vincoli reali, poi
  parliamo.
- Verifica invece di fidarti. Se un subagente riporta dei numeri,
  rieseguili tu prima di riferirmeli. È già servito.
- Niente cifre non eseguite. Una simulazione descritta e non lanciata
  non è evidenza.
- Ti avviso intorno all'80% del cap token. A quel punto: git push PER
  PRIMO (verifica con `git log --oneline origin/<branch>..HEAD`, non
  assumere), poi aggiorna STATE.md, poi il resto.
- Lavora in un worktree, e ricordati che i commit non pushati dentro
  .claude/worktrees/ spariscono col worktree.

I prossimi passi previsti dal piano:

  FASE 3 — giro componenti completo (bom-component-manager)
    Condensatori di segnale, resistenze dell'attenuatore e del feedback,
    generatori di corrente. Restituisce una ROSA per ogni posizione con
    i dati misurabili a confronto e la disponibilità reale verificata,
    non un vincitore. Parti nuove da coprire: 2N5401, 2N5551, stock
    THAT320 con conferma BV_ceo >= 35 V, e quale contatto del G6K-2F-Y
    e' NO e quale NC.
    Nota importante: nessun agente puo' dirmi quale componente "suona
    meglio" - quella e' una regola di AGENTS.md. Puo' restringere il
    campo su basi misurabili (assorbimento dielettrico, rumore in
    eccesso, coefficiente di tensione); la scelta finale fra parti tutte
    buone e' mia, all'ascolto. Il requisito P6 esiste per questo: i
    componenti di segnale devono essere sostituibili senza dissaldatore.

  IMPORTAZIONE MODELLI SPICE — precondizione di tutto il resto
    Il repository non ha NESSUN modello vendor reale: sono fixture
    generiche, e il macro-modello di operazionale dichiara di non avere
    clipping ne' slew rate. Finche' non ci sono modelli veri, ogni cifra
    di distorsione e' priva di significato - ed e' l'intera ragione per
    cui siamo andati a discreti.
    Il modello LSK489 va importato con la procedura obbligatoria di
    ADR-013: PDF congelato in vendor/ con sha256, trascrizione a mano in
    models/jfet/, provenance che dichiari esplicitamente la trascrizione
    manuale, e controllo incrociato di I_DSS e V_P contro il datasheet
    con scripts/validate_models.py. Il quarto passo e' cio' che rende
    accettabile il secondo.

  FASE 4 — revisione della topologia alla luce dei componenti
    (analog-topology-designer). Puo' iterare piu' di una volta: e'
    normale, ed e' il senso del giro.

  FASE 5 — misure (measurement-analyst)
    La STABILITA' e' la voce di testa, non la distorsione. Il relè del
    guadagno commuta la rete di controreazione, quindi il margine di
    fase e' DIVERSO nelle due modalita'; e l'impedenza dell'attenuatore
    varia con la manopola, quindi varia anche con la posizione del
    volume. La matrice completa e' in REQUIREMENTS.md, V1-V3. Il modo
    peggiore risulta 0 dB, cioe' quello normale.

  FASE 6 — alimentatore (psu-engineer), in parallelo
    +-15 V, 105/110 mA, 3,22 W. V+ e' il rail debole per il PSRR di ~30
    dB ed e' strutturale. Requisito: <= 1 mV picco di ripple a 100 Hz su
    V+ e <= 30 uV di rumore sopra 10 kHz.
    ATTENZIONE: telaio unico, quindi la rete elettrica entra
    nell'apparecchio. L'analisi di sicurezza parte SUBITO, in parallelo
    alla progettazione, non alla fine: al gate G3 la sua assenza e' un
    BLOCK automatico. E il trasformatore finisce vicino a un nodo da 100
    kOhm in un mobile chiuso: il ronzio e' il rischio numero uno.

  G1 — congelamento topologia (design-reviewer)
    Arriva DOPO il giro componenti, non prima: congela una topologia che
    sappiamo costruibile con parti che esistono. Precondizione: uno
    schematico rivedibile da un umano che passi scripts/run_tests.sh.

C'e' anche un lavoro sospeso che mi interessa: il DOSSIER da guardare.
Formato gia' deciso, non riproporre alternative - SVG nel repository
come formato primario (e' testo, quindi versiona e si confronta con git
diff) piu' una pagina da aprire da qualsiasi dispositivo. Niente PDF: lo
stampo dal browser.
Contenuto: lo schematico, i grafici delle misure (risposta nelle due
modalita', guadagno d'anello col margine di fase segnato, PSRR dei due
rail, Z_out in frequenza, il transitorio del rele' affiancato al
controfattuale a -13,68 V, recupero da sovraccarico), la tabella dei
punti di lavoro e le previsioni dichiarate.
Lavoro preliminare: solo 3 testbench su 12 scrivono file dati. Agli
altri nove va aggiunta una riga wrdata dentro il blocco .control gia'
esistente, dopo l'analisi. Non tocca circuito ne' risultati, e serve
comunque a design-reviewer per rieseguire le misure a G1.

Manca anche un diagramma a blocchi del preamp intero: quello del blocco
di guadagno esiste, la vista d'insieme no.

Comincia dicendomi cosa hai trovato leggendo, e da cosa proporresti di
partire.
```
