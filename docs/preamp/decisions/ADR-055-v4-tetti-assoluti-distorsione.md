# ADR-055 — V4: tetti assoluti di distorsione a un livello musicale dichiarato

Data: 2026-10-01 · Stato: accettata

## Contesto

V4 (ADR-053) chiedeva che «la THD a 20 kHz resti dello stesso ordine di quella a 1 kHz», senza
soglie numeriche. L46a ha misurato 25 varianti del blocco: in **nessuna** la crescita da 1 a
20 kHz scende sotto ~25 dB, perché è la pendenza del guadagno d'anello (−6 dB per ottava, ×20 in
frequenza = 26 dB). Una clausola che nessun circuito a controreazione può soddisfare non decide
niente. NC-039 chiedeva un criterio decidibile con un'ADR.

## Decisione

**La prima clausola di V4 diventa un tetto assoluto, a un livello dichiarato.** Su ogni uscita e in
ogni modo di guadagno, coi carichi del banco (sorgente 2,5 kΩ; 47 Ω + 4,7 µF + 10 kΩ):

| Grandezza | Livello | Tetto |
|---|---|---|
| THD a 20 kHz | 0,2 V RMS in uscita (−20 dB, ~99 dB SPL a 1 m) | **≤ 0,001 %** (−100 dB) |
| armoniche dalla 5ª in su (somma) | 0,2 V RMS, 1 / 10 / 20 kHz | **≤ −140 dB** |
| IMD CCIF 19 + 20 kHz, prodotto a 1 kHz contro un tono | toni uguali, picco composto di 0,2 V RMS | **≤ −110 dB** |
| THD a 20 kHz, prova di stress | 2 V RMS in uscita | **≤ 0,01 %** |

Il livello di 0,2 V RMS l'ha deciso l'utente all'inizio di L46a; i tetti li ha scelti fra tre
proposte (decisione del 2026-10-01).

## Perché

- **In SPL**: a 0,2 V la fondamentale è ~99 dB SPL a 1 m (finale ×21,1, Heresy 96 dB/1 W/1 m);
  −100 dB mette le armoniche a ~0 dB SPL, la soglia dell'udito, e comunque sopra i 20 kHz. Ogni
  tono del CCIF a 0,1 V RMS è ~93 dB SPL: −110 dB mette il prodotto a 1 kHz, che cade in piena
  banda udibile, a ~−17 dB SPL.
- **Discriminano**: il blocco di ADR-042 (1 nF) fallisce THD a 20 kHz (0,0017 %), IMD (−96,3 dB) e
  stress (0,17 %); le tre finaliste di L46a passano tutto (ADR-054).
- **La crescita con la frequenza** non si vieta più, si limita col tetto a 20 kHz: è la parte
  della distorsione verso gli acuti che dipende dal progetto, non dalla fisica dell'anello.

Restano di V4 come prima: «lo spettro cala in modo ordinato» (verificato a occhio sulle h2…h7), e
**il tetto complessivo di THD+N, che non è fissato qui**: dipende dal rumore nella banda di misura,
e si fissa con l'utente sulle prime misure del prototipo.

**Cifre di modello.** I tetti si verificano in simulazione coi modelli del costruttore e, quando ci
sarà, sul prototipo; dove le due cose divergono vale la misura.

## Alternative scartate

- **Tetti 10 dB più severi** (0,0003 %, −120 dB, 0,005 % a 2 V): li passava solo l'opzione coi ZXT,
  scartata in ADR-054 per disponibilità e calore.
- **Nessuna soglia fino al prototipo**: lasciava NC-039 aperta senza un criterio per chiuderla.

## Da riaprire se

- Sul prototipo la distorsione misurata a 20 kHz e 0,2 V supera il tetto pur rispettandolo in
  simulazione: il modello sottostima, e il margine va ricostruito (NC-024, NC-025).
- Le prove d'ascolto (P6) trovano un'asprezza che i tetti non vedono: il criterio misura la cosa
  sbagliata.
