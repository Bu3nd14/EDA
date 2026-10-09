# Prompt per la sessione successiva — G1, il congelamento della topologia (e prima il dossier)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **un** lotto del percorso verso G1, e si ferma.

## Perché adesso

L'ordine scelto dall'utente il 2026-10-01 era L46 → L44 → L47 → L48 → **L49** → **G1** → L45 FMEA
→ L50 massa e terra. **L49 è chiuso** (L49a la scheda audio, L49b l'alimentatore e l'assieme, il
2026-10-09): **NC-048 chiusa**, e **nessuna non conformità bloccante per G1 resta aperta**
(`NONCOMPLIANCE.md`: 12 aperte, 1 bloccante, NC-044, per G2).

G1 congela la topologia. Lo fa `design-reviewer` (`AGENTS.md`), **offline su `main`, sul dossier e
sui dati misurati**, rieseguendo le verifiche da sé; il prodotto è un **report datato** in
`reports/` con le non conformità che apre (requisito, evidenza, severità, stato), non un veto su
un merge.

## Il primo punto: il dossier non è aggiornato

Il dossier (`docs/preamp/dossier/`, `build_dossier.py`) è di **L42** e il dossier **non si taglia**
sul percorso verso G1 (lo legge solo l'utente: niente avvisi di obsolescenza, si rigenera come
lotto). Prima di G1 va **rigenerato**. Cosa è cambiato da allora:

- il selettore d'ingresso (ADR-064): la scheda ingressi «a monte» non esiste più;
- **il volume è un potenziometro ALPS RK27 col bilanciamento MN, C_T e R_G (ADR-065)**: il dossier
  descrive l'attenuatore a scatti, e la frase «il trim sta dopo il condensatore d'uscita del blocco
  A» (falsa, NC-041) va riscritta da quello che c'è ora;
- il §14 di `build_dossier.py` («solo l'LSK489A porta KF», «niente distorsione») è superato da L44
  e L46a;
- il mute descritto è quello della VTL5C4, e il dossier cita `tb_e3_e5_ldr.cir` (ora
  `tb_e3_e5.cir`) e `tb_v2_mute_ldr.cir` (ora `tb_v2_mute_taglio.cir`), tutti senza celle;
- la tabella del mute legge la matrice di L29d2 con S: quella di oggi è di L48b (L47c2b1 più il
  gruppo 6 del volume), senza S, col clic dichiarato;
- la sezione dei guasti cita L41c / L42b: le cifre di oggi sono di L47c2b2;
- il firmware descritto è quello di L41b2: la legge delle LDR, 21 falsi, sette sequenze;
- **le schede di prova di L49a e L49b non ci sono**: vanno aggiunte, con le immagini (rame e
  render) e la pianta dell'assieme (`data/2026-10-09/L49a/`, `data/2026-10-09/L49b/psu/`,
  `data/2026-10-09/L49b/assembly/`) e i vincoli numerati dei due report;
- le righe `Stato:` di ADR-038, 039, 040, 049, 050, 058, 059, 060, 061 (superate o precisate da
  ADR-062 e prima), di ADR-032 e ADR-062 (precisate da ADR-063), di **ADR-009** (superata sul
  volume da ADR-065) e di **ADR-053** (E10 precisato da ADR-065) non lo dicono, e quelle di ADR-059
  e ADR-060 nominano ADR più vecchie (il controllo del punto 14 le rifiuta): si allineano con
  l'utente, toccando solo quella riga.

**Da chiedere all'utente all'inizio, per nome e senza sigle**: rigenerare il dossier in un lotto
proprio prima del gate (e se diviso, come), poi G1 nella sessione dopo. Raccomandato: sì, il
dossier prima, perché G1 lo legge.

## Il gate, quando ci si arriva

- `design-reviewer` lanciato **come agente nuovo**, mai come fork; riesegue, non si fida dei
  resoconti; il soggetto è **il prodotto** (circuito, misure, decisioni, disegni), non la
  toolchain: un difetto degli strumenti si annota a parte, senza aprire una non conformità.
- Se l'utente dice di aver trovato un difetto e vuole che lo trovi il revisore: **non cercarlo**,
  dichiara cosa hai già guardato, e scrivi l'esito comunque (controllo cieco).
- Cifre di distorsione dai macro-modelli generici: non sono credibili, e il revisore lo deve dire.

## Le scelte già fatte (non si richiedono)

- Il contenitore di prova: Modushop Pesante 3U, interni 415 × 300 × 115 mm; **il frontale da
  483 mm contro i 450 di P8 si decide al pre-layout** (scelta dell'utente in L49b).
- Due schede, due strati; le piste più larghe possibile; per l'alimentatore «2 strati, stretta
  solo al piedino» (L49b).

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md` (**54 voci**; nuove in L49b la #51–#54).
- `docs/preamp/STATE.md`: «In breve», **L49b**, L49a.
- `AGENTS.md`: i gate G1 / G2 / G3 e le regole operative.
- `NONCOMPLIANCE.md`: lo stato di ogni voce, NC-044, NC-050, NC-037.
- `PRB.md` (il contratto, 29 voci) e `REQUIREMENTS.md`.
- I report di L49a e L49b (i vincoli numerati che tornano al progetto).

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` e `run_simulation.sh` vanno lanciati da soli, senza redirect seguiti da altro);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che **contiene la parola «git»** anche solo
    in un testo;
  - un heredoc Python lungo da solo: gli script si scrivono su file con Write, i testi con Edit;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file. Il venv non è nel
  worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
- `docs/preamp/data/` è versionato per regola: i file grossi vanno in `.gitignore` prima del commit.
- `zsh` espande un `=` a inizio parola; un glob senza corrispondenze ferma il comando: `(N)` in coda.

## NON fa parte di questo percorso

- La FMEA (L45), la massa e la terra (L50), il layout vero (G2), la fabbricazione (G3).
- Cambiare il circuito per un vincolo di L49: si porta all'utente con una ADR, non si applica da sé
  (per esempio i relè separati per canale per accorciare le uscite, vincolo 2 di L49a).
- Tornare a una sfumatura del mute, o mettere un tetto al clic del taglio: li riapre solo l'utente.
- Togliere `models/optocoupler/nsl32sr3_comportamentale.lib` da `models/`: solo se l'utente lo
  chiede. L'adattatore `firmware/preamp_timer/src/main_attiny.c`.
- PR-14 nel PRB dice ancora «il selettore è ancora da progettare»: cambiarlo vuole una ADR, solo
  se l'utente lo chiede.

## CHIUSURA

1. `STATE.md` col lotto **fatto** nella tabella dei lotti e il prossimo indicato.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh <lotto>`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
