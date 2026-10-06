# Prompt per la sessione successiva — L48b (la continua del blocco A attraverso trim e volume)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L48b**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L48 è stato diviso dall'utente all'inizio (2026-10-06, «Due parti»). La prima parte è fatta: il
selettore d'ingresso coi condensatori per ingresso (ADR-064), **NC-040 chiusa**. Resta la seconda
bloccante per G1 trovata dall'architetto avversariale (L43a):

- **NC-041** — la continua del blocco A attraversa trim e volume: ogni scatto del volume (e del
  trim) lascia un gradino al jack (PR-20, V2, F4), e il dossier dice il contrario. Oggi la
  continua nominale del blocco è −6,6 mV (ADR-056); sul prototipo la dispersione la riallarga
  (VGS1−VGS2 dell'LSK489 fino a 20 mV, β del VAS −36…+6 mV, R120/R119 ~7 mV per 1 %).

L'ordine dei lotti scelto dall'utente il 2026-10-01 resta: **L48b** → **L49** placement e routing
di prova → **G1** → **L45** FMEA → **L50** massa e terra.

## Il punto che L48a ha trovato, e che va misurato per primo

NC-041 e il vecchio prompt indicavano come rimedio **un condensatore all'ingresso del blocco B con
la sua resistenza di gate**. Un calcolo a mano di L48a (non ancora una simulazione) dice che **non
toglie il gradino**: a uno scatto la continua del cursore salta di V_A·Δ(rapporto), il salto passa
il condensatore come un gradino e poi decade con la sua costante di tempo, quindi il picco al jack
resta V_A·Δ(rapporto)·G_B. Toglie la continua dal blocco B, non il gradino. Lo stesso vale per il
trim. È scritto in NC-041 («Aggiornamento L48a»).

Le strade che il calcolo indica:
- **un condensatore prima del trim**, all'uscita del blocco A sul ramo variabile: il carico lì
  scende a 1,51 kΩ (la scala del trim ∥ l'attenuatore da 10 kΩ, `trim.py`), quindi ≥ 47 µF per
  ≤ 0,05 dB a 20 Hz (E9 ±0,2 dB su tutta la catena, col 4,7 µF d'uscita); un film di quella
  taglia è grosso, un elettrolitico bipolare va contro lo spirito di ADR-007 (polipropilene);
  alzare l'impedenza della scala del trim cambia ADR-027 ed E5;
- **una continua del blocco A più piccola**: ADR-007 ha escluso il servo («Nessun servo»); un
  trimmer al prototipo o la selezione delle parti non è un rimedio strutturale;
- **il condensatore all'ingresso del blocco B**, per avere il controfattuale misurato.

## Il mandato

### 1. Prima la misura, poi l'utente

Un banco (sotto `data/<data>/L48b/`) con la catena di `tb_trim.cir` e il blocco A con la sua
continua (−6,6 mV nominale e i due estremi della dispersione, per esempio ±30 mV): uno scatto del
volume in cima alla corsa (da 0 a −2 dB, il caso dell'architetto: 3,2 mV / 63,5 dB SPL a 0 dB,
10 mV / 73,5 dB SPL a +10 dB con −15,45 mV) e uno a metà corsa, a ogni guadagno, e un cambio del
trim; il picco al jack principale, in µV **e in dB SPL** contro una stanza silenziosa (100 µV =
33 dB SPL), per: oggi (il controfattuale), il condensatore al blocco B, il condensatore prima del
trim (valori e tipo), e se serve altro. Poi le domande all'utente.

Le domande si fanno **per nome**, mai per sigle; i livelli in **dB SPL**. Chiedere anche se L48b
si divide (la misura e la scelta / il sorgente e le misure rifatte).

### 2. Il lavoro (dopo le scelte)

- Il sorgente in `circuits/preamp/` (mai a mano le netlist), con la ADR che lo decide.
- E5 e il V1 del blocco B rimisurati (`tb_e3_e5.cir`, `tb_trim.cir`, `tb_loop.cir`; attenzione a
  limitations **#45**); E9 a 20 Hz su tutta la catena se si aggiunge un polo.
- **Il volume fra gli eventi del banco di V2**, con uno scatto in cima alla corsa a ogni guadagno
  (NC-041); il generatore è `data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py`, già senza
  celle e col contatto `BSERx` di ADR-063.
- La regressione dei 21 deck: `data/2026-10-06/L48a/script/regressione.sh` (copiarla nel lotto),
  il «prima» è `L48a/regressione/dopo`; `confronta.py` accanto.
- I controlli 2e / 2f se cambia il sorgente, coi loro falsi.

### 3. Non conformità

NC-041 si chiude solo con la misura sul circuito nuovo e col volume nel banco di V2. NC-050 resta
aperta fino al carico congelato (G2). La frase falsa del dossier (NC-041: «il trim sta dopo il
condensatore d'uscita del blocco A») si corregge quando si rigenera il dossier, non qui.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md`. Le trappole che falliscono in silenzio:
  - #22 rinumerazione, #23 i nomi delle reti fuse, #24 nodi del blocco, #29 `altermod`;
  - #33/#38/#40 il «transient op», #34 un `alter` che sopravvive a `destroy all`;
  - #35 la `tran` abortita che scrive zeri, #36 la PWL lunga;
  - #37 le Note nelle tabelle, #44 l'offset nel banco V2, #45 `meas min`.
- In ngspice, dentro `.control`, un `if $x = parola` con una **stringa** non confronta: esegue
  tutti i rami (L48a, il primo dimensionamento). Usare indici numerici, come i deck esistenti.
- SKiDL rinomina in silenzio un riferimento esplicito duplicato (SW3 → SW3_1, L48a): controllare
  i riferimenti nuovi contro la netlist.
- `docs/preamp/STATE.md`: «In breve», **L48a**, L47c2b2, L46b, L46a, L43a.
- `NONCOMPLIANCE.md`: **NC-041** (con l'aggiornamento di L48a), NC-050.
- `PRB.md`: PR-16, **PR-20**; `REQUIREMENTS.md`: F4, E5, E9, V1, **V2**.
- `reports/2026-09-27-L43a-architetto-avversariale.md` (rilievo R3),
  `reports/2026-10-06-L48a-selettore.md`.
- `decisions/ADR-064*`, `056*`, `054*`, `027*`, `007*`, `032*`, `063*`.

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
- il selettore d'ingresso (fatto, ADR-064), salvo che L48b lo tocchi per forza;
- tornare a una sfumatura del mute, o mettere un tetto al clic del taglio: li riapre solo l'utente;
- togliere `models/optocoupler/nsl32sr3_comportamentale.lib` da `models/`: se ne decide con
  l'utente solo se lo chiede;
- l'adattatore `firmware/preamp_timer/src/main_attiny.c`;
- PR-14 nel PRB dice ancora «il selettore è ancora da progettare» nei dettagli: cambiarlo vuole
  una ADR, da allineare con l'utente solo se lo chiede;
- rigenerare il dossier. Quando lo si rigenera:
  - il selettore d'ingresso (ADR-064) non c'è: la scheda ingressi «a monte» non esiste più;
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

1. `STATE.md` con L48b **fatto** (o le sue parti, se l'utente lo divide) e il prossimo lotto nella
   tabella (L49).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L48b` (o il nome della parte).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
