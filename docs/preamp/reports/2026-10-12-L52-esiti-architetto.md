# 2026-10-12 — L52, gli esiti della seconda revisione dell'architetto avversariale

**Documento datato: non si riscrive.** Le voci che apre vivono in `../NONCOMPLIANCE.md`. Il
report dell'architetto, verbatim, è `2026-10-12-L52-architetto-avversariale.md`.

## Che cosa è stato questo lotto

L'utente, il 2026-10-09: «rigeneriamo il dossier […] poi lo passiamo all'avversariale di nuovo,
poi affrontiamo G1». Il dossier è stato rigenerato in L51a–c; questo lotto è la seconda revisione
di `adversarial-architect`, che aveva visto il progetto una volta sola, in L43a (2026-09-27).

### La cecità, com'è andata davvero

- **Agente nuovo, non un fork**, lanciato per primo, in background. Il prompt conteneva la data, i
  tre obiettivi con le parole dell'utente, la richiesta su semplificazioni e over-engineering, e i
  percorsi del prodotto. Niente dei rilievi di L43a, dei 45 tratti ristretti di L51c, delle righe
  `Stato:`.
- **Una domanda in più, dell'utente, con le sue parole**, aggiunta al piano prima del lancio:
  «capire se il blocco di guadagno ha caratteristiche sonore buone in base ai requisiti e in base
  alla letteratura, alla fine il suono è dato da un unico blocco in questo progetto (più o meno) e
  non lo abbiamo mai messo in discussione». Non è un rilievo di un lotto precedente, quindi non
  rompe la cecità; ma ha **orientato** la revisione verso il blocco, e R5 (sotto) va letto così.
- L'architetto dichiara la fase 1 senza `NONCOMPLIANCE.md`, `STATE.md`, `NEXT-SESSION.md` e
  `reports/`, e che la fase 2 non ha tolto né ammorbidito nessun rilievo.

### Il limite di questa revisione: niente è stato rieseguito

In questa sessione l'agente **non ha potuto eseguire nessun comando**: Bash rifiutava tutto
(«worktree-isolated session… refusing to run»), anche `pwd`. In L43a l'architetto aveva rieseguito
i deck; qui **ogni cifra nuova è un calcolo a mano** sui dati pubblicati del dossier e dei CSV,
dichiarato come tale nel report. Per questo ogni voce aperta qui chiede una misura per chiudersi,
non solo una decisione. Per la prossima revisione avversariale: lanciarla in modo che possa
eseguire (vedi `NEXT-SESSION.md`).

## La domanda dell'utente: il blocco di guadagno

Il verdetto dell'architetto: **le scelte del blocco sono quelle che la letteratura associa a un
suono pulito e senza asprezza**. La topologia a tre stadi di Lin/Self con l'ingresso JFET
cascodato e l'uscita sempre in classe A (niente distorsione d'incrocio); lo spettro di modello a
h2 dominante, dalla 5ª al fondo del metodo, intermodulazione −125,6 dB (Geddes e Lee: conta lo
spettro, non la cifra); il rumore all'ascolto normale ~−3 dB SPL a 1 m; i carichi reali in classe A
larga e il margine fino a 4,7 nF di cavo. **Una riserva**: la distorsione d'ingresso a modo comune
delle istanze a guadagno unitario (R5), da misurare prima di dire che V4 è verificato. Come
suonerà lo dirà l'utente sul prototipo (PR-12).

## I rilievi e le decisioni dell'utente

