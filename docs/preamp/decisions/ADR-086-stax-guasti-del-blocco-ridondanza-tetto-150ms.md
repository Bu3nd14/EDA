# ADR-086 — I guasti del blocco che passano il condensatore della Stax: ridondanza nel blocco, e il tetto della Stax a 150 ms

Data: 2026-10-15 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Precisa PR-30 e P10** (ADR-081): sulla fissa 2 (Stax) il tetto di durata sopra 0,87 V passa da
  125 a **150 ms**, col suo carico. Il resto di PR-30 resta.
- **Precisa ADR-081 punto 1**: il condensatore da 1 µF ferma ogni gradino di continua (il blocco al
  rail, 118–124 ms), ma non un'uscita che oscilla o che deriva lenta. Per quei guasti il rimedio sta
  nel blocco.
- **Tocca ADR-006** senza cambiarlo: la ridondanza va in `gain_block()`, la funzione unica delle otto
  istanze; resta una topologia sola.

## Contesto

L60c2 ha messo nel sorgente il condensatore da 1 µF della Stax prima di K3 (ADR-084) e K3 a isolamento
supplementare (ADR-085), e ha rifatto P10 col carico della Stax su **ogni** guasto del blocco di L45a
sulle posizioni A e F2 che a vuoto portava la Stax sopra 0,87 V: 107 modi, condensatore nominale e
+5 % (`data/2026-10-15/L60c2/p10_stax.csv`, `reports/2026-10-15-L60c2-stax-condensatore-e-rele.md`).
Il blocco al rail dà 118 / 124 ms, come ADR-081 e L60c1. Quattro guasti di un solo componente
passano i 125 ms:

| Guasto (blocco A e F2) | Che cosa fa | Sopra 0,87 V sulla Stax |
|---|---|---|
| R109 aperta (la resistenza di gate della JFET d'ingresso, lato retroazione) | l'anello si apre, il buffer oscilla da rail a rail ogni ~80 ms: fronti fino a 28 V | **0,4–1,2 s** |
| R112 aperta, o la source di JQ110B aperta (la degenerazione dello stesso lato) | l'uscita salta a +12 V e torna in ~300 ms | **140–149 ms** |
| Q133 in corto collettore-emettitore (il finale PNP) | l'uscita scende lenta verso −7 V | **127–135 ms** |
| R144 aperta (la cella RC dell'alimentazione dello stadio d'ingresso) | l'uscita scivola al rail in ~1 s | 130 ms (solo a +5 %) |

Il condensatore lascia passare un'oscillazione e una rampa lenta, a qualunque valore che rispetti E9.

## Decisione

Le parole dell'utente (2026-10-15), alle domande poste per nome coi numeri qui sopra:
1. «Fermati, decidiamo il rimedio», poi sul rimedio: **«Ridondanza nel blocco»**;
2. sul dove, dopo aver chiesto «ma perché non modifichiamo solo il blocco STAX?»: **«Tutti e otto i
   blocchi»**;
3. sul quando: **«Lotto suo, dopo»**;
4. sulla voce del contratto: **«Tetto a 150 ms»**.

- **La ridondanza in `gain_block()`, nelle otto istanze**: R109 con una resistenza da ~10 kΩ in
  parallelo (aperta R109, l'anello resta chiuso); R112 e R144 sdoppiate in due resistenze in parallelo
  (aperta una, il blocco resta in funzione con la degenerazione o la cella cambiate). I valori e le
  prove sono del lotto **L60d**, prima di L45d2b2.
- **PR-30 e P10: la Stax al più 150 ms** sopra il tetto di non-danno, col suo carico. Copre i due
  guasti che la ridondanza non toglie: la source di JQ110B aperta (140–149 ms) e Q133 in corto
  (127–135 ms).

## Perché

- **Solo il blocco della Stax non basta.** Il blocco A alimenta il buffer F2, che lo copia fedelmente:
  R109 aperta in A dà 0,4–0,8 s sulla Stax, R112 aperta in A 140–147 ms. Il minimo sono A e F2, quattro
  istanze su otto; farle tutte e otto lascia una topologia sola (ADR-006) e una regressione sola,
  perché il blocco A sta anche sul percorso principale e va rimisurato comunque. Il risparmio di A e
  F2 soli era di 12 resistenze. Protegge anche la principale e la Singxer da questi guasti.
- **La ridondanza toglie il guasto peggiore alla radice**: R109 aperta è l'unico modo che oscilla, e
  con 10 kΩ in parallelo l'anello resta chiuso. R112 e R144 sdoppiate non danno più il salto.
- **Non può togliere** la source della JFET aperta (un difetto interno della parte doppia) né il
  finale in corto. Il tetto a 150 ms li copre: il peggiore è 148,6 ms al condensatore +5 %, 1,4 ms di
  margine. È una scelta dell'utente sul testo proposto, ed è un margine stretto.
- **La finestra di livello su K3** (due comparatori per canale sull'uscita del buffer della Stax che
  aprono solo K3 oltre ~5 V) copriva tutti e quattro, ma è un circuito nuovo; non scelta.

## Alternative scartate

- **Una finestra di livello sull'uscita del buffer della Stax che apre K3**, da sola o insieme alla
  ridondanza: più parti e un circuito nuovo da provare.
- **La ridondanza solo nei blocchi A e F2**: due varianti del blocco da tenere valide, per 12
  resistenze.
- **Il rischio residuo accettato su tutti e quattro**: lasciava sulla Stax un'oscillazione da rail a
  rail per oltre un secondo.
- **Un condensatore più piccolo**: E9 lo vieta sotto 895 nF, e un'oscillazione passa comunque.

## Conseguenze

- **Aperta NC-069** (maggiore, prima di G1): R109 aperta fuori dal tetto di 150 ms sulla Stax
  (0,4–1,2 s), finché la ridondanza non è costruita e i guasti di A e F2 rifatti. Con il tetto a
  150 ms R112, la source di JQ110B, Q133 e R144 stanno dentro già oggi.
- **L60d**: la ridondanza in `gain_block()`, il sottocircuito, il disegno del blocco; la regressione
  del blocco (stabilità, rumore, distorsione, i deck veloci); i guasti di L45a sulle parti nuove e su
  quelle sdoppiate, e P10 sulla Stax rifatto sui modi di questa tabella.
- **Il «Da riaprire se» di ADR-081** non cambia; quello di P10 sì (sotto).

## Da riaprire se

- Dopo la ridondanza un guasto della tabella, o uno delle parti nuove, supera ancora 150 ms sulla
  Stax.
- La tolleranza del condensatore da 1 µF si allarga oltre ±5 %, o il carico della Stax cambia: il
  margine di 1,4 ms della source della JFET aperta sparisce.
- Si trova un criterio di danno pubblicato per le elettrostatiche più severo di ~150 ms (lo stesso
  «Da riaprire se» di ADR-081, spostato).
