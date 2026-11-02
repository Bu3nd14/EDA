# Prompt per la sessione successiva — L64, il dossier rigenerato una volta sola prima di G1

Nome della sessione: **hi-fi preamp L64** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura del lotto della catena a guadagno unitario (2026-11-02, NC-055 chiusa,
> ADR-112: ogni blocco si giudica al livello a cui lavora; il circuito non è cambiato). Con quel lotto
> si chiude l'ultimo lavoro sul sorgente prima di G1. L'ordine verso G1: **L64** → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L64**, e si
ferma.

## Che cosa fare

**Il dossier rigenerato, una volta sola, adesso che il circuito smette di cambiare** (decisione
dell'utente dopo L45d2b3b2a, 2026-10-22, «si mi va bene»). L'ultimo dossier è di L51 (2026-10-10). Da lì
non mostra l'inseguitore e l'aiuto dello specchio (L56), il rivelatore tolto e il condensatore della
Stax (L60), i diodi del moltiplicatore e dei finali (L62, ADR-095), l'alimentatore di ADR-091…094, R153
sdoppiata (ADR-097), i rimedi del calore e i dissipatori (ADR-099), il limitatore del VAS (ADR-111), gli
schematici completi (L63), la FMEA con le misure adottate, l'autodiagnosi (ADR-110, `DIAGNOSI.md`), la
catena a guadagno unitario e V4 sulla catena (ADR-112).

1. **Leggi prima**:
   - la riga di L64 nella tabella dei lotti di `STATE.md`;
   - `docs/preamp/dossier/build_dossier.py`: la regola «nessuna cifra scritta a mano», le due strade per
     ogni numero, il rifiuto sui dati dei segnaposto;
   - i report di L51, l'ultima rigenerazione (`reports/2026-10-09-L51a-dossier-scheda-audio.md`,
     `2026-10-09-L51b-dossier-alimentatore.md`, `2026-10-10-L51c-dossier-schede.md`): com'era diviso il
     lavoro, che cosa ha rifiutato il generatore;
   - in `STATE-STORIA.md`, la sezione sul dossier («si rigenera come lotto, come ingresso di una
     revisione»).
2. **Il generatore sul progetto di oggi, prima di ogni sezione nuova**: `build_dossier.py` com'è deve
   girare sui dati che cita, oppure rifiutare con una ragione. Ogni rifiuto si legge: dice quale dato è
   vecchio o mancante.
3. **Le sezioni nuove**, ognuna coi suoi numeri letti dai file versionati sotto `docs/preamp/data/` e
   passati per una seconda strada. Le cifre del blocco sono quelle a caldo (ogni giunzione alla sua
   temperatura), dove esistono.
4. **Se il lavoro è più grande di una sessione**: dividilo con l'utente all'inizio, come L51 («Tre
   parti»), coi nomi delle parti.
5. **La consegna**: il dossier in PDF all'utente (vedi la memoria «Consegne in PDF»), un file per
   documento.

## I vincoli

- **Il dossier ha un solo lettore, l'utente**: niente avvisi di obsolescenza, si rigenera come lotto. E
  **non si taglia**: tutto il progetto di oggi, anche sotto pressione di tempo.
- **Il circuito non cambia in questo lotto.** Se una sezione scopre un difetto, si apre una non
  conformità e si porta all'utente; non si corregge il sorgente qui.
- Quelli di L58 e dei lotti dopo:
  - comandi semplici, percorsi assoluti, script scritti con Write;
  - `git add` un percorso alla volta;
  - commit e push prima di ogni lista lunga.
- **Le forme d'onda e le corse grezze non si committano**: prima di ogni `git add` di una cartella dati,
  `.gitignore` deve coprire `run/` e le cartelle delle corse.
- **Una catena di più blocchi** vuole i `.nodeset` dal blocco da solo (limitations #86), se il dossier
  rifà una corsa sulla catena.
- Le domande all'utente si fanno per nome; i colpi al jack in dB SPL; le distorsioni in dB contro il
  tetto.
- Il controllo del worktree rifiuta i comandi composti (cicli, pipe con variabili, heredoc con git,
  `xargs` con `find`): scriverli in uno script.

## CHIUSURA

1. `STATE.md`: L64 **fatto**, il prossimo **L65**; le celle di In breve; il diario (la voce più vecchia
   delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L65 («Nome della sessione: hi-fi preamp L65»): la forma della revisione
   (l'architetto avversariale cieco, la lettura dell'utente, o tutte e due) si decide con l'utente
   all'apertura.
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L64`; rimuovi il worktree; fermati.
