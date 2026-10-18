# Prompt per la sessione successiva — L60d2, i guasti sulla Stax e V2 con la media

Nome della sessione: **hi-fi preamp L60d2** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L60d2**, la seconda parte di L60d, e si ferma. Non iniziarne un
secondo, salvo che l'utente lo chieda esplicitamente nella sessione. Se L60d2 si rivela più grande
di una sessione, **dividilo con l'utente all'inizio** (per esempio: i guasti sulla Stax, poi V2).

## Perché questo lotto, e perché adesso

La prima parte (2026-10-18, `reports/2026-10-18-L60d1-ridondanza-e-inseguitore.md`) ha messo nel
sorgente la ridondanza di **ADR-086** nelle otto istanze del blocco: sul blocco del file **R150**
da 4,7 kΩ in parallelo a R109 (col guasto il margine resta ≥ 62,6°), **R112 / R151** due da 200 Ω,
**R144 / R152** due da 20 Ω. Ha trovato la causa di **NC-070** (la principale fuori in V2 col blocco
di L56):
- l'**inseguitore davanti al VAS** (Q146) non aveva limite: col mute inserito il blocco B non regge
  i 47 Ω, l'inseguitore conduce fino a 82 mA e satura il VAS, che ne esce di colpo con un fronte di
  134 ns; e in P7 dissipava **0,41 W** (NC-071, aperta e chiusa);
- **V2 campiona a 96 kHz senza anti-aliasing**: quegli impulsi diventano 132 µV di B1; con la media
  su ogni campione 3,3 µV (limitations #60).

L'utente (**ADR-087**): **«4,7 kΩ sul collettore»** (R153, costruita: Q146 a 0,027 W), **«Media su
ogni campione»**, **«Rimedio qui, metodo dopo»**. Regressione del blocco uguale (V1 −0,4°, E5
5,10 µV, V4 0 fuori su 48); scheda audio a 522 parti.

Restano due cose, e sono questo lotto:
- **NC-069** (maggiore, prima di G1): R109 aperta sulla Stax era 0,4–1,2 s sopra 0,87 V. Con R150
  l'anello resta chiuso; va provato coi guasti e P10.
- **NC-070** (maggiore, prima di G1, confermata dall'utente): si chiude con la matrice di V2 corsa
  col metodo nuovo, 0 verdetti fuori sulla principale.

## Che cosa costruire

1. **I guasti rifatti sulla Stax** (banco di L60c2, `data/2026-10-15/L60c2/script/genera_L60c2.py`:
   il gruppo `guasti` legge i modi da `p10_blocco.csv` di L45b, va esteso):
   - i modi di L45a delle parti nuove e sdoppiate, aperta e corto di ciascuna: R150, R151, R152, R153
     e R112 / R144 col valore nuovo, sulle posizioni A e F2, condensatore nominale e +5 %;
   - P10 sulla Stax sui modi della tabella di ADR-086 (R109 aperta, R112 aperta, la source di JQ110B
     aperta, Q133 in corto, R144 aperta): **R109 aperta sotto 150 ms**;
   - il resto dei modi di A e F2 non deve peggiorare. R153 in corto rimette l'inseguitore senza
     limite: misura anche la sua dissipazione (`p7_l56.py` della prima parte).
2. **V2 con la media su ogni campione** (ADR-087, che precisa ADR-032 e ADR-063):
   - in `scripts/v2_metodo.py` ogni campione a 96 kHz è la media del segnale di ngspice, lineare a
     tratti e senza diradamento, sul suo intervallo (`data/2026-10-18/L60d1/script/b1_confronto.py`
     lo fa già, ed è il riferimento);
   - la lettura di oggi resta come colonna di confronto;
   - gli autotest e i sabotaggi di `v2_metodo.py` (uno nuovo: il metodo vecchio deve far cadere il
     caso degli impulsi stretti); il 2k di `run_tests.sh` se li tocca;
   - una ADR solo se il metodo, scrivendolo, chiede una scelta che ADR-087 non ha fatto.
3. **La matrice di V2 rifatta** (~8 ore; i comandi in `data/2026-10-15/L60c2/README.md`), sul
   blocco finale col metodo nuovo: **0 verdetti fuori sulla principale**; il confronto con L48b e
   L60c2 per uscita (`verdetto_per_uscita.py` di L60c2).
4. **P7: la potenza di R123** in `tb_mute_corto.cir` si calcola con 91 Ω (`x123`), il valore di prima
   di ADR-054; oggi è 56 Ω. Correggere il deck e rifare `p7.py`.
5. **NC-069 e NC-070 si chiudono** se i numeri reggono; NC-042 avanza.

## Prima di tutto

- `CLAUDE.md`, `AGENTS.md`, `docs/limitations.md` (in particolare **#57–#61**).
- `docs/preamp/STATE.md`: «In breve» e le voci della prima parte di L60d e di L60c2.
- **ADR-087**, ADR-086, ADR-063, ADR-032, ADR-081, ADR-067.
- Il report della prima parte e `data/2026-10-18/L60d1/README.md`; `data/2026-10-15/L60c2/README.md`.
- `NONCOMPLIANCE.md`: **NC-069**, **NC-070**, NC-071, NC-042.

## I vincoli

- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB e dB SPL.
- Nel worktree vengono rifiutati:
  - i comandi composti, `cd … && script`, le variabili di shell nei percorsi, `xargs` sulla riga di
    comando, gli script lunghi passati sulla riga di comando (scriverli su file e lanciarli);
  - un comando che nomina la storia del repository in forma che il guardiano non sa verificare: le
    versioni vecchie dei file si estraggono prima di entrare nel worktree, o un file per comando;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito.
- Nei deck in AC l'interruttore con isteresi di ngspice resta aperto nel punto di lavoro: un contatto
  chiuso si scrive come resistenza (L60c1).
- Le corse dei guasti che si fermano presto si rifanno col metodo gear.
- Un punto di lavoro si giudica anche dalla corrente dei rail (limitations #59); un guasto di R109
  non si prova coi deck d'anello com'è (#61).
- `analizza_p10.py` di L45b vuole una cartella per corsa, e solo corse di guasto.
- Le forme d'onda del banco (`run/`) non si committano.

## NON fa parte di questo lotto

- **L45d2b2** (i diodi della tenuta, il regolatore negativo, il comando, i 5 V, i massimi, NC-063):
  dopo questo lotto. Il suo prompt pronto è `data/2026-10-15/L60c2/NEXT-SESSION-L45d2b2.md`: alla
  chiusura di questo lotto va in questo file, con le correzioni di L60d (ADR-087, R150–R153, la
  scheda a 522 parti, i vincoli di potenza della 47 Ω a ≥ 1,3 W e delle 22 Ω a ≥ 0,34 W).
- L45d2b3, L58. La finestra di livello su K3 (scartata in ADR-086).
- Le decisioni di ADR-086 e ADR-087 non si riaprono, salvo che scatti un loro «Da riaprire se».

## CHIUSURA

1. `STATE.md` con L60d2 **fatto** nella tabella dei lotti, e il prossimo (L45d2b2).
2. Riscrivi QUESTO file per il lotto successivo, con la riga «Nome della sessione: hi-fi preamp
   <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L60d2`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
