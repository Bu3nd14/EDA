# Prompt per la sessione successiva — L29b, ripresa (mute graduale a monte con LDR)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è
organizzato in LOTTI PICCOLI: questa sessione **riprende L29b**, che è rimasto a metà, e
si ferma. Non iniziarne un secondo.

## ATTENZIONE: il lavoro sta su un ramo non mergiato

- Ramo **`worktree-L29b`**, pushato su origin. **`main` non lo contiene.**
- Il worktree era `/Users/roberto/EDA/.claude/worktrees/L29b`. Se non esiste più, rientra
  dal ramo:
  `git worktree add .claude/worktrees/L29b worktree-L29b`
  e lavora lì (EnterWorktree con `path`).
- Verifica prima di tutto: `git log --oneline -12` sul ramo deve mostrare i commit
  «L29b (in corso)».

## Cosa è successo nella sessione interrotta (2026-09-16)

Leggi la voce **«L29b — IN CORSO»** in cima al diario di `STATE.md`. In breve:

1. L29b è stato **diviso**: il caso peggiore di V2 è **L29c**.
2. **ADR-037**: MOSFET contrapposti con driver fotovoltaico al jack. Scelta dell'utente,
   poi **superata** nella stessa sessione:
   - il modello del MOSFET non ha regione sottosoglia;
   - rampe calcolate da 7–10 s;
   - il banco non converge alle tolleranze di V2.
3. Una **ricerca in rete**, chiesta dall'utente, ha trovato che l'industria muta a monte e
   che nessuno punta a soglie come le nostre.
4. **ADR-038**, decisione dell'utente («Opzione 1 più ipotesi 1»):
   - **mute graduale a monte**: LDR VTL5C4 in serie e verso massa all'ingresso del
     blocco A;
   - **relè NC al jack tenuto**: si chiude solo a musica spenta;
   - **guadagno e trim si cambiano solo col jack a massa**;
   - un'unica variabile di profondità, reversibile se l'utente inverte il mute a metà.
5. Ultimo passo: `models/optocoupler/vtl5c4_comportamentale.lib`, **mai eseguito con
   successo**. La prova è stata interrotta senza cifre.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`**.
2. **`docs/preamp/STATE.md`**: la voce L29b in cima al diario, le righe L29b, L29c e L36.
3. **`docs/preamp/decisions/ADR-038-mute-graduale-ldr-a-monte.md`** per intero; ADR-037
   (superata) solo per il contesto; ADR-036, ADR-035, ADR-032.
4. **`docs/preamp/REQUIREMENTS.md`**: V2 per intero, E3, E5, F5 con la sua nota, F6, F8,
   P7.
5. **`docs/preamp/NONCOMPLIANCE.md`**: NC-028.
6. **I dati di L29b**, `docs/preamp/data/2026-09-16/L29b/`: i README di ogni cartella, e
   `vtl5c4_modello/genera_modello.py`.

## IL LAVORO CHE RESTA, in ordine

1. **Far girare `vtl5c4_modello/prova_modello.cir`** e confrontarlo coi punti digitalizzati
   (`tabelle.py`): statica a 0,2 / 1 / 10 / 40 mA; spegnimento da 40 mA a 105, 305, 689 ms;
   10 s.
   - La corsa superava i 300 s: prova `tran` con passo più largo, e lanciala in
     background.
   - Se il modello non riproduce la sua fonte, correggi il generatore, **non il .lib**.
   - Poi la voce in `validate_models.py --check-provenance`, e aggiorna `notes` nella
     provenance.
2. **Scratch col metodo di V2 sulla catena intera.** Tolti gli elementi ideali, due LDR per
   canale all'ingresso del blocco A, comando dei LED ideale, relè al jack alla profondità
   completa.
   - Tolleranze del blocco CANALE: `vntol=1e-6 abstol=1e-12`. Se non converge,
     **dillo**, non allentare in silenzio.
   - Misura:
     - C della dissolvenza a 1 kHz sulle tre uscite, col pavimento;
     - C alla chiusura del relè a 20 kHz (ADR-038 stima 0,57 mV);
     - il carico minimo sulla sorgente durante la dissolvenza (ipotesi ≥ 10 kΩ, serie
       alta prima che la derivazione scenda);
     - l'inversione a metà.
3. **Con i numeri, torna dall'utente** se la dissolvenza è molto peggiore dell'ideale di
   ADR-036, o se le tolleranze non tengono.
4. **Il sorgente.** In `circuits/preamp/preamp_audio.py`:
   - LDR, comando dei LED fuori dal percorso del segnale (ADR-022) e la variabile di
     profondità;
   - il relè al jack che segue la profondità completa;
   - poi netlist, disegni (2d), diagramma a blocchi (2f) e `check_relay_safe_state.py`,
     fatto fallire prima di fidarsene.
5. **Il deck versionato** `spice/preamp/tb/tb_v2_mute_ldr.cir`:
   - lo stesso blocco CANALE (`v2_metodo.py canale`);
   - tre uscite, 10 e 100 kΩ, 20 Hz / 1 kHz / 20 kHz, A senza segnale, B, C2 col pavimento;
   - corse lunghe in background, con `save`.
6. **E3 ed E5 con la LDR in serie; P7 riletto** (ADR-038: a mute inserito gli stadi d'uscita
   non hanno segnale).
7. **L'esito.** NC-028 resta aperta (manca L29c) e si aggiorna. Report datato.

Se non entra in una sessione, **dividi di nuovo** (L29b / L29b2) in `STATE.md` e chiudine
uno.

## I vincoli

- **Il metodo di V2 non si cambia in silenzio.**
- **Il modello VTL5C4 è comportamentale**: ogni cifra porta «modello comportamentale dal
  datasheet, con estrapolazione dichiarata». NC-028 non si chiude su un deck solo.
- **Trappole già pagate in L29b**:
  - un LED pilotato solo da un generatore di corrente senza percorso DC fa fallire l'op, e
    ngspice non dà errore;
  - un nodo flottante di source si pompa al picco del segnale;
  - `reltol` ≥ 1e-5 o `abstol` ≥ 1e-9 sono più larghi di B e di C.
- **Nessun cambio di tecnica senza l'utente**: ADR-038 è la sua decisione.

## Cosa NON accettare

- Una cifra su `v(OUT)`, o senza il metodo di V2.
- Un modello che non riproduce i punti da cui è stato generato.
- **Tolleranze allentate senza una verifica** che le cifre non cambino.
- NC-028 chiusa con un rimedio che esiste solo in un deck.

## NON fa parte di questo lotto

- **L29c** (caso peggiore), **L36** (forma dell'interblocco del guadagno), **L35**, L28,
  L30, il dossier.
- Non toccare i file già in `vendor/`.

## Come lavoriamo

- Verifica invece di fidarti. Niente cifre non eseguite. Un lotto per volta.
- Gli script zsh si lanciano da soli; `git` e comandi con variabili di shell composte
  vengono rifiutati nel worktree: comandi semplici e separati, script su file.
- **Scipy non c'è**: stdlib con `/usr/bin/python3`.

## CHIUSURA

1. `STATE.md` con L29b **fatto** e il successivo come prossimo.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L29b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
