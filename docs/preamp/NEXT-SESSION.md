# Prompt per la sessione successiva — L64c, il dossier rigenerato: la chiusura

Nome della sessione: **hi-fi preamp L64c** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura della seconda parte del dossier (2026-11-03: l'alimentatore e il
> temporizzatore). L'utente ha diviso L64 in tre parti («Three parts, like last time»). L'ordine verso
> G1: **L64c** → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L64c**, e
si ferma.

## Che cosa fare

**La terza parte del dossier, la chiusura**, sul circuito di oggi (il circuito non cambia): gli schemi
completi (L63), la FMEA con le misure adottate (L45d2b3b3 e le righe dopo: L58a2, L58b, L66), le schede
di prova (L49a, L49b), «Cosa questo dossier non dice» riscritta sul progetto di oggi, `PARTI` completa,
`index.html` accanto al generatore, e il PDF all'utente.

1. **Leggi prima**:
   - la riga di L64c nella tabella dei lotti di `STATE.md`;
   - i report di L64a e L64b (`reports/2026-11-03-L64a-dossier-scheda-audio.md`,
     `reports/2026-11-03-L64b-dossier-alimentatore.md`): com'è fatta la seconda strada sul circuito di
     oggi, le eccezioni dichiarate, i sabotaggi;
   - il report di L51c (`reports/2026-10-10-L51c-*.md`) e, in `build_dossier.py`, i punti 18–19 del
     docstring, `measure_boards`, la sezione `s14` e quella della provenienza.
2. **Il generatore con `PARTI` completa, prima di ogni sezione**: con `"schede"` accesa, ogni rifiuto si
   legge. `s14` usa ancora nomi di L51b (il micro, «Cosa non dice» sul firmware è già tolta in L64b,
   ma il resto della sezione è di L51c). Le schede di prova sono del 9 ottobre: dicono la netlist di
   allora, e la pagina deve dirlo.
3. **Le sezioni**: gli schemi di L63 accanto a `index.html`; la FMEA con le misure adottate, letta dai
   CSV versionati; «Cosa non dice» riscritta; la provenienza (i modelli del costruttore e il comparatore
   tarato del banco dell'alimentatore, ADR-103). Ogni numero letto dai dati versionati e passato per
   una seconda strada; i lotti vecchi solo da `vecchio()`.
4. **Il PDF all'utente**: un PDF per documento (`stampa_a4.py`), copiato dove l'utente vuole.
5. **Le domande all'utente** coi numeri, per nome.

## I vincoli

- **Il dossier ha un solo lettore, l'utente**, e **non si taglia**.
- **Il circuito non cambia.** Un difetto trovato apre una non conformità e si porta all'utente.
- **La macchina è un MacBook Air senza ventole**: al più **3 simulazioni insieme**, con `nice -n 10`;
  prima di lanciare, `pgrep ngspice`. Se l'utente dice che girano altre sessioni, al più **2**.
- Comandi semplici, percorsi assoluti, script scritti con Write; il controllo del worktree rifiuta i
  comandi composti (cicli, variabili calcolate, `nice` in una catena, `git` con percorsi relativi da
  una sottocartella): scriverli in uno script, o `git -C <radice>`.
- Una lista che `xargs` sta leggendo non si riscrive (L64b: una riga tagliata, otto corse saltate).
- `git add` un percorso alla volta; commit e push prima di ogni lista lunga.
- Le forme d'onda e le corse grezze non si committano: `.gitignore` prima di ogni `git add` di una
  cartella dati.
- Le domande si fanno per nome; i colpi al jack in dB SPL; le distorsioni in dB contro il tetto.

## CHIUSURA

1. `STATE.md`: L64c **fatto**, L64 **fatto**, il prossimo **L65**; le celle di In breve; il diario (la
   voce più vecchia delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L65 («Nome della sessione: hi-fi preamp L65»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L64c`; rimuovi il worktree; fermati.
