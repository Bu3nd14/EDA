# ADR-063 — Con la musica, il residuo a mute inserito è la musica che passa davvero; il contatto in serie del banco V2 ha il fronte di 4,55 µs

Data: 2026-10-05 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Precisa ADR-032** (il metodo di V2) sul solo residuo B con la musica. A, il filtro, i nodi,
  i carichi e le soglie restano.
- **Precisa ADR-062**: la coda del filtro dopo il taglio va col clic, dichiarata senza soglia.
- Non tocca il circuito né il PRB.

## Contesto

In L47c2b1 la matrice V2 col mute che taglia (ADR-062) ha dato due problemi, trovati sulle corse
e non sui testi (`data/2026-10-05/L47c2b1/sonda/`):

1. **Il banco si fermava.** 34 corse su 145, tutte quelle con la musica dove il contatto in serie
   al jack si muove, finivano su «Timestep too small». Si fermavano ogni volta che l'interruttore
   ideale del banco (100 mΩ ↔ 1 TΩ, commutazione in tempo zero) si **chiudeva con volt di musica
   ai suoi capi**: il rimbalzo dell'apertura, 400 µs dopo, col lato del condensatore a −12,02 V e
   il jack a −3 µV; la chiusura del rilascio. `trtol=1`, `rshunt=1e12`, `gear` e un cavo da
   100 pF non bastano. Con le fotoresistenze non succedeva: il contatto si muoveva a musica già
   attenuata di ~70 dB.
2. **Il residuo con la musica misurava il taglio.** B2 (ADR-032: il jack filtrato 20 Hz–20 kHz,
   picco da t_ins + t_grad + 20 ms) sulla principale a 20 Hz valeva **0,732 V** (~111 dB SPL a
   1 m). Lo stesso metodo su un taglio ideale allo stesso istante ne dava 0,698. Il jack grezzo,
   nella stessa finestra, era a **4,3 µV** (~6 dB SPL); il riferimento sempre in mute a 0,45 nV.
   Il passa-alto, partito da t = 0, porta nella finestra la coda del taglio. NC-053 era lo stesso
   meccanismo, con la cella al posto del taglio.

## Decisione

Le risposte dell'utente (2026-10-05, domande per nome e in dB SPL):

1. **«Musica che passa davvero».** Con la musica, il residuo a mute inserito si giudica (≤ 100 µV,
   ~33 dB SPL) su due letture:
   - **B2g**, il jack **grezzo**, senza filtro, nella finestra di B2;
   - **B1**, il riferimento **sempre in mute** della stessa riga, filtrato, da 0,5 s.

   B2 filtrato con la musica è la coda del taglio, e si **dichiara col clic**, accanto al taglio
   ideale. Senza segnale B2 resta il verdetto, com'era.
2. **«Tutta la matrice».** Nel banco V2 il contatto in serie al jack è il contatto
   comportamentale del blocco CANALE (`BSERx`): conduttanza `pow(10, -12 + 13·(1 − SSER))`, con
   SSER dai rimbalzi di L29c filtrati da 1 kΩ + 4,55 nF, cioè un fronte di ~4,55 µs. Lo stesso
   banco per tutte le corse; l'interruttore nativo `SKSx` resta aperto. La derivazione lato
   condensatore resta l'interruttore nativo.

## Perché

- **B2g e B1 misurano quello che V2 chiede**: «la musica che arriva al jack a mute inserito».
  A mute inserito il jack sta a massa attraverso il suo bleed, quindi la continua non sporca la
  lettura grezza. Il controllo nuovo di `v2_metodo.py` (T15) lo prova su un taglio ideale da 12 V
  a 20 Hz: filtrato 0,803 V, grezzo 0; il sabotaggio `b_grezzo_filtrato` lo fa cadere.
- **Lasciare B2 filtrato come verdetto** avrebbe fatto fallire V2 con la musica su ogni taglio, per
  costruzione, contro PR-21 firmata («il mute taglia»).
- **Il fronte di 4,55 µs è del banco, non un'invenzione**: è il contatto che il blocco CANALE usa
  per il jack da L29a. Il datasheet del G6K non dà la durata del fronte (REQUIREMENTS, V2: «fronte
  e rimbalzi modellati e dichiarati»). Sulle stesse corse della sonda, rispetto all'interruttore
  ideale con l'apertura netta: C2 all'inserimento 9,015 contro 8,939 V (+0,8 %, il rimbalzo che
  l'apertura netta non ha), al rilascio 0,4723 contro 0,4728 V, B2 0,732 contro 0,700 V; senza
  segnale tutto al pavimento numerico (~10⁻¹¹ V) in tutti e due.
- **I rimbalzi del contatto in serie** seguono la sequenza del blocco: all'apertura quella che
  L29c usa per la chiusura, al rilascio quella dell'apertura. Dichiarato: è il modello del blocco,
  non una misura.

## Alternative scartate

- **La differenza fra il circuito e il taglio ideale** come verdetto del residuo: proposta, non
  scelta. Più lavoro sul metodo, e dice quanto aggiunge il circuito, che sta già nella tabella del
  clic.
- **Lasciare il metodo com'è**: V2 fallisce per costruzione con la musica.
- **Le opzioni di convergenza** (`trtol=1`, `rshunt=1e12`, `method=gear`) e **il cavo da 100 pF**:
  provati, non bastano.
- **Il contatto comportamentale solo sulle 34 corse fermate**: due banchi nella stessa matrice.
- **L'apertura del contatto in serie senza rimbalzo**: fa passare l'inserimento, non il rilascio,
  che chiude per forza sulla musica.

## Da riaprire se

- la misura sul prototipo dà un fronte del G6K molto diverso da qualche µs;
- un banco futuro mette il jack a una tensione diversa da zero a mute inserito (la lettura grezza
  conterebbe la continua);
- l'utente vuole un tetto al clic (ADR-062), e la coda del filtro va riletta come parte di quel
  tetto.
