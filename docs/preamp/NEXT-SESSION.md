# Prompt per la sessione successiva — L73, la prova di spazio sul circuito di oggi

Nome della sessione: **hi-fi preamp L73** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L72 (2026-11-05, report `reports/2026-11-05-L72-testi-e-parti.md`). La Stax
> ha la sua finestra (ADR-121), la lista ammessa dei condensatori sta sotto P6 coi pezzi più grandi (ADR-122),
> le resistenze del guadagno sono allo 0,1 % (ADR-123), PR-30 è firmata sulla potenza del finale (ADR-124).
> L'ordine verso G1: **L73** → L74 → G1 (la tabella dei lotti di `STATE.md`; concordato dall'utente il 2026-11-04).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L73**, e si ferma.

## La regola dell'utente sul prototipo (PR-12, ADR-118)

«Il prototipo sarà molto costoso e quindi dobbiamo essere certi che funzioni perfettamente, l'unica cosa che
vogliamo valutare sul proto è la qualità audio percepita.» **Ciò che si può simulare si simula qui**, e lo
spazio si prova qui: «un problema di spazio scoperto al layout rimanda al progetto, quindi va scoperto prima di
congelare la topologia» (l'utente su NC-048, 2026-10-01).

## Che cosa fare

1. **Leggi prima**: `STATE.md`, `NONCOMPLIANCE.md` (**NC-048**, «Cosa serve per chiuderla»; NC-080 e NC-082,
   le impronte; NC-072, il rame), in `REQUIREMENTS.md` P4, P8 e la lista ammessa sotto P6, ADR-029, ADR-121,
   ADR-122, i report di L49a / L49b (`data/2026-10-09/L49a/`, `data/2026-10-09/L49b/`) e il rilievo R1 di
   `reports/2026-11-04-L65-architetto-avversariale.md`.
2. **La prova di spazio della scheda audio** sul netlist di oggi (653 parti), come L49a: piazzamento e
   sbroglio di prova nel contenitore di P8 (Modushop Pesante 3U), coi **sedici dissipatori WA-T220-101E** al
   potenziale di collettore (non devono toccarsi), i test point, e **le impronte sui pezzi più grandi della
   lista ammessa**: 26,5 × 7 × 16,5 mm a passo 22,5 (1 µF, ingressi e Stax), 31,5 × 15 × 26 a passo 27,5
   (4,7 µF della principale), 41,5 × 19 × 32 a passo 37,5 (10 µF di C_T e, se ammesso, del Singxer). Le impronte
   di prova stanno nello scratch del lotto: il sorgente le prende solo per decisione (G2).
3. **L'impronta della Stax distinta** da quella del Singxer (NC-080): se la prova lo permette, proponila.
4. **La prova dell'alimentatore** sul `psu.net` di oggi, come L49b (piste larghe: la memoria dell'utente).
5. **DRC** su entrambe; le altezze contro l'interno del contenitore (P8, 112 mm utili con l'Audiophonics,
   122 esterni col Pesante). Se qualcosa non entra, **non** si ritocca il circuito: si porta all'utente con le
   alternative coi numeri (restringere una finestra di ADR-122, un altro contenitore, un'altra disposizione).
6. **Le domande all'utente** si fanno per nome, coi numeri; ogni opzione con la sua temperatura / potenza
   contro il limite, a rete ±10 %.

## I vincoli

- **La macchina è un MacBook Air senza ventole**: al più **3 processi pesanti insieme** (simulazioni o
  Freerouting), con `nice -n 10`; prima di lanciare, `pgrep ngspice` e `pgrep java`. Se l'utente dice che
  girano altre sessioni, al più **2**.
- Comandi semplici, percorsi assoluti, script scritti con Write; il controllo del worktree rifiuta i comandi
  composti (`git` con altro, `cd` + `git`, `nice` dentro un `;` o un `&&`, il Python lungo in linea): `git -C
  <worktree>` un comando alla volta, il resto in uno script.
- Uno script di un lotto vecchio scrive nella **sua** cartella: non rieseguirlo per confronto; copiarlo.
- **Prima di iniziare e di nuovo prima di fare la domanda all'utente**: `git -C <worktree> fetch origin main`
  e `git -C <worktree> log --oneline HEAD..origin/main`. Se `main` ha già chiuso L73, fermarsi e dirlo.
- `git add` un percorso alla volta; **`.gitignore` prima** di ogni `git add` di una cartella dati.
- Prima di una domanda che fa aspettare l'utente, un commit di lavoro pushato.

## CHIUSURA

1. `STATE.md`: L73 **fatto**, il prossimo **L74**; le celle di In breve; il diario (la voce più vecchia
   delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L74 («Nome della sessione: hi-fi preamp L74»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L73`; rimuovi il worktree; fermati.
