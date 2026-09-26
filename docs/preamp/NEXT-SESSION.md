# Prompt per la sessione successiva — L41b (il temporizzatore dell'alimentatore)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L41b** e si ferma. Non iniziarne un secondo. Se si divide
ancora (L41b1, L41b2…), la divisione si scrive nella tabella dei lotti di `STATE.md` prima di
chiudere.

## Il mandato

L41a ha portato in `circuits/preamp/psu.py` la potenza, `VRELAY`, il relè di rete e il
sorvegliante (**ADR-048**). Manca il **temporizzatore**, che oggi è il segnaposto **J509
`TIMER_IO`**. L41b lo realizza nella forma decisa dall'utente, cioè **ibrida** (ADR-048 punto 6):

1. **Il microcontrollore** (ammesso fuori dal segnale da ADR-022), con la sua **specifica
   scritta** come contratto verificabile. Deve fare:
   - la sequenza del mute: profilo v4 delle LDR, Td = 6 s, reversibile a metà (ADR-039/040,
     il contratto accanto a J3); `MUTE_CMD` 0,5 s dopo d = 1; `PERMIT_CMD` Δ dopo (20 ms
     nominali, ≥ 10 ms);
   - l'accensione dallo standby: `MAINS_REQ`, i rail, poi `PERMIT_CMD` non prima di 10 + 3 ms da
     `VRELAY` valida (ADR-027);
   - lo spegnimento morbido dal frontale (`FRONT_SW`): il mute completo, poi il relè di rete
     ≥ 50 ms dopo;
   - l'OR con SW3 (`MUTE_SW`, un filo rotto mette in mute) e il debounce;
   - dopo un buco di rete che i rail hanno retto (`MUTE_G` tirato giù dal rivelatore): il
     rilascio con la sequenza normale;
   - dopo un guasto con la rete presente: stacca K501 e resta spento fino a un nuovo comando
     dal frontale.
2. **L'ordine di sicurezza in hardware**: `PERMIT_CMD` si rilascia **non prima di Δ dopo
   `MUTE_G`**, per un ritardo RC fra `PERMIT_REQ` e `PERMIT_G`, e si eccita non dopo
   `MUTE_CMD`. Deve valere col micro morto o in reset.
3. **Il pilota delle LDR** su J3: dal micro una tensione di comando, poi un convertitore
   esponenziale analogico. Due stringhe (serie e derivazione), da 20 mA a 10 nA, con 10 nA di
   riposo mai a zero.
4. **NC-037, lo standby**: in standby il temporizzatore **toglie `VRELAY` alla scheda audio**
   (un interruttore sul lato alto verso J1 pin 4). Oggi le bobine del trim, pilotate di continuo
   in mute, fanno ~0,44 W da sole, contro 0,5 W. Poi il bilancio dello standby.

**La verifica**:
- la sequenza sul circuito, col micro comportamentale (le uscite come sorgenti che seguono la
  specifica);
- Δ in hardware col micro fermo;
- il profilo delle LDR contro la tabella di ADR-039 alle temperature del telaio;
- il 2j esteso ai pin di J509 sostituito.

## Prima di tutto

- **La scelta del micro** tocca l'utente solo se cambia qualcosa che vede: parlane
  conversando, con i numeri (consumo in standby, reperibilità, come si programma). Non con un
  questionario.
- **Il firmware non si simula in SPICE.** Proponi all'utente dove vive e come si prova (per
  esempio una specifica a tabella più un test sull'host), prima di scriverlo.
- **I bump si dicono in dB SPL di picco a 1 m contro il silenzio di una stanza**, non in mV.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`** (la #34 è nuova: un `alter` sopravvive a
   `destroy all`).
2. **`docs/preamp/STATE.md`**: la voce di diario di L41a, e le righe L41a, L41b, L41c.
3. **ADR-048** (tutta), **ADR-046**, **ADR-045** (Δ), **ADR-039** (il profilo v4), **ADR-027**
   (i 13 ms), **ADR-022** (il micro fuori dal segnale).
4. **Il report di L41a** (`reports/2026-09-26-L41a-alimentatore-potenza-sorvegliante.md`) e il
   README dei suoi dati: il generatore `genera_tb_psu.py`, da estendere.
5. **`circuits/preamp/psu.py`** (J509, `MUTE_G`, i sink, il sorvegliante), i contratti accanto
   a J3 e J4 in `preamp_audio.py`, `docs/preamp/SAFETY.md`, **NC-036** e **NC-037**.

## Quello che L41a ti consegna

- **Il sorgente** `psu.py` → `psu.net`, ERC con 16 avvisi e 2 «errori» spiegati nel sorgente.
- **Il banco** `data/2026-09-26/L41a/deck/genera_tb_psu.py`, generato dalla netlist:
  - rifiuta una parte che non conosce;
  - ogni caso rimette tutte le alterazioni a valore di netlist;
  - regolatori e comparatore sono comportamentali, dichiarati.
- **Le cifre**:
  - perdita di rete: `MUTE_CMD` rilasciato in 14,2–14,4 ms coi rail a 15 V;
  - un regolatore che cede: scatto a 13,56 / −13,52 V, tenuta dei rail 19,4 ms;
  - `VRELAY` ≥ 25 ms in tolleranza;
  - il guasto di U503: 32,9 ms sopra l'80 %.
- **Il 2j** (`scripts/check_psu_harness.py`): il cablaggio J1–J4 fra le schede, e il pad dei
  TPS7A a GND. 8 falsi in `data/2026-09-26/L41a/falsi/`.

## I vincoli

- **La scheda audio non si tocca.** Il deck V2 `spice/preamp/tb/tb_v2_casopeggiore.cir`
  rigenerato deve restare **byte-identico**. Se un contratto di J1, J3 o J4 non si può
  rispettare, si cambia con una ADR, all'utente.
- **Sicurezza di rete (P2)**: aggiorna `SAFETY.md` se tocchi la sezione rete.
- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script;
  - i cicli con variabili calcolate a runtime;
  - `awk -v`;
  - i `sed` con più `-e` o con `a\`;
  - i percorsi calcolati a runtime (anche `$CLAUDE_JOB_DIR` dentro un comando).

  Si usano comandi semplici, **percorsi assoluti**, script su file, ed Edit per i testi.
- Le forme d'onda del banco pesano ~100 MB a corsa: non si committano (il `.gitignore` di L41a).

## NON fa parte di questo lotto

- **L41c**, il banco di L30 col circuito vero, e la decisione sul corto dell'uscita di U503
  (~90 dB SPL, sotto il tetto);
- **NC-004** (il rumore 1/f, bloccante per G1);
- **NC-011** (la quota di ADR-020 coi TPS7A4701);
- **L28**;
- il dossier;
- il layout dei PCB e il contenitore (G2).

## CHIUSURA

1. `STATE.md` con L41b (o la parte fatta) **fatto** e il prossimo lotto.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L41b` (o il nome della parte).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
