# Prompt per la sessione successiva — L71, il frontale mosso durante una sequenza

Nome della sessione: **hi-fi preamp L71** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L70 (2026-11-04, report `reports/2026-11-04-L70-semplificazioni.md`). Le due
> semplificazioni dell'architetto sono state misurate e **non scelte**: l'utente, «Tenere com'è» (ADR-119). Il
> circuito non è cambiato: il temporizzatore su cui si lavora è quello di L69 / L69b. L'ordine verso G1:
> **L71** → L72 → L73 → L74 → G1 (la tabella dei lotti di `STATE.md`; l'ordine concordato dall'utente il
> 2026-11-04).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L71**, e si ferma.

## La regola dell'utente sul prototipo (PR-12, ADR-118)

«Il prototipo sarà molto costoso e quindi dobbiamo essere certi che funzioni perfettamente, l'unica cosa che
vogliamo valutare sul proto è la qualità audio percepita.» **Ciò che si può simulare si simula qui.**

## Che cosa fare

1. **Leggi prima**: `STATE.md`, `PRB.md` (PR-20, PR-23, PR-24), `NONCOMPLIANCE.md` (**NC-083**, maggiore, prima
   di G1), il rilievo dell'architetto in `reports/2026-11-04-L65-architetto-avversariale.md` («Le omissioni
   cercate»), ADR-102 (il temporizzatore), e il README del banco di L69b (`data/2026-11-04/L69b/`) e di L70
   (`data/2026-11-04/L70/`: lo stesso banco copiato, con `script/lista_buchi.py`, `script/analizza_v.sh` e
   `script/ponte_v.sh` per una famiglia di corse a parte).
2. **Le tre sequenze di NC-083**, sul banco del temporizzatore di oggi (copiato da L70 o da L69b, non
   rieseguito sul posto), a rete −10 / 0 / +10 %:
   - il **frontale spento prima che la musica arrivi** (la musica arriva a ~1209 ms dall'accensione): più
     istanti dentro quella finestra;
   - il **frontale riacceso dentro lo spegnimento** (i ~120 ms fra il frontale spento e K501 aperto): più
     istanti;
   - **SW3 mosso dentro Δ** (il ritardo fra il mute e il permissivo).
   Per ciascuna: i colpi al jack in dB SPL (la catena al jack, come `ponte.sh` / `ponte_v.sh`), che cosa fanno
   K501, il mute e il permissivo, e il calore delle parti contro i loro limiti.
3. **Le opzioni all'utente coi numeri**, per nome, se qualcosa esce: i colpi al jack in dB SPL, ogni parte con
   la sua temperatura contro il limite, a rete ±10 %. Se il circuito cambia: ADR, sorgente, netlist, disegni,
   FMEA, `run_tests.sh`.

## I vincoli

- **La macchina è un MacBook Air senza ventole**: al più **3 simulazioni insieme**, con `nice -n 10`; prima di
  lanciare, `pgrep ngspice`. Se l'utente dice che girano altre sessioni, al più **2**.
- Comandi semplici, percorsi assoluti, script scritti con Write; il controllo del worktree rifiuta i comandi
  composti (`git` con altro, `cd` + `git`, `sed` con valori calcolati, i glob passati a `nice`, `zsh -c` in
  linea, e qualunque comando che nomini il file `.gitignore`: leggerlo con Read, scriverlo con `cat >>`):
  `git -C <worktree>` un comando alla volta, il resto in uno script.
- Uno script di un lotto vecchio scrive nella **sua** cartella: non rieseguirlo per confronto; copiarlo.
- `build_dossier.py` riscrive `dossier/index.html` e `dossier.summary.json` del repo: se lo si corre per un
  controllo, riportarli com'erano (`git -C <worktree> checkout -- <i due file>`); il dossier si rigenera in L74.
- `git add` un percorso alla volta; `.gitignore` prima di ogni `git add` di una cartella dati.
- Le domande si fanno per nome; i colpi al jack in dB SPL; ogni opzione con la sua temperatura contro il
  limite. L'utente vuole una **raccomandazione** con le opzioni, non solo l'elenco («poi devi aiutarmi a
  decidere», L70).

## CHIUSURA

1. `STATE.md`: L71 **fatto**, il prossimo **L72**; le celle di In breve; il diario (la voce più vecchia delle
   tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L72 («Nome della sessione: hi-fi preamp L72»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L71`; rimuovi il worktree; fermati.
