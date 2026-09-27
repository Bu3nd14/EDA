# 2026-09-27 — L43a, gli esiti della revisione dell'architetto avversariale

**Documento datato: non si riscrive.** Le voci che apre vivono in `../NONCOMPLIANCE.md`. Il
report dell'architetto, verbatim, è `2026-09-27-L43a-architetto-avversariale.md`.

## Che cosa è stato questo lotto

L43 prevedeva due revisioni del dossier in parallelo, col PRB come contratto: quella
dell'utente e, alla cieca, la prima di `adversarial-architect`. **Decisione dell'utente, a
sessione iniziata**: «voglio chiudere questa sessione con il solo contributo dell'architetto
avversariale, io non ho finito la review e faremo una sessione subito dopo questa con i miei
input». L43 si è quindi diviso:
- **L43a** (questo): l'architetto lanciato, i suoi rilievi discussi uno per uno con l'utente;
- **L43b**: la revisione dell'utente e il report di sintesi con chi ha trovato cosa.

### La cecità, com'è andata davvero

- **L'architetto era cieco rispetto all'utente.** È un agente nuovo, non un fork; il prompt conteneva
  solo la data, i tre obiettivi con le parole dell'utente e i percorsi del prodotto. Niente dei
  punti «per L43» di `STATE.md`. L'architetto dichiara di aver fatto la fase 1 senza leggere
  `NONCOMPLIANCE.md`, `STATE.md` e `reports/`, e che la fase 2 non ha tolto né ammorbidito
  nessun rilievo.
- **L'utente, da qui in avanti, non è più cieco rispetto all'architetto.** Ha visto i rilievi prima di finire la
  propria lettura, per sua richiesta (il prompt lo consentiva: «o non lo chiede lui»). In L43b
  la taratura va letta così: un difetto che l'utente registra e che l'architetto aveva già
  trovato non conta come scoperta indipendente.

## I rilievi e le decisioni dell'utente

| Rilievo | In breve | Severità proposta | Decisione dell'utente | Voce |
|---|---|---|---|---|
| R1 | THD e IMD crescono verso gli acuti, il Miller da 1 nF ne costa 20–27 dB (PR-8, V4, ADR-042) | bloccante | **accettato, bloccante** | **NC-039** |
| R2 | Ingresso in continua: il cambio d'ingresso porta la differenza fra le continue delle sorgenti (PR-14, F1) | bloccante | **accettato, bloccante** | **NC-040** |
| R3 | La continua del blocco A attraversa trim e volume; il dossier dice il contrario (PR-20, V2) | maggiore | **accettato, bloccante** | **NC-041** |
| R4 | PR-2 contro PR-3: i tre livelli di guadagno non servono alla catena | maggiore | **respinto**: i tre livelli restano | — |
| R5 | Nessuna FMEA della scheda audio (PR-22–24) | maggiore, prima di G2 | **accettato, maggiore**; la FMEA a piano come **L45** | **NC-042** |
| R6 | La VTL5C4 dell'Excelitas è fuori produzione (PR-29, T8) | maggiore | **accettato, bloccante per G2**: «non possiamo produrre se non cambiamo» | **NC-043** |
| R7 | Il ronzio da anello di massa non ha requisiti (PR-5, `SAFETY.md`) | maggiore | **accettato, bloccante per il layout** | **NC-044** |
| R8 | Il pilota delle LDR e Td = 6 s servono un criterio superato (PR-21, ADR-039/049/050) | minore | **accettato, minore**, con le semplificazioni 3 e 4: «sono disposto a cambiare e a ridurre il tempo di mute» | **NC-045** |
| R9 | La metrica in dB SPL ignora le cuffie | minore | **accettato, minore** | **NC-046** |

Due severità le ho assunte, e le ho dette all'utente mentre registravo. Per R5 l'utente ha
detto solo «accetto»: resta la proposta, maggiore. Per R6 «bloccante» l'ho reso come
bloccante per **G2**, perché il layout ha bisogno del pezzo vero.

**Le semplificazioni**:
- la 1 (togliere il guadagno commutato) e la 2 (togliere il trim) cadono con R4;
- la 3 (pilota delle LDR analogico) e la 4 (Td più corto) sono accettate, in NC-045;
- la 5 (togliere i buffer delle fisse) è **respinta**: «non togliamo i buffer, vanno tenuti»;
- la 6 non propone di togliere niente.

**Le ADR che l'architetto riaprirebbe**:
- ADR-042 finisce in NC-039;
- ADR-004, ADR-026, ADR-019 §3 e ADR-027 restano con R4 respinto; la clausola di ADR-027 sulla
  bobina di K6 va nella FMEA;
- ADR-038 e ADR-039 finiscono in NC-043;
- ADR-039 (Td), ADR-049 e ADR-050 finiscono in NC-045.

Nessuna ADR è stata scritta in questo lotto: le scriveranno i lotti che realizzano i rimedi.

## Che cosa ha fatto l'orchestratore, oltre a registrare

- Una risposta alla domanda dell'utente «che effetto udibile ha una THD alta alle alte
  frequenze?», dalla letteratura e senza rieseguire niente: le armoniche di un acuto cadono
  fuori dall'udito; si sente l'intermodulazione, che porta toni differenza in centro banda; e
  il livello musicale reale a 19–20 kHz sta molto sotto il fondo scala del test CCIF.
- La copia dei deck dell'architetto da `/tmp/l43a/` a `data/2026-09-27/L43a/architetto/`, perché
  una NC vuole un'evidenza apribile.
- Leggendo uno di quei log ho trovato una cifra che l'architetto non cita nel suo report. È la
  variante `_lo`, a +10 dB e 20 kHz con la sorgente 12 dB più bassa: **0,00543 %** contro
  0,168 %. È scritta in NC-039.

## I punti «per L43» di STATE.md

Nessuno dei tre è stato trovato dall'architetto:

| Punto | Trovato dall'architetto |
|---|---|
| S del mute con la cima delle LDR a 12 mA (ADR-050) mai misurato | no |
| La tenuta di `VRELAY` scesa da 62,8 a 36,1 ms (P9 ≥ 25 regge) | no |
| Il commento di `C_VRELAY` in `psu.py` con le cifre di L41a | no |

Restano per L43b, dove l'utente dirà se li ha visti.

## Taratura provvisoria dell'architetto

Da completare in L43b, quando ci saranno i rilievi dell'utente.
- **Il suo punto forte è l'omissione di giudizio**: R2, R3, R5, R7 sono cose che nessun documento
  del repo presenta come difetti. R3 contiene anche un'affermazione falsa del dossier,
  verificabile sulla netlist.
- **Il suo punto debole**: non ha rieseguito V1, V2 né l'alimentatore, e i tre punti «per L43»,
  tutti sull'alimentatore o sul mute a 12 mA, gli sono sfuggiti.
- **La proporzione**: su 9 rilievi l'utente ne ha accettati 8, e ne ha alzato la severità in 3 (R3,
  R6, R7; R1 e R2 erano già bloccanti). Ha respinto quello che toccava una scelta di prodotto
  (R4) e la semplificazione che riportava il blocco A a tre carichi in parallelo (la 5).
