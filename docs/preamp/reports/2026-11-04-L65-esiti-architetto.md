# 2026-11-04 — L65, gli esiti della terza revisione dell'architetto avversariale

**Documento datato: non si riscrive.** Le voci che apre vivono in `../NONCOMPLIANCE.md`. Il report
dell'architetto, verbatim, è `2026-11-04-L65-architetto-avversariale.md`.

## Che cosa è stato questo lotto

La revisione del dossier rigenerato in L64a–c e L69b, prima del gate G1 (come L43 dopo L42 e L52 dopo L51).
La forma l'ha scelta l'utente all'apertura: **solo l'architetto**, con un accento detto con le sue parole:

> «Il prototipo sarà molto costoso e quindi dobbiamo essere certi che funzioni perfettamente, l'unica cosa
> che vogliamo valutare sul proto è la qualità audio percepita. Le modifiche post prototipo devono limitarsi
> a cambio condensatori di accoppiamento.»

Il PDF del dossier all'utente: `/Users/roberto/Documents/preamp-dossier-L65.pdf` (A4, `stampa_a4.py`), rifatto
alla fine del lotto sul dossier con PR-12 e PR-30 nuovi.

### La cecità, com'è andata

- **Agente nuovo, non un fork**, lanciato in background dalla sessione già nel worktree. Il prompt conteneva
  la data, l'accento dell'utente verbatim tradotto in tre domande (che cosa è ancora affidato al prototipo;
  quali difetti solo il prototipo rivelerebbe che non si correggono con un condensatore; se i condensatori di
  accoppiamento sono davvero gli unici punti di regolazione e se si cambiano), i percorsi del prodotto. Niente
  dei rilievi di L43a, L52, L59.
- L'accento dell'utente **orienta** la revisione verso il rischio del prototipo: i rilievi R1–R3 vanno letti
  così. Non è un rilievo di un lotto precedente, quindi non rompe la cecità.
- L'architetto dichiara la fase 1 senza `NONCOMPLIANCE.md`, `STATE.md`, `STATE-STORIA.md`, `NEXT-SESSION.md` e
  `reports/`; in fase 2 ha letto `NONCOMPLIANCE.md` e le righe di `STATE.md` su G1 e sui lotti, e non ha tolto
  né ammorbidito nessun rilievo.

### Questa volta ha potuto eseguire

In L52 e L59 Bash veniva rifiutato all'architetto («worktree-isolated session… refusing to run»), perché la sua
cartella era il checkout condiviso. Lanciato dalla sessione dentro il worktree, **ha eseguito**: il banco della
THD a 20 kHz del dossier (`data/2026-11-02/L64a/distorsione/deck/oggi/thd_20k.cir`) così com'è, 0,000446 % a
0,2 V e 0,00449 % a 2 V contro i 0,000447 / 0,00449 % del dossier, e con un condensatore su NX–NY (neutro); i
calcoli della Stax, dello squilibrio dei canali e dei dB SPL in Python. Le riesecuzioni sono in
`/Users/roberto/.claude/jobs/9cc1317d/tmp/l65/`, fuori dal repo (usa-e-getta). Le altre cifre sono lette dal
dossier, e il report lo dice.

### Controllato dall'orchestratore

Prima di portare le scelte all'utente: `REQUIREMENTS.md` dice davvero E8 «4,7 µF su tutte e tre le uscite» e T5
«dopo ciascuno […] 4,7 µF», contro l'1 µF della Stax di ADR-081 (R3 regge); NC-048 era chiusa il 2026-10-09 su
L49a, 458 parti (R1 regge); PR-12 diceva «senza dissaldare», in contrasto con la scelta dell'utente di oggi.

## La risposta alle domande dell'utente sul prototipo

Il verdetto dell'architetto: **nessun difetto che faccia mancare il funzionamento elettrico del circuito
simulato**; i rischi del primo prototipo stanno **nel fisico** (lo spazio, le impronte, la massa) e **nelle
scelte di parti ancora aperte**, non nella topologia del segnale. Le tre cose che oggi impedirebbero di limitare
le modifiche dopo il prototipo ai condensatori:

1. la scheda audio non è piazzata sul circuito di oggi (R1, NC-048);
2. i condensatori di segnale non hanno una lista ammessa e le impronte sono del poliestere (R2, NC-082); quello
   della Stax è fissato da PR-30 e si monta scambiato col Singxer (R3, NC-080);
3. l'equilibrio dei canali dipende da una tolleranza delle resistenze non scritta (R6, NC-081).