| Rilievo | In breve | Severità proposta | Decisione dell'utente | Voce |
|---|---|---|---|---|
| R1 | Guasti singoli nei blocchi, contatto del mute incollato, nessun tetto sulle fisse; il rimedio tocca la topologia | maggiore, prima di G1 | **la FMEA prima di G1**, maggiore («Move the analysis before G1») | **NC-042** aggiornata |
| R2 | +3/+10 dB e trim non servono alla catena, e da L43a costano tre ADR e il guasto di ADR-051 | maggiore | **respinto di nuovo**: i tre livelli e il trim restano | — |
| R3 | Il micro e il firmware non hanno più la loro ragione dopo ADR-062 | maggiore | **accettato, maggiore, prima di G1** | **NC-054** |
| R4 | Spegnimento morbido e standby non servono al silenzio: la perdita di rete dà 39 nV contro 34 | minore | **accettato, unito al micro** («Accept, with the micro»): maggiore, prima di G1 | **NC-054** |
| R5 | Distorsione d'ingresso a modo comune nelle istanze unitarie; V4 non misurato sulla sorgente peggiore né sulla catena | minore per il suono, maggiore per la verifica | **accettato, maggiore per la verifica**, prima di G1 | **NC-055** |
| R6 | Il MJE15032/33 sovradimensionato; la sua capacità ha guidato la compensazione | minore | **minore, con la valutazione prima di G1** (risposta libera dell'utente) | **NC-056** |
| R7 | E3 misura il minimo di \|Zin\| a 20 kHz, ma esiste per il taglio ai bassi | minore | **accettato, minore** | **NC-057** |
| Omissione | V1 e V4 non corsi alla temperatura del telaio (57 °C) | — | **accettata, da verificare prima di G1** | **NC-058** |
| Omissione | Inserimento a caldo di un RCA sull'ingresso selezionato | — | **accettata, da verificare prima di G1** | **NC-059** |

Per le due omissioni l'utente ha detto solo «both to be verified before G1»: la severità
**minore** è quella che avevo proposto nella domanda, ed è scritta così nelle voci.

**Le semplificazioni**:
- guadagno commutato e trim: cadono con R2, respinto;
- micro e firmware, standby e spegnimento morbido: in NC-054;
- un solo buffer per le due fisse: **respinta di nuovo** (come in L43a e ADR-023).

**Le ADR che l'architetto riaprirebbe**:
- ADR-048 punti 3 e 6, ADR-049: in NC-054;
- ADR-014, ADR-055: in NC-055;
- ADR-042 / ADR-017: in NC-056;
- ADR-004, 026, 027, 041, 045, 051: restano, con R2 respinto.

Nessuna ADR è stata scritta in questo lotto; nessuna modifica al PRB, al circuito, al firmware, ai
deck o al dossier.

## La taratura contro L43a

| Tema | L43a | L52 |
|---|---|---|
| Guasti singoli della scheda audio | R5 → NC-042, prima di G2 | **ripetuto** (R1), già noto; nuovo l'argomento sulla scadenza, accolto |
| Tre livelli di guadagno e trim | R4, respinto | **ripetuto** (R2), già deciso; argomento nuovo (il costo cresciuto), respinto di nuovo |
| Buffer delle fisse | semplificazione 5, respinta | **ripetuta**, già decisa (ADR-023), respinta di nuovo |
| Distorsione verso gli acuti | R1, il Miller → NC-039, chiusa da ADR-054 | **nuovo meccanismo** (R5, la C_gd a modo comune), sollecitato dalla domanda dell'utente; R6 riprende il lato del MJE di NC-039, già deciso in ADR-054 per i ZXT, nuovo per un driver |
| Micro e firmware | NC-045 trattava il pilota delle LDR | **nuovo** (R3): il micro dopo ADR-062 |
| Standby | — | **nuovo l'argomento acustico** (R4) su una scelta già decisa (ADR-048) |
| E3 | — | **nuovo** (R7) |
| Temperatura del telaio, RCA a caldo | — | **nuove** omissioni |
| Ingresso in continua, continua nel volume, VTL5C4, pilota delle LDR | R2, R3, R6, R8 → NC-040, 041, 043, 045 | non ripetuti: tutte chiuse nel frattempo, e l'architetto non ne ha trovato il residuo |
| Anello di massa | R7 → NC-044 (bloccante per G2) | **non ripetuto**: l'architetto non l'ha nominato; la voce resta aperta |
| Metrica delle cuffie | R9 → NC-046 | citato in R1 come già noto |

In sintesi: su sette rilievi tre ripetono temi di L43a (due respinti di nuovo, uno con la scadenza
anticipata), quattro sono nuovi, più due omissioni nuove. Le cose nuove stanno dove il progetto è
cambiato (il micro dopo ADR-062, lo standby dopo ADR-056) e dove l'utente ha chiesto di guardare
(il blocco). Non ha trovato rilievi bloccanti.

## Il lotto successivo

Proposta del piano: L53 la lettura del dossier da parte dell'utente, oppure G1. **La risposta
dell'utente**: «I will read the dossier in parallel, please run remedies, FMEA, and all what is
needed before G1 in the meantime». La lettura dell'utente corre in parallelo e i suoi rilievi
entrano quando arrivano; i lotti di rimedio prima di G1, nell'ordine che ho scelto (l'utente non
l'ha fissato), le misure veloci prima perché possono cambiare i lotti grandi:
1. **L53** — le misure veloci: la distorsione contro l'impedenza di sorgente e V4 sulla catena
   (NC-055), V1 e V4 a 57 °C (NC-058), l'RCA a caldo (NC-059);
2. **L45** — la FMEA della scheda audio (NC-042);
3. **L54** — il micro, lo standby e lo spegnimento morbido (NC-054);
4. **L55** — il dispositivo d'uscita (NC-056);
5. poi **G1**; NC-057 (minore) può stare in uno qualunque di questi, o dopo.
