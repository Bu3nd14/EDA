# Prompt per la sessione successiva — L73b, le quattro strade misurate

Nome della sessione: **hi-fi preamp L73b** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L73a (2026-11-05, report `reports/2026-11-05-L73a-prova-di-spazio-due-strati.md`,
> dati e script `data/2026-11-05/L73/`). La scheda audio di oggi si sbroglia a due strati **al limite**
> (392,6 × 198,3 mm, riempimento 0,46, 1 connessione aperta, 2 distanze di 0,248 mm) e nel Pesante 3U a fondo
> piatto **mancano 18,3 mm**. L'ordine verso G1: **L73b** → L74 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L73b**, e si ferma.

## Che cosa ha detto l'utente (2026-11-05)

«Se non ci sono margini, dobbiamo considerare che lo sbroglio vero con massa a stella e piani di massa
potrebbe peggiorare le cose, no? Al limite pensiamo a due case separati o ad aumentare i layer o a creare
daughter boards.» Alla domanda su quali strade misurare ha scelto **tutte e quattro**. E: «tieni d'occhio i
token residui e se serve spezza il lavoro» — se il lotto non sta in una sessione, si spezza (L73b1, L73b2).

## Che cosa fare

1. **Leggi prima**: `STATE.md`, il report di L73a, `data/2026-11-05/L73/README.md`, NC-048 nel registro, P4,
   P8 e PR-27 (PRB). Gli script di L73a si **copiano** in `data/<data>/L73b/script/`, non si rieseguono sul
   posto.
2. **Lo sbroglio dell'alimentatore** di oggi (a L73a era in corsa alla chiusura): `script/psu/run.sh` a 110
   mm, logica 3,0, **piste larghe** (memoria dell'utente: le più larghe compatibili; prova 1,0 / 1,5 mm per
   la classe senza piedini fini), DRC 0 / 0 come L49b.
3. **Le quattro strade**, ognuna con la sua prova e il **margine** che lascia (in mm e in riempimento,
   contro lo 0,46 di oggi; la prova di L49a, più rilassata, era ~0,38):
   - **contenitore più profondo**: l'Hifi2000 Slimline 3U 350 (Audiophonics, letto il 2026-11-05: interni
     415 × 350 × 120, esterni 435 × 361 × 122 mm col frontale da 10 mm, ~135 €), dentro P8. La pianta di
     `floorplan.py` coi 350 mm, e quanto può crescere la scheda audio;
   - **quattro strati**: lo sbroglio della scheda audio con gli strati interni a massa e alimentazioni (in
     `make_board.py` il numero di strati, in `route.py` / Freerouting le reti sui piani); la DRC e la misura
     a parità di contorno, poi più piccola;
   - **scheda figlia**: le quattro uscite fisse (gruppi F1 / F2, ~256 parti) su una seconda scheda; le due
     superfici e le altezze (le bande di `heights.py`) contro i 115–120 mm interni. Va contro P4: dirlo;
   - **due contenitori**: alimentatore e toroidali a parte; la scheda audio con tutta la profondità, la
     distanza dei toroidali dagli ingressi (P3). Va contro PR-27, il contratto firmato: dirlo.
4. **Il rilievo dei transistor**: `Q_NPN` / `Q_PNP` (piedini B / C / E) non si collegano alle piazzole 1 / 2
   / 3 delle impronte SOT-23 / SOT-223 / TO-220 (L73a, `script/pinmap.py`; la scheda di L49a ne aveva 64
   scollegati). Proporre all'utente di registrarlo come non conformità, con la severità che sceglie lui
   (proposta: maggiore, prima di G2).
5. **La domanda all'utente**, per nome e coi numeri: le quattro strade a confronto (margine, che cosa cambia
   nei requisiti, costo). Ogni opzione con la temperatura / potenza contro il limite a rete ±10 % quando
   cambia (un contenitore più grande o separato scalda meno: dirlo coi numeri di P5).
6. Se la scelta tocca P4, P8 o PR-27: una ADR, e il PRB solo con la firma dell'utente.

## I vincoli

- **La macchina è un MacBook Air senza ventole**: al più **3 processi pesanti insieme** (simulazioni o
  Freerouting), con `nice -n 10`; prima di lanciare, `pgrep ngspice` e `pgrep java`. Se l'utente dice che
  girano altre sessioni, al più **2**. `kinet2pcb` sulla scheda audio impiega ~4 minuti.
- Freerouting scrive il suo log in `en/` nella cartella corrente: lanciarlo da una cartella ignorata.
- Comandi semplici, percorsi assoluti, script scritti con Write; il controllo del worktree rifiuta i comandi
  composti (`git` con altro, `cd` + `git`, `nice` dentro un `;` o un `&&`, il Python lungo in linea): `git -C
  <worktree>` un comando alla volta, il resto in uno script.
- **Prima di iniziare e di nuovo prima di fare la domanda all'utente**: `git -C <worktree> fetch origin main`
  e `git -C <worktree> log --oneline HEAD..origin/main`. Se `main` ha già chiuso L73b, fermarsi e dirlo.
- `git add` un percorso alla volta; **`.gitignore` prima** di ogni `git add` di una cartella dati.
- Prima di una domanda che fa aspettare l'utente, un commit di lavoro pushato.

## CHIUSURA

1. `STATE.md`: L73b **fatto**, il prossimo (L74, o il lotto che la scelta dell'utente apre); le celle di In
   breve; il diario (la voce più vecchia delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per il lotto successivo («Nome della sessione: hi-fi preamp <lotto>»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L73b`; rimuovi il worktree; fermati.
