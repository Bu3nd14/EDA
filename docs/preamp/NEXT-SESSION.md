# Prompt per la sessione successiva — L67, la distorsione delle istanze a guadagno unitario sulla catena

Nome della sessione: **hi-fi preamp L67** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura del lotto del VAS a 126 °C (2026-11-02, NC-076 chiusa, ADR-111). L67 l'ha
> chiesto l'utente in quella sessione: «creare un lotto prima di L64 per la distorsione delle catene a
> guadagno unitario». L'ordine verso G1: **L67** → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L67**, e si
ferma.

## Che cosa fare

**NC-055** (maggiore, prima di G1). È la distorsione delle istanze a guadagno unitario, con la sorgente
peggiore e sulla catena. In L56 la sorgente reggeva (20 su 20, margine 2,7 dB); sulla catena **54 casi su
56** erano dentro. Fuori restavano la **principale col volume a metà, 0 e +3 dB, 20 kHz, 0,2 V, sorgente
2,5 kΩ**: 0,00133 / 0,00106 % contro 0,001. Da allora il blocco è cambiato: ADR-097, ADR-099 (i rimedi
del calore, i dissipatori) e ADR-111 (il limitatore del VAS a 36,5 + 18,7 Ω).

1. **Leggi prima**:
   - NC-055 in `NONCOMPLIANCE.md`, con gli avanzamenti di L53 e L56;
   - ADR-014, ADR-055, ADR-065, ADR-099, ADR-111;
   - `data/2026-10-12/L56/` (README, `rs/`, `catena/`) e `data/2026-10-12/L53/` (`rs/`, `catena/`);
   - `data/2026-11-02/L66/README.md` (il banco di V4 a caldo e le varianti del blocco).
2. **Il caso noto prima di ogni numero nuovo**: il banco della catena di L56 sul blocco di allora deve
   ridare le sue cifre (i due casi fuori, 0,00133 / 0,00106 %).
3. **La catena e la sorgente rifatte sul blocco di oggi** (`spice/preamp/`), a 27 °C e a caldo (ogni
   giunzione alla sua temperatura, il metodo di `v4caldo.py`). Tutte e tre le uscite, il carico di V4.
4. **Se un caso resta fuori**: il rimedio con l'utente, coi numeri. Per esempio il cascode pilotato o R_F
   adattata (le strade dell'architetto in L52), oppure un'accettazione dichiarata. Ogni opzione col suo
   costo sugli altri requisiti (margine di fase, rumore, P7).
5. **Se il circuito cambia**:
   - sorgente, netlist, disegni;
   - i casi noti dei banchi;
   - `run_tests.sh` e la regressione;
   - le righe della FMEA del blocco (`data/2026-11-02/L66/fmea_l66.csv`) da rileggere.

## I vincoli

- Quelli di L58 e del lotto del VAS:
  - comandi semplici, percorsi assoluti, script scritti con Write;
  - `git add` un percorso alla volta;
  - commit e push prima di ogni lista lunga.
- **Le forme d'onda e le corse grezze non si committano**: prima di ogni `git add` di una cartella dati,
  `.gitignore` deve coprire `run/` e le cartelle delle corse (`regressione/*/*/`). Nel lotto del VAS ~260
  MB sono finiti sul ramo per questo.
- **I casi lenti si corrono da soli e corti** (limitations #75: R120 in corto a 0,6 s, mai in una lista
  con `-P`).
- Le domande all'utente si fanno per nome; i colpi al jack in dB SPL; le distorsioni in dB contro il
  tetto.
- Il controllo del worktree rifiuta i comandi composti (cicli, pipe con variabili, heredoc con git,
  `xargs` con `find`): scriverli in uno script.

## CHIUSURA

1. `STATE.md`: L67 **fatto**, il prossimo **L64**; le celle di In breve; il diario (la voce più vecchia
   delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L64 («Nome della sessione: hi-fi preamp L64»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L67`; rimuovi il worktree; fermati.
