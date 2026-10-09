# Prompt per la sessione successiva — L49b (l'alimentatore, i toroidali e l'assieme nel contenitore)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L49b**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L49 è stato diviso dall'utente il 2026-10-09 («Divisa»). **L49a è fatto**: la scheda audio si
piazza e si sbroglia, **399,0 × 162,8 mm**, due strati, routing al 100 % in 45 s, DRC 0 / 0
(`reports/2026-10-09-L49a-scheda-audio-prova.md`). Resta una sola non conformità bloccante per G1:

- **NC-048** — il dossier non garantisce che il progetto sia fattibile. L'utente, in L43b: «Non
  voglio scoprire alla fine che non basta lo spazio o che abbiamo problemi di placement che ci
  rimandano al design […] il dossier non fornisce garanzia di fattibilità senza un draft placing
  and routing.» La scheda audio regge; **l'assieme no ancora**.

L'ordine dei lotti scelto dall'utente il 2026-10-01 resta: **L49b** → **G1** → **L45** FMEA →
**L50** massa e terra.

## Le scelte già fatte (non si richiedono)

Dall'utente, il 2026-10-09:

- **il contenitore**: Modushop Pesante 3U — interni **415 mm fra i fianchi** (hifi2000; la pagina
  di Modushop dice 430) × **300** × ~115–120 mm;
- **le schede**: due, la scheda audio e l'alimentatore (P4);
- **la tecnologia**: due strati, le impronte del sorgente, tracce e isolamenti ≥ 0,25 mm;
- **le impostazioni globali di Freerouting** si possono cambiare («puoi cambiare i setting globali
  se serve»): il fan-out è spento (limitations #50).

## Il mandato

### 1. Misurare prima, poi chiedere solo ciò che il repo non fissa

La scheda audio lascia nel Pesante **8 mm per lato** e **137,2 mm** davanti (300 − 162,8). Lì
devono stare, o sopra / sotto con le quote:

- la **scheda dell'alimentatore** (`circuits/preamp/psu.net`, **118 parti, 48 cm²** di impronte;
  6 elettrolitici D16, due ponti KBL, il relè di rete G2RL, il portafusibile, le morsettiere);
- i **due toroidali** di P3 (2×15 V 50 VA per i rail; il piccolo per `VRELAY`, la logica e lo
  standby): le misure **vere** da un datasheet di un modello disponibile, non stimate;
- il **corpo dei comandi del frontale** (PR-19, da L48b sei: selettore SW4, volume ALPS RK27 col
  bilanciamento, trim SW1, guadagno SW2, mute SW3, il LED) — profondità dietro il pannello dai
  datasheet;
- l'**ingresso nel telaio dei 14 RCA** e della presa IEC con l'interruttore posteriore;
- le **distanze della sezione di rete** (P2, `SAFETY.md`).

Se non ci sta, **le leve sono già misurate** (report di L49a, «I vincoli»): compattare la scheda
audio (densità 32 %, `sweep_size.sh`), metterla a sbalzo sopra l'alimentatore, o spostare i
toroidali. Le alternative si portano all'utente **per nome**, coi numeri.

Da portare all'utente comunque: **il frontale del Pesante venduto oggi è 483 mm**, oltre i 450 di
P8 / PR-27 (ADR-029 citava 450 × 130). Gli interni di prova restano 415 × 300; la scelta del
contenitore è entro G2.

### 2. Il lavoro

- La pipeline c'è: `layout/preamp/audio/` (`make_board.py`, `place.py`, `route.py`, `run.sh`,
  `drc_summary.py`, `measure.py`). Per l'alimentatore una cartella sorella `layout/preamp/psu/`,
  con un piazzamento per gruppi suo (rete, trasformatori, rail, `VRELAY`, sorvegliante,
  temporizzatore) — **la sezione di rete separata** con le distanze di P2.
- L'assieme: un disegno in pianta (le due schede, i toroidali, i comandi, i RCA, la IEC) dentro i
  415 × 300 mm, con le quote; meglio se generato da script e versionato, come le schede.
- I dati sotto `docs/preamp/data/<data>/L49b/`, le immagini in PNG e PDF (l'utente le vuole
  vedere: «fammi poi vedere in qualche modo placement e routing»).

### 3. Non conformità

