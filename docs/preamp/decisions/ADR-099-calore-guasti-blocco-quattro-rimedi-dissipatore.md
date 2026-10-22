# ADR-099 — Il calore dei guasti del blocco: quattro rimedi nel blocco e un dissipatore sui finali

Data: 2026-10-22 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Risponde ad ADR-097 punto 4** («Lotto dedicato»): il rimedio dei quindici guasti del blocco che
  portano una parte oltre i limiti termici, senza rimedio da quando ADR-081 ha tolto il rivelatore
  che li fermava (ADR-072, «col calore»).
- **Estende ADR-087** (R153, il limite di corrente dell'inseguitore): la stessa logica, una resistenza
  nel collettore, sull'aiuto dello specchio.
- **Tocca ADR-054** (la degenerazione del VAS, 56 Ω): diventa 33 + 22 Ω, con la presa per il limitatore.
- **Non cambia ADR-021** (P7): lo applica; e **ADR-089 / ADR-098** (la Stax) si rimisurano nella seconda
  parte, come chiede il «Da riaprire se» di ADR-098.
- Il sorgente, la netlist, i disegni e le verifiche sono di **L45d2b3b2b**.

## Contesto

L45d2b3b2a (`data/2026-10-22/L45d2b3b2a/`, README), sul banco del calore di L45d2b3b1, provato prima sul
suo caso noto (5920 celle, 0 diverse). Coi rail ideali a ±15 V e 60 °C d'aria, quindici guasti singoli
del blocco portano una parte oltre i limiti: l'aiuto dello specchio Q148 fino a 5123 °C (R149 in corto,
~12,6 W in SOT-23), lo specchio Q121 a 574 °C (Q148 in corto), il VAS Q122 a 307 °C (il finale PNP in
corto), i diodi del riferimento a ~35 000 °C (R101 in corto), i finali a 149–160 °C (l'altro finale in
corto).

**Lo stato dopo**, simulato (la parte bruciata aperta o in corto da t = 0, il guasto di partenza a
0,3 s; due giri): la parte che si apre ferma il danno in metà dei casi (Q148 aperto: 4 guasti su 8);
quella che va in corto lo propaga quasi sempre (Q148 in corto: lo specchio a 493–577 °C; con R149
anche in corto, le due 20 Ω della cella a **45 W** ciascuna; Q122 in corto: il finale NPN a 309 °C).
Lasciare bruciare non è un rimedio.

## Decisione

Parole dell'utente (2026-10-22), alle due domande coi numeri del banco:

1. **«Quattro rimedi»**, in ognuna delle otto istanze di `gain_block()`:
   - **una 10 kΩ fra il collettore dell'aiuto Q148 e il rail negativo** (sigla nuova; R161 sul banco);
   - **un limite di corrente del VAS**: la 56 Ω d'emettitore (R123) divisa in **33 Ω dal rail filtrato
     + 22 Ω verso l'emettitore**, e un **MMBT5401** con l'emettitore sul rail filtrato, la base fra le
     due resistenze e il collettore sulla base del VAS: conduce oltre ~16 mA nel VAS (Q168 / R167 sul
     banco);
   - **una 1 kΩ fra il nodo dei source e il collettore della sorgente di coda Q106** (R169 sul banco);
   - **la resistenza del riferimento R101 in due da 3,40 kΩ in serie** (6,80 kΩ contro 6,81; R162 sul
     banco).
2. **«Dissipatore scelto ora»**: ciascun finale (MJE15032, MJE15033) col dissipatore a clip **Ohmite
   WA-T220-101E**, sedici sulla scheda.

## Perché

I numeri (`sintesi_rv2.csv`, `regressione/misure_rv2.csv`, `p7_rv2.csv`, `op_caldo.csv`,
`dissipatore.csv`):

- **13 dei 15 guasti entro** coi quattro rimedi (simulato): R149 in corto 5123 → 86 °C, Q148 in corto
  574 → 82 °C, Q121A base-emettitore in corto 885 → 79 °C, R107 in corto 553 → 82 °C, Q106 in corto
  515 → 94 °C, R101 in corto (diodi a ~35 000 °C) → 80 °C. Il più caldo è il VAS, **123 °C contro 125**
  (D102 / D103 aperti, Q125 in corto, R126 in corto), **119 °C** coi dispositivi del banco a 60 °C: a
  caldo la soglia del limitatore scende. I guasti delle cinque parti nuove: al più 87 °C.
- **Il blocco sano non cambia**: margine di fase minimo 43,1 → 43,6°, rifiuto delle alimentazioni entro
  ±0,34 dB a ogni frequenza, rumore entro lo 0,006 %, la continua d'uscita entro 0,04 mV; a riposo il
  limitatore conduce 0,06 / 0,9 / 7,5 µA a 27 / 60 / 90 °C contro gli 83 µA di base del VAS, e la
  corrente del VAS resta quella di oggi entro 3 µA. P7 non peggiora: il finale PNP 93 → 85 °C, Q148
  79 → 63 °C, le parti nuove al più 0,024 W e 62 °C.
