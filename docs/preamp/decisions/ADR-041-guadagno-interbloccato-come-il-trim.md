# ADR-041 — Il cambio di guadagno si interblocca col mute come il trim: si cambia solo a mute inserito, niente mute automatico, e il guadagno ha i suoi LED

Data: 2026-09-22 · Stato: accettata

## Contesto

ADR-038 ha deciso che guadagno e trim si cambiano solo col jack a massa, a musica
già spenta, e ha lasciato a **L36** la forma. Le due strade aperte erano:
- l'**interblocco da premere** (ADR-030, strada B: prima il mute, poi il selettore);
- il **mute automatico** al cambio (il selettore avvia da sé dissolvenza, commutazione
  e rientro).

## Decisione

Parole dell'utente, il 2026-09-22: «interlock al mute, come TRIM, nessuna invenzione,
avremo LED anche per il guadagno».
- **Il guadagno si cambia solo a mute inserito**, come il trim (F8, ADR-027).
  Fuori mute il selettore non muove nulla. L'utente inserisce il mute, gira, rilascia.
- **Niente mute automatico** al cambio.
- **LED dello stato vero del guadagno**, a pannello e cablati (ADR-028), come quelli del
  trim (F9).
- **La realizzazione è la strada B di ADR-030**, già scelta con l'utente: K1 e K5
  monostabili, ciascuno con un relè ausiliario in autoritenuta fuori mute, e i tre LED
  letti dai poli liberi degli ausiliari. È la lettura di L29b2 di «come TRIM»: lo
  stesso principio del trim, non gli stessi relè bistabili, che ADR-030 aveva scartato
  per ragioni scritte. Se l'utente intendeva i bistabili, ADR-030 va riaperta.

## Perché

- È la decisione dell'utente, e non introduce un meccanismo nuovo. Il trim funziona già
  così (L16), coi LED dello stato vero.
- Il mute a monte (ADR-038, v4 di ADR-040) spegne la musica prima del cambio, e il
  relè al jack assorbe il gradino d'offset del blocco B (6–114 mV, ADR-030) in
  τ ≈ 0,22 ms. È un ragionamento; la misura col mute reale è di **L29c**.

## Alternative scartate

- **Il mute automatico al cambio**: parole dell'utente, «nessuna invenzione».
- **Il cambio a caldo con regola d'uso**: già escluso da ADR-038.

## Da riaprire se

- L29c trova che il cambio sotto mute seguito dal rilascio porta al jack A o S fuori
  soglia.
- L36 trova che la corsa fra lo scambio del permissivo e il rilascio delle bobine non si
  chiude con la strada B.
- L'utente intendeva i relè bistabili del trim.
