# Prompt per la sessione successiva — L61, le Stax: vanno protette, e come

Nome della sessione: **hi-fi preamp L61** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L61**, e si ferma. **È un lotto piccolo per scelta dell'utente**:
tieni il contesto stretto, leggi solo ciò che serve, niente banchi grandi.

## Perché questo lotto, e perché adesso

L59 ha deciso un rivelatore differenziale (ADR-080), da costruire in L60. Dopo la chiusura l'utente
ha chiesto se, visto che nessun preamplificatore ha un rivelatore sulle uscite, sia davvero
necessario. Il rivelatore esiste per **PR-30 / P10** (ADR-069), che assume a valle un apparecchio
**accoppiato in continua e senza protezione propria**. Senza rivelatore un blocco al rail lascia sopra
0,87 V per ~1,5 s la principale e ~3,1 s le fisse, a vuoto (ADR-069).

Le parole dell'utente (2026-10-15): «facciamo un lotto piccolo […] il nodo sono le STAX, non voglio
romperle, pensiamo come proteggere le STAX e capiamo se é davvero necessario, in un lotto dedicato,
piccolo. Se non serve proteggerle il rilevatore cade, se troviamo una soluzione per una sola uscita
magari riduciamo complessitá (anche se non credo)».

La catena di oggi:
- **la principale** → il finale cj EV250, a valvole col trasformatore d'uscita, che blocca la
  continua verso i diffusori (ADR-069). Un finale futuro diverso è possibile;
- **la fissa 1** → il Singxer SA-1, interno sconosciuto;
- **la fissa 2** → l'energizzatore **Stax SRM-T1**, che da recensioni, non da uno schema, risulta
  accoppiato in continua (ADR-069, «Da riaprire se»).

**L60 aspetta**: il suo prompt pronto è nella storia del repository (commit f622b372,
`docs/preamp/NEXT-SESSION.md`), e l'esito di questo lotto decide se si fa, si riduce o cade.

## Che cosa fare

1. **La SRM-T1, dai documenti** (in rete: manuale di servizio, schema, forum seri come head-fi e
   diyAudio, Stax stessa). Con le fonti citate, e ciò che non si trova si dice:
   - l'ingresso è accoppiato in continua o in alternata? Con quale costante di tempo?
   - ha un servo, una protezione propria, un ritardo all'accensione?
   - che cosa fa una continua all'ingresso: il guadagno fino agli statori, la tensione di
     polarizzazione (580 V), quanto si sposta la membrana, se si arriva all'arco o al contatto;
   - **un criterio di danno per le cuffie elettrostatiche**: quanta continua agli statori e per quanto
     tempo. Se non si trova, lo si dice.
2. **Il Singxer SA-1**, lo stesso, più breve: ingresso in continua o in alternata, protezione.
3. **Se le Stax vanno protette, le strade per una sola uscita**, con i numeri:
   - **il condensatore d'uscita della fissa 2 dimensionato al limite di E9.** Un polo singolo con
     ±0,2 dB a 20 Hz sta a ~4,3 Hz (τ ≥ 37 ms); con τ = 37 ms il gradino da 14,9 V resta sopra
     0,87 V ~105 ms, quasi P10 da solo. Va rifatto col budget di E9 di tutta la catena (C_IN,
     C_T, gli altri poli), col carico vero della Stax (50 kΩ) e a vuoto come vuole P10;
   - un rivelatore differenziale sulla sola fissa 2 (A contro F2), e che cosa lascia scoperto;
   - altre strade che la ricerca suggerisce.
4. **L'esito con l'utente**, per nome e senza sigle, coi numeri. Le tre uscite possibili:
   - **le Stax non vanno protette** (per esempio ingresso in alternata): si propone di restringere
     PR-30 alla catena nota, con la condizione che un finale nuovo fa rivedere il preamp. Il
     rivelatore cade, NC-064 e NC-065 si chiudono togliendolo, L60 si cancella;
   - **vanno protette e basta una soluzione su una sola uscita**: L60 si riduce a quella;
   - **vanno protette e serve il rivelatore**: L60 resta com'è.
   Cambiare PR-30 vuole una ADR nuova e la firma dell'utente (ADR-053).
5. Un report datato in `docs/preamp/reports/` (`2026-…-L61-stax.md`), STATE.md, il prompt del
   lotto successivo.

## Prima di tutto

- `CLAUDE.md` e `docs/preamp/STATE.md`, «In breve» e la voce di L59.
- **ADR-069** (perché 100 ms, la catena generica, i «Da riaprire se»), ADR-080, PR-30 e P10.
- Le memorie: la catena a valle generica, le domande senza sigle.
- Non serve rileggere il report di L59 per intero: gli esiti bastano.

## I vincoli

- Domande all'utente per nome, senza sigle; i colpi in dB SPL.
- Nessun cambio al circuito in questo lotto.
- Nel worktree vengono rifiutati i comandi composti, `cd … && script`, le variabili di shell nei
  percorsi, `xargs`, un comando che contiene la parola «git» in un testo, un titolo di PR con
  l'apostrofo (il corpo va su file, con `--body-file`).

## NON fa parte di questo lotto

- L60 (il rivelatore differenziale), L45d2b2, L45d2b3, L58.
