# Prompt per la sessione successiva — L71, il frontale mosso durante una sequenza

Nome della sessione: **hi-fi preamp L71** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L70 (2026-11-04, report `reports/2026-11-04-L70-semplificazioni.md`). Le due
> semplificazioni dell'alimentatore sono state misurate e respinte dall'utente, **«Tenere tutto»** (ADR-119):
> il temporizzatore è quello di oggi, invariato da L69. L'ordine verso G1: **L71** → L72 → L73 → L74 → G1
> (la tabella dei lotti di `STATE.md`; concordato dall'utente il 2026-11-04).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L71**, e si ferma.

## La regola dell'utente sul prototipo (PR-12, ADR-118)

«Il prototipo sarà molto costoso e quindi dobbiamo essere certi che funzioni perfettamente, l'unica cosa che
vogliamo valutare sul proto è la qualità audio percepita.» **Ciò che si può simulare si simula qui.**

## Che cosa fare

1. **Leggi prima**: `STATE.md`, `PRB.md` (PR-20, PR-23, PR-24), `NONCOMPLIANCE.md` (**NC-083**), P9 in
   `REQUIREMENTS.md`, ADR-102, ADR-116, ADR-119, il README di `data/2026-11-04/L69b/` (il banco) e quello di
   `data/2026-11-04/L70/` (come si sono fatte le corse nuove su quel banco). Utili anche `script/lista_buchi.py`,
   `script/analizza_v.sh` e `script/ponte_v.sh` di `data/2026-11-04/L70bis/` (una famiglia di corse e la sua catena al
   jack a parte).
2. **Le tre sequenze di NC-083**, sul banco del temporizzatore di oggi (`data/2026-11-04/L69b/`, **copiato**
   in una cartella di L71, non rieseguito sul posto), a rete −10 / 0 / +10 %:
   - il frontale spento **prima che la musica arrivi** (oggi a 1209 ms dall'accensione), a più istanti;
   - il frontale **riacceso durante lo spegnimento** (i ~120 ms prima che K501 si apra), a più istanti;
   - **SW3** (il tasto del mute) mosso **dentro Δ** (fra MUTE_CMD e PERMIT_CMD).
   Il generatore (`psu/genera_tb_psu.py`) ha già `--rimbalzo` e i casi `ritenuta_frontale`, `rilascio`:
   guarda come sono fatti prima di aggiungere eventi.
3. **Le misure**: i colpi al jack in **dB SPL** (il ponte e la catena al jack di L69b, `script/ponte.sh`), lo
   stato finale (la musica torna? K501? la ritenuta scattata a torto?), il calore delle parti contro i loro
   limiti se qualcosa resta acceso.
4. **Se qualcosa esce**: le opzioni all'utente coi numeri, per nome; se cambia il circuito: ADR, sorgente,
   netlist, disegni, FMEA, `run_tests.sh`. Se tutto è dentro: NC-083 chiusa col report.

## I vincoli

- **La macchina è un MacBook Air senza ventole**: al più **3 simulazioni insieme**, con `nice -n 10`;
  prima di lanciare, `pgrep ngspice`. Se l'utente dice che girano altre sessioni, al più **2**.
- Comandi semplici, percorsi assoluti, script scritti con Write; il controllo del worktree rifiuta i comandi
  composti (`git` con altro, `cd` + `git`, `nice` + `xargs`, i glob e le variabili dentro un comando,
  `pdftotext` in un ciclo): `git -C <worktree>` un comando alla volta, il resto in uno script.
- Uno script di un lotto vecchio scrive nella **sua** cartella: non rieseguirlo per confronto; copiarlo.
- **Prima di iniziare e di nuovo prima di fare la domanda all'utente**: `git -C <worktree> fetch origin main`
  e `git -C <worktree> log --oneline HEAD..origin/main`. Se `main` ha già chiuso L71, fermarsi e dirlo (L70 è
  stato fatto due volte da due sessioni in parallelo: L70bis).
- `git add` un percorso alla volta; **`.gitignore` prima** di ogni `git add` di una cartella dati (le forme
  d'onda delle sequenze sono ~45 MB l'una: L70 ne ha lasciate 12 GB sul disco, fuori dal commit).
- Il push verso GitHub ha risposto una volta «Internal Server Error» in L70: si riprova, e si verifica con
  `git log origin/<ramo>..HEAD`.
- Le domande si fanno per nome; i colpi al jack in dB SPL; ogni opzione con la sua temperatura contro il
  limite.

## CHIUSURA

1. `STATE.md`: L71 **fatto**, il prossimo **L72**; le celle di In breve; il diario (la voce più vecchia
   delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L72 («Nome della sessione: hi-fi preamp L72»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L71`; rimuovi il worktree; fermati.
