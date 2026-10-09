# Prompt per la sessione successiva — L49 (placement e routing di prova)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L49**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L48 è finito: il selettore d'ingresso (L48a, ADR-064, NC-040 chiusa) e la continua fuori dal
volume (L48b, ADR-065, **NC-041 chiusa**). Resta una sola non conformità bloccante per G1:

- **NC-048** — il dossier non garantisce che il progetto sia fattibile: nessun placement e routing
  di prova. Trovata dall'utente in L43b: «Non voglio scoprire alla fine che non basta lo spazio o
  che abbiamo problemi di placement che ci rimandano al design […] il dossier non fornisce garanzia
  di fattibilità senza un draft placing and routing.»

L'ordine dei lotti scelto dall'utente il 2026-10-01 resta: **L49** → **G1** → **L45** FMEA →
**L50** massa e terra.

## Il mandato

### 1. Prima le domande all'utente

Un placement di prova ha bisogno di tre cose che il repo non fissa ancora. Si chiedono **per nome**,
mai per sigle, con le alternative misurate o calcolate prima:

- **il contenitore candidato** (P8: «i PCB si verificano sulle misure interne del contenitore
  scelto»; PR-27: un solo telaio, grande quanto il SU-9070): le misure interne;
- **quante schede** e dove: la scheda audio e l'alimentatore (P4, ADR-048), i due toroidali (P3),
  i comandi a pannello di PR-19 (da L48b sei: selettore, volume, **bilanciamento**, trim, guadagno,
  interruttore di mute) e i loro cablaggi;
- **la tecnologia della scheda** per la prova: strati, tracce minime, THT o misto (oggi i
  footprint sono quasi tutti THT; i relè sono SMD).

Chiedere anche se L49 si divide (per esempio: la scheda audio / l'alimentatore).

### 2. Il lavoro (dopo le scelte)

- La pipeline esiste ed è collaudata solo sulla fixture RC: `smoke/run_pipeline.sh`, `kinet2pcb`
  sul Python di KiCad, Freerouting, `run_drc.sh`. Leggere `README.md` (workflow PCB) e le
  limitazioni sui due interpreti prima di scrivere codice.
- Le board vanno in una cartella nuova e versionata (non in `smoke/` o `pcb/`, che sono scratch);
  i dati sotto `docs/preamp/data/<data>/L49/`.
- Il risultato: le schede entrano nel contenitore? Il routing automatico completa? La DRC è
  pulita? E soprattutto **quali vincoli di piazzamento tornano al progetto**, ognuno col suo
  numero.
- È un draft: non sostituisce il layout di G2 né i requisiti di massa di NC-044 (L50).

### 3. Non conformità

NC-048 si chiude se il placement e il routing di prova completano dentro il contenitore candidato,
con la DRC pulita, e i vincoli trovati sono scritti. NC-050 resta aperta fino al carico congelato
(G2); NC-044 resta di L50.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md` (49 voci). In particolare per questo lotto:
  - i due interpreti (SKiDL sul venv 3.13, `pcbnew` / `kinet2pcb` sul Python 3.9 di KiCad);
  - `export_fab.sh` rifiuta su qualsiasi violazione di DRC, e non ha flag di bypass;
  - #22 rinumerazione, #23 i nomi delle reti fuse, #47 i riferimenti duplicati di SKiDL.
- `docs/preamp/STATE.md`: «In breve», **L48b**, L48a, L43b.
- `NONCOMPLIANCE.md`: **NC-048**, NC-044, NC-050.
- `PRB.md`: PR-19, PR-27, PR-28; `REQUIREMENTS.md`: **P8**, P1, P3, P4, F10.
- `decisions/ADR-029*`, `048*`, `065*`.
- Gli ingombri che pesano: C_T **C265 / C465** (10 µF in polipropilene, impronta
  `C_Rect_L31.5mm_W17.0mm_P27.50mm_MKS4`, ADR-065), i 4,7 µF d'uscita (`P22.50`), i 16 relè, le
  celle RC da 1000 µF (ADR-056), le tenute dell'alimentatore (P9: ≥ 1500 µF effettivi per rail,
  4700 µF su `VRELAY`).

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` e `run_simulation.sh` vanno lanciati da soli, senza redirect seguiti da altro);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che **contiene la parola «git»** anche solo
    in un testo (L47c2b2);
  - in L48b anche **un heredoc Python lungo da solo** è stato rifiutato («too complex to verify»):
    gli script si scrivono su file con Write, i testi si cambiano con Edit;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. Il venv non è nel worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
- I file di `models/` con un blocco del costruttore si modificano **sui byte** (#39).
- `docs/preamp/data/` è versionato per regola: le forme d'onda grosse vanno in `.gitignore` prima
  del commit.
- `zsh` espande un `=` a inizio parola: `echo =====` fallisce («not found»). Un glob senza
  corrispondenze ferma il comando: `(N)` in coda.
- Un deck ngspice che non finisce non dà errore: si sonda fermandolo a istanti crescenti, e si usa
  `/opt/homebrew/bin/timeout`.

## NON fa parte di questo lotto

- la FMEA (L45); la massa e la terra (L50);
- il circuito: L49 lo piazza e lo sbroglia, non lo cambia. Un vincolo che lo cambierebbe si porta
  all'utente con una ADR, non si applica da sé;
- tornare a una sfumatura del mute, o mettere un tetto al clic del taglio: li riapre solo l'utente;
- il volume a scatti: ADR-065 l'ha sostituito con un potenziometro e il bilanciamento, per scelta
  dell'utente (costo);
- togliere `models/optocoupler/nsl32sr3_comportamentale.lib` da `models/`: se ne decide con
  l'utente solo se lo chiede;
- l'adattatore `firmware/preamp_timer/src/main_attiny.c`;
- PR-14 nel PRB dice ancora «il selettore è ancora da progettare» nei dettagli: cambiarlo vuole
  una ADR, da allineare con l'utente solo se lo chiede;
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
  - le righe `Stato:` di ADR-038, 039, 040, 049, 050, 058, 059, 060, 061 (superate o precisate da
    ADR-062 e prima), di ADR-032 e ADR-062 (precisate da ADR-063), di **ADR-009** (superata sul
    volume da ADR-065) e di **ADR-053** (E10 precisato da ADR-065) non lo dicono, e quelle di
    ADR-059 e ADR-060 nominano ADR più vecchie (il controllo del punto 14 le rifiuta): si allineano
    con l'utente, toccando solo quella riga.

## CHIUSURA

1. `STATE.md` con L49 **fatto** (o le sue parti, se l'utente lo divide) e il prossimo lotto nella
   tabella (G1).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L49` (o il nome della parte).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
