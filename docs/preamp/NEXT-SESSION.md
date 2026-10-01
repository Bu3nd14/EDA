# Prompt per la sessione successiva — L46 (il blocco di guadagno: compensazione, distorsione verso gli acuti, PSRR+)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L46**, o la sua prima metà se va diviso, e si ferma. Non
iniziarne un secondo.

## Perché questo lotto, e perché adesso

La revisione del dossier (L43a l'architetto, L43b l'utente) ha aperto sei bloccanti per G1.
L'utente ha scelto l'ordine dei rimedi il 2026-10-01: **L46 → L44 → L47 → L48 → L49 → G1 → L45 →
L50** (tabella dei lotti in `STATE.md`). L46 è il primo perché tutto il resto poggia sul blocco di
guadagno, e due bloccanti hanno la stessa radice, **il Miller da 1 nF di ADR-042** (C124):

- **NC-039 — la distorsione cresce verso gli acuti.** Coi modelli del costruttore la THD a 20 kHz
  è 0,0616 % (0 dB) / 0,168 % (+10 dB) con 1 nF, contro 0,0060 % / 0,0118 % con 470 pF; l'IMD
  CCIF −59,6 dB contro −85,4 dB. A −12 dB di livello la THD a 20 kHz scende di ~30 dB (0,0054 %):
  il difetto dipende molto dal livello, e va giudicato a un livello musicale dichiarato. La radice
  indicata è la CJE di 3,06 nF dei MJE15032/33, per cui ADR-042 portò il Miller a 1 nF valutando
  solo alternative di compensazione. Deck: `data/2026-09-27/L43a/architetto/` (README dentro).
- **NC-047 — il PSRR del rail positivo è troppo basso per contare sul solo alimentatore**
  (rilievo dell'utente: «dovremo mettere mano al circuito audio per aumentare la PSRR»). PSRR+ a
  +10 dB: 23,01 dB a 10 kHz (`data/2026-09-27/L42/dopo/tb_zout_psrr_noise/`), contro 76 dB del
  rail −; il Miller da 1 nF ne è costato ~6,5 dB (L40). Il budget di ADR-020 sul rail + è 14,2 µV
  RMS per un tono a 10 kHz, ≤ 87 nV/√Hz di rumore bianco; il residuo dei rail **non è mai stato
  simulato** (regolatori comportamentali; il modello TI del TPS7A4701 dà un punto di lavoro
  sbagliato). NC-011 resta la verifica sul prototipo.
- **NC-052** (minore): la «Nota su E5» di `REQUIREMENTS.md` cita
  `data/2026-09-23/L40/dopo/tb_zout_psrr_noise/*_psrr{p,m}_10db.csv`, che non esistono. Si
  ripunta quando si ricalcolano i limiti.

## Il mandato

1. **All'inizio, con l'utente**: il livello musicale a cui si giudica la distorsione verso gli
   acuti (NC-039 lo chiede), e se il lotto va diviso (probabile: **L46a** compensazione e
   distorsione, **L46b** PSRR+ e ADR-020). Le domande si fanno **per nome**, non per sigle: «non
   ricordo sigle a memoria, devi essere più leggibile nelle domande».
2. **La compensazione**: alternative al Miller da 1 nF (non solo valori di Miller: la CJE dei MJE
   è la causa), ciascuna misurata su V1 (≥ 60° su ogni istanza e nel gruppo B, ADR-019), THD e
   IMD a 1 / 10 / 20 kHz al livello deciso, slew, PSRR+ e rumore. Il controfattuale (470 pF, 1 nF)
   corre sullo stesso banco.
3. **Il PSRR+ nel blocco**, se la compensazione non basta: cella di filtro locale o alimentazione
   separata dello stadio d'ingresso. La scelta di dove sta il rimedio (blocco o alimentatore) è
   dell'utente, e diventa una **ADR**.
4. **ADR-020 ricalcolato** sul blocco nuovo con `data/2026-09-23/L40/script/limiti_psrr.py`, la
   tabella per tono in `REQUIREMENTS.md` aggiornata, la nota ripuntata a CSV che esistono
   (chiude NC-052).
5. **Tracciabilità**: ogni valore nuovo in `circuits/preamp/*.py` col commento che punta alla
   ADR. Netlist rigenerate; deck versionati rigenerati e confrontati.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (le trappole che falliscono in silenzio), e in
  `docs/preamp/STATE.md` «In breve» e le voci di diario di L43b, L43a e L40.
- `NONCOMPLIANCE.md`: NC-039, NC-047, NC-011, NC-052.
- `decisions/ADR-042*`, `decisions/ADR-020*`, `reports/2026-09-23-L40-v1-costruttore.md`.

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `awk` con programmi, i cicli con variabili e i percorsi calcolati a runtime;
  - gli heredoc;
  - un titolo di PR con l'apostrofo (`gh pr create`): il corpo va su file (`--body-file`).

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi.
- Le cifre di THD dai modelli sono cifre di modello: conta il trend, non il valore assoluto
  (`CLAUDE.md`, «Nessun agente giudica come suona un circuito»).

## NON fa parte di questo lotto

- il rumore 1/f (NC-004, è L44, dopo questo); la cella del mute (L47); il selettore d'ingresso e
  la continua (L48); il placement e routing di prova (L49); la FMEA (L45); massa e terra (L50);
- rigenerare il dossier;
- l'alimentatore, salvo quello che il rimedio del PSRR+ deciso dall'utente richiede.

## CHIUSURA

1. `STATE.md` con L46 (o L46a) **fatto** e il prossimo lotto nella tabella.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L46` (o `L46a`).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
