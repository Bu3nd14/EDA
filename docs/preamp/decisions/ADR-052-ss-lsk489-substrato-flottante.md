# ADR-052 — I pin SS dell'LSK489 restano flottanti; se mai collegati, sopra i gate e mai al negativo

Data: 2026-09-26 · Stato: accettata

## Contesto

Il datasheet congelato dell'LSK489 (`vendor/jfet/linear_systems/LSK489/LSK489DSRevA38.pdf`,
contenuto Rev A40, pag. 1, «SOIC-A Top View») assegna i pin **3 e 7** a «SS», ma nessuna riga
dice cosa siano. L'unica definizione trovata in L10, «SS: SUBSTRATE, LEAVE THESE PINS FLOATING
(N/C)», è stampata per l'**LSK389**. È **NC-027** (minore, precondizione di G2): il layout deve
sapere cosa fare di ogni pin. `circuits/preamp/gain_block.py` li lascia scollegati da L10.

La fonte per *questa* parte l'ha trovata l'utente il 2026-09-22 (verificata in L29b2):
Bob Cordell, *LSK489 Application Note*, Rev A2, dal sito del costruttore. L28 l'ha scaricata e
congelata: `vendor/jfet/linear_systems/LSK489/4be30b_49c5a96bc52f4868a7bf2a5c17150351.pdf`,
SHA-256 `84f21b11…149f1d8f`, uguale a quello registrato prima del download
(`PROVENANCE-L28-addendum.json`).

## Decisione

1. **I pin 3 e 7 (SS) dell'LSK489 restano flottanti**, come oggi: nessuna modifica al circuito.
2. **Se un giorno vengono collegati**, è solo a una tensione continua fissa **uguale o superiore
   alla massima tensione che i gate G1 e G2 raggiungono**, segnale compreso. **Mai al negativo**
   e mai a un nodo che possa scendere sotto uno dei gate.
3. Il simbolo resta com'è: pin SS **`passive`**, non `no_connect`.

## Perché

**La nota del costruttore definisce SS per l'LSK489** (pag. 6, «The Common Substrate», e la
Figura 2 a pag. 7):
- «the substrate is shared between the two integrated JFET devices»;
- «The two gates are isolated from the common substrate through reverse-biased substrate
  diodes […] The anodes of these diodes are connected to the gates while the cathodes are
  connected to the common substrate»;
- «The substrate is not normally accessible, and it harmlessly floats as a result»;
- «the 8-pin SOIC package brings out the substrate for possible connection by the user»;
- «In some applications it may be useful to connect the substrate to a fixed DC voltage».

Da qui i due punti:
- **flottante è l'uso normale**: è lo stato delle versioni a 6 pin, dove il substrato non è
  nemmeno accessibile, ed è l'istruzione scritta per l'LSK389, che dichiara la stessa
  piedinatura. Le due fonti ora concordano;
- **la direzione del collegamento viene dalla polarità dei diodi**: anodo sul gate, catodo sul
  substrato. Sono in inversa solo finché V(SS) ≥ V(G). Un substrato al rail negativo, o sotto un
  gate, porta in diretta la giunzione gate-substrato: il gate si aggancia al negativo attraverso
  un diodo, l'ingresso perde l'alta impedenza, e i due gate si accoppiano fra loro.

Un collegamento a una tensione fissa sopra i gate avrebbe senso solo per quello che la nota
elenca (diafonia debolissima fra i gate attraverso il substrato flottante, capacità
gate-substrato che dipende dall'inversa). Oggi nessun requisito lo chiede: la diafonia fra G1
(ingresso) e G2 (retroazione) della stessa coppia differenziale non è una diafonia fra canali.

**Il simbolo.** `no_connect` affermerebbe che il pin *non deve* essere collegato; la nota dice
il contrario («for possible connection by the user»), e l'ERC protesterebbe se il layout un
giorno lo collegasse come permette il punto 2. `passive` non afferma niente di falso.

## Alternative scartate

- **SS al rail negativo, o ai pin 1 e 8.** Un testo prodotto da un altro modello lo proponeva:
  è sbagliato due volte. Al negativo, i diodi gate-substrato vanno in diretta (vedi sopra); e i
  pin 1 e 8 del SOIC sono **S1** e **G2**, non il substrato.
- **Applicare l'istruzione dell'LSK389 in forza della compatibilità dichiarata**: era la
  seconda strada di NC-027 prima che ci fosse la fonte. Superata: la definizione per l'LSK489
  ora esiste, e l'istruzione LSK389 le è coerente.
- **SS a massa.** I gate del blocco di guadagno stanno intorno a 0 V e oscillano col segnale in
  entrambe le direzioni: a massa, un gate in escursione positiva porterebbe in diretta il suo
  diodo. Stessa ragione del negativo, in piccolo.
- **Bootstrap del substrato col segnale** (la nota lo cita come possibilità): aggiunge un
  circuito per un effetto che nessun requisito chiede.

## Da riaprire se

- una revisione del datasheet o della nota dell'LSK489 dice altro sul substrato;
- una misura sul prototipo mostra diafonia o distorsione attribuibili alla capacità
  gate-substrato;
- al layout (G2) c'è una ragione concreta per portare il substrato a un potenziale (per esempio
  una guardia o uno schermo): allora vale il punto 2, con la tensione scritta e verificata contro
  la massima escursione dei gate.
