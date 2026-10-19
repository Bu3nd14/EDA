# Prompt per la sessione successiva — L62b, il moltiplicatore di Vbe: i quattro diodi nel sorgente e la verifica

Nome della sessione: **hi-fi preamp L62b** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L62b**, la seconda e ultima parte di L62, e si ferma. Non
iniziarne un secondo, salvo che l'utente lo chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

**NC-062** è bloccante per G1: quattro guasti singoli del moltiplicatore di Vbe (Q127 emettitore
aperto, Q127 base-emettitore in corto, R129 in corto, R128 aperta) spengono Q127, e la corrente del
VAS porta i finali a **213–216 °C con 60 °C d'aria** e le 22 Ω fino a 7,5 W, senza niente al jack
(L45a, rifatto in L62a sul blocco di oggi con le stesse cifre).

In **L62a** (2026-10-19) l'utente ha scelto il rimedio coi numeri del banco: **«Quattro diodi»** →
**ADR-090**. Si mettono quattro 1N4148 (DO-35, modello D1N914 come D102 / D103) in serie fra NX e NY,
anodo verso NX, in tutte le otto istanze di `gain_block()`. Sul banco, come variante del subckt:
- i finali stanno a **97–98 °C** con 60 °C d'aria e le 22 Ω a 0,041 W;
- i guasti dei diodi sono innocui (riposo 19,7–22,1 mA);
- a blocco sano: riposo −0,05 mA, V1 ≤ 0,05°, P7 uguale.

Questo lotto mette i diodi nel sorgente, verifica che il blocco generato dia gli stessi numeri e
chiude NC-062. **Viene prima di L45d2b2**: quel lotto legge i massimi e la dissipazione dei finali
sul blocco finale.

## Che cosa costruire

1. **I diodi in `circuits/preamp/gain_block.py`**, nella sezione 4 (il moltiplicatore), col commento
   che punta ad ADR-090. **Si aggiungono IN FONDO alla funzione**, come R150–R153 (limitations #22:
   ogni sigla esistente resta la stessa, una rinumerazione rompe i deck in silenzio). Le sigle le dà
   il sorgente: sul banco erano D160–D163, nomi di comodo.
2. **Rigenera** il sottocircuito e l'include piatto del blocco, le netlist della scheda audio
   (522 → 554 parti) e il disegno del blocco: il controllo del disegno (2d) conta i dispositivi e
   deve cadere finché il disegno non ha i diodi. Aggiorna i commenti di riepilogo in fondo a
   `gain_block.py` (riposo, P7).
3. **La verifica**:
   - i quattro modi di NC-062 e i guasti dei diodi (aperto e corto, ognuno) sul banco di L62a
     (`data/2026-10-19/L62a/script/genera_L62a.py`), con la variante `base` che ora è il blocco del
     sorgente. Le cifre vanno confrontate con la variante `diodi` di L62a (`sintesi.csv`,
     `temperatura.csv`); se differiscono, lo si dice prima di tutto;
   - **la regressione dei 21 deck veloci** (`data/2026-10-18/L60d1/script/regressione.sh`) contro
     L60d2;
   - **V4 a caldo** (`L60d1/script/caldo.py`), che L62a non ha rifatto;
   - **P7** (`tb_mute_corto` con le misure di `p7_l56.py`);
   - **la matrice di V2** solo se il blocco cambia dove conta: dillo coi numeri.
4. **NC-062 chiusa** nel registro, con l'evidenza; ADR-090 non si riscrive.

## Prima di tutto

- `CLAUDE.md`, `AGENTS.md`, `docs/limitations.md` (in particolare **#22**, **#57**, **#59**, **#62**,
  **#64**).
- `docs/preamp/STATE.md`: «In breve» e la voce di L62a.
- **ADR-090**; `reports/2026-10-19-L62a-moltiplicatore-vbe.md`; `data/2026-10-19/L62a/README.md`.
- `NONCOMPLIANCE.md`: **NC-062** («Avanzamento L62a»).
- `circuits/preamp/gain_block.py`: la sezione 4 e la coda delle parti aggiunte (R150–R153).

## I vincoli

- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB e dB SPL, le temperature in °C.
- Nel worktree vengono rifiutati:
  - i comandi composti, `cd … && script`, le variabili di shell nei percorsi, `xargs` sulla riga di
    comando, gli script lunghi passati sulla riga di comando (scriverli su file e lanciarli);
  - un comando che nomina la storia del repository in forma che il guardiano non sa verificare: le
    versioni vecchie dei file si estraggono prima di entrare nel worktree, o un file per comando;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- I gradini dei guasti si leggono col metodo della media; se uno cambia rispetto a L62a, si legge
  anche col metodo puntuale e sulla forma d'onda (limitations #64).
- Un punto di lavoro si giudica anche dalla corrente dei rail (limitations #59).
- Le forme d'onda del banco (`run/`) non si committano.

## NON fa parte di questo lotto

- **L45d2b2**: dopo L62. Il suo prompt pronto è `data/2026-10-19/dopo-L60d2/NEXT-SESSION-L45d2b2.md`.
- L45d2b3 (con R153 in corto, Q146 a 0,41 W), L58.
- Le decisioni di ADR-086…090 non si riaprono, salvo che scatti un loro «Da riaprire se».
- Le righe mancanti di ADR-087…089 nell'indice `decisions/README.md` (trovate in L62a): solo se
  l'utente lo chiede.

## CHIUSURA

1. `STATE.md` con L62b **fatto** nella tabella dei lotti, e il prossimo (L45d2b2).
2. Riscrivi QUESTO file per il lotto successivo: per L45d2b2 parti da
   `data/2026-10-19/dopo-L60d2/NEXT-SESSION-L45d2b2.md`, e metti la riga «Nome della sessione: hi-fi
   preamp L45d2b2» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L62b` (quello del worktree).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
