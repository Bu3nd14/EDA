# Prompt per la sessione successiva — L42 (il dossier rigenerato sul progetto di oggi)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L42** e si ferma. Non iniziarne un secondo. Se si divide (la
tabella dei lotti prevede probabilmente **L42a scheda audio, L42b alimentatore**), la divisione si
scrive nella tabella dei lotti di `STATE.md` prima di chiudere, e questa sessione fa solo la
prima metà.

## Il mandato

Il dossier (`docs/preamp/dossier/`, generato da `build_dossier.py`) è fermo a L32/L37, cioè ai
dati del 2026-09-15. È il documento con cui l'utente **guarda** il progetto, ed è l'ingresso di
**L43**, la sua revisione umana, la seconda dopo L5e. L'ordine è deciso dall'utente il
2026-09-26: L42 → L43 → L44 (NC-004) → G1.

Oggi il dossier non mostra:
- **scheda audio**:
  - V1 coi modelli del costruttore (L39, L40: Miller 1 nF, ADR-042);
  - il mute a LDR col profilo v4 e il relè al jack in serie, geometria iii, coi risultati di V2
    (L29a–L29e, ADR-044);
  - il guadagno interbloccato e i comandi a pannello (L36, L35, ADR-041, ADR-045);
  - il calore (L30, ADR-047);
- **alimentatore**, la seconda scheda: potenza, sorvegliante, temporizzatore, firmware e
  failsafe, coi numeri di L41a–L41c (ADR-048 … ADR-051);
- gli schemi di **tutte e due** le schede.

Le regole di `build_dossier.py` restano:
- **nessuna cifra scritta a mano**: ogni numero letto dai dati versionati;
- ogni numero passa per una **seconda strada** indipendente;
- rifiuta invece di scrivere quando le due strade divergono;
- nessun flag di bypass.

Estenderlo vuol dire puntarlo ai dati nuovi (`docs/preamp/data/2026-09-2*/`) con le stesse
garanzie, non incollare numeri dai report.

**Nessun avviso di obsolescenza** e nessun banner: il dossier lo legge solo l'utente. Niente PDF.

## Prima di tutto

- Leggi `CLAUDE.md` e `docs/limitations.md`.
- In `docs/preamp/STATE.md`: «In breve», le voci di diario da L29a a L41c, e le righe L42–L44
  della tabella dei lotti.
- `docs/preamp/dossier/build_dossier.py`, soprattutto la docstring e i controlli incrociati,
  e i README delle cartelle `data/` dei lotti da portare dentro.
- **Proponi all'utente la divisione e la scaletta delle sezioni prima di scrivere codice**: il
  dossier è per lui, e cosa mostrare (quali grafici, quali tabelle) è una sua scelta.

## Lo stato che trovi

- Ultimo lotto chiuso: SS dell'LSK489 (ADR-052, NC-027 chiusa, nessuna modifica al circuito).
- **9 non conformità aperte, 1 bloccante**: **NC-004**, per G1. Nessuna non conformità blocca il
  layout.
- Deck V2 versionato: `spice/preamp/tb/tb_v2_casopeggiore.cir`, generato da
  `data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py --matrice sorgente`.

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script;
  - `awk` con programmi, e i percorsi calcolati a runtime.

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi.
- `vendor/` è di sola lettura, tranne che con `freeze_vendor.sh`.
- Rigenerare una netlist SKiDL cambia ~1800 righe (tag casuali, tstamps): per dire che la
  connettività non è cambiata, confronta coi campi volatili tolti.

## NON fa parte di questo lotto

- **NC-004** (è L44), **NC-011**, **NC-037**;
- qualsiasi modifica al circuito o ai deck: il dossier legge, non cambia il progetto;
- la revisione umana (L43, la fa l'utente);
- il layout dei PCB (G2) e `src/main_attiny.c`.

## CHIUSURA

1. `STATE.md` con L42 (o L42a) **fatto** e il prossimo lotto nella tabella.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L42` (o `L42a`).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
