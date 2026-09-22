# Prompt per la sessione successiva — L40 (V1 coi modelli del costruttore)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è
organizzato in LOTTI PICCOLI: questa sessione fa **L40** e si ferma. Non iniziarne un
secondo.

## Perché adesso

Il lotto precedente ha messo i modelli del costruttore nel progetto, e **V1 è caduto** su
ogni istanza a guadagno unitario (**NC-034**, bloccante):

| Istanza | Prima (segnaposto) | Dopo (costruttore) |
|---|---|---|
| blocco B, 0 dB | 61,80° | **55,55°** |
| blocco A (cablaggio ≤ 1 nF) | 63,36° | **57,93°** |
| buffer delle fisse | 61,63° | **54,92°** |
| blocco B, +3 / +10 dB | 69,77 / 102,98° | 63,90 / 100,19° |

**La direzione è dell'utente (2026-09-22)**: «non sono convinto che ci serva quasi un
megaherz di banda passante a 0 dB, preferisco rispettare i margini di fase e ridurre la
banda passante o alzare il guadagno fino a 1,5 dB».

L29c (il caso peggiore di V2) viene **dopo** questo lotto: misurarlo su un circuito che
cambia compensazione vorrebbe dire rifarlo.

## Da dove si parte

- **I modelli sono tutti del costruttore** (`models/`), nel sorgente e nei 25 deck. Solo
  l'LSK489A ha KF; nessun modello porta la dispersione; NC-020, NC-024 e NC-025 dicono
  dove i modelli stanno sotto i propri datasheet.
- **L'esplorazione di L39** (`data/2026-09-22/L39/esplorazione/`, solo sul blocco B, nessun
  valore cambiato):
  - **C_f** (C137, 330 pF, ADR-025) non aiuta a 0 dB: con R_g aperta la controreazione è
    già totale;
  - **il Miller** (C124, 470 pF): 680 p 59,26°, **820 p 60,70°**, 1 n 62,08°. Il crossover a
    vuoto scende da 889 a 520 kHz (820 p).
  Non misurati: blocco A e buffer col Miller nuovo, slew rate, V3, risposta, THD di modello.
- **La seconda strada, il guadagno minimo fino a +1,5 dB**, non è stata misurata. Tocca la
  rete di controreazione di ogni istanza oggi a guadagno 1 (blocco A, blocco B a «0 dB»,
  buffer), quindi E2, la struttura del guadagno di ADR-001/ADR-019, l'headroom (NC-009),
  il rumore e V2. È una modifica di **topologia**: si misura, si confronta con la prima
  strada e **si chiede all'utente prima di toccare il sorgente**.
- **La corrente di riposo d'uscita** (**NC-035**) è 20,3 / 20,4 mA invece di 14,6. La Vbe
  dei MJE veri è 0,57 / 0,54 V. Lo sweep del moltiplicatore (1,5–1,87 kΩ) dà 17,3–23,2 mA:
  i ~15 mA stanno sotto 1,5 kΩ. La corrente tocca i poli dello stadio d'uscita, quindi
  **si decide insieme a V1**, non dopo.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`**, in particolare #22, #24, #27, #29 e #30.
2. **`docs/preamp/STATE.md`**: la voce L39 del diario e le righe L40 e L29c.
3. **`reports/2026-09-22-L39-modelli-costruttore.md`**, soprattutto §4 e §5.
4. **ADR-019** (V1), **ADR-024** (la cella di V1), **ADR-025** (C_f 330 pF), **ADR-017**
   (che prevede di ridecidere il Miller con una ADR propria), **ADR-031** («da riaprire
   se» scatta), ADR-001, ADR-004, ADR-026 (la struttura del guadagno), ADR-023 (classe A).
5. **`NONCOMPLIANCE.md`**: NC-034, NC-035, NC-025, NC-029, NC-009, NC-021 (chiusa, la
   stessa forma).

## IL LAVORO, in ordine

1. **Separare le cause** della caduta di V1: MJE (f_T, NC-025) contro MMBT (VAF, CJE)
   contro corrente di riposo. Si fa sostituendo un modello alla volta in un deck
   d'esplorazione, **senza toccare `models/`** (limitations #29 per gli `altermod`: nome
   giusto, `showmod`, sonda).
2. **Le due strade, misurate su tutte e tre le istanze a guadagno unitario** (blocco A,
   blocco B a 0 dB, buffer), con la cella di ADR-024:
   - (a) banda ridotta: il Miller (e, se serve, un'altra compensazione) al valore minimo
     che dia ≥ 60° **con un margine** su tutte e tre, più +3 e +10 dB;
   - (b) guadagno minimo fino a +1,5 dB: quale rete, quale margine, e cosa costa ad E2,
     all'headroom, al rumore.
   Per ciascuna: crossover, banda −3 dB, slew rate, V3.
3. **La corrente di riposo**, insieme: ~15 mA con un valore nuovo del moltiplicatore
   (sweep esteso sotto 1,5 kΩ) oppure ~20 mA accettati, con dissipazione (NC-029) e
   budget di corrente.
4. **Chiedere all'utente** con i numeri delle due strade e della corrente. **Niente nel
   sorgente prima della risposta.**
5. Con la risposta: **una ADR**; il valore nel sorgente, con il commento che la cita; il
   blocco rigenerato; la **regressione di L39 rifatta** (gli script sono in
   `data/2026-09-22/L39/script/`: `esegui_deck.sh`, `confronta.py`, `margini.py`, `p7.py`,
   `classe_a.py`, `v3.py`, `v2_cella.sh`). ADR-031: rimisurare la dispersione del gruppo B
   sul circuito nuovo, blocco A e buffer compresi.
6. **L'esito**: NC-034 si chiude se V1 ≥ 60° ovunque e la regressione regge; NC-035 si
   chiude con la corrente decisa. Report datato.

**Se non entra in una sessione, dividi**: prima i punti 1–4 (misura e domanda); poi 5–6.
Scrivilo in `STATE.md`.

## I vincoli

- **Nessun cambio di topologia né di valore senza l'utente.**
- I file in `vendor/` non si toccano; i modelli in `models/` si cambiano solo col loro
  processo (provenienza, `validate_models.py`).
- Il blocco generato non si edita a mano: si cambia `gain_block.py` e si rigenera.
- Un deck che include `gain_block_flat.inc` non usa nomi di nodo del blocco (#24); un
  anello si confronta col guadagno a bassa frequenza, che coi modelli veri vale
  **~81 dB**, non più ~72.
- Il blocco A coi modelli veri converge per source stepping (L39): normale, ma un'analisi
  che non converge va guardata, non ignorata.
- Gli script zsh si lanciano da soli. `git` e i comandi con costrutti composti (`$(...)`,
  `cd … &&`, heredoc, `awk -v`, cicli con pipe) vengono rifiutati nel worktree: comandi
  semplici e separati, script su file. Scipy non c'è; numpy c'è nel venv 3.13.

## NON fa parte di questo lotto

- **L29c** (viene subito dopo: la bozza aggiornata ai modelli del costruttore è
  `data/2026-09-22/L39/bozza_prompt_L29c.md`), L36, L35, L28, L30, il dossier.

## CHIUSURA

1. `STATE.md` con L40 **fatto** e L29c come prossimo.
2. Riscrivi QUESTO file per L29c, partendo dalla bozza
   `data/2026-09-22/L39/bozza_prompt_L29c.md` aggiornata ai valori di L40.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L40`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
