# Prompt per la sessione successiva — L65, la revisione del dossier rigenerato

Nome della sessione: **hi-fi preamp L65** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L69b (2026-11-04: l'evidenza dell'alimentatore rifatta sul sorgente di
> ADR-116 in `data/2026-11-04/L69b/`, `build_dossier.py` «OK», i sabotaggi tutti caduti). Il dossier su
> `main` è di nuovo quello del circuito di oggi. L'ordine verso G1: **L65** → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L65**, e si
ferma.

## Che cosa fare

**La revisione del dossier rigenerato, prima del gate** (come L42 → L43 e L51 → L52; la riga di L65 nella
tabella dei lotti di `STATE.md`).

1. **Leggi prima**: `STATE.md`, `PRB.md` (il contratto: è l'ingresso di ogni revisione), il report di L69b
   (`reports/2026-11-04-L69b-dossier-alimentatore.md`) e `NONCOMPLIANCE.md`.
2. **La forma si decide con l'utente all'apertura**, ed è la prima cosa da chiedere: l'architetto
   avversariale cieco (`adversarial-architect`, lanciato nuovo e alla cieca rispetto ad altre revisioni),
   la lettura dell'utente, o tutte e due. Se l'utente ha già trovato un difetto, non cercarlo tu (il
   controllo cieco).
3. **Il dossier da rivedere** è `docs/preamp/dossier/index.html` su `main`; si rigenera con
   `/usr/bin/python3 docs/preamp/dossier/build_dossier.py --standalone <fuori dal repo>/dossier.html`
   (11 s). Il PDF, se l'utente lo vuole, in `/Users/roberto/Documents`, un PDF per documento.
4. **Gli esiti** in un report datato in `reports/`; i rilievi che diventano non conformità in
   `NONCOMPLIANCE.md`, ognuno col requisito, l'evidenza, la severità proposta e lo stato. Le scelte
   all'utente, per nome e coi numeri.

## I vincoli

- **La macchina è un MacBook Air senza ventole**: al più **3 simulazioni insieme**, con `nice -n 10`;
  prima di lanciare, `pgrep ngspice`. Se l'utente dice che girano altre sessioni, al più **2**.
- Comandi semplici, percorsi assoluti, script scritti con Write; il controllo del worktree rifiuta i
  comandi composti (`git` con altro, `cd` + `git`, `time -p`, `sed` con valori calcolati, gli script in
  linea): `git -C <worktree>` un comando alla volta, il resto in uno script.
- Uno script di un lotto vecchio scrive nella **sua** cartella: non rieseguirlo per confronto; copiarlo.
- I sabotaggi toccano i file per un istante: niente commit mentre girano.
- `git add` un percorso alla volta; `.gitignore` prima di ogni `git add` di una cartella dati.
- Le domande si fanno per nome; i colpi al jack in dB SPL; ogni opzione con la sua temperatura contro il
  limite.

## CHIUSURA

1. `STATE.md`: L65 **fatto**, il prossimo **G1**; le celle di In breve; il diario (la voce più vecchia
   delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per G1 («Nome della sessione: hi-fi preamp G1»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L65`; rimuovi il worktree; fermati.