NC-048 si chiude se l'alimentatore si piazza e si sbroglia con la DRC pulita, e l'assieme entra
nel contenitore candidato coi comandi e i RCA, e i vincoli trovati sono scritti. NC-050 resta
aperta fino al carico congelato (G2); NC-044 resta di L50.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md` (**50 voci**). In particolare per questo lotto:
  - i due interpreti (SKiDL sul venv 3.13, `pcbnew` / `kinet2pcb` sul Python 3.9 di KiCad);
  - **#50** — il fan-out di Freerouting stringe le tracce: deve restare spento;
  - `export_fab.sh` rifiuta su qualsiasi violazione di DRC, e non ha flag di bypass;
  - #9 (`ImportSpecctraSES` dice solo vero / falso), #23 (i nomi delle reti fuse), #47.
- `reports/2026-10-09-L49a-scheda-audio-prova.md`: le iterazioni e **i sette vincoli**.
- `docs/preamp/STATE.md`: «In breve», **L49a**, L48b, L43b.
- `NONCOMPLIANCE.md`: **NC-048**, NC-044, NC-050.
- `PRB.md`: PR-19, PR-26, PR-27, PR-28; `REQUIREMENTS.md`: **P8**, P1, **P2**, P3, P4, P9.
- `decisions/ADR-029*`, `048*`; `SAFETY.md`.
- Le tenute dell'alimentatore (P9: ≥ 1500 µF effettivi per rail dopo i regolatori, 4700 µF su
  `VRELAY`).

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` e `run_simulation.sh` vanno lanciati da soli, senza redirect seguiti da altro);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che **contiene la parola «git»** anche solo
    in un testo (L47c2b2);
  - un heredoc Python lungo da solo («too complex to verify»): gli script si scrivono su file con
    Write, i testi si cambiano con Edit;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. Il venv non è nel worktree: `/Users/roberto/EDA/env/venv/bin/python3`. Il jar di
  Freerouting non è nel worktree: `/Users/roberto/EDA/scripts/tools/freerouting.jar`.
- Freerouting scrive una cartella `en/` dove parte (in `.gitignore`); le schede intermedie
  (~3 MB l'una) vanno in `.gitignore` come quelle di L49a.
- `docs/preamp/data/` è versionato per regola: i file grossi vanno in `.gitignore` prima del
  commit.
- `zsh` espande un `=` a inizio parola: `echo =====` fallisce. Un glob senza corrispondenze ferma
  il comando: `(N)` in coda.

## NON fa parte di questo lotto

- la FMEA (L45); la massa e la terra (L50): la massa resta una rete di tracce, come in L49a;
- il circuito: L49b lo piazza e lo sbroglia, non lo cambia. Un vincolo che lo cambierebbe si porta
  all'utente con una ADR, non si applica da sé (per esempio: relè separati per canale per
  accorciare le uscite di L49a, vincolo 2);
- il layout vero e la fabbricazione: sono di G2 / G3;
- tornare a una sfumatura del mute, o mettere un tetto al clic del taglio: li riapre solo l'utente;
- il volume a scatti: ADR-065 l'ha sostituito con un potenziometro e il bilanciamento;
- togliere `models/optocoupler/nsl32sr3_comportamentale.lib` da `models/`: solo se l'utente lo
  chiede;
- l'adattatore `firmware/preamp_timer/src/main_attiny.c`;
- PR-14 nel PRB dice ancora «il selettore è ancora da progettare»: cambiarlo vuole una ADR, solo se
  l'utente lo chiede;
- rigenerare il dossier. Quando lo si rigenera:
  - il selettore d'ingresso (ADR-064) non c'è: la scheda ingressi «a monte» non esiste più;
  - **il volume è un potenziometro ALPS RK27 col bilanciamento MN, C_T e R_G (ADR-065)**: il
    dossier descrive l'attenuatore a scatti e la frase «il trim sta dopo il condensatore d'uscita
    del blocco A» (falsa, NC-041) va riscritta da quello che c'è ora;
  - il §14 di `build_dossier.py` («solo l'LSK489A porta KF», «niente distorsione») è superato da L44
    e L46a;
  - il mute descritto è quello della VTL5C4, e il dossier cita `tb_e3_e5_ldr.cir` (ora
    `tb_e3_e5.cir`) e `tb_v2_mute_ldr.cir` (ora `tb_v2_mute_taglio.cir`), tutti senza celle;
  - la tabella del mute del dossier legge la matrice di L29d2 con S: la matrice di oggi è quella
    di L48b (L47c2b1 più il gruppo 6 del volume), senza S, col clic dichiarato;
  - la sezione dei guasti cita L41c / L42b: le cifre di oggi sono di L47c2b2;
  - il firmware descritto è quello di L41b2: la legge delle LDR, 21 falsi, sette sequenze;
  - le schede di prova di L49a / L49b non ci sono: vanno aggiunte, con le immagini;
  - le righe `Stato:` di ADR-038, 039, 040, 049, 050, 058, 059, 060, 061 (superate o precisate da
    ADR-062 e prima), di ADR-032 e ADR-062 (precisate da ADR-063), di **ADR-009** (superata sul
    volume da ADR-065) e di **ADR-053** (E10 precisato da ADR-065) non lo dicono, e quelle di
    ADR-059 e ADR-060 nominano ADR più vecchie (il controllo del punto 14 le rifiuta): si allineano
    con l'utente, toccando solo quella riga.

## CHIUSURA

1. `STATE.md` con L49b **fatto** (o le sue parti, se l'utente lo divide) e il prossimo lotto nella
   tabella (**G1**).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L49b` (o il nome della parte).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
