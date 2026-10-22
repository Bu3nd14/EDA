# L45d2b3b1 — i guasti singoli rifatti sul circuito di oggi (2026-10-22)

Lotto di **NC-042** (prima di G1). Prima parte di L45d2b3b, divisa dall'utente all'inizio: **«Due
parti»** (le corse qui, la sintesi dopo). Decisioni **ADR-097** e **ADR-098**; **NC-075** aperta.
Dati: `data/2026-10-22/L45d2b3b1/` (README).

## Che cosa si è rifatto

Le 88 righe di `data/2026-10-14/L45d2a/decisioni.csv` destinate a L45d2b e le 9 basse delle
sovratensioni, sul circuito di oggi: dopo il rivelatore tolto (ADR-081), il condensatore della Stax
(ADR-084/085), la ridondanza del blocco (ADR-086/087), i diodi del moltiplicatore e dei finali
(ADR-090, ADR-095), l'alimentatore di ADR-091…094. Più i modi delle parti nuove, R144 contro la sua
parte, R153 in corto, le durate sulla Stax.

Cinque banchi, ciascuno di un lotto precedente e **provato su un suo caso noto prima dei numeri
nuovi**:

| Banco | Caso noto | Esito |
|---|---|---|
| il calore, ogni modo del blocco nelle cinque posizioni (da L62b) | il blocco di L62b sui suoi modi | 897 celle su 897 uguali |
| la Stax col suo carico e 1 µF (da L60d2) | il blocco di L60d2 su sei casi | 306 celle su 306 |
| i relè, le scelte 6 / 8 / 9 / 10 (da L60a) | i riferimenti di L60a | uguali, salvo il blocco cambiato |
| l'alimentatore col firmware (da L45d2b2b2) | due casi del sorgente | punto fisso e firmware uguali |
| P7 con le giunzioni (da L45d2b2c) | il blocco sano; R153 a 1 Ω sul blocco di L60d2 | 29 400 celle; 0,4112 / 2,006 W |

Le righe una per una, con l'effetto di oggi e la fonte: `righe_b1.csv`. Le colonne «dopo il
rimedio» di ADR-070 sono della sintesi.

## Gli esiti

