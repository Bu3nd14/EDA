# Prompt per la sessione successiva — L36 (il guadagno interbloccato dal mute)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L36** e si ferma. Non iniziarne un secondo.

## Il mandato

**ADR-041** ha deciso la forma, con le parole dell'utente del 2026-09-22: «interlock al mute,
come TRIM, nessuna invenzione, avremo LED anche per il guadagno».
- Il guadagno si cambia **solo a mute inserito**, come il trim (F8, ADR-027). Fuori mute il
  selettore non muove nulla.
- **Niente mute automatico.**
- **LED dello stato vero** del guadagno, come quelli del trim (F9).

La realizzazione è la **strada B di ADR-030**:
- K1 e K5 restano monostabili;
- ciascuno ha un relè ausiliario in autoritenuta fuori mute;
- i tre LED si leggono dai poli liberi degli ausiliari.

L29c ha soddisfatto il criterio 3 di ADR-030 (il cambio sotto mute seguito dal rilascio regge).
L29e ha portato nel sorgente il mute al jack in geometria iii (ADR-044), su cui L36 si appoggia:
**«col jack a massa» di ADR-038 punto 4 si legge ora «col lato del condensatore a massa e il jack
staccato».**

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`** (in particolare #22 e #29–#33).
2. **`docs/preamp/STATE.md`**: la voce di diario di L29e e la riga L36.
3. **ADR-041**, poi ADR-030 (la strada B e perché i bistabili sono stati scartati), ADR-027
   (il trim: permissivo K6, bistabili, spie), ADR-026 (K5 mai senza K1), ADR-044.
4. **`circuits/preamp/trim.py`** e **`circuits/preamp/preamp_audio.py`** (K1, K5, K6,
   `MUTE_CMD`), e **`scripts/check_relay_safe_state.py`**: la prova di raggiungibilità
   dell'interblocco del trim (`interlock()`), che L36 estende al guadagno.
5. **`reports/2026-09-25-L29e-geometria-iii-sorgente.md`**.

## IL LAVORO

1. **Il cablaggio** in `circuits/`: i due relè ausiliari con autoritenuta su K1/K5, sul comando
   del mute.
   - **Piedinatura dal datasheet** (`vendor/relays/omron/G6K/en-g6k.pdf`: il G6K-2F-Y è a
     **pagina 6** del PDF; la mappa è l'unica copia in `preamp_audio.py`). Mai dedotta (NC-014).
   - Ref nuove **esplicite** o in fondo: nessuna parte esistente si rinumera (#22).
   - Ogni valore non ovvio porta il commento che punta ad ADR-041/ADR-030.
2. **La corsa al rilascio del mute**: lo scambio di K6 contro il rilascio delle bobine. Va
   simulata e chiusa. **Se non si chiude con la strada B, ci si ferma e si porta all'utente**: è
   il «Da riaprire se» di ADR-041.
3. **Il 2e esteso al guadagno**: fuori mute nessuna bobina di guadagno raggiungibile dal
   selettore, in mute tutte. Va fatto fallire su varianti sabotate, come
   `data/2026-09-25/L29e/falsi/`.
4. **I tre LED dello stato vero** dai poli liberi degli ausiliari.
5. **Il budget delle bobine** (~169 mA fuori mute a +10 dB, a 5 V) consegnato all'alimentatore,
   scritto dove psu-engineer lo troverà.
6. Se la corsa si chiude bene: **rivalutare la stessa strada per il trim**, come proposta
   all'utente, non come modifica.

**Esito**: sorgente, 2e esteso, corsa simulata, budget; NC-028 aggiornata per la parte che L36
tocca; ADR nuova solo se la realizzazione si scosta da ADR-041/ADR-030.

## I vincoli

- **Nessun cambio di topologia oltre ADR-041/ADR-030 senza l'utente.**
- `set numdgt=15` prima di ogni `wrdata` (#30); `pwl()` estrapola (#31); nessun corpo di `if`
  vuoto (#32); una corsa col transient op non vale (#33).
- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script;
  - `awk -v`;
  - i `sed` con più `-e` o con `a\`;
  - i percorsi calcolati a runtime (anche `$CLAUDE_JOB_DIR` dentro un comando).

  Si usano comandi semplici, **percorsi assoluti**, script su file, ed Edit per i testi.
- Il deck V2 versionato (`spice/preamp/tb/tb_v2_casopeggiore.cir`) da L29e si **genera dalla
  netlist** (`--matrice sorgente`): se L36 tocca il mute al jack, il generatore rifiuta finché
  la netlist non è di nuovo la iii.

## NON fa parte di questo lotto

- **L35** (comandi e LED a pannello nel sorgente), che viene dopo; **L30** (lo spegnimento, le 7
  corse che non finiscono, i 3,96 mV non spiegati); il failsafe di ADR-043; L28; il dossier.

## CHIUSURA

1. `STATE.md` con L36 **fatto** e il prossimo lotto.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L36`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
