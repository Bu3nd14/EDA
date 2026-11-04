# Prompt per la sessione successiva — L70, le due semplificazioni

Nome della sessione: **hi-fi preamp L70** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura della revisione dell'architetto sul dossier rigenerato (2026-11-04, report
> `reports/2026-11-04-L65-esiti-architetto.md`). Fra le semplificazioni proposte dall'architetto, l'utente ha
> scelto di studiarne **due prima di G1**. L'ordine verso G1: **L70** → L71 → L72 → L73 → L74 → G1 (la tabella
> dei lotti di `STATE.md`; l'ordine concordato dall'utente il 2026-11-04: «concordo con la sequenza»).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L70**, e si ferma.

## La regola dell'utente sul prototipo (PR-12, ADR-118)

«Il prototipo sarà molto costoso e quindi dobbiamo essere certi che funzioni perfettamente, l'unica cosa che
vogliamo valutare sul proto è la qualità audio percepita.» Dopo il prototipo si cambiano solo i condensatori
di accoppiamento e le resistenze critiche, dissaldandoli. **Ciò che si può simulare si simula qui.**

## Che cosa fare

1. **Leggi prima**: `STATE.md`, `PRB.md`, il report degli esiti e quello verbatim dell'architetto
   (`reports/2026-11-04-L65-architetto-avversariale.md`: «Le semplificazioni proposte», righe S1 e S2, e il
   rilievo R12), `NONCOMPLIANCE.md` (NC-073, NC-077), ADR-102, ADR-109, ADR-115, ADR-116.
2. **S2, togliere il rivelatore di rete**: resta il sorvegliante dei rail a 13,5 V. Da misurare sul banco del
   temporizzatore di oggi (`data/2026-11-04/L69b/`, copiato, non rieseguito sul posto): la perdita di rete e
   lo spegnimento al jack (l'architetto legge 87 µV con U501 spento) e il buco di rete di 20 ms che oggi
   toglie la musica per ~613 ms (dossier, sezione 25). Che cosa dice P9 (b) senza il rivelatore.
3. **S1, la ritenuta dopo un guasto di rail sostituita da fusibili**: un fusibile per rail sul secondario di
   T1 e R550 / R551 a film antifiamma, al posto di Q513 / Q514, R581–R585, C552–C555 e parte di U515. Da
   misurare: l'I²t del fusibile contro l'impulso di R550 (NC-073), il toroidale acceso fino al frontale dopo un
   guasto, quante righe alte della FMEA cadono (l'architetto stima ~25 su 47).
4. **Le opzioni all'utente coi numeri**, per nome: i colpi al jack in dB SPL, ogni parte con la sua temperatura
   contro il limite, a rete ±10 %. Se una semplificazione è scelta: ADR, sorgente, netlist, disegni, FMEA,
   `run_tests.sh`.

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

1. `STATE.md`: L70 **fatto**, il prossimo **L71**; le celle di In breve; il diario (la voce più vecchia
   delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L71 («Nome della sessione: hi-fi preamp L71»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L70`; rimuovi il worktree; fermati.
