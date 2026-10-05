# Prompt per la sessione successiva — L47c2b2 (il mute coi soli relè: i guasti e la regressione)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L47c2b2**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L47c2b è stato diviso dall'utente all'inizio: **«Due parti»**. **L47c2b1** (fatto, nessuna ADR)
ha tolto le fotoresistenze dai deck V2 e S dal banco, e ha corso la matrice V2 col mute che taglia
(vedi `STATE.md`, diario di L47c2b1, e `reports/2026-10-05-L47c2b1-v2-senza-celle.md`).

**L47c2b2** chiude L47c: la catena dei guasti di L41c sull'alimentatore di L47c2a, i 21 deck
veloci, il firmware sull'host. Dopo, l'ordine dei lotti di rimedio resta quello dell'utente:
**L48** selettore d'ingresso → **L49** placement e routing di prova → **G1** → **L45** FMEA →
**L50** massa e terra.

## Il mandato

### 1. All'inizio, con l'utente

Le domande si fanno **per nome**, mai per sigle; i livelli in **dB SPL** contro una stanza
silenziosa, non in mV. Da portare: se `spegnimento_l` accorciato a TE + 1,1 s (lo fa già il
generatore di L47c2a) va bene, o se si tiene la durata di L41c (TE + 7,6 s), che con la sfumatura
tolta non serve più.

### 2. La catena dei guasti di L41c (`data/2026-09-26/L41c/README.md`, in due tempi)

- **Il primo tempo** usa il generatore di L47c2a (`data/2026-10-05/L47c2a/deck/genera_tb_psu.py`,
  `corri_seq.sh`, `tutti_seq.sh`). Ha già i casi di L41c (`spegnimento_l`, `perdita`,
  `perdita_min`, `guasto_u501`, `guasto` (U502), `guasto_u503`, `guasto_u503_min`, `cf_nodelta`,
  `corto_u503`) e `corri_seq.sh` ne conosce preambolo e fine.
- **I criteri r ed s** di L41c (il jack aperto prima che il guadagno possa muoversi; prima che V+
  scenda a 10,6 V) stanno in `L41c/psu/analizza_seq.py`, non in quello di L47c2a: vanno riportati.
  Scriverli prima delle corse.
- **Il ponte** (`L41c/ponte/estrai_ponte.py`) porta anche le correnti delle stringhe LED: togliere
  quel ramo (le stringhe non ci sono più). Il generatore V2 **non le legge più** (L47c2b1:
  `--matrice l41c` senza `is`/`ip`).
