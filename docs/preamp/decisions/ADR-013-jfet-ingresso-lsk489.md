# ADR-013 — JFET d'ingresso: LSK489

Data: 2026-09-08 · Stato: accettata

## Contesto

La Fase 1 ha stabilito che le parti si trovano, ma che il punto debole è
la **provenienza dei modelli SPICE** — cioè proprio ciò da cui dipende
l'argomento principale a favore del discreto (ADR-003).

L'analisi delle capacità d'ingresso, nata da una domanda dell'utente, ha
poi escluso un candidato e promosso un altro.

## Decisione

**LSK489** (Linear Systems), JFET duale monolitico a canale N.

## Perché

**Capacità d'ingresso: 4 pF**, contro 20 pF dell'LSK170 e 13 pF del
JFE2140. La più bassa dei candidati.

**Appaiamento monolitico**: i due dispositivi stanno sullo stesso die,
con appaiamento e tracking termico **intrinseci**. È superiore al
"stesso lotto" di ADR-005 — e **manda in pensione il problema del
date-code** che la Fase 1 aveva segnalato come azione manuale non
garantita contrattualmente.

**Genealogia audio reale**: esiste una nota applicativa dedicata di
**Bob Cordell**. Non è la discendenza storica del 2SK170, ma è
progettazione audio moderna e documentata.

**Disponibilità verificata**: 921 pz su DigiKey, $9,73 (qty 1), MOQ 1.

## Costo accettato consapevolmente

Il modello SPICE di Linear Systems è distribuito come **PDF contenente
il testo `.MODEL`**, non come `.lib`. Va **trascritto a mano**, e la
trascrizione da PDF è un punto in cui si introducono errori silenziosi.

Procedura obbligatoria, non facoltativa:

1. Congelare il PDF in `vendor/` con sha256 e URL registrati.
2. Trascrivere i parametri in `models/jfet/`.
3. Il `.provenance.json` deve dichiarare **esplicitamente** "trascritto
   manualmente da PDF vendor, non estratto meccanicamente".
4. **Controllo incrociato** dei parametri trascritti (I_DSS, V_P) contro
   i valori del datasheet, con `scripts/validate_models.py`.

Il punto 4 non è un di più: è ciò che rende accettabile il punto 2.

## Alternative scartate

**LSK170 + LSJ74** — l'LSJ74 ha **105 pF di C_iss e 32 pF di C_rss**,
cinque e sei volte l'LSK170. Non è un dispositivo da percorso del
segnale. In più il suo modello SPICE **non si risolve affatto** (Fase 1).
Nella nostra topologia il canale P non serve comunque: lo specchio si fa
meglio con PNP appaiati o con l'array THAT320, che ha la migliore
provenienza SPICE di tutto il giro.

**TI JFE2140** — **aveva la provenienza SPICE più pulita di tutte**
(modelli nativi TI, scaricabili e verificati) ed era il più economico.
Era la raccomandazione della squadra di progetto. **L'utente ha scelto
diversamente**, accettando consapevolmente l'onere della trascrizione in
cambio di capacità più bassa e della genealogia Cordell. Registrato come
tale.

## Da riaprire se

Il controllo incrociato del modello trascritto contro il datasheet non
torna, oppure l'LSK489 esce di produzione. In entrambi i casi il JFE2140
resta il ripiego naturale: stessa funzione, impatto topologico nullo,
solo polarizzazioni da ricalcolare.
