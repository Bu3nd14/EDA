# Prompt per la sessione successiva — L42b (il dossier, l'alimentatore)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L42b** e si ferma. Non iniziarne un secondo.

## Il mandato

L42 è stato diviso dall'utente il 2026-09-27: la scheda audio è fatta (il lotto precedente), qui
si porta nel dossier **la seconda scheda, l'alimentatore**. Il dossier è `docs/preamp/dossier/`,
generato da `build_dossier.py`; è l'ingresso di **L43**, la revisione umana. L'ordine resta:
L42b → L43 → L44 (NC-004) → G1.

Da portare dentro, coi numeri dei lotti e dalle loro cartelle `data/`:
- **potenza, `VRELAY`, relè di rete, sorvegliante** (L41a, ADR-048): `data/2026-09-26/L41a/`
  (`rete/analisi.csv`, `guasti/analisi.csv`, `scelte/`);
- **temporizzatore, hardware** (L41b1, ADR-049): Δ in hardware, standby, pilota delle LDR
  (`data/2026-09-26/L41b1/timer/`, `ldr/`);
- **firmware** (L41b2, ADR-050): le 7 sequenze sul circuito (`seq/`), la tabella delle LDR a 12 mA
  (`ldr/`); i test sull'host stanno già nel 2k di `run_tests.sh`;
- **spegnimento e failsafe sul circuito vero** (L30, L41c, ADR-046, ADR-051):
  `data/2026-09-26/L41c/tabella.csv`, `data/2026-09-26/L30/tabella.csv` (i gradini al jack si
  dicono in dB SPL, come nelle tabelle);
- **lo schema a blocchi di `psu.py`**: oggi non esiste nessun disegno dell'alimentatore. Sul
  modello di `docs/preamp/schematic/preamp_blocks_draw.py`: un diagramma a blocchi, ogni cifra
  letta da `circuits/preamp/psu.net` e asserita, il builder che lo copia accanto alla pagina.

Le regole di `build_dossier.py` restano:
- **nessuna cifra scritta a mano**: ogni numero letto dai dati versionati;
- ogni numero passa per una **seconda strada** indipendente (una ricorsa, un ricalcolo da un file
  a monte, uno script rieseguito);
- rifiuta invece di scrivere quando le due strade divergono;
- nessun flag di bypass;
- ogni controllo nuovo si fa fallire: si aggiunge a `data/2026-09-27/L42/script/sabotaggi.py`, o
  a una copia nella cartella di L42b.

**Nessun avviso di obsolescenza** e nessun banner: il dossier lo legge solo l'utente. Niente PDF.

## Prima di tutto

- Leggi `CLAUDE.md` e `docs/limitations.md` (ora 37 voci; la **#37** è di L42a e riguarda ogni
  log letto riga per riga).
- In `docs/preamp/STATE.md`: «In breve», le voci di diario da L30 a L42a, e le righe L42–L44 della
  tabella dei lotti.
- `docs/preamp/data/2026-09-27/L42/README.md`: come L42a ha costruito le seconde strade.
- `docs/preamp/dossier/build_dossier.py`: la docstring, `measure_l40`, `measure_mute`,
  `measure_heat`, `log_lines` (le `print` spezzate).
- **Proponi all'utente la scaletta delle sezioni dell'alimentatore prima di scrivere codice**:
  quali grafici e quali tabelle è una sua scelta, come per L42a.

## Lo stato che trovi

- Il dossier della scheda audio è rigenerato sul circuito di oggi; `build_dossier.py` passa,
  15 sabotaggi su 15 cadono.
- **9 non conformità aperte, 1 bloccante**: **NC-004**, per G1.
- **Trovato in L42a, non in questo lotto**: S del mute con la cima dei LED a 12 mA (ADR-050) non è
  mai stato misurato; la matrice di V2 è corsa a 20 mA. È scritto nel dossier ed è materia per L43.

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `awk` con programmi, e i percorsi calcolati a runtime.

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi.
- `vendor/` è di sola lettura, tranne che con `freeze_vendor.sh`.
- Le forme d'onda grandi (`.dat`, `wrdata`) non si committano: si tengono analisi, tabelle, log.

## NON fa parte di questo lotto

- **NC-004** (è L44), **NC-011**, **NC-037**; la misura di S a 12 mA;
- qualsiasi modifica al circuito, al firmware o ai deck: il dossier legge, non cambia il progetto;
- la revisione umana (L43, la fa l'utente);
- il layout dei PCB (G2) e `src/main_attiny.c`.

## CHIUSURA

1. `STATE.md` con L42b **fatto** e il prossimo lotto (L43) nella tabella.
2. Riscrivi QUESTO file per il lotto successivo (L43 lo fa l'utente: il prompt gli dice come
   leggere il dossier e dove scrivere ciò che trova).
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L42b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
