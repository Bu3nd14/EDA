# ADR-101 — L'ingresso del blocco A protetto da 1 kΩ e un limitatore a ±5,6 V; nel manuale, i cavi d'ingresso col mute inserito

Data: 2026-10-25 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Rimedio di NC-059** (maggiore, prima di G1, «Remedy in circuit, major», decisione dell'utente in L53).
  Si chiude in **L57b** col rimedio nel sorgente e la regressione.
- Non cambia il selettore di ADR-064 (C_IN 1 µF, R_SEL 470 kΩ, R_J 10 MΩ): la protezione sta fra il
  contatto del relè del selettore e l'ingresso del blocco A, dopo C_IN.
- Non cambia il blocco di guadagno (ADR-006, una sola topologia): la protezione è del canale, davanti
  al blocco A, come R_SEL. Le uscite fisse e il blocco B non hanno ingressi dall'esterno.
- La catena a valle è quella generica: l'RCA a caldo non è un guasto della scheda audio, ADR-081 non vale.
- Il tetto di riferimento è quello di PR-23, 0,87 V al jack (~112,2 dB SPL a 1 m), con la catena di
  NC-028, come in L53.

## Contesto

L57a (`data/2026-10-25/L57a/`, README; report `reports/2026-10-25-L57a-rca-a-caldo.md`). Il banco di L53,
provato sul suo caso noto (88 celle su 88), sul circuito di oggi. Una sorgente in classe II ha la massa a
metà rete attraverso i condensatori Y (1 nF tipico, 3,46 nF al limite di 0,25 mA della norma); se il polo
caldo dell'RCA tocca prima dello schermo, l'ingresso del blocco A vede il 50 Hz a decine di volt.

Senza rimedio, col caso peggiore (3,46 nF):

- **la coppia d'ingresso** (LSK489, datasheet p. 2): gate-gate **23,8 / 28,0 / 32,2 V** a rete −10 / 0 /
  +10 %, contro una rottura di ±30 V minima, **oltre a rete +10 %**; gate-drain fino a −55,6 V contro 60 V
  (L53 non lo misurava). I 29–39 mA nel gate sono capacitivi, < 1 µs, al contatto della massa (forma
  d'onda, `rca/forma/forma.txt`): la giunzione gate-drain non va mai in avanti;
- **al jack principale** (dB SPL di picco a 1 m): alla posizione d'ascolto del K11 107,1 a 0 dB e il clip
  del finale (~113,8) a +10 dB; col volume in cima il clip. **Le fisse** +11,1 dB sopra il picco del K11 a
  piena scala.

## Decisione

Parole dell'utente (2026-10-25), alle due domande coi numeri:

1. **«Limitatore ±5,6 V»**: per canale, fra il contatto del selettore e l'ingresso del blocco A, una
   resistenza da **1 kΩ** in serie e due diodi verso due riferimenti a **±5 V** (la soglia ~±5,6 V); i
   riferimenti sono comuni ai due canali. Le parti (i diodi, a bassa dispersione e bassa capacità; i
   riferimenti, a shunt perché devono assorbire la corrente dei diodi) si scelgono in L57b.
2. **«Sì, mute prima»**: un avviso nel manuale d'uso. Il testo, finché non c'è un manuale:

   > Inserire o togliere un cavo d'ingresso col mute inserito. Una sorgente con la spina a due poli
   > (classe II) può portare, nell'istante in cui il polo centrale tocca prima della massa, un colpo
   > fino al clip del finale col volume alto; col mute inserito il colpo resta sotto il livello di
   > non-danno.

## Perché

Le cifre al caso peggiore delle tre reti e della sorgente in classe II (`sintesi.csv`), con 1N4148 come
modello dei diodi e sorgenti ideali come riferimenti (dichiarato):

- **La parte torna nei limiti con margine**: gate-gate **4,3 V** su 30, gate-drain 14,7 V su 60, la
  corrente di gate 0,17 mA (IG(F) 10 mA), i diodi ≤ 1,1 mA. Le tre reti danno la stessa cifra: la soglia
  non dipende dalla rete.
- **Il jack alla posizione d'ascolto sta sotto il tetto in entrambi i modi**: **99,8 dB SPL a 0 dB e
  109,8 a +10 dB**, contro 112,2. È l'unica delle strade misurate che lo fa: i diodi verso i rail e la
  variante di Elliott Sound Products (AN-015, diodi e zener da 12 V) lasciano il clip a +10 dB.
- **Le fisse** passano da +11,1 a **+3,4 dB** sopra il picco del K11 a piena scala: la catena a valle
  generica (un amplificatore per cuffie elettrostatiche, un DAC) vede 5,5 V invece di 13,4 V di 50 Hz.
- **Il costo al segnale sta dentro** (banco del costo, sorgente 2,5 kΩ di V4, la fissa col carico di V4):
  THD a 20 kHz **0,000764 %** a 0,2 V RMS (tetto 0,001 %, senza protezione 0,000686 %), **0,00765 %** a
  2 V RMS (tetto 0,01 %); h5+ ≤ −145 dB dove V4 lo chiede; E5 stimato per eccesso **4,92 µV** (tetto
  9,95; il rumore aggiunto è il termico di 1 kΩ, 0,574 µV, portato al jack col guadagno peggiore). A
  pieno livello d'ingresso (E6, 2,7 V RMS a 20 kHz), dove V4 non ha un tetto, le armoniche dalla 5ª in
  su sono −137,6 dB contro −142,2 coi diodi verso i rail: il limitatore è a 1,8 V dal picco del segnale.
- **La resistenza**: 1 kΩ è il minimo di AN-015 («almeno 1k, meglio 1,5k»). Più grande costa
  distorsione: da 4,7 kΩ si esce da V4 (0,00105 %), per il meccanismo di NC-055 (più impedenza davanti al
  JFET). Fra 1 e 2,2 kΩ la protezione della parte cambia poco (4,3 → 3,3 V).
- **L'avviso**: col volume in cima nessuna protezione dell'ingresso evita il clip, perché lì lo fa già la
  musica a pieno livello (3,82 V di picco contro 0,87 V di tetto a 0 dB). Col mute inserito durante il
  gesto il jack principale resta a **77,0 / 82,5 dB SPL** alla posizione d'ascolto (0 / +10 dB) e a
  **105,3** in cima, sotto il tetto. È una procedura, non una protezione: dichiarato.

## Alternative scartate

- **Diodi verso i rail, 1 kΩ** (tre parti per canale): la parte dentro (gate-gate 8,1 V), ma il clip a
  +10 dB alla posizione d'ascolto e le fisse a +11,1 dB. AN-015 la chiama protezione «finta» contro i
  guasti energetici (i rail gonfiati da una sorgente che dà corrente); qui la sorgente dà ≤ 0,25 mA, ma
  il jack resta sopra il tetto.
- **Diodi e zener da 12 V (AN-015), 1 o 1,5 kΩ**: misurata su richiesta dell'utente. Come i rail: la
  parte dentro (7,3–7,9 V), il clip a +10 dB alla posizione d'ascolto, le fisse +10,3 dB.
- **Resistenza 2,2 kΩ**: più margine sulla parte, ma più distorsione (0,000857 %) e rumore (5,31 µV) per
  un jack che non cambia.
- **Sola resistenza in serie**: toglie il picco di corrente nel gate, non la tensione: gate-gate 28,0 V.
- **Solo l'avviso, o solo il mute**: la parte resta oltre il limite a rete +10 % (32,2 V) — contro la
  decisione di L53, rimedio nel circuito.
- **Un mute automatico** (un rivelatore del sovraccarico che apra i relè): una parte nuova del progetto,
  che dovrebbe agire entro pochi ms; non progettata né misurata. Non proposta.

## Da riaprire se

- la scelta della parte in L57b dà diodi o riferimenti con cui la THD a 20 kHz a 0,2 V RMS supera
  0,0009 % (il 90 % del tetto) o la regressione esce da V4, V1 o E5;
- il livello d'ingresso di E6 sale oltre ~3,5 V RMS (il limitatore a meno di 0,7 V dal picco);
- una sorgente reale o una misura sul prototipo porta più corrente di contatto di 0,25 mA (classe I
  guasta, una sorgente con condensatori Y più grandi), e i diodi o i riferimenti escono dai loro limiti;
- un manuale d'uso viene scritto senza l'avviso del punto 2.