- **I due corti dei finali** non li tocca nessun rimedio del blocco: l'altro finale porta 1,4–1,6 W, e in
  TO-220 senza dissipatore (62,5 °C/W) va a 149 / 160 °C, oltre P7 e — l'NPN — oltre i 150 °C del
  massimo assoluto (onsemi MJE15032/D). Col WA-T220-101E (20 °C/W a 1 W dalla curva del costruttore, la
  cifra peggiore; 2,5 °C/W giunzione-case; **2 °C/W d'interfaccia, ipotesi**): **99 / 95 °C** a calcolo.
  Riposo 79 → 67 °C, P7 85 → 70 °C.
- **La rete non conta qui**: il blocco vede i rail regolati a ±15 V a rete −10 / 0 / +10 %; conta solo
  con un regolatore in corto (+20 V), che è un secondo guasto.
- Ogni rimedio è il più piccolo che chiude il suo meccanismo: l'aiuto e la coda prendono la base o la
  corrente da un nodo senza limite, e una resistenza nel collettore toglie a tutti e due insieme corrente
  e tensione; il VAS invece regge il segnale, e il limitatore a riposo è spento (0,35 V sulla 33 Ω).

## Alternative scartate

- **Solo la 10 kΩ sull'aiuto** (1 parte per blocco): chiude 6 guasti, ne lascia 9 oltre i limiti (il VAS
  a 307 / 229 °C, i diodi del riferimento a ~35 000 °C, la coda a 203 °C).
- **Le resistenze sdoppiate e i diodi del riferimento in parallelo** (R101, R107, R126 in due, D102 /
  D103 doppi): chiudono il riferimento e la coda, ma i diodi in parallelo abbassano il riferimento e
  spostano il punto di lavoro (finali −3 %, banda d'anello 531 → 488 kHz, la base-collettore interna
  dello specchio Q121A da −40 a −95 mV, verso il ginocchio tolto da ADR-067).
- **Lasciare bruciare la parte** (lo stato dopo): sopra.
- **Un fusibile ripristinabile o un limite per blocco sui rail**: il guasto aggiunge al blocco da 9 a
  508 mA (`sintesi_oggi.csv`), con 38 mA a riposo; una soglia che prenda i 9–75 mA dei guasti dello
  specchio è a ridosso del riposo, e un fusibile ripristinabile scatta in secondi, mentre l'aiuto in
  SOT-23 a 12 W si apre in millisecondi. Non simulato: il confronto coi numeri del banco basta a
  scartarlo.
- **Un vincolo di dissipazione rimandato al layout** (G2): la scelta dell'utente è stata di scegliere la
  parte ora.
- **Accettare i corti dei finali**: l'NPN supera il massimo assoluto.

Letteratura: poca e di seconda mano sul limite del VAS (discussioni che citano Self; un brevetto sul
limite con resistenza di sensing); nessuna fonte sulla protezione di uno stadio di piccolo segnale da un
guasto singolo. I rimedi vengono dal meccanismo e sono giudicati sui numeri.

## Vincoli per la seconda parte (L45d2b3b2b)

- **R169 (la 1 kΩ della coda) ≥ 0,5 W a 60 °C**: arriva a 0,236 W con R107 in corto (`nuove_max_rv2.csv`),
  il 94 % di una 0207. Le altre parti nuove ≤ 0,089 W.
- **I dissipatori sono al potenziale del collettore** (il tab: rail + per l'NPN, rail − per il PNP): non
  devono toccarsi né toccare il telaio. Tre piedini del TO-220 e due del dissipatore: l'impronta cambia.
- **L'accoppiamento termico del moltiplicatore di Vbe col finale NPN** (ADR-034, ADR-082 punto 4) è in
  rame sulla scheda: col dissipatore il finale è più freddo e più lento. La corrente di riposo e V4 a
  caldo si rifanno col blocco nuovo.
- Il blocco nuovo rifà: il calore dei 15 e dei modi delle parti nuove, la Stax dei casi oltre 100 ms
  (ADR-098), P7, la regressione, V1.

## Da riaprire se

- Il limite del VAS, coi dispositivi alla loro temperatura (il metodo di L56), cambia la distorsione a
  20 kHz o l'intermodulazione oltre V4.
- La corrente di riposo dei finali, col dissipatore e l'accoppiamento in rame, si sposta oltre quanto
  ADR-042 accetta.
- Il VAS supera 125 °C in uno dei quattro guasti che lo limitano, sul blocco del sorgente.
- Il WA-T220-101E esce di produzione o non è disponibile: la sostituta deve dare ≤ 40 °C/W giunzione-aria
  con 1,6 W.
- Il «Da riaprire se» di ADR-097 («un rimedio che cambia le correnti dei rail del blocco»): a riposo
  non le cambia (VAS 10,715 contro 10,713 mA, finali 20,45 mA uguali); nei guasti le abbassa. Se il
  blocco del sorgente dà altro, la cella RC e R153 si rimisurano.
