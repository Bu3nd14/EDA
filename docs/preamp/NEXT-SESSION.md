# Prompt per la sessione successiva — L43 (la revisione umana del dossier)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L43** e si ferma. Non iniziarne un secondo.

## Il mandato

**L43 lo fa l'utente**: legge il dossier rigenerato in L42a (la scheda audio) e L42b
(l'alimentatore), e ogni cosa che trova diventa una voce di `docs/preamp/NONCOMPLIANCE.md`, col
suo requisito, la sua severità e la sua evidenza, come nella prima revisione umana (L5e).
L'ordine resta: **L43 → L44 (NC-004) → G1**.

Il ruolo della sessione è **trascrivere e dare evidenza**, non revisionare:

- **Non cercare difetti per conto tuo**, né prima né durante la lettura dell'utente. Se l'utente
  ha trovato qualcosa, il suo giudizio è il dato del lotto; un difetto trovato da te al suo posto
  distrugge l'informazione su cosa la revisione umana vede. Se ti chiede di verificare una sua
  osservazione, verifica **quella**, sui dati, e dì che cosa hai guardato.
- **Il soggetto è il prodotto**: il circuito, il suo comportamento misurato, le decisioni (ADR) e
  i disegni che lo rappresentano. Gli script, i banchi e la toolchain restano fuori: un loro
  difetto si annota a parte, senza aprire una non conformità di prodotto.
- **Le domande una alla volta, conversando**, quando servono davvero: niente questionari.
- I gradini al jack si dicono in **dB SPL di picco a 1 m** contro una stanza silenziosa, come il
  dossier; le tensioni solo fra parentesi.

## Come si legge il dossier

- La pagina: `/Users/roberto/EDA/docs/preamp/dossier/index.html` (dal checkout principale, dopo
  il merge di L42b). Le figure e i tre schemi (`gain_block.svg`, `preamp_blocks.svg`,
  `psu_blocks.svg`) stanno accanto, nella stessa cartella. Una copia autoconsistente, se serve:
  `/usr/bin/python3 docs/preamp/dossier/build_dossier.py --standalone <file.html>`.
- Venticinque sezioni: 1–15 la scheda audio, 16–22 l'alimentatore, poi i requisiti, «Cosa questo
  dossier non dice» e la provenienza. Sotto ogni titolo c'è il deck e la cartella dei dati da cui
  vengono i numeri: è l'evidenza che una voce deve nominare.
- Già scritti nella pagina, e **l'utente decide se diventano voci**: S del mute con la cima dei
  LED a 12 mA mai misurato (sezione del mute); la tenuta di `VRELAY` scesa da 62,8 a 36,1 ms a
  rete −10 % col carico di L41b1/L41b2, e il commento di `C_VRELAY` in `psu.py` che cita ancora
  L41a (sezione della potenza); i limiti di «Cosa questo dossier non dice».

## Come si scrive una voce

Il formato è in `NONCOMPLIANCE.md`, sezione «Formato di una voce»: requisito, severità
(bloccante / maggiore / minore, con la tabella «Severità, e cosa blocca davvero»), «Aperta da»,
stato; poi **Evidenza** (il file di dati sotto `docs/preamp/data/<data>/` e la misura) e **Cosa
serve per chiuderla**. Il numero è il successivo libero (l'ultimo aperto è NC-038, chiusa). La
severità la decide l'utente; tu proponi la tua lettura del requisito solo se te la chiede.

## Prima di tutto

- Leggi `CLAUDE.md` e, in `docs/preamp/STATE.md`, «In breve» e le voci di diario di L42a e L42b.
- In `NONCOMPLIANCE.md`: «A cosa serve», «Severità», «Formato di una voce», e l'elenco delle voci
  aperte (9, una bloccante: **NC-004**).
- `docs/preamp/data/2026-09-27/L42/README.md` e `docs/preamp/data/2026-09-27/L42b/README.md`:
  come sono state costruite le seconde strade, se l'utente chiede da dove viene una cifra.

## Lo stato che trovi

- Il dossier è rigenerato su tutte e due le schede; `build_dossier.py` passa, 47 sabotaggi su 47
  cadono (`data/2026-09-27/L42b/script/sabotaggi.txt`).
- **9 non conformità aperte, 1 bloccante**: **NC-004**, per G1.

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `awk` con programmi, i cicli con variabili e i percorsi calcolati a runtime.

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi.
- `vendor/` è di sola lettura, tranne che con `freeze_vendor.sh`.

## NON fa parte di questo lotto

- **Correggere** quello che l'utente trova: L43 apre le voci, i rimedi sono lotti successivi (e
  una modifica sostanziale ai requisiti vuole una ADR);
- **NC-004** (è L44), la misura di S a 12 mA, qualsiasi modifica al circuito, al firmware, ai
  deck o al dossier;
- il layout dei PCB (G2) e `src/main_attiny.c`.

## CHIUSURA

1. Le voci nuove in `NONCOMPLIANCE.md`, con la riga «Ultimo aggiornamento»; un report datato in
   `docs/preamp/reports/<data>-L43-revisione-umana.md` con le osservazioni dell'utente, **con le
   sue parole**, e dove sono finite.
2. `STATE.md` con L43 **fatto** e il prossimo lotto (L44) nella tabella.
3. Riscrivi QUESTO file per il lotto successivo (L44, NC-004: il modo si decide con l'utente
   all'inizio del lotto).
4. Commit, push, PR.
5. `/bin/zsh scripts/chunk_close.sh L43`.
6. Rimuovi il worktree coi comandi che lo script stampa.
7. **Fermati.**
