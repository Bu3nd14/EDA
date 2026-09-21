# Prompt per la sessione successiva — L29b2 (il mute LDR nel sorgente, e il rilascio reso decidibile)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è
organizzato in LOTTI PICCOLI: questa sessione fa **L29b2** e si ferma. Non iniziarne un
secondo.

## Da dove si parte

Il lotto precedente ha chiuso la **misura** del mute graduale a monte con due LDR
VTL5C4 (ADR-038). La decisione è dell'utente: il **sorgente** è di questo lotto.

- **Il modello** `models/optocoupler/vtl5c4_comportamentale.lib` è verificato contro i
  punti del datasheet. È comportamentale, con un'estrapolazione dichiarata sopra ~10 kΩ.
  **Si corregge solo dal generatore**,
  `docs/preamp/data/2026-09-16/L29b/vtl5c4_modello/genera_modello.py`, mai a mano.
- **Il profilo del comando dei LED da portare nel sorgente** è **v3, con Td = 6 s**
  (scelta dell'utente):
  - la profondità `d` è un'unica variabile reversibile, da 0 a 1 in Td;
  - **serie**: 20 mA → 0,2 mA per d da 0 a 0,1, poi **0,2 mA → 4,5 µA** per d da 0,1 a
    0,45, poi 10 nA a d = 0,5. È log-lineare a tratti;
  - **derivazione**: 10 nA → 20 mA, log-lineare, per d da 0,5 a 1;
  - **10 nA di riposo** su entrambi i LED;
  - **il relè al jack** si chiude 0,5 s dopo d = 1 e si apre all'inizio del rilascio.
- **Cosa è misurato** (1 kHz, 100 kΩ, scratch):
  - C2 d'inserzione **2,56 / 0,62 mV** (principale / fisse), contro un pavimento di
    0,68 / 0,22 mV;
  - A ≤ 0,03 µV, B2 0,29 µV;
  - relè 0,07 mV a 1 kHz e 0,56 mV a 20 kHz;
  - carico sulla sorgente ≥ 714 kΩ.
- **Cosa NON è decidibile**: il rilascio e l'inversione. Con le LDR attive il pavimento
  numerico di C2 sale a **4,6–7,2 mV** sulla principale (1,9–2,3 sulle fisse). Succede
  nella coda del rilascio, a livello pieno, con la serie accesa e la derivazione che si
  fa buia. Il meccanismo non è attribuito.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`**, **`docs/limitations.md`**.
2. **`docs/preamp/STATE.md`**: la voce L29b del diario e le righe L29b2, L29c e L36.
3. **`docs/preamp/reports/2026-09-21-L29b-mute-ldr-misura.md`** per intero.
4. **`docs/preamp/data/2026-09-21/L29b/ldr_catena/README.md`** e `build.py`: il banco,
   i profili, il pavimento.
5. **`docs/preamp/data/2026-09-16/L29b/vtl5c4_modello/README.md`**: il modello e le tre
   trappole.
6. **ADR-038** per intero; ADR-036, ADR-035, ADR-032, ADR-012, ADR-021, ADR-022.
7. **`docs/preamp/REQUIREMENTS.md`**: V2 per intero, E3, E5, F6, P7.
8. **`docs/preamp/NONCOMPLIANCE.md`**: NC-028, l'aggiornamento del 2026-09-21.

## IL LAVORO, in ordine

1. **Il pavimento di C2 con le LDR.**
   - Capire perché due corse nello stesso stato fisico differiscono di ~6,5 mV sulla
     principale nella coda del rilascio.
   - Gli strumenti sono `ldr_catena/c2curva.py` e `c2spettro.py`.
   - Candidati da falsificare, uno per volta:
     - il passo (TMAX 5 e 2 µs);
     - la forma del modello (`BDX` con `min()`, la tabella a gradini dello spegnimento);
     - `method=gear`, **ma solo se** il metodo di V2 e l'utente lo consentono (il blocco
       CANALE non si tocca in silenzio).
   - Poi il **rilascio** e l'**inversione** del profilo v3 Td 6 s, ciascuno col suo
     pavimento misurato su tutta la sequenza, non solo all'evento.
   - Se il pavimento non scende sotto la soglia, **dillo all'utente** prima di andare
     avanti.
2. **Il sorgente**, in `circuits/preamp/preamp_audio.py`:
   - due LDR per canale;
   - il comando dei LED fuori dal percorso del segnale (ADR-022);
   - la variabile di profondità;
   - il relè al jack che segue la profondità completa.

   Un commento con l'ADR su ogni valore non ovvio. Poi netlist, disegni (2d), diagramma a
   blocchi (2f) e `check_relay_safe_state.py`, **fatto prima fallire** con un sabotaggio.
3. **Il deck versionato** `spice/preamp/tb/tb_v2_mute_ldr.cir`:
   - lo stesso blocco CANALE (`v2_metodo.py canale`);
   - tre uscite, 10 e 100 kΩ, 20 Hz / 1 kHz / 20 kHz;
   - A senza segnale, B, C2 con il **suo** pavimento;
   - corse lunghe in background, con `save`.
4. **E3** ed **E5** con la LDR in serie (E5: 88 Ω di serie, più l'accoppiamento
   LED–cella di 0,5 pF). **P7 riletto**: a mute inserito gli stadi d'uscita non hanno
   segnale.
5. **L'esito.** NC-028 resta aperta (manca L29c) e si aggiorna. Report datato.

Se non entra in una sessione, **dividi di nuovo** in `STATE.md` e chiudine una parte.

## I vincoli

- **Il metodo di V2 non si cambia in silenzio.** Il pavimento si misura e si riporta
  accanto a ogni C2. Un valore sotto il pavimento non è una misura.
- **Ogni cifra sulla LDR** porta «modello comportamentale dal datasheet, con
  estrapolazione dichiarata».
- **Trappole già pagate:**
  - un LED senza percorso DC fa fallire l'op in silenzio;
  - `alter` + `op` in sequenza non convergono col modello della LDR;
  - col trapezio, un gradino sul LED fa oscillare la corrente della cella;
  - un gradino di corrente del LED della derivazione salta dentro un nodo a 1 MΩ
    (A in mV);
  - `analizza` accetta eventi solo per t > 0,3 s;
  - `awk` col locale italiano non legge i `.dat`: si usa Python.
- **Nessun cambio di tecnica senza l'utente**: ADR-038 e il profilo v3 sono sue scelte.
- Gli script zsh si lanciano da soli. `git` e i comandi con variabili di shell composte
  vengono rifiutati nel worktree: comandi semplici e separati, script su file. **Scipy
  non c'è**: stdlib con `/usr/bin/python3`.

## NON fa parte di questo lotto

- **L29c** (caso peggiore), **L36** (forma dell'interblocco del guadagno), L35, L28, L30,
  il dossier.
- I file in `vendor/` non si toccano.

## CHIUSURA

1. `STATE.md` con L29b2 **fatto** e il successivo come prossimo.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L29b2`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
