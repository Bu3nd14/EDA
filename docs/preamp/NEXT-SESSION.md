# Prompt per la sessione successiva — L64b, il dossier rigenerato: l'alimentatore e il temporizzatore

Nome della sessione: **hi-fi preamp L64b** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura della prima parte del dossier (2026-11-03: la scheda audio, ADR-113 per
> PR-24). L'utente ha diviso L64 in tre parti («Three parts, like last time»). L'ordine verso G1:
> **L64b** → L64c → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L64b**, e
si ferma.

## Che cosa fare

**La seconda parte del dossier: l'alimentatore e il temporizzatore**, sul circuito di oggi (il
circuito non cambia dopo L67). Da L51b l'alimentatore è cambiato quasi tutto: la partenza morbida dei
regolatori (ADR-091, 092), lo Schottky dopo i regolatori (ADR-093), il comando dei relè e i 5 V
(ADR-094), la retroazione dei regolatori (ADR-096), il temporizzatore a comparatori con lo standby
al posto del micro e del firmware (ADR-102…105, 108), R585 (ADR-109), l'autodiagnosi con Q501 in
serie a Q509 (ADR-110, `DIAGNOSI.md`).

1. **Leggi prima**:
   - la riga di L64b nella tabella dei lotti di `STATE.md`;
   - il report di L64a (`reports/2026-11-03-L64a-dossier-scheda-audio.md`): com'è fatta la seconda
     strada sul circuito di oggi, le eccezioni dichiarate, i sabotaggi;
   - il report di L51b (`reports/2026-10-09-L51b-dossier-alimentatore.md`) e, in `build_dossier.py`,
     i punti 7–13 del docstring e le funzioni dell'alimentatore (`measure_psu_power`,
     `measure_supervisor`, `measure_timer`, `measure_fw`, `measure_shutdown`, `measure_heat`);
   - i README dei lotti dell'alimentatore dopo L51b: L45d2b2a, L45d2b2b1, L45d2b2b2, L45d2b3a,
     L54b1, L54b2, L54b3a, L54b3b, L58a, L58b.
2. **Il generatore con `PARTI = ("audio", "alimentatore")`, prima di ogni sezione**: in L64a, con le
   parti dell'alimentatore accese, rifiutava R512 a 220 k (atteso 110 k, limitations #34) in tutti i
   log di L51b, i deck della rete e dei guasti che non si rigenerano più, le quindici sequenze e i
   quattro deck del temporizzatore. Ogni rifiuto si legge.
3. **Le sezioni**: il firmware non c'è più (ADR-102): la sua sezione esce o si riscrive come il
   temporizzatore a comparatori; lo standby; l'autodiagnosi; il calore del telaio coi carichi di oggi.
   Ogni numero letto dai dati versionati e passato per una seconda strada; i lotti vecchi solo da
   `vecchio()`.
4. **Le domande all'utente** coi numeri, per nome.

## I vincoli

- **Il dossier ha un solo lettore, l'utente**, e **non si taglia**.
- **Il circuito non cambia.** Un difetto trovato apre una non conformità e si porta all'utente.
- **La macchina è un MacBook Air senza ventole**: al più **3 simulazioni insieme**, con `nice -n 10`;
  prima di lanciare, `pgrep ngspice`. Gli script copiati dai lotti vecchi che ne lanciano di più si
  chiamano con 3. Le corse lunghe della notte: `caffeinate -i -w <pid>`.
- Comandi semplici, percorsi assoluti, script scritti con Write; il controllo del worktree rifiuta i
  comandi composti (cicli, variabili calcolate, `nice` in una catena): scriverli in uno script.
- `git add` un percorso alla volta; commit e push prima di ogni lista lunga.
- Le forme d'onda e le corse grezze non si committano: `.gitignore` prima di ogni `git add` di una
  cartella dati.
- Una catena di più blocchi vuole i `.nodeset` dal blocco da solo (limitations #86).
- Le domande si fanno per nome; i colpi al jack in dB SPL; le distorsioni in dB contro il tetto.

## CHIUSURA

1. `STATE.md`: L64b **fatto**, il prossimo **L64c**; le celle di In breve; il diario (la voce più
   vecchia delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L64c («Nome della sessione: hi-fi preamp L64c»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L64b`; rimuovi il worktree; fermati.