Restano al prototipo, dichiarati: l'RK27 montato (pezzo di pannello), la diafonia, il calore del telaio (57,7 °C
contro 60 °C, margine 2,3 °C), le perdite a vuoto di T2 (NC-037), il ronzio d'anello (NC-044). L'elenco
completo è nel report dell'architetto, «Il prototipo».

## Le scelte dell'utente

| Domanda | Scelta, con le sue parole |
|---|---|
| Lo spazio sulla scheda audio (R1) | **«Riaprire, bloccante G1»**: NC-048 riaperta |
| Le maggiori nuove (R2, R3, R6) | il condensatore della Stax (**NC-080**), le resistenze allo 0,1 % (**NC-081**), i condensatori di segnale **«solo per la lista ammessa e non per lo zoccolo (dissalderemo)»** (**NC-082**) |
| Il tetto della Stax (R5) | **«Tenere e dichiarare»** (ADR-117); i «Dettagli» di PR-30 firmati, **«Firmo così»** |
| PR-12, che diceva «senza dissaldare» | **«Tenere le resistenze»**: dopo il prototipo si cambiano solo i condensatori di accoppiamento e le resistenze critiche, dissaldandoli (ADR-118) |
| Le semplificazioni | studiare prima di G1 **togliere il rivelatore di rete** (S2, che toglie anche R12) e **la ritenuta → fusibili** (S1); non scelte: togliere i buffer delle fisse (S3) e il +10 dB (S4) |

## I rilievi, uno per uno

| Rilievo | Esito |
|---|---|
| R1 la fattibilità fisica | **NC-048 riaperta**, bloccante per G1 |
| R2 condensatori di segnale | **NC-082**, maggiore; niente zoccoli per scelta dell'utente, PR-12 riscritta (ADR-118) |
| R3 il condensatore della Stax | **NC-080**, maggiore |
| R4 il ronzio d'anello | già **NC-044** (bloccante per G2), invariata; l'architetto nota che il prototipo non si fa senza |
| R5 il tetto della Stax | **ADR-117**, ipotesi dichiarata nei «Dettagli» di PR-30; **NC-046 resta aperta**, minore, per la metrica del fastidio in cuffia (la chiusura con ADR-117 proposta nella domanda non tiene: NC-046 chiede un'altra cosa) |
| R6 l'equilibrio dei canali | **NC-081**, maggiore |
| R7 la motivazione della principale | **NC-084**, minore (proposta dell'architetto) |
| R8 il moltiplicatore di Vbe, S6 | **NC-088**, minore (proposta dell'architetto) |
| R9 l'RK27 a 3 dB | **NC-085**, minore (proposta dell'architetto) |
| R10 i relè sempre eccitati | **NC-086**, minore (proposta dell'architetto) |
| R11 E3 | già **NC-057**, invariata |
| R12 il buco di rete di 20 ms | dentro lo studio di S2 (L70): se il rivelatore esce, sparisce |
| R13 il +10 dB, S4 | **respinto** (S4 non scelta dall'utente); NC-009 invariata |
| S3 i buffer delle fisse | **respinta** (non scelta); ADR-023 resta |
| S5 il rame fra moltiplicatore e finale (ADR-034) | non portata all'utente in questo lotto: resta nel report, con NC-019 |
| Omissione: il frontale mosso durante una sequenza | **NC-083**, maggiore **proposta dall'orchestratore** (si simula; un difetto lì non si corregge con un condensatore), da confermare con l'utente |
| Omissione: i colpi delle sorgenti sulle fisse | **NC-087**, minore (proposta dell'architetto) |
| Omissione: il cavo a caldo | già NC-059 (chiusa, ADR-101) |

Le minori sono registrate con la severità proposta dall'architetto, senza una domanda all'utente: le domande di
questo lotto erano sulle maggiori e sulle firme.

## L'ordine verso G1, proposto

Il circuito cambierà ancora (S1, S2), quindi il dossier va rigenerato di nuovo prima del gate. L'ordine che
propongo, in `STATE.md`: **L70** le due semplificazioni (studio coi numeri, scelta dell'utente, sorgente) →
**L71** il frontale mosso (NC-083), sul temporizzatore che esce da L70 → **L72** i testi e le parti (NC-080,
NC-081, NC-082, NC-084) → **L73** la prova di spazio (NC-048) col circuito e le impronte di oggi → **L74** il
dossier rigenerato → **G1**. L'utente può cambiarlo all'apertura di L70.

## Il registro

**26 voci aperte, 2 bloccanti** (NC-048 per G1, NC-044 per G2). Il dossier rigenerato coi testi nuovi del PRB e
le ADR 117–118: «OK: tutti i controlli incrociati sono passati».
