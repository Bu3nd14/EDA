# ADR-003 — Classe A pura a discreti, nessun operazionale

Data: 2026-09-08 · Stato: accettata — precisata da ADR-021 (classe B ammessa solo a mute inserito e in corto) e da ADR-022 (definizione verificabile di percorso del segnale)

## Contesto

Scelta dell'utente, dichiarata dopo che l'architettura era già
delineata attorno a operazionali audio (OPA1612 e simili).

## Decisione

Tutto il percorso del segnale è **a componenti discreti, in Classe A
pura**. Nessun operazionale integrato, in nessun punto del percorso del
segnale — **servo di continua inclusi** (vedi ADR-007).

## Perché

È una scelta dell'utente, e va registrata come tale. Ma ha due
conseguenze tecniche reali che vale la pena aver messo per iscritto.

**A favore — la simulazione diventa credibile.** Il macro-modello di
operazionale presente in `models/` dichiara nella propria intestazione di
non avere clipping, slew rate né assorbimento dalle alimentazioni:
qualunque cifra di distorsione ricavata da lì è priva di significato. Un
BJT simulato con un modello Gummel-Poon vero, o un JFET con i suoi
parametri reali, riproduce la non-linearità **fisica** del dispositivo —
cioè lo stesso meccanismo che genera distorsione nel circuito costruito.
Resta una previsione, non una misura, ma diventa una previsione su cui
si può progettare.

**Contro — meno guadagno d'anello, e stabilità non regalata.** Un
OPA1612 ha ~130 dB di guadagno ad anello aperto; un blocco discreto a
tre stadi ben fatto ne dà 60-80. Meno anello significa meno correzione
della distorsione e Zout più alta: il discreto deve essere progettato
bene per pareggiare un buon operazionale, non lo fa per il fatto di
essere discreto. E un discreto retroazionato si destabilizza molto più
facilmente di un operazionale, che arriva già compensato — **margine di
fase e comportamento su carico capacitivo sono verifiche obbligatorie**,
non formalità.

Il calore invece **non** è un problema: in Classe A scotta un finale, non
uno stadio di linea. Con ~15 mA per stadio su rail ±15 V siamo intorno a
0,55 W per blocco, cioè ~3-4 W totali con l'alimentatore.

## Alternative scartate

- **Operazionali audio** (OPA1612, OPA1656): prestazioni misurate
  migliori con meno lavoro, ma escluse dall'utente.
- **Ibrido** (discreto sul percorso principale, operazionali sui buffer
  ausiliari): incoerente, e le uscite cuffia meritano la stessa qualità.

## Da riaprire se

Le misure mostrano che il blocco discreto non raggiunge obiettivi che
per l'utente contano più del vincolo sui discreti — decisione che
spetta a lui, non alla squadra di progetto.
