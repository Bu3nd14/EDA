# Prompt per la sessione successiva — L29e (la geometria iii nel sorgente)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L29e** e si ferma. Non iniziarne un secondo.

## Il mandato

**ADR-044** ha scelto il mute al jack in **geometria iii**, con le parole dell'utente del
2026-09-25: «iii», «Il bleed basta», «C dal datasheet + cavo realistico». La scelta prevede la
serie fra il condensatore d'uscita e il jack, più la derivazione a massa dal lato del
condensatore. L29d2 l'ha misurata **solo nel banco**: 0 celle fuori su 253.

Poi l'utente ha deciso: «chiudi la parte mute di NC-028, e L29e prima di L36». Questo lotto porta
la iii in `circuits/` e **conferma sul sorgente** la misura su cui la parte del mute è stata
chiusa. **Se il sorgente non riproduce le celle peggiori di L29d2, la parte del mute di NC-028 si
riapre**, e lo si dice all'utente.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`** (in particolare #29–#33).
2. **`docs/preamp/STATE.md`**: la voce di diario di L29d2, e le righe L29e e L36.
3. **`reports/2026-09-25-L29d2-matrice-contatto-serie.md`** per intero, in particolare §§ 4 e 5.
4. **ADR-044**, poi ADR-012, ADR-038 (punti 2 e 4), ADR-043.
5. **`NONCOMPLIANCE.md`**: NC-028 (l'aggiornamento di L29d2) e NC-014 (la trappola della
   piedinatura del G6K).

## IL LAVORO

1. **Il cablaggio** in `circuits/preamp/preamp_audio.py`: i tre G6K-2F-Y del mute al jack, su
   `MUTE_CMD`, righe ~353–425. La forma proposta in ADR-044 è **un deviatore per uscita**:
   - comune al lato del condensatore;
   - NC a massa;
   - NO al jack.

   Un relè serve ancora L e R con due scambi.
   - La **piedinatura** si legge dal datasheet: `vendor/relays/omron/G6K/en-g6k.pdf`, pagina 7.
     Non si eredita da un altro relè (NC-014). Il disegno è lo stato **diseccitato**.
   - Ogni valore non ovvio porta il commento che punta ad ADR-044.
   - **Se il deviatore non si fa** (poli, piedinatura, un altro motivo): ci si ferma e si porta
     all'utente. È una condizione di «Da riaprire se» di ADR-044.
2. **Il bleed lato condensatore**: nelle misure di L29d2 c'era, 220 k / 470 k. Nel deviatore
   conta solo durante il trasferimento, e non è mai stato misurato senza. **Decide l'utente**:
   tenerlo, oppure toglierlo dopo una prova.
3. **Rilettura**:
   - l'ERC;
   - il 2e di `run_tests.sh`, dove asserisce il cablaggio del mute (va aggiornato e fatto
     fallire una volta);
   - il deck versionato (`spice/preamp/tb/tb_v2_casopeggiore.cir` e i blocchi generati).

   Il blocco CANALE oggi ha il contatto al jack (`BJKx`, `SSER`, `RBYx`, `RBCx`). Se cambia, il
   generatore di L29c deve ridare L29c e L29d2 per differenza dichiarata, non per caso.
4. **P7**: la nota in `preamp_audio.py:421` dice che con i jack a massa gli stadi d'uscita vanno
   in classe B. Con la iii a massa va il **lato del condensatore**, dietro gli stessi 47 Ω: il
   carico visto dallo stadio non cambia. Va riletto e scritto, non assunto.
5. **Le celle peggiori di L29d2 sul sorgente**. Il sorgente è il deck generato da `circuits/`,
   non il banco. Le celle:
   - `gm0x10_lz` (il cambio a relè chiuso);
   - `x01000_dpmaxmax` (la dispersione);
   - `on_r300p` (l'accensione);
   - `mh01_1k` e `mh01_20` (la musica).

   Coi loro riferimenti, contro `data/2026-09-25/L29d2/tabella.csv`.

**Esito**:
- una tabella «sorgente contro banco»;
- NC-028 aggiornata: la parte del mute **confermata** o **riaperta**;
- nessuna ADR nuova, se il cablaggio è quello di ADR-044.

## I vincoli

- **Nessun cambio di topologia oltre ADR-044 senza l'utente.**
- `set numdgt=15` prima di ogni `wrdata` (#30); `pwl()` estrapola (#31); nessun corpo di `if`
  vuoto (#32); una corsa col transient op non vale (#33).
- Nel worktree `git` vengono rifiutati:
  - i comandi composti;
  - `awk -v`;
  - i `sed` con più `-e` o con `a\`;
  - i percorsi calcolati a runtime.

  Si usano comandi semplici, **percorsi assoluti**, script su file, ed Edit per i testi.
- I tempi di L29d2: sulla iii la dispersione e il mute a 1 kHz durano fino a 36 min a corsa;
  si lanciano per primi.

## NON fa parte di questo lotto

- **L36**, che viene dopo; L30 (lo spegnimento, le 7 corse che non finiscono, i 3,96 mV non
  spiegati); il failsafe di ADR-043; L35; L28; il dossier.

## CHIUSURA

1. `STATE.md` con L29e **fatto** e il prossimo lotto (**L36**).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L29e`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
