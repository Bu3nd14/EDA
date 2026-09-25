# Prompt per la sessione successiva — L35 (comandi e LED a pannello nel sorgente)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L35** e si ferma. Non iniziarne un secondo.

## Il mandato

**ADR-028** e **NC-032**. Sul pannello passa solo la continua di bobine e LED, nessun segnale
(F10, F11). Nel sorgente oggi:
- i LED di trim (D4–D6, `trim.py`) e guadagno (D7–D9, `gain_interlock.py`) sono sulla scheda;
- SW1 e SW2 sono header a 16 vie;
- manca il comando del mute: `MUTE_CMD` non esce dalla scheda, e il LED rosso di mute non c'è.

L35 porta tutto questo a pannello, **senza cambiare la logica** provata dal 2e in L16 (trim) e
in L36 (guadagno, compresa la corsa al rilascio).

## Primo punto: ADR-045, deciso dall'utente il 2026-09-25

Il residuo di L36 **non è accettato**. È la manopola del guadagno girata fuori mute e poi il mute
inserito: fino a ~90 dB SPL di picco a 1 m, contro ~33 dB della soglia V2. Il trim ha lo stesso
caso. La decisione è **ADR-045**: K6 su un comando proprio, `PERMIT_CMD`.
- **All'inserimento del mute** `PERMIT_CMD` rilascia Δ (~20 ms, più dei 3 ms di rilascio massimo)
  **dopo** `MUTE_CMD`.
- **Al rilascio del mute** si eccita non dopo `MUTE_CMD`.

Lo si fa **prima** del pannello, perché cambia i fili del comando del mute.

**Parla dei bump in dB SPL contro il silenzio di una stanza, non in mV** (preferenza
dell'utente): soglia V2 ~33 dB di picco, stanza silenziosa ~25–35 dB(A).

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`** (in particolare #22).
2. **`docs/preamp/STATE.md`**: la voce di diario di L36 e la riga L35.
3. **ADR-045** (lo sfasamento di K6, con la nota per il failsafe), **ADR-028** (comandi e LED a
   pannello), **ADR-033** (LED dai relè, guasto accettato), **ADR-041** e il report di L36.
4. **`circuits/preamp/trim.py`**, **`circuits/preamp/gain_interlock.py`**,
   **`circuits/preamp/preamp_audio.py`** (`MUTE_CMD`, J1) e **`scripts/check_relay_safe_state.py`**
   (la visita `reach()` e le prove del trim e del guadagno).

## IL LAVORO

0. **ADR-045 nel sorgente.**
   - La bobina di K6 va su `PERMIT_CMD`, e `PERMIT_CMD` va al connettore con `MUTE_CMD`.
   - Il contratto col temporizzatore si scrive accanto al connettore, come fa J3 per le LDR:
     all'inserimento Δ dopo `MUTE_CMD`, al rilascio non dopo.
   - Il 2e oggi vuole la bobina del permissivo sulle net del mute. Va riscritto: bobina su
     `PERMIT_CMD`, e nella prova d'interblocco K6 trattato come «eccitato fuori mute».
   - Va fatto fallire, per esempio con K6 di nuovo su `MUTE_CMD`.
   - Poi NC-028 per la parte che chiude, e nessuna ADR nuova se la realizzazione è quella di
     ADR-045.
1. **Gli header di cablaggio** al posto dei LED sulla scheda, per il trim e il guadagno.
   - Ref nuove **esplicite**; nessuna parte esistente si rinumera (#22).
   - Il 2e oggi riconosce i LED del guadagno dal loro **anodo sui contatti degli ausiliari**. Se
     i LED escono dalla scheda, la prova dei LED va riscritta sul connettore, e rifatta fallire.
2. **SW1 e SW2 a pannello**: restano header, e il cablaggio non cambia. La tabella di SW2 è in
   `gain_interlock.SW_TABLE` e, come dato, in `check_relay_safe_state.GAIN_KNOB`.
3. **L'interruttore di mute combinato col temporizzatore d'accensione** (F10): il mute è inserito
   se l'interruttore lo chiede **oppure** se il temporizzatore non è scaduto.
   - `MUTE_CMD` va a un connettore.
   - Il temporizzatore resta all'alimentatore: qui c'è solo il contratto.
4. **Il LED rosso di mute** (F11), letto da un contatto che dica lo stato vero.
5. **Il 2e esteso** a quanto sopra, e fatto fallire su varianti sabotate, come
   `data/2026-09-25/L36/falsi/`.
6. **Il budget delle bobine e dei LED** aggiornato, se cambia (L36: 168,8 mA a 5 V a +10 dB).

**Esito**: sorgente, 2e esteso e fatto fallire, NC-032 aggiornata o chiusa, ADR nuova solo se la
realizzazione si scosta da ADR-028.

## I vincoli

- **Nessun cambio di topologia oltre ADR-028 e ADR-045 senza l'utente.** La logica di interblocco di trim
  e guadagno non si tocca.
- Il deck V2 versionato si rigenera dalla netlist e deve restare **byte-identico**: L35 non
  tocca il segnale.
- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script;
  - `awk -v`;
  - i `sed` con più `-e` o con `a\`;
  - i percorsi calcolati a runtime (anche `$CLAUDE_JOB_DIR` dentro un comando).

  Si usano comandi semplici, **percorsi assoluti**, script su file, ed Edit per i testi.

## NON fa parte di questo lotto

- **L30** (lo spegnimento, le 7 corse che non finiscono, i 3,96 mV non spiegati);
- il failsafe di ADR-043, con la nota di ADR-045: alla caduta di `VRELAY` lo sfasamento sparisce.
  È di L30;
- L28;
- l'alimentatore;
- il dossier;
- la proposta per il trim, se l'utente non la sceglie.

## CHIUSURA

1. `STATE.md` con L35 **fatto** e il prossimo lotto.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L35`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