- **Il controllo del deck** `L41c/deck/controlla_deck.py` **rifiuta** il deck di oggi («BILS/BILP
  non sono quelli del ponte»): provato in L47c2b1 sui JSON di L41c. Va copiato nel lotto senza
  quel controllo, tenendo quello degli `alter` oltre 800 numeri (#36).
- **Il banco audio**: `genera_tb_v2_casopeggiore.py --matrice l41c --ponte <cartella>`, già senza
  celle e col contatto in serie col fronte di 4,55 µs (ADR-063: cambia anche il banco dei guasti,
  e va detto accanto al confronto con L46b); poi `corri.sh`, la guardia `L47b2b1/script/guardia_v2.py`, `solo_riuscite.py`,
  `analizza_par.py`, e la tabella di `L41c/script/tabella.py` (criteri di L41c: V2 per lo
  spegnimento morbido, 2 mV di obiettivo e 0,87 V di tetto per i guasti, il controfattuale deve
  fallire). Confronto con L46b (`data/2026-10-01/L46b/l41c/`), l'ultima ricorsa.
- **Attenzione alle colonne degli stati**: da L47c2b1 la `wrdata` degli stati non ha più le celle
  (`v(ina) v(vplus) v(vminus) v(main_a) …`). Ogni script che le legge **per posizione** va
  controllato: `L29c/script/verifica_partenza.py` le leggeva sbagliate senza errore, e L47c2b1 ne
  ha una copia corretta in `data/2026-10-05/L47c2b1/script/verifica_partenza.py`.

### 3. La regressione

- **I 21 deck veloci**: `docs/preamp/data/2026-10-05/L47c1/script/regressione.sh`, il «prima» è
  `L47c1/regressione/dopo`.
- **Il firmware sull'host** (il blocco 2k di `run_tests.sh`).

### 4. Non conformità

NC-050 resta aperta fino al carico congelato (G2). Le altre come le ha lasciate L47c2b1.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md`. Le trappole che falliscono in silenzio:
  - #22 rinumerazione, #23 i nomi delle reti fuse, #24 nodi del blocco, #29 `altermod`;
  - #33/#38/#40 il «transient op», #34 un `alter` che sopravvive a `destroy all`;
  - #35 la `tran` abortita che scrive zeri, #36 la PWL lunga;
  - #37 le Note nelle tabelle, #44 l'offset nel banco V2, #45 `meas min`.
- `docs/preamp/STATE.md`: «In breve», **L47c2b1**, **L47c2a**, **L47c1**, L41c, L46b.
- `decisions/ADR-063*` (il banco V2: il contatto in serie col fronte di 4,55 µs, che vale anche
  per `--matrice l41c`; il residuo con la musica), `062*`, `046*`, `051*`, `045*`.
- `reports/2026-10-05-L47c2b1-v2-senza-celle.md`, `reports/2026-10-05-L47c2a-firmware-alimentatore.md`,
  `reports/2026-09-26-L41c-banco-l30-circuito-vero.md`.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` e `run_simulation.sh` vanno lanciati da soli, senza redirect seguiti da altro);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. Il venv non è nel worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
- I file di `models/` con un blocco del costruttore si modificano **sui byte** (#39).
- `docs/preamp/data/` è versionato per regola: le forme d'onda grosse vanno in `.gitignore` prima
  del commit.
- `zsh` espande un `=` a inizio parola: `echo =====` fallisce («not found»).

## NON fa parte di questo lotto

- tornare a una sfumatura (fotoresistenze, JFET, relè a gradini, gradino fisso a −20 dB): l'ha
  deciso l'utente, e si riapre solo se lo chiede;
- il clic del taglio: dichiarato in L47c2b1, senza tetto (ADR-062); lo riapre solo l'utente;
- togliere `models/optocoupler/nsl32sr3_comportamentale.lib` da `models/`: se ne decide con
  l'utente solo se lo chiede;
- l'adattatore `firmware/preamp_timer/src/main_attiny.c`;
- il selettore d'ingresso e la continua del blocco A (L48); il placement e il routing di prova
  (L49); la FMEA (L45); la massa e la terra (L50);
- rigenerare il dossier. Quando lo si rigenera:
  - il §14 di `build_dossier.py` («solo l'LSK489A porta KF», «niente distorsione») è superato da L44
    e L46a;
  - il mute descritto è quello della VTL5C4, e il dossier cita `tb_e3_e5_ldr.cir` (ora
    `tb_e3_e5.cir`) e `tb_v2_mute_ldr.cir` (ora `tb_v2_mute_taglio.cir`), tutti senza celle;
  - la tabella del mute del dossier legge la matrice di L29d2 con S: la matrice di oggi è quella
    di L47c2b1, senza S, col clic dichiarato;
  - il firmware descritto è quello di L41b2: la legge delle LDR, 21 falsi, sette sequenze;
  - le righe `Stato:` di ADR-038, 039, 040, 049, 050, 058, 059, 060, 061 (superate o precisate da
    ADR-062 e prima), e di ADR-032 e ADR-062 (precisate da ADR-063), non lo dicono, e quelle di ADR-059 e ADR-060 nominano ADR più vecchie (il
    controllo del punto 14 le rifiuta): si allineano con l'utente, toccando solo quella riga.

## CHIUSURA

1. `STATE.md` con L47c2b2 **fatto** e il prossimo lotto nella tabella (L48).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L47c2b2`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
