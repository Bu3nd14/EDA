# Prompt per la sessione successiva — L29d (il contatto in serie al jack)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è
organizzato in LOTTI PICCOLI: questa sessione fa **L29d** e si ferma. Non iniziarne un
secondo.

## Perché adesso

**L29c** ha misurato il caso peggiore di V2 col mute reale (LDR v4 a monte più il relè al
jack). **Con la musica regge ovunque** (S ≤ 11 dB contro 20). **Senza musica, tre condizioni
sono fuori dai 100 µV di A**, per una causa sola: il contatto di mute **in derivazione**, 0,1 Ω
dietro 47 Ω, attenua solo ~1/471 un salto in continua dell'uscita del blocco:
- il cambio di guadagno o di trim a relè chiuso: 98–116 µV, **267 µV** con ±20 mV di VOS
  dell'LSK489;
- l'accensione: fino a 11 mV sulle fisse;
- lo spegnimento: fino a volt. Questo va all'alimentatore (**ADR-043**, L30), non qui.

**Decisione dell'utente del 2026-09-23**: si misura un **contatto in serie** al jack, in due
varianti, e poi si sceglie coi numeri; la scelta diventa una ADR. Le LDR **restano**: S le
vuole, perché un contatto taglia la musica di colpo (~70 dB in un istante).

## Da dove si parte

- **Il banco**: `spice/preamp/tb/tb_v2_casopeggiore.cir`, **generato** da
  `data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py`. Si estende il generatore, non il
  deck. Il README di `data/2026-09-23/L29c/` dice script e cartelle.
- **La posizione in serie esiste già nel blocco CANALE**: `BSERM` / `BSER1` / `BSER2` fra il
  condensatore e il jack, col ponte `RBYM` / `RBY1` / `RBY2` da 1 mΩ da aprire con `alter`, e lo
  stato `SSER` (`VTISER`, `VTRSER`, `VMHSER`, netto coi rimbalzi). È la variante «serie» di L29a
  (`tb_v2_mute_varianti.cir`), misurata allora con l'elemento ideale e i segnaposto.
  **Attenzione**: è una conduttanza comportamentale `pow(10, …)` in serie al segnale, la forma
  che in L29c ha reso l'op dipendente dal percorso (limitations #33). Se dà problemi: un
  interruttore nativo fuori dal blocco, in parallelo a `BSERx` lasciato aperto, come K1/K5 in L29c.
- **Le cifre di L29c da battere** (`reports/2026-09-23-L29c-v2-caso-peggiore.md`): cambio a relè
  chiuso 116 µV (267 µV con la dispersione `dp…max`), accensione 11 mV sulle fisse; il rilascio,
  S e B2 già in soglia.
- **Gli strumenti di L29c**:
  - `corri.sh` rifiuta il transient op e riprova senza `.nodeset` e con un `.nodeset` esteso;
  - `verifica_partenza.py` controlla da dove è partita ogni corsa;
  - `analizza_par.py` fa l'analisi in parallelo, con una cartella di lavoro per manifesto;
  - `verdetto.py` legge la colonna `conta`.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`**, in particolare #22, #26, #29, #30, #31, #32 e
   **#33** (il transient op).
2. **`docs/preamp/STATE.md`**: le voci L29c e L29b2 del diario, le righe L29d, L36, L30.
3. **`reports/2026-09-23-L29c-v2-caso-peggiore.md`** per intero.
4. **ADR-012** (lo stato sicuro: il mute è NC, a macchina spenta le uscite sono a massa),
   **ADR-038/039/040/041**, **ADR-043**.
5. **`NONCOMPLIANCE.md`**: NC-028, l'aggiornamento di L29c.

## IL LAVORO, in ordine

1. **Il contatto in serie nel generatore**, due varianti, nello stesso deck o in due:
   - **(i) serie più derivazione**: la serie si apre, poi la derivazione si chiude; al rilascio
     l'inverso. Da scrivere la sequenza e i suoi tempi;
   - **(ii) serie sola**: la derivazione resta aperta.
   Il contatto aperto ha la sua capacità (ipotesi da dichiarare: qualche pF, più il cavo).
   Controfattuale: con la serie sempre chiusa il deck ridà L29c cella per cella.
2. **Le celle che stavano fuori**, nelle due varianti: il cambio di guadagno e di trim a relè
   chiuso (punti 1 e 2), la dispersione peggiore (`dp…max`, punto 3), l'accensione (punto 5).
3. **Le celle che reggevano**, per non romperle: il mute semplice e le inversioni con musica
   (S, B2) a 1 kHz e 20 Hz, e A del rilascio senza segnale. B col contatto aperto è la domanda
   vera della variante (ii).
4. **20 kHz**: solo se serve, e pianificato prima (in L29c una corsa ha richiesto 6–7 ore coi
   core contesi).

**Esito**: la tabella delle due varianti contro L29c. **L'utente sceglie**, e la scelta diventa
una ADR che tocca ADR-012 (lo stato sicuro) e dà la base al failsafe di ADR-043. Se una variante
porta tutte le celle sotto 100 µV (tranne lo spegnimento, che è di L30), **NC-028 si può
chiudere per la parte del mute**. Scrivilo con l'utente, non da solo.

## I vincoli

- **Nessun cambio di topologia né di valore senza l'utente.** L29d misura; la scelta è sua.
- `set numdgt=15` prima di ogni `wrdata` (#30); `pwl()` estrapola (#31); nessun corpo di `if`
  vuoto (#32); una corsa col transient op non vale (#33).
- **Il manifesto non è l'elenco delle corse**: una cella si estrae dalla colonna `file`.
- Gli script zsh si lanciano da soli; nel worktree `git` e i comandi composti vengono
  rifiutati: comandi semplici e separati, script su file.
- Le forme d'onda non si committano: c'è un `.gitignore` nella cartella dati di L29c, da
  copiare.
- `analizza` è lento coi core pieni: ~2 ore per 87 corse con 3 processi. Pianificalo.

## NON fa parte di questo lotto

- **L36** (viene dopo: il cablaggio del mute al jack lo decide L29d), L30 e il failsafe
  (ADR-043), L35, L28, il dossier.

## CHIUSURA

1. `STATE.md` con L29d **fatto** e il prossimo lotto.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L29d`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