- **Sedici guasti del blocco portano una parte oltre i suoi limiti** con 60 °C d'aria, e non hanno
  più un rimedio dal giorno in cui il rivelatore è uscito (ADR-072 li fermava spegnendo i rail;
  ADR-081 ha rimesso all'utente le scelte 6, 8, 9 e 10, non queste righe):

  | Guasto | La parte più calda |
  |---|---|
  | R149 in corto | l'aiuto dello specchio, 5123 °C (~12,6 W in un SOT-23) |
  | Q121A base-emettitore in corto; Q121A aperto, R119 aperta, R107 in corto, Q106 in corto | l'aiuto dello specchio, 515–885 °C |
  | Q148 in corto | lo specchio, 574 °C |
  | D102 / D103 aperti | l'aiuto dello specchio, 416 °C |
  | Q133 in corto; Q125 in corto | il VAS, 308 / 229 °C |
  | R101 in corto; R126 in corto | l'aiuto 239 °C, i diodi del riferimento; il carico del VAS 193 °C |
  | Q121B base-emettitore in corto; Q132 in corto | 149 °C (P7: 125) |
  | C145 in corto | R144 / R152 a 11,2 W ciascuna |

  I rail del banco sono ideali: le potenze sono a regime col guasto inserito. Una parte da 12 W in
  SOT-23 si apre in millisecondi; che cosa lasci dopo è parte del lavoro che viene. → **un lotto
  dedicato** (ADR-097, punto 4) per quindici; C145 in corto no: sull'alimentatore vero il rail crolla
  e resta l'impulso nelle due 20 Ω, che va alla parte (NC-075, sotto).
- **La Stax**: nessun guasto oltre 150 ms. Il peggiore, D102 / D103 aperti nel blocco A, 141,7 /
  145,8 ms (erano 125 / 129 in L60d2: li hanno allungati i diodi aggiunti dopo). Q132 / Q133 in
  corto salgono da ~20 a 107–124 ms (il limite di corrente di ADR-095). I modi dei diodi nuovi: 0 ms.
  Quattro corse fermate subito dopo il guasto, rifatte in gear: come L60d2.
- **ADR-089 riaperta** dal suo «Da riaprire se» (R153 cambia valore): i 121 casi oltre 100 ms
  rifatti sul blocco nuovo si spostano al più di 0,4 ms. L'utente: **«Confermare, D102/D103 al
  calore»** → ADR-098.
- **R153 in corto**: col mute inserito l'inseguitore a 0,39 W, **216 °C** contro 150. L'utente:
  **«Resistenza sdoppiata»** → due 2,4 kΩ in serie (R153 + R160): con una metà in corto 0,029 W, 72 °C.
  Il SOT-223 dava ~108 °C a calcolo.
- **I relè**: il selettore 116 / 95 ms sulla Stax, la cima del trim 118 ms (era 70), R126 in corto
  71 ms (era 37). K3 escluso dall'isolamento rinforzato, K2 / K4 senza durata sulla principale e sulla
  fissa 1 (ADR-081).
- **L'alimentatore**, le parti di ADR-093 / ADR-094 aperte e in corto alle tre reti: tutte dentro,
  salvo **C536 in corto: il primo regolatore dei 5 V a massa, 2,99 W**. Lo stesso caso dei corti dei 5 V
  a massa di L45c2, finora contati solo come «i 5 V persi». L'utente: **«Accettare la protezione»**
  (lo spegnimento termico del regolatore).
- **La cella RC in corto** sull'alimentatore di oggi: ciascuna 20 Ω 11,1 W di picco, **1,09–1,28 J**
  (il sorgente diceva 0,69 J). L'utente: **«Alla scelta della parte»** → NC-075.

## Il circuito

`gain_block.py`: R153 2,4 kΩ e R160 2,4 kΩ in serie dal collettore dell'inseguitore al rail negativo
(R160 in fondo al blocco, sezione 13). Scheda audio 570 → 578 parti. Le netlist confrontate per piedini:
cambia solo il rail negativo, più tre nomi di reti che SKiDL ha scelto diversamente (limitations #74,
la pagina completa li chiede con un sinonimo). I tre disegni: il blocco 62 su 62, la scheda audio 578
su 578, l'alimentatore invariato. La regressione dei 21 deck veloci: fuori da P7 lo 0,4 % al più, i
massimi di P7 entro lo 0,2 %. `run_tests.sh` **15 / 0**.

## Il crash

A metà lotto il Mac si è bloccato. Le cinque corse di R120 in corto del banco del calore, su 2,3 s,
stavano a ~9 GB ciascuna: ~45 GB su 24 (otto eventi di memoria esaurita, poi il riavvio forzato). Il
lavoro era su disco e si è salvato; le corse sono rifatte a 0,6 s, poche alla volta, a ~1,3 GB.
L'errore era nel numero di corse in parallelo scelto sui processori e non sulla memoria:
**limitations #75**.

## Trovati per strada

- **limitations #73**: nel banco dell'alimentatore il micro assorbe 2 mA anche senza alimentazione;
  con i 5 V spenti V5 va a −20 V, e l'analisi lo dà «dentro» perché guarda solo il massimo.
- **limitations #74**: SKiDL tiene un solo nome di due reti unite; aggiungere parti lo cambia.

## Dopo

**L45d2b3b2 — il calore**: i rimedi dei sedici guasti (e D102 / D103 aperti sulla Stax), misurati,
con l'utente. Poi **L45d2b3b3 — la sintesi**: le colonne dopo il rimedio di ADR-070 su `righe_b1.csv`,
e NC-042 chiusa se i numeri lo permettono.
