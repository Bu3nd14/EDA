# ADR-022 — Operazionali e microcontrollore fuori dal percorso del segnale

Data: 2026-09-14 · Stato: accettata

## Contesto

Ci sono due vincoli, con estensioni diverse:
- **ADR-003 e T1** vietano gli operazionali **nel percorso del segnale**, ma
  non dicono in modo verificabile che cosa sia quel percorso;
- **ADR-009** vieta il microcontrollore «**in tutto il progetto**», come
  conseguenza del «niente telecomando».

La protezione dal corto di **ADR-021** può volere un comparatore o un
coordinatore. L'utente ha deciso il 2026-09-13:

> «e se decidessimo che operazionali e micro non devono essere sul percorso
> segnale ma possono essere nel circuito?» — «si procedi come hai detto»

## Decisione

**1. Il percorso del segnale, definito.** Un componente vi appartiene se
**almeno una** delle due condizioni è vera:
- (a) il segnale audio **lo attraversa**, fra un connettore d'ingresso e un
  connettore d'uscita;
- (b) **chiude un anello** su un nodo di segnale, cioè la sua uscita torna in
  un nodo di segnale o di controreazione.

T1 vieta gli integrati in (a) e in (b). Il servo di continua resta escluso
(T2, ADR-007) per la (b), anche se non sta in serie. I relè e le parti
discrete comandate da un integrato **non** diventano integrati: un contatto
in serie è un componente discreto del percorso.

**2. Un ingresso di sola rilevazione su un nodo di segnale è ammesso**, se il
suo effetto è **misurato**, confrontando il carico dell'ingresso collegato e
scollegato, e resta sotto tre soglie:

| Effetto | Soglia |
|---|---|
| Zout all'uscita interessata (E4) | **Δ ≤ 1 Ω** a 1 kHz |
| Risposta in frequenza | **Δ ≤ 0,01 dB** in 20 Hz–20 kHz |
| Rumore in uscita (E5) | dentro la **quota ausiliaria** del punto 4 |

**3. Il microcontrollore è ammesso fuori dal percorso del segnale.** Supera la
clausola «nessun microcontrollore in tutto il progetto» di ADR-009. Il
telecomando resta escluso, e l'attenuatore a scatti di ADR-009 resta
com'è. Valgono tre condizioni:
1. **stato sicuro senza firmware.** Con il microcontrollore spento, in reset,
   in brown-out o coi pin in alta impedenza, ogni relè che comanda è **a
   riposo**, e il riposo è lo stato che `check_relay_safe_state.py` asserisce.
   Il guardiano **si estende** alle linee di comando quando il
   microcontrollore entra nella topologia, e si fa fallire prima di fidarsene;
2. **la protezione dal corto non dipende solo dal firmware.** La catena
   rilevamento → intervento di ADR-021 funziona anche col microcontrollore
   bloccato su un livello qualsiasi. Il firmware può coordinare e decidere il
   ricollegamento, ma non essere l'unica barriera;
3. **il rumore ha un budget misurato.**

**4. La quota ausiliaria di E5 è 1 µV RMS**, 20 Hz–20 kHz in uscita, per il
rumore **digitale e dei circuiti di rilevazione** sommati in quadratura. È una
ripartizione di E5 come ADR-020: al circuito del segnale restano
√(10² − 1² − 1²) = **9,90 µV**. La parte digitale ha un'**alimentazione
separata**, requisito consegnato al lotto dell'alimentatore.

## Perché

- **Il divieto degli operazionali non cambia estensione:** la definizione rende
  verificabile ciò che ADR-003 intendeva. Il servo resta fuori per la stessa
  ragione di ADR-007.
- **ADR-009 vietava il microcontrollore come conseguenza del «niente
  telecomando»,** non per una ragione sua. La ragione vera — niente firmware
  fra il segnale e le uscite — la conservano le condizioni 1 e 2.
- **Le soglie del punto 2 sono piccole rispetto ai margini di oggi:**
  - 1 Ω contro i ≈ 40 Ω che separano la Zout al jack (59-61 Ω a 1 kHz,
    `data/2026-09-13/`) dai 100 Ω di E4;
  - 0,01 dB è metà dello scarto che NC-007 ha misurato come partitore.

  Sono scelte **per preferenza**, dichiarata: nessuna misura dice che 2 Ω o
  0,02 dB sarebbero udibili.
- **1 µV è la stessa quota di ADR-020, per la stessa ragione:** 20 dB sotto E5,
  e il circuito non ne sente il costo.

## Alternative scartate

- **Lasciare ADR-009 com'è:** escluderebbe il coordinamento di una protezione
  e un ritardo di mute temporizzato, senza una ragione tecnica.
- **Ammettere il microcontrollore senza condizioni:** un mute che dipende dal
  firmware si guasta verso il suono. È il difetto che NC-014 aveva prodotto in
  hardware.
- **Una sola quota per PSU e ausiliari (2 µV):** l'alimentatore e i
  circuiti ausiliari li progettano lotti diversi. Una quota condivisa andrebbe
  rinegoziata a ogni misura.

## Da riaprire se

- Il rumore misurato del circuito del segnale **supera 9,90 µV**: le quote si
  ripartiscono di nuovo, con una ADR nuova.
- Una rilevazione utile non riesce a stare nelle soglie del punto 2.
- L'utente chiede un telecomando: allora si riapre ADR-009 per intero.
