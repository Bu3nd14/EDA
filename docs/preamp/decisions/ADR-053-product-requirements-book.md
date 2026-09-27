# ADR-053 — Il Product Requirements Book è il contratto; sette requisiti nuovi

Data: 2026-09-27 · Stato: accettata

## Contesto

Prima della revisione umana del dossier (L43) l'utente ha osservato che un dossier non si legge
senza i requisiti, e che `REQUIREMENTS.md` (623 righe) e le ADR (~5300) non si leggono per
intero: serve un contratto corto per capire se l'accordo fra utente e team è chiaro e univoco.
Rileggendo i requisiti per scriverlo, sette punti sono risultati senza un requisito.

## Decisione

`docs/preamp/PRB.md` è il contratto: 29 voci di al più tre righe, approvato dall'utente
(«l'ho letto e posso firmarlo con le integrazioni attuali»), ingresso di ogni revisione e lotto.
Sta **sopra** `REQUIREMENTS.md`, che dice come si misura; una contraddizione fra i due è un
difetto da decidere con l'utente. Cambiare una voce vuole una ADR.

Le sette decisioni, con le parole dell'utente, e i requisiti tecnici che nascono:
- **distorsione**: «mi interessa soprattutto il carattere», poi «limitiamoci a niente di aspro e
  abbandoniamo altri dettagli» → V4 precisato (PR-8);
- **risposta**: «±0,2 dB in banda e nient'altro» → E9 (PR-9);
- **canali**: «vanno bene entrambi, lascia fuori la sorgente non selezionata» → E10, E11 (PR-10);
- **cambio d'ingresso**: «a caldo senza clic» → F1 precisato (PR-14);
- **continua in uscita**: «≤ 1 mV e lista di tipi ammessi» → E12, P6 precisato (PR-11);
- **uscite fisse**: «0 dB ± 0,1 dB ma se fosse difficile da raggiungere rilassiamo dopo» → E13
  (PR-15);
- **standby**: «obiettivo nostro ≤ 0,5 W alla presa o rilassabile se troppo difficile (é per
  uso personale)» → P9 (a) precisato, NC-037 (PR-25).

## Perché

- Un contratto di 29 voci si legge in dieci minuti; i requisiti tecnici no, e senza un contratto
  leggibile una revisione giudica contro requisiti che l'utente non ha davanti.
- I sette punti erano vuoti veri: un lotto poteva peggiorare la risposta di 1 dB, o mandare
  continua al finale con un condensatore di prova, e nessun controllo l'avrebbe segnalato.
- I numeri scelti stanno con margine sulle misure di oggi dove esistono: risposta peggiore
  −0,134 dB (+10 dB, 20 kHz) contro ±0,2; uscita a guadagno 1 a −0,007 dB contro ±0,1.
- La 2ª armonica predominante è stata scartata dall'utente dopo aver saputo che la coppia
  differenziale d'ingresso la cancella per costruzione: farne un obbligo riaprirebbe la topologia.

## Alternative scartate

- **Appendici col testo intero di requisiti e ADR nel dossier**: 120–150 pagine, illeggibili.
- **Il PRB come copia riassunta di `REQUIREMENTS.md`**: due fonti della stessa cosa; qui sono due
  livelli, il cosa e il come si misura.
- **Il consumo in standby agganciato al Reg. (UE) 2023/826**: il testo non è stato letto, e per
  un apparecchio per uso personale non è vincolante.
- **Il cambio d'ingresso solo in mute**, come trim e guadagno: sicuro ma scomodo sul gesto più
  frequente.

## Da riaprire se

- una revisione (L43, l'architetto avversariale) trova una voce ambigua, o due voci che si
  contraddicono;
- una soglia rilassabile (E13, P9 (a)) si rivela costosa al giro della distinta o sul prototipo;
- le prime misure di distorsione coi modelli del costruttore rendono le soglie di V4 decidibili.
