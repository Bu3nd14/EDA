# Prompt per la sessione successiva — L48 (il selettore d'ingresso e la continua)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L48**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

Il mute è chiuso: L47 (a, b, c) ha tolto le fotoresistenze, il mute taglia coi soli relè
(ADR-062), V2 regge (L47c2b1, ADR-063) e i guasti dell'alimentatore reggono (L47c2b2). L'ordine
dei lotti di rimedio è quello scelto dall'utente il 2026-10-01: **L48** selettore d'ingresso →
**L49** placement e routing di prova → **G1** → **L45** FMEA → **L50** massa e terra.

L48 chiude due non conformità **bloccanti per G1**, trovate dall'architetto avversariale (L43a):

- **NC-040** — l'ingresso è accoppiato in continua: il cambio d'ingresso porta sulle uscite la
  differenza fra le continue delle sorgenti (PR-14, F1). Stima dell'architetto: ~10 mV da
  un'uscita a valvole con un film da 1 µF, 100 volte i 100 µV del jack fisso.
- **NC-041** — la continua del blocco A attraversa trim e volume: ogni scatto del volume lascia un
  gradino al jack (PR-20, V2, F4), e il dossier dice il contrario. Oggi la continua nominale del
  blocco è −6,6 mV (ADR-056), ma sul prototipo la dispersione la riallarga.

Il selettore d'ingresso **non è mai stato progettato** (PR-14: «il selettore è ancora da
progettare»).

## Il mandato

### 1. All'inizio, con l'utente

Le domande si fanno **per nome**, mai per sigle; i livelli in **dB SPL** contro una stanza
silenziosa, non in mV. Prima di tutto chiedere se L48 si **divide** (è grande: il selettore, il
condensatore d'ingresso, quello del blocco B, il banco nuovo, e le misure rifatte).

Da portare coi numeri, misurati prima della domanda dove si può:

- **Il cambio d'ingresso**: un condensatore per ingresso con la sua resistenza a massa (il rimedio
  classico di NC-040), oppure commutare sotto mute. NC-040 dice «~13 s col profilo di oggi»: è
  **superato**, col mute che taglia il silenzio arriva in ~24 ms dal tasto (L47c2a). Le due strade
  non si escludono.
- **La continua di trim e volume**: un condensatore all'ingresso del blocco B con la sua
  resistenza di gate (il rimedio di NC-041). E5 e il V1 del blocco B si rimisurano.
- I relè del selettore (tipo, bistabili o no, chi li comanda: il firmware del temporizzatore ha
  6 pin liberi col buffer d'ingresso disattivato, `pin_liberi`).

### 2. Il lavoro (dopo le scelte)

- Il sorgente in `circuits/preamp/` (mai a mano le netlist), con la ADR che lo decide.
- E3 ed E5 rimisurati sull'ingresso nuovo (`tb_e3_e5.cir`, `tb_trim.cir`; attenzione a
  limitations **#45**, `meas min` che salta i 20 kHz).
- **F1 sul banco con due sorgenti a continue diverse** (NC-040).
- **Il volume fra gli eventi del banco di V2**, con uno scatto in cima alla corsa a ogni guadagno
  (NC-041); il generatore è `data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py`, già senza
  celle e col contatto `BSERx` di ADR-063.
- La regressione dei 21 deck (`data/2026-10-06/L47c2b2/script/regressione.sh`, il «prima» è
  `L47c2b2/regressione/dopo`); il firmware sull'host se lo si tocca.
- I controlli 2e / 2j se cambiano ingressi e cablaggio, coi loro falsi.

### 3. Non conformità

NC-040 e NC-041 si chiudono solo con la misura sul circuito nuovo. NC-050 resta aperta fino al
carico congelato (G2). La frase falsa del dossier (NC-041) si corregge quando si rigenera il
dossier, non qui.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md`. Le trappole che falliscono in silenzio:
  - #22 rinumerazione, #23 i nomi delle reti fuse, #24 nodi del blocco, #29 `altermod`;
  - #33/#38/#40 il «transient op», #34 un `alter` che sopravvive a `destroy all`;
  - #35 la `tran` abortita che scrive zeri, #36 la PWL lunga;
  - #37 le Note nelle tabelle, #44 l'offset nel banco V2, #45 `meas min`.
- `docs/preamp/STATE.md`: «In breve», **L47c2b2**, **L47c2b1**, L47c1, L46b, L43a, L43b.
- `NONCOMPLIANCE.md`: **NC-040**, **NC-041**.
- `PRB.md`: PR-11, PR-13, **PR-14**, PR-16, **PR-20**; `REQUIREMENTS.md`: F1, F3, F4, E3, E5, E12, V2.
- `reports/2026-09-27-L43a-architetto-avversariale.md` (rilievi R2, R3),
  `reports/2026-10-06-L47c2b2-guasti-regressione.md`.
- `decisions/ADR-062*`, `063*`, `056*`, `053*`, `038*` (superata), `007*`.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` e `run_simulation.sh` vanno lanciati da soli, senza redirect seguiti da altro);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che **contiene la parola «git»** anche solo
    in un testo (L47c2b2);
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. Il venv non è nel worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
- I file di `models/` con un blocco del costruttore si modificano **sui byte** (#39).
- `docs/preamp/data/` è versionato per regola: le forme d'onda grosse vanno in `.gitignore` prima
  del commit.
- `zsh` espande un `=` a inizio parola: `echo =====` fallisce («not found»).
- Un deck ngspice che non finisce non dà errore: si sonda fermandolo a istanti crescenti
  (`data/2026-10-06/L47c2b2/sonda_u503/`), e si usa `/opt/homebrew/bin/timeout`.

## NON fa parte di questo lotto

- il placement e il routing di prova (L49); la FMEA (L45); la massa e la terra (L50);
- tornare a una sfumatura del mute, o mettere un tetto al clic del taglio: li riapre solo l'utente;
- togliere `models/optocoupler/nsl32sr3_comportamentale.lib` da `models/`: se ne decide con
  l'utente solo se lo chiede;
- l'adattatore `firmware/preamp_timer/src/main_attiny.c`;
- rigenerare il dossier. Quando lo si rigenera:
  - il §14 di `build_dossier.py` («solo l'LSK489A porta KF», «niente distorsione») è superato da L44
    e L46a;
  - il mute descritto è quello della VTL5C4, e il dossier cita `tb_e3_e5_ldr.cir` (ora
    `tb_e3_e5.cir`) e `tb_v2_mute_ldr.cir` (ora `tb_v2_mute_taglio.cir`), tutti senza celle;
  - la tabella del mute del dossier legge la matrice di L29d2 con S: la matrice di oggi è quella
    di L47c2b1, senza S, col clic dichiarato;
  - la sezione dei guasti cita L41c / L42b: le cifre di oggi sono di L47c2b2;
  - il firmware descritto è quello di L41b2: la legge delle LDR, 21 falsi, sette sequenze;
  - la frase «il trim sta dopo il condensatore d'uscita del blocco A» è falsa (NC-041);
  - le righe `Stato:` di ADR-038, 039, 040, 049, 050, 058, 059, 060, 061 (superate o precisate da
    ADR-062 e prima), e di ADR-032 e ADR-062 (precisate da ADR-063), non lo dicono, e quelle di
    ADR-059 e ADR-060 nominano ADR più vecchie (il controllo del punto 14 le rifiuta): si allineano
    con l'utente, toccando solo quella riga.

## CHIUSURA

1. `STATE.md` con L48 **fatto** (o le sue parti, se l'utente lo divide) e il prossimo lotto nella
   tabella (L49).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L48` (o il nome della parte).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
