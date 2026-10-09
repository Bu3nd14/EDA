# Prompt per la sessione successiva — L51, il dossier rigenerato

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L51** (o la sua prima parte, se l'utente lo divide), e si
ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'utente, il 2026-10-09 dopo L49b: «rigeneriamo il dossier, mettilo nel prossimo lotto abbiamo
cambiato molto, poi lo passiamo all'avversariale di nuovo, poi affrontiamo G1». L'ordine è quindi
**L51** il dossier → **L52** l'architetto avversariale sul dossier nuovo → **G1** → L45 FMEA → L50
massa e terra.

Il dossier (`docs/preamp/dossier/`, `build_dossier.py`, PDF A4 con `stampa_a4.py`) è di **L42**
(2026-09-27). Lo legge **solo l'utente** e **non si taglia** sul percorso verso G1: si rigenera,
non si aggiungono avvisi di obsolescenza. Nessuna non conformità bloccante per G1 è aperta
(`NONCOMPLIANCE.md`: 12 aperte, 1 bloccante, NC-044, per G2).

## La regola del generatore (non cambia)

**Nessuna cifra del dossier è scritta a mano**: ogni numero si legge dai file versionati sotto
`docs/preamp/data/` e passa per una seconda strada indipendente; se le due divergono oltre la
tolleranza dichiarata il generatore **rifiuta e non scrive niente**. Nessun dato di un giorno in
cui il circuito era diverso da quello descritto. Il controllo del punto 14 (`contratto.py`) tiene
PRB, ADR e indice dei requisiti in biiezione.

## Cosa è cambiato da L42 (il mandato)

- **Il mute coi soli relè** (ADR-062, ADR-063): niente celle, niente sfumatura; il dossier
  descrive ancora la VTL5C4 e cita `tb_e3_e5_ldr.cir` (ora `tb_e3_e5.cir`) e `tb_v2_mute_ldr.cir`
  (ora `tb_v2_mute_taglio.cir`); la tabella del mute legge la matrice di L29d2 con S — quella di
  oggi è di **L48b** (L47c2b1 più il gruppo 6 del volume), senza S, col clic dichiarato.
- **Il selettore d'ingresso** (ADR-064, L48a): la scheda ingressi «a monte» non esiste più; F1 sul
  banco (`tb_f1_selettore.cir`).
- **Il volume a potenziometro ALPS RK27 col bilanciamento MN, C_T e R_G** (ADR-065, L48b): il
  dossier descrive l'attenuatore a scatti; la frase «il trim sta dopo il condensatore d'uscita del
  blocco A» (falsa, NC-041) va riscritta da quello che c'è ora.
- **Il §14 di `build_dossier.py`** («solo l'LSK489A porta KF», «niente distorsione») è superato da
  L44 (il flicker dei bipolari, ADR-057) e L46a (la compensazione, ADR-054 / 055).
- **L'alimentatore e il firmware**: il firmware descritto è quello di L41b2 (la legge delle LDR, 21
  falsi, sette sequenze): oggi è quello di **L47c2a** (19 falsi, sei sequenze, senza LDR); il
  pilota delle LDR non c'è più; la tenuta di `VRELAY` e lo standby di L47c2a / L48a; i guasti
  citano L41c / L42b: le cifre di oggi sono di **L47c2b2**.
- **Le schede di prova di L49** (nuove): la scheda audio (L49a) e l'alimentatore (L49b) con le
  immagini (rame e render), la pianta dell'assieme nel Pesante 3U, e i vincoli numerati dei due
  report (`data/2026-10-09/L49a/`, `data/2026-10-09/L49b/psu/`, `data/2026-10-09/L49b/assembly/`).
- **Le righe `Stato:` delle ADR**: ADR-038, 039, 040, 049, 050, 058, 059, 060, 061 (superate o
  precisate da ADR-062 e prima), ADR-032 e ADR-062 (precisate da ADR-063), **ADR-009** (superata
  sul volume da ADR-065) e **ADR-053** (E10 precisato da ADR-065) non lo dicono, e ADR-059 e
  ADR-060 nominano ADR più vecchie (il controllo del punto 14 le rifiuta): si allineano **con
  l'utente**, toccando solo quella riga.
- **PR-14** nel PRB dice ancora «il selettore è ancora da progettare»: cambiarlo vuole una ADR, solo
  se l'utente lo chiede. Portarglielo per nome.

## All'inizio, con l'utente

Misurare prima (quante sezioni cambiano, quanti dati sono da ricorrere), poi chiedere per nome e
senza sigle:

- **dividere o no** (in L42: L42a scheda audio, L42b alimentatore; qui c'è in più L49);
- le righe `Stato:` delle ADR, una per una;
- PR-14.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md` (**54 voci**; per il dossier in particolare #26, #37, e le
  trappole del generatore).
- `docs/preamp/STATE.md`: «In breve», «Dopo L49b», **L42a** e **L42b** (come si è rigenerato
  l'ultima volta), L42d (il contratto nel dossier).
- `docs/preamp/dossier/build_dossier.py` per intero, `contratto.py`, `stampa_a4.py`.
- I report da L44 a L49b.

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

## NON fa parte di questo lotto

- L'architetto avversariale (**L52**) e il gate (**G1**): vengono dopo, nell'ordine dell'utente.
- Cambiare il circuito, i deck o il firmware: il dossier li descrive com'è oggi. Un difetto trovato
  rigenerando si scrive e si porta all'utente, non si corregge da sé (vale anche per un rilievo
  che l'architetto potrebbe trovare: non cercarlo per lui).
- La FMEA (L45), la massa e la terra (L50), il layout vero (G2).
- Tornare a una sfumatura del mute, o mettere un tetto al clic del taglio: li riapre solo l'utente.
- Togliere `models/optocoupler/nsl32sr3_comportamentale.lib` da `models/`: solo se l'utente lo
  chiede. L'adattatore `firmware/preamp_timer/src/main_attiny.c`.

## CHIUSURA

1. `STATE.md` con L51 **fatto** (o le sue parti) nella tabella dei lotti, e il prossimo (**L52**).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L51` (o il nome della parte).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
