# Prompt per la sessione successiva — L66, il VAS a 126 °C e i modi fuori dai quindici

Nome della sessione: **hi-fi preamp L66** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L58b (2026-11-01). L58 è chiuso (L58a1, L58a2, L58b). L'ordine verso
> G1, confermato dall'utente: **L66** → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L66**, e si
ferma.

## Che cosa fare

**NC-076** (maggiore, prima di G1). Col finale NPN in corto base-emettitore (Q132_be) il VAS Q122 porta
0,53 W e arriva a **126 °C** con 60 °C d'aria, contro P7 125. La riga della FMEA diceva 115 °C, dal
blocco di prima di ADR-099. In L58b lo stesso modo, sullo stesso banco, porta **l'uscita del blocco al
rail** (−13,6 V): non è il degrado silenzioso che la riga di ADR-071 diceva.

1. **Leggi prima**:
   - la riga di L66 e la voce di L55 in `STATE-STORIA.md`;
   - NC-076 in `NONCOMPLIANCE.md`, con l'aggiornamento di L58b;
   - ADR-068, ADR-097, ADR-099, ADR-100;
   - `data/2026-10-29/L55/` (README, `calore_fmje.csv`, `fmea_correzione.csv`) e
     `data/2026-11-01/L58b/censimento_blocco.csv`.
2. **Il meccanismo, misurato**: perché in quel modo il VAS porta 0,53 W, e perché l'uscita va al rail.
3. **I modi del blocco fuori dai quindici di ADR-099**, rifatti sul sorgente col banco del calore.
   - Il banco: L45d2b3b2b2; L55 e L58b lo hanno usato col caso noto.
   - In L58b `data/2026-11-01/L58b/script/genera.py` lo carica per percorso e prende una lista di modi:
     è il punto di partenza.
   - Vanno cercati: quali modi sono cambiati dopo i rimedi di ADR-097 / ADR-099, e se qualcuno esce da
     P7 o da P10.
4. **Il rimedio, con l'utente, coi numeri**. Per esempio più rame sotto il VAS, o il limite del VAS di
   ADR-099. Ogni opzione verificata sui limiti a rete ±10 %, con 60 °C d'aria.
5. **La riga della FMEA rifatta**, e quella di Q132_be anche in `fmea_l58b.csv`, che oggi rimanda a NC-076.
6. **Se il circuito cambia**:
   - sorgente (`circuits/preamp/gain_block.py`), netlist, disegni (il blocco e la scheda audio);
   - i casi noti del banco;
   - `run_tests.sh`, la regressione;
   - le righe del blocco di `fmea_l58b.csv`, da rileggere: il «Da riaprire se» di ADR-110.

## I vincoli

- Quelli di L58: comandi semplici, percorsi assoluti, script scritti con Write, `git add` un percorso alla
  volta, le forme d'onda non si committano, commit e push prima di ogni lista lunga.
- Le domande all'utente per nome, i colpi al jack in dB SPL. Prima di chiedere una conferma su un colpo,
  ricordargli i dB.
- Il controllo del worktree rifiuta i comandi composti (pipe con variabili, heredoc con git, percorsi con
  spazi): scriverli in uno script.

## CHIUSURA

1. `STATE.md`: L66 **fatto**, il prossimo **L64**; In breve; diario (la più vecchia delle tre in
   `STATE-STORIA.md`).
2. Riscrivi questo file per L64 («Nome della sessione: hi-fi preamp L64»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L66`; rimuovi il worktree; fermati.
