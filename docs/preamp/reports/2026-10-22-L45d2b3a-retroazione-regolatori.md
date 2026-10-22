# L45d2b3a — La retroazione dei regolatori dei rail: sul piedino o sul rail

Data: 2026-10-22 · Lotto: L45d2b3a (prima parte di L45d2b3) · Dati: `data/2026-10-22/L45d2b3a/`
(README) · Decisione: **ADR-096** · Non conformità: nessuna aperta o chiusa · Circuito: invariato

## In breve

- **La domanda dell'utente.** Leggendo lo schematico di L63a, l'utente ha notato che la retroazione di
  U501 / U502 è presa prima di D515 / D516, mentre una mia spiegazione in chat diceva «a valle del
  diodo». Lo schematico era giusto e la spiegazione sbagliata. Poi la domanda vera: con la retroazione
  sul rail la taratura non dipenderebbe dal diodo. Non è la scelta migliore? L'utente ha voluto
  rimisurarla in questo lotto («facciamolo in questo lotto»), e L45d2b3 si è diviso: questo, e i guasti
  in L45d2b3b.
- **Il modello del costruttore di TPS7A4701 gira.** L41a l'aveva lasciato «DO NOT USE» (uscita ~1,0 V).
  La causa è `LIMIT`, che ngspice senza modo di compatibilità non legge come PSpice (limitations #72).
  Corretto, dà 15,294 V alla taratura di U501 e 3,34 mV sul gradino della figura 5-19. Sta in
  `models/ldo_regulator/`, e `validate_models.py` ora conta 61 controlli su 61.
- **Ma nessun modello del costruttore dice la banda del regolatore vero.** Quello di TPS7A4701 con SENSE
  sull'uscita non ha anello; quello di TPS7A3301 non ce l'ha mai. Il margine si è quindi misurato in
  due modi:
  - col modello di TI;
  - con un regolatore generico a un polo e la banda da 10 kHz a 1 MHz.

  In tutti e due la rete è quella vera, con ESR, cavo, carico e temperatura fatti variare.
- **I numeri**:
  - sul piedino: **89–91°** in ogni caso;
  - sul rail, al carico di regime: **51–109°** col modello di TI (9 casi su 48 sotto 60°) e **22–97°**
    col generico, a seconda della banda;
  - a carico leggero il margine scende fino a 7–21°;
  - il caso peggiore sono sempre i condensatori della tenuta a ESR bassa.
- **Il beneficio della forma sul rail non tocca nessun requisito**: rail a 15,00 V invece di 14,97 V, e
  4 mΩ invece di 0,13 Ω. La diafonia che ne viene è già sotto −140 dB contro i −70 dB del contratto. Il
  rumore va dall'altra parte: col diodo fuori dall'anello la tenuta filtra il regolatore (−8 dB a
  1 kHz).
- **L'utente: «Sul piedino»** (ADR-096). Il circuito non cambia; il commento di `psu.py` ora cita la
  misura.

## Il modello del costruttore di TPS7A4701

L41a aveva applicato due patch (i `TC=0,0` e gli interruttori `VSWITCH`) e ottenuto un deck che girava
con l'uscita a ~1,0 V qualunque fosse la taratura. Riprodotto qui, il nodo di riferimento interno era a
~100 V e il piedino NR a 100 kV.

1. **Un errore mio**, trovato per primo: la regex della patch degli interruttori leggeva `ROFF=1G` come
   1 Ω. L'interruttore che scarica NR verso massa restava chiuso. Corretto coi suffissi SPICE.
2. **La causa vera**: `LIMIT(x, a, b)`. Su un deck di una riga ngspice dà `LIMIT(5, −1, 2)` = 0 e
   `LIMIT(0.5, 2, −1)` = −1,5, senza errori. Il modello la usa in due ordini (`G_LIM` col minimo prima,
   `POLE_LIM` col massimo prima). Riscritta come `MIN(MAX(x, MIN(a, b)), MAX(a, b))`, provata nei due
   ordini.

**I casi noti**:
- **La taratura di U501** (ANY-OUT 6,4 + 6,4 + 0,8 + 0,2 + 0,1, 19 V, 0,3 A): 15,294 V.
- **La figura 5-19** (5 V, 3,3 V, 10 → 845 mA, 10 µF): l'uscita scende di 3,37 mV e resta lì. La figura
  dà ~5 mV di picco e ~3 mV a regime, letti a occhio su 10 mV per divisione.

**Che cosa è il modello**, e perché il secondo caso noto non basta:
- l'uscita vale V(NR) × V(OUT) / V(SENSE), dietro un ritardo di 50 Ω / 32 nF (1,6 µs) e 4 mΩ;
- con SENSE sull'uscita il rapporto vale 1 identicamente: **non c'è anello**, e il gradino è solo la
  resistenza da 4 mΩ;
- con SENSE altrove nasce un integratore che attraversa a ~94 kHz. Nessuna curva del datasheet lo
  conferma: il PSRR del modello passa per un ramo a parte (`ZERO_POLE`), non per l'anello.

Il modello di TPS7A3301 ha la stessa forma senza nemmeno il ritardo: un regolatore algebrico, senza
dinamica. **U502 non ha un margine del costruttore.**

## Il banco del margine

**La rete**, per rail:
- sul piedino C511 / C512 da 10 µF;
- l'SB340 col modello di L45d2b2b1: 0,126 Ω dinamici a 0,3 A;
- la tenuta C505 / C506 a −20 % con il suo ESR;
- il cavo verso la scheda audio;
- 800 µF sulla scheda audio, più le celle RC sul + (8000 µF dietro 1,25 Ω);
- il carico come generatore di corrente: non smorza, il caso prudente.

**La misura**: iniezione di tensione sull'ingresso di misura del regolatore, che ha impedenza infinita in
tutti e due i modelli. Così l'iniezione è esatta: T = −V(nodo) / V(ingresso).

**Lo strumento**, provato su due anelli noti prima di qualunque numero:
- un integratore senza rete: 10 kHz e **90,00°**;
- un polo RC: **3834 Hz e 22,54°** contro 3834 Hz e 22,55° calcolati a mano.

**Le grandezze che non si conoscono**, fatte variare, perché le parti non sono scelte:

| Grandezza | Valori |
|---|---|
| ESR della tenuta | 10, 20, 30, 60 mΩ |
| ESR per condensatore della scheda audio | 0,05 Ω (ADR-056) e 0,2 Ω |
| cavo | assente, oppure 20 mΩ e 200 nH |
| carico | 0,30 A (il vero, `carico.txt` di L45d2b2b1), 0,1 A e 0,03 A |
| temperatura | 0, 25 e 60 °C |
| banda del regolatore (solo generico) | 10, 30, 100, 300 kHz e 1 MHz |

## I risultati

**Col modello di TI** (il +, 144 casi per forma):

| | Sul piedino | Sul rail |
|---|---|---|
| carico di regime (48 casi) | 90,1–90,9° | **51,0–108,8°**, 9 sotto 60°, 0 sotto 45° |
| tutti i carichi | 88,8–90,9° | 20,6–108,8°, 82 sotto 60°, 41 sotto 45° |
| il peggiore | — | tenuta a 10 mΩ, 30 mA, 60 °C: 20,6° a 2,1 kHz |

**Col regolatore generico** (sul rail; sul piedino è 90° per costruzione), il margine peggiore e
il migliore al carico di regime, sui 48 casi di rete:

| Banda | Rail + | Rail − |
|---|---|---|
| 10 kHz | 22,2–58,1° | 21,2–57,5° |
| 30 kHz | 23,7–71,3° | 23,2–71,2° |
| 100 kHz | 32,2–95,0° | 32,2–95,1° |
| 300 kHz | 43,2–110,9° | 43,2–110,4° |
| 1 MHz | 59,2–96,5° | 59,5–96,3° |

Con tutti i carichi il peggiore scende a 7–32°. Il caso peggiore è quasi sempre lo stesso: la tenuta a
10 mΩ, la scheda calda, il carico leggero.

**Il caso nominale** (ESR 30 mΩ e 0,05 Ω, niente cavo, 0,30 A, 25 °C):

| | Sul piedino | Sul rail |
|---|---|---|
| TI: attraversamento, margine | 94 kHz, 90,3° | 9,1 kHz, **58,9°** |
| generico a 94 kHz | 94 kHz, 90° | 9,3 kHz, **43,9°** |
| rail (TI) | 14,974 V | 14,995 V |
| gradino di 50 mA sul rail (TI) | 6,3 mV, fermo | 0,5 mV |

**Perché i due modelli non coincidono.** Sopra 30 kHz modulo e fase di T sono gli stessi. Sotto, il
modello di TI ha meno guadagno e meno ritardo: a 10 Hz 434 contro 9127, e −68° contro −94°. La
ragione è che il suo rapporto legge l'uscita *dopo* la sua resistenza da 4 mΩ, e questo crea un anello
locale (T ≈ b·H / (sτ + Ro / Z_piedino)). Non viene dalla resistenza in sé: il generico con 4 mΩ dà
43,6°. È una costruzione comportamentale, e nessuna misura del datasheet dice quale dei due somigli al
chip. **Nessuno dei due è un limite**: il regolatore vero ha almeno il polo del suo dispositivo di
passaggio sul condensatore del piedino.

**Il meccanismo**, lo stesso nei due modelli. Visto dall'anello, il diodo con la tenuta è un passa-basso
(~500 Hz), con uno zero dato dall'ESR dei condensatori. La forma sul rail moltiplica il guadagno
d'anello per quella rete. Quando l'attraversamento cade fra il polo e lo zero il margine crolla; e con
un ESR più basso lo zero sale e l'attraversamento scende.

**Il beneficio** (TI, nominale; `zrail.csv`), impedenza del rail vista dalla scheda audio:

| Frequenza | Sul piedino | Sul rail |
|---|---|---|
| 10–100 Hz | 0,13 Ω | 3,9 mΩ |
| 1 kHz | 53 mΩ | 4,1 mΩ |
| 10 kHz | 13 mΩ | 14 mΩ |

Il piatto della forma sul rail è la resistenza del modello: conta l'ordine di grandezza. **Contro il
contratto il beneficio non pesa.**
- **Diafonia.** Quella che passa per il rail è circa Z_rail / R_carico. Già con 1 kΩ di carico e
  nessuna reiezione del blocco sono −78 dB; con la reiezione del blocco (oltre 70 dB, ADR-056) sotto
  −140 dB, contro i −70 dB di PR-10. E il blocco è in classe A: la corrente del rail segue poco il
  segnale.
- **Rumore.** È a favore del piedino. Il rumore del regolatore arriva al rail attraverso la stessa rete
  diodo e tenuta: |H| 0,38 a 1 kHz (−8 dB) e 0,10 a 10 kHz (−20 dB). Sul rail l'anello lo riporta tutto,
  fino alla sua banda.
- **Calore e riserva.** Non cambiano: in tutte e due le forme il piedino sta a ~15,3 V.

## La decisione

Domanda all'utente, per nome:
- «Sul piedino», il consigliato;
- «Sul rail, dopo il diodo»;
- «Sul piedino, e sul prototipo» (due ponticelli per provare l'altra forma).

**«Sul piedino»** → ADR-096: conferma il punto 2 di ADR-093, circuito invariato, il modello di TI in
`models/`.

## Limiti dichiarati

- **La banda del regolatore vero non è nota.** I margini della forma sul rail stanno fra due modelli
  che nessun caso del datasheet distingue. La forma sul piedino non dipende da questo: è la
  configurazione del costruttore.
- **Gli ESR sono ipotesi**: le parti non sono scelte. L'intervallo 10–60 mΩ copre dal polimero
  all'elettrolitico generico; a freddo l'ESR sale (meglio per la forma sul rail), a caldo e negli anni
  cambia.
- **L'SB340 è il modello del banco di L45d2b2b1**, ricavato a occhio dalla curva tipica a 25 °C.
- **Il carico come generatore di corrente** non smorza: è il caso prudente per tutte e due le forme.
- **I 60° sono la soglia del blocco di guadagno (PR-7)**, presa a prestito: il contratto non ne fissa
  una per i regolatori. La scelta non dipende da lei: anche a 45° la forma sul rail ha 41 casi su 144
  sotto col modello di TI.
- **Il rumore** è letto dal modulo di H, non simulato: il modello di TI non modella il rumore d'uscita
  (intestazione del costruttore).

## Che cosa resta, e a chi

- **L45d2b3b**: i guasti rifatti e la sintesi, sul circuito di oggi, che questo lotto non ha cambiato.
- `README.md` e `CLAUDE.md` citano ancora «38/38» controlli dei modelli: erano già fuori allineamento
  prima di questo lotto (59 prima, 61 ora). È deriva documentale, registrata qui e non corretta.
