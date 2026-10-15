# Prompt per la sessione successiva — L60c, la Stax ha il suo condensatore

Nome della sessione: **hi-fi preamp L60c** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L60c**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se L60c si rivela più grande di una sessione, **dividilo con
l'utente all'inizio** (è un lotto M: il circuito e un banco di prove).

## Perché questo lotto, e perché adesso

ADR-081 (L61) ha tolto il rivelatore di continua: la Stax è protetta dal condensatore d'uscita della
fissa 2 a **1 µF film**, la principale e la fissa 1 dalla protezione a valle. L60 è stato diviso
dall'utente in tre parti («Tre parti»):
- **L60a (fatto)**: le scelte 6, 8, 9 e 10 che il rivelatore copriva → **ADR-082**;
- **L60b (fatto)**: il rivelatore tolto dal sorgente; J1 a sette pin con due masse e J4 di nuovo a tre
  (**ADR-083**); i moltiplicatori di Vbe in SOT-223;
- **L60c (questo)**: il condensatore da 1 µF della Stax **dopo il relè di mute K3**, e le sue prove.

Oggi la fissa 2 è `BUFFER F2 → 47 Ω → 4.7u → K3 → jack` (`preamp_audio.py`, `("STAX", "4.7u")`
in `channel()`, ~:265; lo schema in testa al file, ~:14). ADR-082 punto 1 la vuole
`BUFFER F2 → 47 Ω → K3 → 1 µF → jack`: tutti i contatti di K3 a monte del condensatore, così i 12 V
di una bobina che cede arrivano alla Stax solo come colpo che decade (a calcolo ~108 ms).

## Che cosa fare

1. **Il circuito.** Il condensatore della fissa 2 a 1 µF film, fra K3 e il jack, nei due canali; la
   fissa 1 (Singxer) **non cambia**. La geometria del mute su quell'uscita si riprogetta (ADR-044 la
   precisa ADR-082): dove va il contatto di riposo di K3 (a massa prima o dopo il condensatore), i
   bleed che tengono a zero le due armature quando il relè è aperto, la continua sul condensatore a
   mute inserito. Le scelte che non sono ovvie si chiedono all'utente per nome, coi numeri. Ogni
   valore nuovo porta il commento con la sua ADR. Netlist, disegno a blocchi, `run_tests.sh`.
2. **Le prove sulla fissa 2, col carico della Stax** (50 kΩ, ADR-081; il banco di L60a,
   `data/2026-10-15/L60a/`, è il punto di partenza: riprodurre prima i suoi numeri noti):
   - **E9**: la risposta in basso col banco su ogni carico (con 1 µF era 0,15–0,18 dB a 20 Hz in
     L61);
   - **P10**: ≤ 125 ms sopra 0,87 V sulla Stax per il blocco al rail, i guasti di L45a che portano
     continua, **K3 che cede** (isolamento bobina-contatti sul NO e sul comune, 10 Ω e 1 kΩ — oggi
     12 V per sempre) e **un pin di un rail aperto** sui due di J1 (ADR-083; con un filo solo erano
     388–421 ms);
   - **V2**: i gradini del mute sulla fissa 2 con la geometria nuova;
   - **l'inserimento a caldo** del jack della Stax.
3. **Se una di quelle prove non passa**: il condensatore torna dov'era e K3 diventa un relè con
   isolamento rinforzato fra bobina e contatti (ADR-082 punto 1), da scegliere sul datasheet — e si
   torna all'utente prima di farlo.
4. NC-042 avanza; se le prove passano le scelte 6 e 8 sono chiuse nel circuito.

## Prima di tutto

- `CLAUDE.md`, `AGENTS.md`, `docs/limitations.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L60b, L60a e L61.
- **ADR-081**, **ADR-082**, **ADR-083**, ADR-044 (la geometria del mute), ADR-021 / ADR-023 (le
  fisse e i loro buffer), ADR-069 / PR-30 come riscritta da ADR-081.
- `reports/2026-10-15-L60a-scelte-scoperte.md`, `reports/2026-10-15-L61-stax.md`,
  `reports/2026-10-15-L60b-rivelatore-esce.md`.
- `NONCOMPLIANCE.md`: NC-042, NC-046 (il tetto delle fisse), NC-062.

## I vincoli

- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB e dB SPL.
- Nel worktree vengono rifiutati:
  - i comandi composti, `cd … && script`, le variabili di shell nei percorsi, `xargs` sulla riga di
    comando, gli script lunghi passati sulla riga di comando (scriverli su file e lanciarli);
  - un comando che nomina la storia del repository in forma che il guardiano non sa verificare: le
    versioni vecchie dei file si estraggono prima di entrare nel worktree, o un file per comando;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito.

## NON fa parte di questo lotto

- L45d2b2 (i diodi, il comando, i 5 V, i massimi, NC-063): il suo prompt pronto è nella storia del
  repository (commit 22315ab1, `docs/preamp/NEXT-SESSION.md`), da aggiornare con ADR-081, ADR-082 e
  ADR-083 (il rivelatore non c'è più, J1 ha sette pin). L45d2b3 (i guasti rifatti), L58 (la
  diagnosi).
- La fissa 1 e la principale: contano sulla protezione a valle (ADR-081).
